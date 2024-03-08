# LangSmith Cookbook

Welcome to the LangSmith Cookbook — your practical guide to mastering [LangSmith](https://smith.langchain.com/). While our [standard documentation](https://docs.smith.langchain.com/) covers the basics, this repository delves into common patterns and some real-world use-cases, empowering you to optimize your LLM applications further.


This repository is your practical guide to maximizing [LangSmith](https://smith.langchain.com/). As a tool, LangSmith empowers you to debug, evaluate, test, and improve your LLM applications continuously. These recipes present real-world scenarios for you to adapt and implement.

**Your Input Matters**

Help us make the cookbook better! If there's a use-case we missed, or if you have insights to share, please raise a GitHub issue (feel free to tag [Will](https://github.com/hinthornw)) or contact the LangChain development team. Your expertise shapes this community.

## Tracing your code

Tracing allows for seamless debugging and improvement of your LLM applications. Here's how:


- [Tracing without LangChain](./tracing-examples/traceable/tracing_without_langchain.ipynb): learn to trace applications independent of LangChain using the Python SDK's @traceable decorator.
- [REST API](./tracing-examples/rest/rest.ipynb): get acquainted with the REST API's features for logging LLM and chat model runs, and understand nested runs. The run logging spec can be found in the [LangSmith SDK repository](https://github.com/langchain-ai/langsmith-sdk/blob/main/openapi/openapi.yaml).
- [Customizing Run Names](./tracing-examples/runnable-naming/run-naming.ipynb): improve UI clarity by assigning bespoke names to LangSmith chain runs—includes examples for chains, lambda functions, and agents.
- [Tracing Nested Calls within Tools](./tracing-examples/nesting-tools/nest_runs_within_tools.ipynb): include all nested tool subcalls in a single trace by using `run_manager.get_child()` and passing to the child `callbacks`
- [Display Trace Links](./tracing-examples/show-trace-url-streamlit/README.md): add trace links to your app to speed up development. This is useful when prototyping your application in its unique UI, since it lets you quickly see its execution flow, add feedback to a run, or add the run to a dataset.

## LangChain Hub

Efficiently manage your LLM components with the [LangChain Hub](https://smith.langchain.com/hub). For dedicated documentation, please see the [hub docs](https://docs.smith.langchain.com/hub/quickstart).

- [RetrievalQA Chain](./hub-examples/retrieval-qa-chain/retrieval-qa.ipynb): use prompts from the hub in an example RAG pipeline.
- [Prompt Versioning](./hub-examples/retrieval-qa-chain-versioned/prompt-versioning.ipynb): ensure deployment stability by selecting specific prompt versions over the 'latest'.
- [Runnable PromptTemplate](./hub-examples/runnable-prompt/edit-in-playground.ipynb): streamline the process of saving prompts to the hub from the playground and integrating them into runnable chains.


## Testing & Evaluation

Test and benchmark your LLM systems using methods in these evaluation recipes:

### Python Examples


**Retrieval Augmented Generation (RAG)**
- [Q&A System Correctness](./testing-examples/qa-correctness/qa-correctness.ipynb): evaluate your retrieval-augmented Q&A pipeline end-to-end on a dataset. Iterate, improve, and keep testing.
- [Evaluating Q&A Systems with Dynamic Data](./testing-examples/dynamic-data/testing_dynamic_data.ipynb): use evaluators that dereference a labels to handle data that changes over time.
- [RAG Evaluation using Fixed Sources](./testing-examples/using-fixed-sources/using_fixed_sources.ipynb): evaluate the response component of a RAG  (retrieval-augmented generation) pipeline by providing retrieved documents in the dataset

**Chat Bots**
- [Chat Bot Evals using Simulated Users](./testing-examples/chatbot-simulation/chatbot-simulation.ipynb): evaluate your chat bot using a simulated user. The user is given a task, and you score your assistant based on how well it helps without being breaking its instructions.
- [Single-turn evals](./testing-examples/chat-single-turn/chat_evaluation_single_turn.ipynb): Evaluate chatbots within multi-turn conversations by treating each data point as an individual dialogue turn. This guide shows how to set up a multi-turn conversation dataset and evaluate a simple chat bot on it.

**Extraction**
- [Evaluating an Extraction Chain](./testing-examples/data-extraction/contract-extraction.ipynb): measure the similarity between the extracted structured content and structured labels using LangChain's json evaluators.
- [Exact Match](./testing-examples/exact-match/exact_match.ipynb): deterministic comparison of your system output against a reference label.

**Agents**
- [Evaluating an Agent's intermediate steps](./testing-examples/agent_steps/evaluating_agents.ipynb): compare the sequence of actions taken by an agent to an expected trajectory to grade effective tool use.
- [Tool Selection](./testing-examples/tool-selection/tool-selection.ipynb): Evaluate the precision of selected tools. Include an automated prompt writer to improve the tool descriptions based on failure cases.

**Multimodel**
- [Evaluating Multimodal Models](./testing-examples/multimodal/multimodal.ipynb): benchmark a multimodal image classification chain

**Fundamentals**
- [Evaluating Existing Runs](./testing-examples/evaluate-existing-test-project/evaluate_runs.ipynb): add ai-assisted feedback and evaluation metrics to existing run traces.
- [Naming Test Projects](./testing-examples/naming-test-projects/naming-test-projects.md): manually name your tests with `run_on_dataset(..., project_name='my-project-name')`
- [How to download feedback and examples from a test project](./testing-examples/download-feedback-and-examples/download_example.ipynb): export the predictions, evaluation results, and other information to programmatically add to your reports.

### TypeScript / JavaScript Testing Examples

Incorporate LangSmith into your TS/JS testing and evaluation workflow:

- [Vision-based Evals in JavaScript](./typescript-testing-examples/vision-evals/vision-evals.ipynb): evaluate AI-generated UIs using GPT-4V


We are working to add more JS examples soon. In the meantime, check out the JS eval quickstart the following guides:

- [JS LangSmith walkthrough](https://js.langchain.com/docs/guides/langsmith_evaluation)
- [Evaluation quickstart](https://docs.smith.langchain.com/evaluation/quickstart)


## Using Feedback

Harness user [feedback](https://docs.smith.langchain.com/tracing/faq/logging_feedback), "ai-assisted" feedback, and other signals to improve, monitor, and personalize your applications. Feedback can be user-generated or "automated" using functions or even calls to an LLM:

- [Streamlit Chat App](./feedback-examples/streamlit/README.md): a minimal chat app that captures user feedback and shares traces of the chat application.
    - The [vanilla_chain.py](./feedback-examples/streamlit/vanilla_chain.py) contains an LLMChain that powers the chat application.
    - The [expression_chain.py](./feedback-examples/streamlit/expression_chain.py) contains an equivalent chat chain defined exclusively with [LangChain expressions](https://python.langchain.com/docs/expression_language/). 
- [Next.js Chat App](./feedback-examples/nextjs/README.md): explore a simple TypeScript chat app demonstrating tracing and feedback capture.
    - You can [check out a deployed demo version here](https://langsmith-cookbook.vercel.app/).
- [Building an Algorithmic Feedback Pipeline](./feedback-examples/algorithmic-feedback/algorithmic_feedback.ipynb): automate feedback metrics for advanced monitoring and performance tuning. This lets you evaluate production runs as a batch job.
- [Real-time Automated Feedback](./feedback-examples/realtime-algorithmic-feedback/realtime_feedback.ipynb): automatically generate feedback metrics for every run using an async callback. This lets you evaluate production runs in real-time.
- [Real-time RAG Chat Bot Evaluation](./feedback-examples/streamlit-realtime-feedback/README.md): This Streamlit walkthrough showcases an advanced application of the concepts from the [Real-time Automated Feedback](./feedback-examples/realtime-algorithmic-feedback/realtime_feedback.ipynb) tutorial. It demonstrates how to automatically check for hallucinations in your RAG chat bot responses against the retrieved documents. For more information on RAG, [check out the LangChain docs](https://python.langchain.com/docs/use_cases/question_answering/).
- [LangChain Agents with LangSmith](./feedback-examples/streamlit-agent/README.md) instrument a LangChain web-search agent with tracing and human feedback.


## Exporting data for fine-tuning

Fine-tune an LLM on collected run data using these recipes:

- [OpenAI Fine-Tuning](./fine-tuning-examples/export-to-openai/fine-tuning-on-chat-runs.ipynb): list LLM runs and convert them to OpenAI's fine-tuning format efficiently.
- [Lilac Dataset Curation](./fine-tuning-examples/lilac/lilac.ipynb): further curate your LangSmith datasets using Lilac to detect near-duplicates, check for PII, and more.

## Exploratory Data Analysis

Turn your trace data into actionable insights:

- [Exporting LLM Runs and Feedback](./exploratory-data-analysis/exporting-llm-runs-and-feedback/llm_run_etl.ipynb): extract and interpret LangSmith LLM run data, making them ready for various analytical platforms.
- [Lilac](./exploratory-data-analysis/lilac/lilac.ipynb): enrich datasets using the open-source analytics tool, [Lilac](https://github.com/lilacai/lilac), to better label and organize your data.
