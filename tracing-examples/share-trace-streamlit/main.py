"""Example Streamlit chat UI that exposes a Feedback button and link to LangSmith traces."""

import inspect
import logging
import operator
import os
import time
import uuid
from datetime import datetime

import langsmith
import streamlit as st
from langchain import callbacks, chat_models, memory, prompts
from langchain.schema import runnable

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="Chat LangSmith",
    page_icon="🦜",
)
"""# Displaying 🦜🛠️ Trace URLs

Have a chat! After each conversation turn, you should see\
 a "🛠️" button linking to the LangSmith trace for this
 chat bot. Ask the bot how it works!
"""
st.sidebar.markdown(
    """
# Menu
"""
)


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
    prompt = prompts.ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a Socratic CS tutor tasked with teaching the human"
                " about LangSmith. You areto guide the human through lesson on hw to add a link to a LangSmith trace"
                " in your LLM app. First introduce what and why this is useful, then walk them through defining te chain,"
                " using the collect_runs callback manager to capture the trace, and finally how to use the cient to fetch the URL."
                " This is useful when developing or debugging"
                " an LLM application, since it traces out the data flow through the Chain's execution graph."
                " For any give turn, only teach one step of the lesson, giving the human time to pause and ask questions."
                " The user can click the 🛠️ button in the side bar to see the trace for the conversation at point in time."
                " Here is the code for the tutorial:\n<CODE_{uuid}>\n{code}\n</CODE_{uuid}>"
                " \nIt's currently {time}."
                " Remember to stay on task! The user can't see the code.",
            ),
            prompts.MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    ).partial(
        uuid=lambda: uuid.uuid4(), code=sourcecode, time=lambda: str(datetime.now())
    )
    # The | operator promotes this DAG into a RunnableSequence,
    # which provides streaming, tracing, and other functionality
    # by default.
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
                # This
                for chunk in chain.stream(
                    {"input": user_input}, config={"tags": ["share-trace-url-demo"]}
                ):
                    full_response += chunk.content
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                chain_memory.save_context(
                    {"input": user_input}, {"output": full_response}
                )

                # If environment is set to "DEV", incorporate the trace
                # Useful for debugging. This is useful for when you want
                # to be annotating runs for eval/training or for when you want
                # to visualize the execution of you rchain in the browser
                if os.environ.get("ENVIRONMENT", "DEV"):
                    with st.elements.spinner.spinner("Fetching trace"):
                        client = langsmith.Client()
                        while True:
                            try:
                                url = client.read_run(cb.traced_runs[0]).url
                                # Convert http://localhost/o/00000000-0000-0000-0000-000000000000/projects/p/5998238e-c46b-424f-af29-2803133bf91e/r/4f3121dc-7798-4bc8-9228-55c6f6c8d1e0
                                # to http://localhost/o/00000000-0000-0000-0000-000000000000/playground/r/4f3121dc-7798-4bc8-9228-55c6f6c8d1e0
                                # Stri projects/p/UUID
                                # Or if you wat to share the run publicly
                                # url = client.share_run(run.id)
                                st.sidebar.markdown(
                                    f'<a href="{playground_url}" target="_blank"><button>'
                                    "Playground: </button></a>",
                                    unsafe_allow_html=True,
                                )
                                st.sidebar.markdown(
                                    f'<a href="{url}" target="_blank"><button>'
                                    "Latest Trace: 🛠️</button></a>",
                                    unsafe_allow_html=True,
                                )
                                break
                            except Exception as e:
                                # Currently (20230815) we fetch app path from server
                                # runs are commited async
                                logging.info(f"Retrying to read run. {e}")
                                time.sleep(1)


main()
