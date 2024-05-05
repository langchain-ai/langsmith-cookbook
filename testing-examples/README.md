---
sidebar_label: Testing & Evaluation
sidebar_position: 4
---

# Testing & Evaluation Recipes

**Retrieval Augmented Generation (RAG)**

- [Q&A System Correctness](./qa-correctness/qa-correctness.ipynb): evaluate your retrieval-augmented Q&A pipeline end-to-end on a dataset. Iterate, improve, and keep testing.
- [Evaluating Q&A Systems with Dynamic Data](./dynamic-data/testing_dynamic_data.ipynb): use evaluators that dereference a labels to handle data that changes over time.
- [RAG Evaluation using Fixed Sources](./using-fixed-sources/using_fixed_sources.ipynb): evaluate the response component of a RAG (retrieval-augmented generation) pipeline by providing retrieved documents in the dataset
- [RAG evaluation with RAGAS](./ragas/ragas.ipynb): evaluate RAG pipelines using the [RAGAS](https://docs.ragas.io/en/stable/) framework. Covers metrics for both the generator AND retriever in both labeled and reference-free contexts (answer correctness, faithfulness, context relevancy, recall and precision).

**Chat Bots**

- [Chat Bot Evals using Simulated Users](./chatbot-simulation/chatbot-simulation.ipynb): evaluate your chat bot using a simulated user. The user is given a task, and you score your assistant based on how well it helps without being breaking its instructions.
- [Single-turn evals](./chat-single-turn/chat_evaluation_single_turn.ipynb): Evaluate chatbots within multi-turn conversations by treating each data point as an individual dialogue turn. This guide shows how to set up a multi-turn conversation dataset and evaluate a simple chat bot on it.

**Extraction**

- [Evaluating an Extraction Chain](./data-extraction/contract-extraction.ipynb): measure the similarity between the extracted structured content and structured labels using LangChain's json evaluators.
- [Exact Match](./exact-match/exact_match.ipynb): deterministic comparison of your system output against a reference label.

**Agents**

- [Evaluating an Agent's intermediate steps](./agent_steps/evaluating_agents.ipynb): compare the sequence of actions taken by an agent to an expected trajectory to grade effective tool use.
- [Tool Selection](./tool-selection/tool-selection.ipynb): Evaluate the precision of selected tools. Include an automated prompt writer to improve the tool descriptions based on failure cases.

**Multimodel**

- [Evaluating Multimodal Models](./multimodal/multimodal.ipynb): benchmark a multimodal image classification chain

**Fundamentals**

- [Adding Metrics to Existing Tests](./evaluate-existing-test-project/evaluate_runs.ipynb): Apply new evaluators to existing test results without re-running your model, using the `compute_test_metrics` utility function. This lets you evaluate "post-hoc" and backfill metrics as you define new evaluators.
- [Production Candidate Testing](./backtesting/backtesting.ipynb): benchmark new versions of your production app using real inputs. Convert production runs to a test dataset, then compare your new system's performance against the baseline.
- [Naming Test Projects](./naming-test-projects/naming-test-projects.md): manually name your tests with `run_on_dataset(..., project_name='my-project-name')`
- [Exporting Tests to CSV](./export-test-to-csv/export-test-to-csv.ipynb): Use the `get_test_results` beta utility to easily export your test results to a CSV file. This allows you to analyze and report on the performance metrics, errors, runtime, inputs, outputs, and other details of your tests outside of the Langsmith platform.
- [How to download feedback and examples from a test project](./download-feedback-and-examples/download_example.ipynb): goes beyond the utility described above to query and export the predictions, evaluation results, and other information to programmatically add to your reports.