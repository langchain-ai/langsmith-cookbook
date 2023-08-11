# LangSmith Cookbook

This repository stores code tutorials showing different ways to get more out of [LangSmith](https://smith.langchain.com/). LangSmith is a platform that helps you debug, test, evaluate, and monitor your LLM applications.

These cookbook recipes are meant to complement the [LangSmith Documentation](https://docs.smith.langchain.com/) by showing common use cases and tactics within "end-to-end" examples, which you can take and adapt to your needs. The existing examples are written in python, but we are working to build out our JS/TS examples as well!

If you have any specific requests or common patterns you'd like to see highlighted, create a GitHub issue or let one of the core LangChain devs know. We also welcome contributions!

## Using Feedback

The following walkthroughs show ways to capture and use [feedback](https://docs.smith.langchain.com/evaluation/capturing-feedback) on runs using LangSmith. This is useful for anything from app monitoring, to personalization, to evaluation and finetuning.

- The [Streamlit Chat App](./feedback-examples/streamlit/README.md) contains a minimal example of a Chat application that captures user feedback and shares traces of the chat application.
    - The [vanilla_chain.py](./feedback-examples/streamlit/vanilla_chain.py) contains an LLMChain that powers the chat application.
    - The [expression_chain.py](./feedback-examples/streamlit/expression_chain.py) contains an equivalent chat chain defined exclusively with [LangChain expressions](https://python.langchain.com/docs/guides/expression_language/).

## Testing & Evaluation

The following walkthroughs demonstrate ways to evaluate common application scenarios.
- The [Q&A System Correctness](./testing-examples/qa-correctness.ipynb) notebook walks through creating a dataset for a retrieval-augmented Q&A pipeline, evaluating the responses for correctness, and using LangSmith to iterate and improve.
- The [Evaluating Q&A Systems with Dynamic Data](./testing-examples/testing_dynamic_data.ipynb) notebook shows how to evaluate a Q&A pipeline when the underlying data may change over time by using an evaluator that dereferences a label at evaluation time.

## Tracing your code

Setting up tracing in LangChain is as simple as setting a couple environment variables. We've also added support through the LangSmith SDK to trace applications that don't rely on LangChain. The following walkthroughs addresss common questions around tracing your code!
- The [Tracing without LangChain](./tracing-examples/tracing_without_langchain.ipynb) notebook uses the python SDK's `@traceable` decorator to trace and tag run in an app that does not use depend on LangChain.
