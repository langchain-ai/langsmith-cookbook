---
sidebar_label: Feedback
sidebar_position: 6 
---
# Feedback

Harness user [feedback](https://docs.smith.langchain.com/evaluation/capturing-feedback) and other signals to improve, monitor, and personalize your applications:

- [Streamlit Chat App](./streamlit/README.md): a minimal chat app that captures user feedback and shares traces of the chat application.
    - The [vanilla_chain.py](./streamlit/vanilla_chain.py) contains an LLMChain that powers the chat application.
    - The [expression_chain.py](./streamlit/expression_chain.py) contains an equivalent chat chain defined exclusively with [LangChain expressions](https://python.langchain.com/docs/guides/expression_language/). 
- [Next.js Chat App](./nextjs/README.md): explore a simple TypeScript chat app demonstrating tracing and feedback capture.
    - You can [check out a deployed demo version here](https://langsmith-cookbook.vercel.app/).
- [Building an Algorithmic Feedback Pipeline](./algorithmic-feedback/algorithmic_feedback.ipynb) Automate feedback metrics for advanced monitoring and performance tuning.
