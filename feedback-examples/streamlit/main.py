"""Example Streamlit chat UI that exposes a Feedback button and link to LangSmith traces."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import streamlit as st
from langchain.callbacks.tracers.run_collector import RunCollectorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnableConfig, RunnableMap
from langsmith import Client

client = Client()

st.set_page_config(
    page_title="LangSmith Feedback",
    page_icon="🦜",
    layout="wide",
)

"# Chat🦜🔗"
# Initialize State
if "messages" not in st.session_state:
    print("Initializing message history")
    st.session_state["messages"] = []
if st.sidebar.button("Clear message history"):
    print("Clearing message history")
    st.session_state.messages = []
if "executor" not in st.session_state:
    st.session_state.executor = ThreadPoolExecutor(max_workers=1)


# Create Chain
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


def _get_openai_type(msg):
    if msg.type == "human":
        return "user"
    if msg.type == "ai":
        return "assistant"
    if msg.type == "chat":
        return msg.role
    return msg.type


# Display chat messages from history on app rerun
for msg in st.session_state.messages:
    with st.chat_message(_get_openai_type(msg)):
        st.markdown(msg.content)
    # Re-hydrate memory on app rerun
    memory.chat_memory.add_message(msg)


def send_feedback(run_id, score):
    st.session_state.executor.submit(
        client.create_feedback, run_id, "user_score", score=score
    )


if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        run_collector = RunCollectorCallbackHandler()
        runnable_config = RunnableConfig(
            callbacks=[run_collector],
            tags=["Streamlit Chat"],
        )
        full_response = ""
        for chunk in chain.stream({"input": prompt}, config=runnable_config):
            full_response += chunk.content
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        memory.save_context({"input": prompt}, {"output": full_response})
        st.session_state.messages = memory.buffer
        # The run collector will store all the runs in order. We'll just take the root and then
        # reset the list for next interaction.
        run = run_collector.traced_runs[0]
        run_collector.traced_runs = []
        col_blank, col_text, col1, col2, col3 = st.columns([10, 2, 1, 1, 1])
        with col_text:
            st.text("Feedback:")

        with col1:
            st.button("👍", on_click=send_feedback, args=(run.id, 1))

        with col2:
            st.button("👎", on_click=send_feedback, args=(run.id, 0))
        url = client.read_run(run_id).url
        with col3:
            st.markdown(
                f'<a href="{url}" target="_blank"><button>🔍</button></a>',
                unsafe_allow_html=True,
            )
