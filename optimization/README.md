---
sidebar_label: Optimization
sidebar_position: 7 
---
# Optimization Recipes

Use LangSmith to help optimize your LLM systems, so they can continuously learn and improve.

- [Prompt Bootstrapping](./assisted-prompt-bootstrapping/assisted-prompt-engineering.ipynb): Optimize your prompt over a set of examples by incorporating human feedback and an LLM prompt optimizer. Works by rewriting an optimized system prompt.
    - [Prompt Bootstrapping for style transfer: Elvis-Bot](./assisted-prompt-bootstrapping/elvis-bot.ipynb): Extend prompt bootstrapping to generate outputs in the style of a specific persona. This notebook demonstrates how to create an "Elvis-bot" that mimics the tweet style of @omarsar0 by iteratively refining a prompt using Claude's exceptional prompt engineering capabilities and feedback collected through LangSmith's annotation queue.
- [Iterative Prompt Optimization](https://github.com/langchain-ai/tweet-critic): Streamlit app demonstrating real-time prompt optimization based on user feedback and dialog, leveraging few-shot learning and a separate "optimizer" model to dynamically improve a tweet-generating system.
- [Automated Few-shot Prompt Bootstrapping](./bootstrap-fewshot/bootstrap-few-shot.ipynb): Automatically curate the most informative few-shot examples based on performance metrics, removing the need for manual example engineering. Applied to an entailment task on the SCONE dataset.