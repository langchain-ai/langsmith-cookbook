import logging

import langsmith
import streamlit as st
from langchain import callbacks, chat_models
from langchain_core.prompts import ChatPromptTemplate

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="LangSmith Trace Tutor",
    page_icon="🦜",
    initial_sidebar_state="collapsed",
)
"""# Using 🦜🛠️ Trace URLs

Have a chat! When you're done, click the 🛠️ button to see the trace URL."""
client = langsmith.Client()


#### Define Chain
chain = (
    ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful bot but don't remember much."),
            ("user", "{input}"),
        ]
    )
    # You can use another model provider, such as ollama, openai, etc.
    | chat_models.ChatAnthropic(model="claude-instant-1.2", temperature=1)
)

if user_input := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(user_input)
    with st.chat_message("assistant", avatar="🦜"):
        message_placeholder = st.empty()
        full_response = ""
        with callbacks.tracing_v2_enabled() as cb:
            for chunk in chain.stream(
                {"input": user_input}, config={"tags": ["share-trace-url-demo"]}
            ):
                full_response += chunk.content
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            url = cb.get_run_url()
    # Useful for when you want to debug or annotating runs
    # for eval/training while you're developing
    st.markdown(
        f'<a href="{url}" target="_blank">Latest Trace: 🛠️</a>',
        unsafe_allow_html=True,
    )
