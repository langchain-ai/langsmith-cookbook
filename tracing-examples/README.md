## Tracing your code

Setting up tracing in LangChain is as simple as setting a couple environment variables. We've also added support through the LangSmith SDK to trace applications that don't rely on LangChain. The following walkthroughs address common questions around tracing your code!
- The [Tracing without LangChain](./traceable/tracing_without_langchain.ipynb) notebook uses the python SDK's `@traceable` decorator to trace and tag run in an app that does not use depend on LangChain.
- The [REST API](./tracing-examples/rest/rest.ipynb) notebook walks through logging runs to LangSmith directly using the REST API, covering how to log LLM and chat model runs for token counting, and how to nest runs. The run logging spec can be found in the [LangSmith SDK repository](https://github.com/langchain-ai/langsmith-sdk/blob/main/openapi/openapi.yaml).
