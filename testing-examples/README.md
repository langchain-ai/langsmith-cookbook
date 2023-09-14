---
sidebar_label: Testing & Evaluation
sidebar_position: 4 
---
# Testing & Evaluation Recipes

- [Q&A System Correctness](./qa-correctness/qa-correctness.ipynb): evaluate your retrieval-augmented Q&A pipeline on a dataset. Iterate, improve, and keep testing.
- [Evaluating Q&A Systems with Dynamic Data](./dynamic-data/testing_dynamic_data.ipynb): use evaluators that dereference a labels to handle data that changes over time.
- [Comparison Evals](./comparing-runs/comparing-qa.ipynb): use labeled preference scoring to contrast system versions and determine the most optimal outputs.
- You can incorporate LangSmith in your existing testing framework:
    - [LangSmith in Pytest](./pytest/) benchmark your chain in pytest and assert aggregate metrics meet the quality bar.
    - [Unit Testing with Pytest](./pytest-ut/): write individual unit tests and log assertions as feedback.
- [Evaluating Existing Runs](./evaluate-existing-test-project/evaluate_runs.ipynb): add ai-assisted feedback and evaluation metrics to existing run traces.
- [Naming Test Projects](./naming-test-projects/naming-test-projects.md): manually name your tests with `run_on_dataset(..., project_name='my-project-name')`
