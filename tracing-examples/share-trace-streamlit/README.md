# Add Traceability to Your Streamlit Chatbot

Debugging conversational AI is difficult. When a bot gives a wrong response, it's hard to understand why. 

Full traceability enables us to inspect the step-by-step reasoning behind each reply. With visibility into execution flow, we can identify and fix failure points.

In this tutorial, you'll add traceability to a Streamlit chatbot by:

- Capturing full traces with LangSmith 
- Displaying trace URLs in the UI
- Letting users view reasoning graphs

This makes it easy to debug your chain or agent, since you can directly interact with the UX your users will face and quickly check traces when the performance is underwhelming.

## Key Takeaway

The concise snippet you can reuse in your code is as follows:

```python
from langchain import callbacks
import langsmith

client = langsmith.Client()

# .. define chain ...
with callbacks.collect_runs() as cb:
    for tok in chain.strem({"input": "<user-input>"}):
        print(tok, end="",flush=True)
    url = client.read_run(cb.traced_runs[0].id).url
    print(url)
```

Using the collect_runs() context manager, you fetch the trace locally. Then, using the LangSmith client, you fetch the URL of the associated trace. Turn this on whenever you're in your dev environment, and you'll be able to view the trace right there.

Now that we've spoiled the surprise, let's walk through the tutorial!

## Overview

In this walkthrough, we'll build a simple question answering bot with:

- Chat history tracking 
- Contextual prompt formatting
- Claude chat model
- `collect_runs` callback to save traces
- Fetch trace URLs with the LangSmith client
- Display links in the Streamlit sidebar

## Prerequisites 

```
python -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt 

# Set API key
export LANGSMITH_API_KEY=...
```

Then run the app!

```python
ENVIRONMENT=dev python -m streamlit run app.py
```

## Walkthrough

### Chat Memory

To track state across turns, we use a `ConversationBufferMemory`:

```python
memory = ConversationBufferMemory(
    chat_memory=StreamlitChatMessageHistory(key="chat_history"),
    memory_key="chat_history"  
)
```

This syncs the log with Streamlit session state.

### Prompt

We define a `ChatPromptTemplate` to format context, question, and instructions:

```python
prompt = ChatPromptTemplate(
    [("system", INSTRUCTIONS),
     MessagesPlaceholder("chat_history"),
     ("human", "{input}")]
)
```

Where `INSTRUCTIONS` defines the conversational task.

### LLM Chain 

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
   response = chain(input=question)
   
   run_id = collector.runs[0].id
```

This saves the full trace data.

### Fetching URLs

We use the LangSmith client to get the URL for a run ID:

```python
client = LangSmithClient()
url = client.read_run(run_id).url 
```

### UI Integration

Finally, we display the link in the sidebar:

```python
st.sidebar.markdown(f"""
[Trace Link]({url}) 
""")
```

Enabling users to view reasoning graphs.

## Next Steps

- Log annotations on runs  
- Analyze traces to identify issues
- Use traces to improve model performance
- Enable user feedback for fine-tuning

This completes the tutorial! Let me know if you would like me to modify or expand any section.