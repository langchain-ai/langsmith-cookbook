# LangSmith Cookbook

This repository stores code tutorials showing different ways to get more out of [LangSmith](https://smith.langchain.com/). LangSmith is a platform that helps you debug, test, evaluate, and monitor your LLM applications.

These cookbook recipes are meant to complement the [LangSmith Documentation](https://docs.smith.langchain.com/) by showing common use cases and tactics within "end-to-end" examples, which you can take and adapt to your needs.

If you have any specific requests or common patterns you'd like to see highlighted, create a GitHub issue or let one of the core LangChain devs know. We also welcome contributions!

## Using Feedback

The following walkthroughs show ways to capture and use [feedback](https://docs.smith.langchain.com/evaluation/capturing-feedback) on runs using LangSmith. This is useful for anything from app monitoring, to personalization, to evaluation and finetuning.

- The [Streamlit Chat App](./feedback-examples/streamlit/README.md) contains a minimal example of a Chat application that captures user feedback and shares traces of the chat application.
    - The [vanilla_chain.py](./feedback-examples/streamlit/vanilla_chain.py) contains an LLMChain that powers the chat application.
    - The [expression_chain.py](./feedback-examples/streamlit/expression_chain.py) contains an equivalent chat chain defined exclusively with [LangChain expressions](https://python.langchain.com/docs/guides/expression_language/). 
- The [Next.js Chat App](./feedback-examples/nextjs/README.md) contains a TypeScript tracing and user feedback example.
    - You can [check out a deployed demo version here](https://langsmith-cookbook.vercel.app/).

## Testing & Evaluation

### Python Examples
The following walkthroughs demonstrate ways to evaluate common application scenarios.
- The [Q&A System Correctness](./testing-examples/qa-correctness/qa-correctness.ipynb) notebook walks through creating a dataset for a retrieval-augmented Q&A pipeline, evaluating the responses for correctness, and using LangSmith to iterate and improve.
- The [Evaluating Q&A Systems with Dynamic Data](./testing-examples/dynamic-data/testing_dynamic_data.ipynb) notebook shows how to evaluate a Q&A pipeline when the underlying data may change over time by using an evaluator that dereferences a label at evaluation time.
- The [Comparison Evals](./testing-examples/comparing-runs/comparing-qa.ipynb) notebook shows how to use labeled preference scoring to help compare two versions of a system and choose the preferred outputs.
- For examples using LangSmith in your testing framework, such as with pytest, you can reference the following:
    - The [LangSmith in Pytest](./testing-examples/pytest/) recipe shows how to directly evaluate your chain or LLM on a dataset and then define your own pass/fail criteria.
    - The [Unit Testing with Pytest](./testing-examples/pytest-ut/) recipe shows how to write individual unit tests so that feedback and traces are all organized by test suite.
- The [Evaluating Existing Runs](./testing-examples/evaluate-existing-test-project/evaluate_runs.ipynb) notebook demonstrates how to evaluate or add automated feedback to existing run traces. This is useful for adding additional evaluation metrics after already conducting a test run, for adding AI-assisted feedback in monitoring projects, and for evaluating runs logged outside of python.

### Typescript / JS Examples

LangSmith supports logging evaluation feedback to any run. The following walkthroughs show how to incorporate LangSmith in your TS/JS testing and evaluation workflows.
- The [Evaluating JS Chains in Python](./typescript-testing-examples/eval-in-python/) walkthrough shows how to run your JS chain over a LangSmith dataset and then evaluate the resulting traces in python, using a custom evaluator to test the structured results. This applies the technique presented in [Evaluating Existing Runs](./testing-examples/evaluate-existing-test-project/evaluate_runs.ipynb).
- The [Logging Assertions as Feedback](./typescript-testing-examples/simple-test/) example shows a how to quickly store your existing CI test assertions as LangSmith feedback. This lets you store annotated traces of your test runs in LangSmith without requiring many changes to your existing test system.


## Tracing your code

Setting up tracing in LangChain is as simple as setting a couple environment variables. We've also added support through the LangSmith SDK to trace applications that don't rely on LangChain. The following walkthroughs address common questions around tracing your code!
- The [Tracing without LangChain](./tracing-examples/traceable/tracing_without_langchain.ipynb) notebook uses the Python SDK's `@traceable` decorator to trace and tag run in an app that does not use depend on LangChain.
- The [REST API](./tracing-examples/rest/rest.ipynb) notebook walks through logging runs to LangSmith directly using the REST API, covering how to log LLM and chat model runs for token counting, and how to nest runs. The run logging spec can be found in the [LangSmith SDK repository](https://github.com/langchain-ai/langsmith-sdk/blob/main/openapi/openapi.yaml).


## Exporting data for fine-tuning

The [LangSmith docs](https://docs.smith.langchain.com/tracing/use-cases/export-runs/local) contains examples of ways to filter and query the runs database for downstream tasks. The examples below share recipes on how to then use that data for fine-tuning.
- The [OpenAI Fine-Tuning](./fine-tuning-examples/export-to-openai/fine-tuning-on-chat-runs.ipynb) recipe shows a fast, simple way to list LLM runs in a project and convert them to OpenAI's fine-tuning format.