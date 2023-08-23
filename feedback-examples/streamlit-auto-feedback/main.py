"""Example Streamlit chat UI that exposes a Feedback button and link to LangSmith traces."""

from concurrent.futures import ThreadPoolExecutor

import streamlit as st
from critique_chain import get_critique_chain
from expression_chain import get_expression_chain
from langchain import callbacks
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain.callbacks.tracers.run_collector import \
    RunCollectorCallbackHandler
from langchain.memory import (ConversationBufferMemory,
                              StreamlitChatMessageHistory)
from langchain.schema.runnable import RunnableConfig
from langsmith import Client
from streamlit_feedback import streamlit_feedback

client = Client()

st.set_page_config(
    page_title="Chat LangSmith",
    page_icon="🦜",
)
"# Chat🦜🛠️"
# Initialize State
if "trace_link" not in st.session_state:
    st.session_state.trace_link = None
if "run_id" not in st.session_state:
    st.session_state.run_id = None
st.sidebar.markdown(
    """
# Menu
"""
)

if st.session_state.get("feedback_executor") is None:
    st.session_state.feedback_executor = ThreadPoolExecutor(max_workers=1)

# Add a button to choose between llmchain and expression chain
_DEFAULT_SYSTEM_PROMPT = (
    "You are a life coach."
)
system_prompt = st.sidebar.text_area(
    "Custom Instructions",
    _DEFAULT_SYSTEM_PROMPT,
    help="Custom instructions to provide the language model to determine style, personality, etc.",
)
system_prompt = system_prompt.strip().replace("{", "{{").replace("}", "}}")
chain_type = st.sidebar.radio(
    "Choose a chain type",
    ("Expression Language Chain", "LLMChain"),
    help="Choose whether to use a vanilla LLMChain or an equivalent chain built using LangChain Expression Language.",
)
memory = ConversationBufferMemory(
    chat_memory=StreamlitChatMessageHistory(key="langchain_messages"),
    return_messages=True,
    memory_key="chat_history",
)
# Create Chain

chain = get_expression_chain(system_prompt, memory)
critique_chain = get_critique_chain(memory, client)

if st.sidebar.button("Clear message history"):
    print("Clearing message history")
    memory.clear()
    st.session_state.trace_link = None
    st.session_state.run_id = None


# Display chat messages from history on app rerun
# NOTE: This won't be necessary for Streamlit 1.26+, you can just pass the type directly
# https://github.com/streamlit/streamlit/pull/7094
def _get_openai_type(msg):
    if msg.type == "human":
        return "user"
    if msg.type == "ai":
        return "assistant"
    if msg.type == "chat":
        return msg.role
    return msg.type


for msg in st.session_state.langchain_messages:
    streamlit_type = _get_openai_type(msg)
    avatar = "🦜" if streamlit_type == "assistant" else None
    with st.chat_message(streamlit_type, avatar=avatar):
        st.markdown(msg.content)

run_collector = RunCollectorCallbackHandler()
runnable_config = RunnableConfig(
    callbacks=[run_collector],
    tags=["Streamlit Chat"],
)
critique_config = RunnableConfig(
    callbacks=[callbacks.LangChainTracer(project_name="streamlit-critic")],
    tags=["Auto-Critic"],
)
if st.session_state.trace_link:
    st.sidebar.markdown(
        f'<a href="{st.session_state.trace_link}" target="_blank"><button>Latest Trace: 🛠️</button></a>',
        unsafe_allow_html=True,
    )


def _reset_feedback():
    st.session_state.feedback_update = None
    st.session_state.feedback = None


if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)
    _reset_feedback()
    # call critique_chain with threadpool executor
    if st.session_state.get("run_id"):
        run_id = st.session_state.run_id
        print("Submitting critique chain")
        st.session_state.feedback_executor.submit(
            critique_chain.invoke, {"input": prompt, "run_id": run_id}, critique_config
        )
    else:
        print("No run id, skipping critique chain")
    with st.chat_message("assistant", avatar="🦜"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in chain.stream({"input": prompt}, config=runnable_config):
            full_response += chunk.content
            message_placeholder.markdown(full_response + "▌")
        memory.save_context({"input": prompt}, {"output": full_response})
        message_placeholder.markdown(full_response)
        # The run collector will store all the runs in order. We'll just take the root and then
        # reset the list for next interaction.
        run = run_collector.traced_runs[0]
        run_collector.traced_runs = []
        st.session_state.run_id = run.id
        wait_for_all_tracers()
        # Requires langsmith >= 0.0.19
        url = client.share_run(run.id)
        # Or if you just want to use this internally
        # without sharing
        # url = client.read_run(run.id).url
        st.session_state.trace_link = url

# Optionally add a thumbs up/down button for feedback
if st.session_state.get("run_id"):
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        key=f"feedback_{st.session_state.run_id}",
    )
    scores = {"👍": 1, "👎": 0}
    if feedback:
        score = scores[feedback["score"]]
        feedback = client.create_feedback(st.session_state.run_id, "user_score")
        st.session_state.feedback = {"feedback_id": str(feedback.id), "score": score}

# Prompt for more information, if feedback was submitted
if st.session_state.get("feedback"):
    feedback = st.session_state.get("feedback")
    feedback_id = feedback["feedback_id"]
    score = feedback["score"]
    if score == 0:
        # Add text input with a correction box
        correction = st.text_input(
            label="What would the correct or preferred response have been?",
            key=f"correction_{feedback_id}",
        )
        if correction:
            st.session_state.feedback_update = {
                "correction": {"desired": correction},
                "feedback_id": feedback_id,
            }
    if score == 1:
        comment = st.text_input(
            label="Anything else you'd like to add about this response?",
            key=f"comment_{feedback_id}",
        )
        if comment:
            st.session_state.feedback_update = {
                "comment": comment,
                "feedback_id": feedback_id,
            }
# Update the feedback if additional information was provided
if st.session_state.get("feedback_update"):
    feedback_update = st.session_state.get("feedback_update")
    feedback_id = feedback_update.pop("feedback_id")
    client.update_feedback(feedback_id, **feedback_update)
    # Clear the comment or correction box
    _reset_feedback()
