# LangChain Agents with LangSmith

This streamlit example highlights the following functionality:
- Implementing an agent with a web search tool (Duck Duck Go)
- Capturing explicit user feedback in LangSmith
- Linking to the run trace for debugging


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

Next, configure your API keys for LangSmith and the LLM provider (we are using OpenAI for the evaluator LLM here and Anthropic for the application LLM).

```bash
export OPENAI_API_KEY=your-openai-api-key
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-langsmith-api-key
export LANGCHAIN_PROJECT=your-project
```

Finally, start the streamlit application.

```bash
python -m streamlit run main.py
```