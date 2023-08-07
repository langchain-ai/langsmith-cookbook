# LangSmith Cookbook

This repository stores code examples showing different ways to get more out of [LangSmith](https://smith.langchain.com/). These are meant to complement the [LangSmith Documentation](https://docs.smith.langchain.com/) by showing common use cases, tactics, and integrations. If you have found any common patterns that suit your needs, we'd love to add them to these examples.

Guide:
- 🦜🧬 means it uses the [LangChain Expression Language](https://python.langchain.com/docs/guides/expression_language/) (LCEL)

## Testing & Evaluation
For simple examples checking for hallucinations and faithfulness in the output, see one of the following notebooks:
- For an example evaluating a `RetrievalQA` chain, check out [Checking for Hallucinations in a RetrievalQA Chain](testing-examples/qa-system/qa-system-retrievalqa.ipynb)
- For an example evaluating a retrieval Q&A chain built using langchain expressions, check out [Checking for Hallucinations in a Q&A System](testing-examples/qa-system/qa-system-lcel.ipynb) [🦜🧬]

## Using Feedback

The following examples show different ways to use 
- The [Streamlit Chat App](./feedback-examples/streamlit/README.md) contains a minimal example of a Chat application that captures user feedback and shares traces of the chat application.
    - The [vanilla_chain.py](./feedback-examples/streamlit/vanilla_chain.py) contains an LLMChain that powers the chat application
    - The [expression_chain.py](./feedback-examples/streamlit/expression_chain.py) contains an equivalent chat chain defined exclusively in LCEL [🦜🧬]