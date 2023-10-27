---
sidebar_label: Tracing
sidebar_position: 2
---
# Tracing your code

Tracing allows for seamless debugging and improvement of your LLM applications. Here's how:


- [Tracing without LangChain](./traceable/tracing_without_langchain.ipynb): learn to trace applications independent of LangChain using the Python SDK's @traceable decorator.
- [REST API](./rest/rest.ipynb): get acquainted with the REST API's features for logging LLM and chat model runs, and understand nested runs. The run logging spec can be found in the [LangSmith SDK repository](https://github.com/langchain-ai/langsmith-sdk/blob/main/openapi/openapi.yaml).
- [Customizing Run Names](./runnable-naming/run-naming.ipynb): improve UI clarity by assigning bespoke names to LangSmith chain runs—includes examples for chains, lambda functions, and agents.
- [Tracing Nested Calls within Tools](./nesting-tools/nest_runs_within_tools.ipynb): include all nested tool subcalls in a single trace by using `run_manager.get_child()` and passing to the child `callbacks`
- [Display Trace Links](./show-trace-url-streamlit/README.md): add trace links to your app to speed up development. This is useful when prototyping your application in its unique UI, since it lets you quickly see its execution flow, add feedback to a run, or add the run to a dataset.