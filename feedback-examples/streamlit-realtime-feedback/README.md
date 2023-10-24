# Realtime Hallucination Evaluation

This tutorial shows how to catch model hallucinations in production using a custom run evaluator. This is a great way to
monitor the behavior of your RAG application to make sure the information in the final response is concordant with the retrieved knowledge.

To do this, we create custom evaluator(s) (in our case, they both wrap [Scoring Evaluators](https://python.langchain.com/docs/guides/evaluation/string/scoring_eval_chain)) and register them as callbacks using the [EvaluatorCallbackHandler](https://api.python.langchain.com/en/latest/callbacks/langchain.callbacks.tracers.evaluation.EvaluatorCallbackHandler.html), which runs them in the background whenever your application is triggered to avoid blocking the main execution.


Below is a quick walkthrough.


## Prerequisites

The requirements for this streamlit application are listed in the [requirements.txt](./requirements.txt) file. 

(Recommended) First, create and activate virtual environment.
```bash
python -m pip -U virtualenv pip
python -m virtualenv .venv
. .venv
```

Then install the app requirements.
```bash
python -m pip install -r requirements.txt
```

Next, configure your API keys for LangSmith and the LLM provider (we are using OpenAI here).

```bash
export OPENAI_API_KEY=your-openai-api-key
export LANGCHAIN_API_KEY=your-langsmith-api-key
```

Finally, start the streamlit application.

```bash
python -m streamlit run main.py
```

You can then ask the chat bot questions about LangSmith. Click the "View trace in 🦜🛠️ LangSmith" links after it responds to view the resulting trace. The evaluation feedback will be automatically populated for the run showing the predicted score.


## Evaluator definitions

In this example, we define two evaluators: a relevance evaluator and a faithfulness evaluator.

The relevance evaluator is instructed to grade the chat bot's response, taking into account the user's question and chat history. 

```python
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

```

The evaluator selects the appropriate keys from the trace inputs and outputs and formats them in a way that is useful for the wrapped evaluator. One situation where this is useful is for when your bot becomes overly influenced by the content in the retrieved documents (e.g., a form of benign prompt injection). Since this evaluator does not consider the retrieved documents in its grade, it is easier for it to detect the shift. 

The second evaluator is a "faithfulness" evaluator, which penalizes cases where the chat bot includes contradictorhy or off-topic information in its response.

```python

class FaithfulnessEvaluator(RunEvaluator):
    def __init__(self):
        self.evaluator = load_evaluator(
            "labeled_score_string",
            criteria={
                "faithfulness": """
Score 1: The answer directly contradicts the reference docs.
Score 3: The answer mentions a topic from the reference docs, but veers off-topic or misinterprets the source.
Score 5: The answer addresses the reference docs but includes some inaccuracies or misconceptions.
Score 7: The answer aligns with the reference but has minor errors or omissions.
Score 10: The answer is completely accurate and aligns perfectly with the reference docs."""
            },
            normalize_by=10, # convert scores to a scale from 0 to 1
        )

    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> EvaluationResult:
        try:
            retrieve_docs_run = [
                run for run in run.child_runs if run.name == "RetrieveDocs"
            ][0]
            docs_string = retrieve_docs_run.outputs["documents"]
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
```

Since the retriever isn't called at the top level of the trace, this evaluator selects the appropriate run (span) by selecting the configured name of that component. It then takes the formatted string containing the documents' page content, user query, and final chat bot response and passes these to the evalutor for grading.


## Use in LangChain

Once these are defined, we can add them to a callback handler and use it whenever we call our RAG chain by passing `config={"callbacks": [evaluation_callback]}` to any of the invoke, batch, or stream methods (or any of their async variants).

```python
evaluation_callback =  EvaluatorCallbackHandler(
    evaluators=[RelevanceEvaluator(), FaithfulnessEvaluator()]
)
CHAIN.stream(
        input_dict,
        config={
            "callbacks": [evaluation_callback],
        },
    ):
```

The evaluations will be run on an separate thread whenever the execution completes to avoid adding latency to the program and to ensure that any errors that occur during evaluation do not interrupt the program.
