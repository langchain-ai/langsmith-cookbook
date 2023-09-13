---
sidebar_label: Feedback
sidebar_position: 6 
---
# Feedback

The following walkthroughs show ways to capture and use [feedback](https://docs.smith.langchain.com/evaluation/capturing-feedback) on runs using LangSmith. This is useful for anything from app monitoring, to personalization, to evaluation and finetuning.

- [Streamlit Chat App](./streamlit/README.md) contains a minimal example of a Chat application that captures user feedback and shares traces of the chat application.
    - The [vanilla_chain.py](./streamlit/vanilla_chain.py) contains an LLMChain that powers the chat application.
    - The [expression_chain.py](./streamlit/expression_chain.py) contains an equivalent chat chain defined exclusively with [LangChain expressions](https://python.langchain.com/docs/guides/expression_language/). 
- [Next.js Chat App](./nextjs/README.md) contains a TypeScript tracing and user feedback example.
    - You can [check out a deployed demo version here](https://langsmith-cookbook.vercel.app/).
- The [Building an Algorithmic Feedback Pipeline](./algorithmic-feedback/algorithmic_feedback.ipynb) notebook guides you through automating feedback metrics for your LLM deployment, enabling advanced monitoring and performance tuning with LangSmith.