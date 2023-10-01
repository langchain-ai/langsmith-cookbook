"""Streamlit tutor teaching how to show a trace URL in the app."""

import inspect
import logging
import operator
import os
import uuid
from datetime import datetime
import webbrowser

import langsmith
import streamlit as st
from langchain import callbacks, chat_models, hub, memory, prompts
from langchain.schema import runnable
from functools import partial

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="LangSmith Trace Tutor",
    page_icon="🦜",
)
"""# Embed 🦜🛠️ Trace URLs

Have a chat! The bot is instructed to teach about how to embed\
 LangSmith trace URLs in your web UI.
After each conversation turn, you should see\
 a "🛠️" button linking to the LangSmith trace for this
 chat bot. Ask the bot how it works!
"""
st.sidebar.markdown(
    """
# Menu
"""
)
client = langsmith.Client()


def navigate_to_trace_url(run):
    url = client.get_run_url(run=run)
    # Or if you wat to share the run publicly
    # url = client.share_run(run.id)
    # Navigate to the URL
    webbrowser.open_new_tab(url)


def main():
    sourcecode = inspect.getsource(main)

    #### Define Chain
    # The ConversationBufferMemory is a simple in-memory list
    # of chat messages.The StreamlitChatMessageHistory
    # populates the streamlit state for you.
    chain_memory = memory.ConversationBufferMemory(
        chat_memory=memory.StreamlitChatMessageHistory(key="langchain_messages"),
        return_messages=True,
        memory_key="chat_history",
    )
    # Define the prompt for the LLM. The conversation is passed into this
    # template for each conversation turn
    prompt: prompts.ChatPromptTemplate = hub.pull("wfh/langsmith-tutor-trace-link")
    prompt = prompt.partial(
        uuid=lambda: uuid.uuid4(), code=sourcecode, time=lambda: str(datetime.now())
    )
    # The | operator promotes this DAG into a RunnableSequence,
    # which provides streaming, tracing, and other functionality
    # by default. Runnables are the composable core of LangChain's expression language
    # https://python.langchain.com/docs/expression_language/cookbook
    chain = (
        # Data flows right to left within the RunnableMap
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
        # | chat_models.ChatOllama(mdel="llama2:7b-chat")
        # You can use another model provider, such as anthropc, openai, etc.
        | chat_models.ChatAnthropic(model="claude-2", temperature=1)
    )

    #### Render Chat Messages from Memory
    if st.sidebar.button("Clear message history"):
        chain_memory.clear()

    for msg in st.session_state.langchain_messages:
        avatar = "🦜" if msg.type == "ai" else None
        with st.chat_message(msg.type, avatar=avatar):
            st.markdown(msg.content)

    # Create the
    if user_input := st.chat_input(placeholder="Ask me a question!"):
        st.chat_message("user").write(user_input)
        with st.chat_message("assistant", avatar="🦜"):
            message_placeholder = st.empty()
            full_response = ""
            with callbacks.collect_runs() as cb:
                # All runnables have a .stream() method (as well as .invoke() and .batch())
                for chunk in chain.stream(
                    {"input": user_input}, config={"tags": ["share-trace-url-demo"]}
                ):
                    full_response += chunk.content
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                chain_memory.save_context(
                    {"input": user_input}, {"output": full_response}
                )

                run = cb.traced_runs[0]
                # If environment is set to "DEV", incorporate the trace
                # Useful for debugging. This is useful for when you want
                # to be annotating runs for eval/training or for when you want
                # to visualize the execution of you rchain in the browser
                if os.environ.get("ENVIRONMENT", "DEV"):
                    # st.sidebar.markdown(
                    #     f'<a href="{url}" target="_blank"><button>'
                    #     "Latest Trace: 🛠️</button></a>",
                    #     unsafe_allow_html=True,
                    # )
                    st.sidebar.button(
                        label="🛠️",
                        help="Navigate to the run trace.",
                        on_click=partial(navigate_to_trace_url, run),
                    )


main()
