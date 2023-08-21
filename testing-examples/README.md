# Testing & Evaluation Recipes

The following walkthroughs demonstrate ways to evaluate common application scenarios.
- The [Q&A System Correctness](./qa-correctness/qa-correctness.ipynb) notebook walks through creating a dataset for a retrieval-augmented Q&A pipeline, evaluating the responses for correctness, and using LangSmith to iterate and improve.
- The [Evaluating Q&A Systems with Dynamic Data](./dynamic-data/testing_dynamic_data.ipynb) notebook shows how to evaluate a Q&A pipeline when the underlying data may change over time by using an evaluator that dereferences a label at evaluation time.
- The [Comparison Evals](./comparing-runs/comparing-qa.ipynb) notebook shows how to use labeled preference scoring to help compare two versions of a system and choose the preferred outputs.
- For examples using LangSmith in your testing framework, such as with pytest, you can reference the following:
    - The [LangSmith in Pytest](./testing-examples/pytest/) recipe shows how to directly evaluate your chain or LLM on a dataset and then define your own pass/fail criteria.
    - The [Unit Testing with Pytest](./testing-examples/pytest-ut/) recipe shows how to write individual unit tests so that feedback and traces are all organized by test suite.