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
export OPENAI_API_KEY=<your-openai-key>
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

It should spin up the chat app, looking something like the following:

![Chat UI](img/chat_overview.png)

Feel free to chat, rate the runs, and view the linked traces using the appropriate buttons!

## Code Walkthrough

The app consists of a main script managed by the `streamlit` event loop. Below are some key code snippets. After importing the required modules, you will want to initialize the streamlit session state with a "messages" key to maintain the chat history:


```python
if "messages" not in st.session_state:
    print("Initializing message history")
    st.session_state["messages"] = []
```

Then you can define the core logic of the chat model. In this example, we are using LangChain's [expression language](https://python.langchain.com/docs/guides/expression_language/) to cleanly model the data flow from input query to prompt to model. It's defined below:

```python
memory = ConversationBufferMemory(return_messages=True)
ingress = RunnableMap(
    {
        "input": lambda x: x["input"],
        "chat_history": lambda x: memory.load_memory_variables(x)["history"],
        "time": lambda _: str(datetime.now()),
    }
)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a funky parrot pal. You are not an AI. You are a parrot."
            " You love poetry, reading, funk music, friendship, and squawking!"
            " It's currently {time}.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)
llm = ChatOpenAI(temperature=0.7)
chain = ingress | prompt | llm
```

Once you've defined the chat model, including it's conversational memory, we define another code block to manage the streamlit session state:

```python
def _get_openai_type(msg):
    if msg.type == "human":
        return "user"
    if msg.type == "ai":
        return "assistant"
    if msg.type == "chat":
        return msg.role
    return msg.type

for msg in st.session_state.messages:
    with st.chat_message(_get_openai_type(msg)):
        st.markdown(msg.content)
    # Re-hydrate memory on app rerun
    memory.chat_memory.add_message(msg)

```

This does two things each time the streamlit event loop is triggered.
1. Re-renders the chat conversation in the UI 
2. Re-hydrates the memory so the chain will resume where you left off.

After this, we define a function for logging feedback to LangSmith. It's a simple wrapper around the client:

```python
# Imported above
from langsmith import Client

client = Client()

def send_feedback(run_id, score):
    client.create_feedback(run_id, "user_score", score=score)
```

This will be used in the `on_click` event for feedback buttons!

The logic for rendering the chat input and streaming the output to the app looks like this:

```python
if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in chain.stream({"input": prompt}, config=runnable_config):
            full_response += chunk.content
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        memory.save_context({"input": prompt}, {"output": full_response})
        st.session_state.messages = memory.buffer
```

This renders a `chat_input` container, and when the user sends an input, it's converted to a "user" chat message. Then an "assistant" message is created, and tokens are streamed in by updating a full response and rendering it to markdown with a "cursor" icon to simulate typing.

Once the response completes, the values are saved to memory, and the streamlit messages state is updated so the conversation can be continued on the next loop.

Finally, you can create feedback for the response directly in the app using the following code:

```python
run = run_collector.traced_runs[0]
run_collector.traced_runs = []
col_blank, col_text, col1, col2, col3 = st.columns([10, 2, 1, 1, 1])
with col_text:
    st.text("Feedback:")

with col1:
    st.button("👍", on_click=send_feedback, args=(run.id, 1))

with col2:
    st.button("👎", on_click=send_feedback, args=(run.id, 0))
with col3:
    url = client.read_run(run.id).url
    st.markdown(
        f'<a href="{url}" target="_blank"><button>🛠️</button></a>',
        unsafe_allow_html=True,
    )
```

The `run_collector` is a callback handler that we included in the `runnable_config` above. It captures all the runs any time the chain is invoked. We select the first `root` run in the tree to associate feedback to. If the user clicks the 👍/👎 buttons, feedback will be logged to the run!

We also fetch the URI using the client and include a "🛠️" button where you can click and view the traced run. **Note** this will link to the private run. You would have to "share" the run for an end user to view the trace if that is what you wanted.

Clicking on the "🛠️" link will take you to the corresponding LangSmith trace:

![LangSmith](img/langsmith.png)

If you have clicked on one of the 👍/👎 buttons, you can click on the "feedback" tab to see the result of your feedback:

![View Feedback](img/chat_feedback.png)


## Reusable Tactics

Below are some 'tactics' used in this example that you could reuse in other situations:

1. **Using the Run Collector:** One way to fetch the run ID is by using the `RunCollectorCallbackHandler`, which stores all run objects in a simple python list. The collected run IDs are used to associate logged feedback and for accessing the trace URLs.

2. **Logging feedback with LangSmith client:** The LangSmith client is used to create feedback for each run. A simple form is thumbs up/down, but it also supports other `value`'s, `comment`'s, `correction`'s, and other input. This way, users and annotators alike can share explicit feedback on a run.

3. **Accessing URLs from saved runs:** The client also retrieves URLs for saved runs. It allows users to inspect their interactions, providing a direct link to LangSmith traces.

4. **LangChain Expression Language:** This example uses LangChain's [expression language](https://python.langchain.com/docs/guides/expression_language/) to create the chain, which makes it more explicit what's going on under the hood.

## Conclusion
The LangSmith Streamlit Chat UI example provides a straightforward approach to crafting a chat interface abundant with features. If you aim to develop conversational AI applications with real-time feedback and traceability, the techniques and implementations in this guide are tailored for you. Feel free to adapt the code to suit your specific needs.