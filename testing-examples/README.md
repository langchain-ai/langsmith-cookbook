---
sidebar_label: Testing & Evaluation
sidebar_position: 4 
---
# Testing & Evaluation Recipes

- [Q&A System Correctness](./qa-correctness/qa-correctness.ipynb): evaluate your retrieval-augmented Q&A pipeline on a dataset. Iterate, improve, and keep testing.
- [Evaluating Q&A Systems with Dynamic Data](./dynamic-data/testing_dynamic_data.ipynb): use evaluators that dereference a labels to handle data that changes over time.
- [RAG Evaluation using Fixed Sources](./using-fixed-sources/using_fixed_sources.ipynb): evaluate the response component of a RAG pipeline by providing retrieved documents in the dataset.
- [Evaluating an Agent's intermediate steps](./agent_steps/evaluating_agents.ipynb): compare the sequence of actions taken by an agent to an expected trajectory to grade effective tool use.
- [Evaluating a Conversational Chat Bot](./chat-single-turn/chat_evaluation_single_turn.ipynb): Evaluate chatbots within multi-turn conversations by treating each data point as an individual dialogue turn. This guide shows how to set up a multi-turn conversation dataset and evaluate a simple chat bot on it.
- [Evaluating an Extraction Chain](./data-extraction/contract-extraction.ipynb): measure the similarity between the extracted structured content and structured labels using LangChain's json evaluators.
- [Comparison Evals](./comparing-runs/comparing-qa.ipynb): use labeled preference scoring to contrast system versions and determine the most optimal outputs.
- You can incorporate LangSmith in your existing testing framework:
    - [LangSmith in Pytest](./pytest/) benchmark your chain in pytest and assert aggregate metrics meet the quality bar.
    - [Unit Testing with Pytest](./pytest-ut/): write individual unit tests and log assertions as feedback.
- [Evaluating Existing Runs](./evaluate-existing-test-project/evaluate_runs.ipynb): add ai-assisted feedback and evaluation metrics to existing run traces.
- [Naming Test Projects](./naming-test-projects/naming-test-projects.md): manually name your tests with `run_on_dataset(..., project_name='my-project-name')`
- [How to download feedback and examples from a test project](./download-feedback-and-examples/download_example.ipynb): export the predictions, evaluation results, and other information to programmatically add to your reports.