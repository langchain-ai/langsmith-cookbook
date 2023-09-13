---
sidebar_label: TS Evaluation
sidebar_position: 4
---
# JavaScrptr Testing & Evaluation Examples

LangSmith supports logging evaluation feedback to any run. The following walkthroughs show how to incorporate LangSmith in your TypeScript or JavaScript testing and evaluation workflows.

- The [Evaluating JS Chains in Python](./eval-in-python/) walkthrough shows how to run your JS chain over a LangSmith dataset and then evaluate the resulting traces in python, using a custom evaluator to test the structured results. This applies the technique presented in [Evaluating Existing Runs](../testing-examples/evaluate-existing-test-project/evaluate_runs.ipynb).
- The [Logging Assertions as Feedback](./simple-test/) example shows a how to quickly store your existing CI test assertions as LangSmith feedback. This lets you store annotated traces of your test runs in LangSmith without requiring many changes to your existing test system.
