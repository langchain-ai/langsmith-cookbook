# Adding Trace Links

When developing, adding a trace link in your UI can help you save time debugging.

In this walkthrough, you will share a link to your LangSmith trace using the following pattern:

```python
from langchain.callbacks import collect_runs
from langsmith import Client

client = Client()

with collect_runs() as cb:
    chain.invoke({"input": "<user-input>"})
    url = client.get_run_url(run=cb.traced_runs[0])
```
```
from langchain.callbacks import tracing_v2_enabled

with tracing_v2_enabled() as cb:
    chain.invoke({"input": "<user-input>"})
    url = cb.last_trace_url
```

The `collect_runs` callback collects the trace in-memory, and then the LangSmith client helps assemble the URL of the run.

The demo app will look like this:

![streamlit-app](./img/embed-trace-app.gif)

## Requirements

First, let's set up by creating a virtual Python environment, activating it, installing requirements, and setting up the key:

```
python -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt 

# Set API key
export LANGCHAIN_API_KEY=...
```

After setup is done, run the application:

```python
ENVIRONMENT=dev python -m streamlit run app.py
```

## Chat Bot Overview

### Memory

To track state across turns, a `ConversationBufferMemory` is used:

```python
memory = ConversationBufferMemory(
    chat_memory=StreamlitChatMessageHistory(key="chat_history"),
    memory_key="chat_history"  
)
```

This small utility bridges the chat log with the Streamlit session state.

### Prompt

We load the [prompt](https://smith.langchain.com/hub/wfh/langsmith-tutor-trace-link) from the hub.

```python
prompt = hub.pull("wfh/langsmith-tutor-trace-link")
```

### The prompt chain

Our chain composes the prompt, model, and memory:

```python 
chain = (
    # dict <- (runnables)
    runnable.RunnableMap(
        {
            "input": operator.itemgetter("input"),
            "chat_history": lambda x: chain_memory.load_memory_variables(x)[
                "chat_history"
            ],
        }
    )
    | prompt
    # You can use another model provider, such as Openai, LlamaCPP, etc.
    | chat_models.ChatAnthropic(model="claude-2", temperature=1)
)
```

### Tracing

We wrap execution in `collect_runs` to capture traces:

```python
with collect_runs() as collector:
   response = chain.invoke({"input": user_input})
   run = collector.runs[0]
```

This captures the full trace locally in memory. We will use this to return the run ID.

### UI Integration

We render a button to navigate to the LangSmith trace URL:

```python
st.button(
    label="Latest Trace: 🛠️",
    help="Navigate to the run trace.",
    on_click=partial(navigate_to_trace_url, run),
)
```

### Fetching URLs

Finally, we use the LangSmith client to get the URL for a run ID, and the python stdlib webbrowser
module to navigate to the link.

```python
client = LangSmithClient()
url = client.get_run_url(run=run)
webbrowser.open_new_tab(url)
```

Letting you inspect and experiment with the trace if you want to see how different prompt templates or different models would respond.

## Conclusion

This completes the tutorial! Displaying URLs inline is an easy way to avoid having to search through your project to replay or analyze a run. 
