# Testing & Evaluation Recipes

The following walkthroughs demonstrate ways to evaluate common application scenarios.
- The [Q&A System Correctness](./qa-correctness/qa-correctness.ipynb) notebook walks through creating a dataset for a retrieval-augmented Q&A pipeline, evaluating the responses for correctness, and using LangSmith to iterate and improve.
- The [Evaluating Q&A Systems with Dynamic Data](./dynamic-data/testing_dynamic_data.ipynb) notebook shows how to evaluate a Q&A pipeline when the underlying data may change over time by using an evaluator that dereferences a label at evaluation time.
- The [Comparison Evals](./comparing-runs/comparing-qa.ipynb) notebook shows how to use labeled preference scoring to help compare two versions of a system and choose the preferred outputs.