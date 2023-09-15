"""Example Streamlit chat UI that exposes a Feedback button and link to LangSmith traces."""

from datetime import datetime

import streamlit as st
from langchain import callbacks
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, StreamlitChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnableMap
from langsmith import Client

client = Client()

st.set_page_config(
    page_title="Chat LangSmith",
    page_icon="🦜",
)
"# Chat🦜🛠️"
# Initialize State
if "run_id" not in st.session_state:
    st.session_state.run_id = None

st.sidebar.markdown(
    """
# Menu
"""
)

### Define the chain
memory = ConversationBufferMemory(
    chat_memory=StreamlitChatMessageHistory(key="langchain_messages"),
    return_messages=True,
    memory_key="chat_history",
)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a friendly robot.\nIt's currently {time}.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

chain = (
    RunnableMap(
        {
            "input": lambda x: x["input"],
            "chat_history": lambda x: memory.load_memory_variables(x)["chat_history"],
            "time": lambda _: str(datetime.now()),
        }
    )
    | prompt
    | ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0.7)
)

if st.sidebar.button("Clear message history"):
    memory.clear()
    st.session_state.run_id = None

for msg in st.session_state.langchain_messages:
    avatar = "🦜" if msg.type == "ai" else None
    with st.chat_message(msg.type, avatar=avatar):
        st.markdown(msg.content)

def show_url(run_id):
    try:
        url = client.read_run(run_id).url
        # Or if you just want to use this internally
        # url = client.share_run(run.id)

        st.sidebar.markdown(
            f'<a href="{url}" target="_blank"><button>Latest Trace: 🛠️</button></a>',
            unsafe_allow_html=True,
        )
    except:
        # TODO: Write queue means it may not be readily available
        pass

if st.session_state.run_id:
    # For internal viewing
    show_url(st.session_state.run_id) 

if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant", avatar="🦜"):
        message_placeholder = st.empty()
        full_response = ""
        with callbacks.collect_runs() as cb:
            for chunk in chain.stream(
                {"input": prompt}, config={"tags": ["Streamlit Chat"]}
            ):
                full_response += chunk.content
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.run_id = cb.traced_runs[0].id
        memory.save_context({"input": prompt}, {"output": full_response})
        show_url(st.session_state.run_id)