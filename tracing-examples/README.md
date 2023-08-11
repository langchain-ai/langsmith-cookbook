## Tracing your code

Setting up tracing in LangChain is as simple as setting a couple environment variables. We've also added support through the LangSmith SDK to trace applications that don't rely on LangChain. The following walkthroughs address common questions around tracing your code!
- The [Tracing without LangChain](./tracing-examples/traceable/tracing_without_langchain.ipynb) notebook uses the python SDK's `@traceable` decorator to trace and tag run in an app that does not use depend on LangChain.
