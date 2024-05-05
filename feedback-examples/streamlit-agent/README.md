# LangChain Agents with LangSmith

[![Open In GitHub](https://img.shields.io/badge/GitHub-View%20source-green.svg)](https://github.com/langchain-ai/langsmith-cookbook/tree/main/./feedback-examples/streamlit-agent/README.md)


This streamlit walkthrough shows how to instrument a LangChain agent with tracing and feedback. It highlights the following functionality:
- Implementing an agent with a web search tool (Duck Duck Go)
- Capturing explicit user feedback in LangSmith
- Linking to the run trace for debugging

Below is an example:

[![Demo Video of Agent](./img/streamlit-agent.gif)](https://smith.langchain.com/public/78a96d44-2b76-48a5-8fda-e434ea504046/r)


## Prerequisites

The requirements for this streamlit application are listed in the [requirements.txt](./requirements.txt) file. 

(Recommended) First, create and activate virtual environment.
```bash
python -m pip install -U virtualenv pip
python -m virtualenv .venv
. .venv/bin/activate
```

Then install the app requirements.
```bash
python -m pip install -r requirements.txt
```

Next, configure your API keys for LangSmith and the LLM provider (we are using OpenAI here for the LLM).

```bash
export OPENAI_API_KEY=your-openai-api-key
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-langsmith-api-key
export LANGCHAIN_PROJECT=langsmith-streamlit-agent
```

Finally, start the streamlit application.

```bash
python -m streamlit run main.py
```

You can interact with it, leave feedback, and view the traces to see what's going on under the hood.