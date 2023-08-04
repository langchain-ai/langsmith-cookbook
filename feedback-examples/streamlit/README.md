## LangSmith Streamlit Chat UI Example

Language model applications benefit from feedback, which can be applied for enhancements like refining few-shot examples, fine-tuning models, personalizing user experiences, and improving application observability.

This example illustrates how to create a ChatGPT-like UI in Streamlit that enables logging feedback for the run to LangSmith and viewing a trace of what's happening under the hood. Whether for customer support bots, interactive teaching assistants, or fun conversational agents, this example offers a practical illustration.

## Prerequisites

You'll need to be connected to [LangSmith](https://smith.langchain.com/) and configure your environment:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
export LANGCHAIN_API_KEY=<your-api-key>
export LANGCHAIN_PROJECT=<your-project>  # defaults to "default" if not specified
```

We recommend using a virtual environment.

```bash
python -m virtualenv .venv
. .venv/bin/activate
```

Then, install the project requirements:

```bash
pip install -r requirements.txt
```

## Running the example

Execute the following command:

```bash
streamlit run main..py
```

This will execute the program, which
- Initializes and manages chat conversation history.
- Allows users to send messages and receive responses from the AI.
- Utilizes the LangSmith client to send feedback and access URLs for specific runs.
- Uses a run collector to trace the run ID from each interaction.

## Key Tactics

1. **Using the Run Collector to Trace Runs:** Utilizing RunCollectorCallbackHandler, the example traces each run, enabling the retrieval of run IDs. The collected run IDs are essential for logging feedback and accessing specific URLs.

2. **Logging Feedback with LangSmith Client:** The LangSmith client is used to create feedback for each run. By using user-defined buttons, users can quickly send their feedback, which is then logged through the client.
3. **Accessing URLs from Saved Runs:** The client also retrieves URLs for saved runs. It allows users to inspect their interactions, providing a direct link to LangSmith traces.

4. **LangChain Expression Language:** This example uses [LCEL](https://python.langchain.com/docs/guides/expression_language/) to create the chain, which makes it more explicit what's going on under the hood.

## Conclusion
The LangSmith Streamlit Chat UI example provides a straightforward approach to crafting a chat interface abundant with features. If you aim to develop conversational AI applications with real-time feedback and traceability, the techniques and implementations in this guide are tailored for you. Feel free to adapt the code to suit your specific needs.