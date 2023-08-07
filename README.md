# LangSmith Cookbook

This repository stores code examples showing different ways to get more out of [LangSmith](https://smith.langchain.com/). LangSmith is a platform that helps you debug, test, evaluate, and monitor your LLM applications.


These cookbook recipes are meant to complement the [LangSmith Documentation](https://docs.smith.langchain.com/) by showing common use cases, tactics, and integrations you can adapt to your needs. Most of the existing examples are written in python, but we are working to build out our JS/TS examples as well. 

If you have any specific requests or common patterns you'd like to see highlighted, let one of the core LangChain devs know or contribute an example yourself!

## Using Feedback

The following examples show ways to capture and use [feedback](https://docs.smith.langchain.com/evaluation/capturing-feedback) on runs using LangSmith. This is useful for anything from app monitoring, to personalization, to evaluation and finetuning.

- The [Streamlit Chat App](./feedback-examples/streamlit/README.md) contains a minimal example of a Chat application that captures user feedback and shares traces of the chat application.
    - The [vanilla_chain.py](./feedback-examples/streamlit/vanilla_chain.py) contains an LLMChain that powers the chat application
    - The [expression_chain.py](./feedback-examples/streamlit/expression_chain.py) contains an equivalent chat chain defined exclusively with [LangChain expressions](https://python.langchain.com/docs/guides/expression_language/).




There is also a brief tutorial on tracing LLM apps to LangSmith without LangChain that can be found in [Tracing Without Langchain](./tracing-examples/tracing_without_langchain.ipynb) guide.