import logging
from typing import Optional

import streamlit as st

st.set_page_config(
    page_title="Realtime Evaluation of Production Runs",
    page_icon="🦜️️🛠️",
    initial_sidebar_state="collapsed",
)

from chain import CHAIN, MEMORY
from langchain.callbacks import tracing_v2_enabled
from langchain.callbacks.tracers.evaluation import EvaluatorCallbackHandler
from langchain.evaluation import load_evaluator
from langchain.schema import get_buffer_string
from langsmith import Client
from langsmith.evaluation import EvaluationResult, RunEvaluator
from langsmith.schemas import Example, Run

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Client()


st.subheader(
    "🦜🛠️ Ask questions about LangSmith. "
    "We'll evaluate for relevance and faithfulness to the retrieved docs."
)

# Add a button to choose between llmchain and expression chain

if st.sidebar.button("Clear message history"):
    MEMORY.clear()

messages = st.session_state.get("langchain_messages", [])
for msg in messages:
    avatar = "🦜" if msg.type == "ai" else None
    with st.chat_message(msg.type, avatar=avatar):
        st.markdown(msg.content)


class RelevanceEvaluator(RunEvaluator):
    def __init__(self):
        self.evaluator = load_evaluator(
            "score_string", criteria="relevance", normalize_by=10
        )

    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> EvaluationResult:
        try:
            text_input = (
                get_buffer_string(run.inputs["chat_history"])
                + f"\nhuman: {run.inputs['query']}"
            )
            result = self.evaluator.evaluate_strings(
                input=text_input, prediction=run.outputs["output"]
            )
            return EvaluationResult(
                **{"key": "relevance", "comment": result.get("reasoning"), **result}
            )
        except Exception as e:
            return EvaluationResult(key="relevance", score=None, comment=repr(e))


class FaithfulnessEvaluator(RunEvaluator):
    def __init__(self):
        self.evaluator = load_evaluator(
            "labeled_score_string",
            criteria={
                "faithfulness": """
Score 1: The answer directly contradicts the information provided in the reference docs.
Score 3: The answer contains a mix of correct information from the reference docs and incorrect or unverifiable information not found in the docs.
Score 5: The answer is mostly aligned with the reference docs but includes extra information that, while not contradictory, is not verified by the docs.
Score 7: The answer aligns well with the reference docs but includes minor, commonly accepted facts not found in the docs.
Score 10: The answer perfectly aligns with and is fully entailed by the reference docs, with no extra information."""
            },
            normalize_by=10,
        )

    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> EvaluationResult:
        try:
            retrieve_docs_run = [
                run for run in run.child_runs if run.name == "RetrieveDocs"
            ][0]
            docs_string = f'Reference docs:\n<DOCS>\n{retrieve_docs_run.outputs["documents"]}</DOCS>'
            input_query = run.inputs["query"]
            prediction = run.outputs["output"]
            result = self.evaluator.evaluate_strings(
                input=input_query,
                prediction=prediction,
                reference=docs_string,
            )
            return EvaluationResult(
                **{"key": "faithfulness", "comment": result.get("reasoning"), **result}
            )
        except Exception as e:
            return EvaluationResult(key="faithfulness", score=None, comment=repr(e))


evaluation_callback = EvaluatorCallbackHandler(
    evaluators=[RelevanceEvaluator(), FaithfulnessEvaluator()]
)
if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant", avatar="🦜"):
        message_placeholder = st.empty()
        full_response = ""
        # Define the basic input structure for the chains
        input_dict = {
            "query": prompt,
        }
        input_dict.update(MEMORY.load_memory_variables({"query": prompt}))

        with tracing_v2_enabled() as cb:
            for chunk in CHAIN.stream(
                input_dict,
                config={
                    "tags": ["Streamlit Evaluation"],
                    "callbacks": [evaluation_callback],
                },
            ):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            MEMORY.save_context(input_dict, {"output": full_response})
            try:
                url = cb.get_run_url()
                st.markdown(
                    f"View trace in [🦜🛠️ LangSmith]({url})",
                    unsafe_allow_html=True,
                )
            except Exception:
                logger.exception("Failed to get run URL.")
        message_placeholder.markdown(full_response)
