---
sidebar_label: Feedback
sidebar_position: 6 
---
# Feedback

Harness user [feedback](https://docs.smith.langchain.com/tracing/faq/logging_feedback), ai-assisted feedback, and other signals to improve, monitor, and personalize your applications:

- [Streamlit Chat App](./streamlit/README.md): a minimal chat app that captures user feedback and shares traces of the chat application.
    - The [vanilla_chain.py](./streamlit/vanilla_chain.py) contains an LLMChain that powers the chat application.
    - The [expression_chain.py](./streamlit/expression_chain.py) contains an equivalent chat chain defined exclusively with [LangChain expressions](https://python.langchain.com/docs/expression_language/). 
- [Next.js Chat App](./nextjs/README.md): explore a simple TypeScript chat app demonstrating tracing and feedback capture.
    - You can [check out a deployed demo version here](https://langsmith-cookbook.vercel.app/).
- [Building an Algorithmic Feedback Pipeline](./algorithmic-feedback/algorithmic_feedback.ipynb) Automate feedback metrics for advanced monitoring and performance tuning.
- [Real-time Automated Feedback](./realtime-algorithmic-feedback/realtime_feedback.ipynb): automatically generate feedback metrics for every run using an async callback. This lets you evaluate production runs in real-time.
- [Real-time RAG Chat Bot Evaluation](./streamlit-realtime-feedback/README.md): This Streamlit walkthrough showcases an advanced application of the concepts from the [Real-time Automated Feedback](./realtime-algorithmic-feedback/realtime_feedback.ipynb) tutorial. It demonstrates how to automatically check for hallucinations in your RAG chat bot responses against the retrieved documents. For more information on RAG, [check out the LangChain docs](https://python.langchain.com/docs/use_cases/question_answering/).
- [LangChain Agents with LangSmith](./streamlit-agent/README.md) instrument a LangChain web-search agent with tracing and human feedback.