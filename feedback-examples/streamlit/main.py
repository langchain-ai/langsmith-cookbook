"""Example Streamlit chat UI that exposes a Feedback button and link to LangSmith traces."""

import streamlit as st
from langchain.callbacks.tracers.run_collector import RunCollectorCallbackHandler
from langchain.schema.runnable import RunnableConfig
from langsmith import Client
from expression_chain import get_expression_chain
from vanilla_chain import get_llm_chain


client = Client()

st.set_page_config(
    page_title="Chat LangSmith",
    page_icon="🦜",
    layout="wide",
)
"# Chat🦜🛠️"
# Initialize State
if "messages" not in st.session_state:
    print("Initializing message history")
    st.session_state["messages"] = []
if "trace_link" not in st.session_state:
    st.session_state["trace_link"] = None
st.sidebar.markdown(
    """
# Menu
"""
)
if st.sidebar.button("Clear message history"):
    print("Clearing message history")
    st.session_state.messages = []

# Add a button to choose between llmchain and expression chain
_DEFAULT_SYSTEM_PROMPT = (
    "You are a funky parrot pal. You are not an AI. You are a parrot."
    " You love poetry, reading, funk music, friendship, and squawking!"
)

system_prompt = st.sidebar.text_area(
    "Custom Instructions",
    _DEFAULT_SYSTEM_PROMPT,
    help="Custom instructions to provide the language model to determine style, personality, etc.",
)
system_prompt = system_prompt.strip().replace("{", "{{").replace("}", "}}")

chain_type = st.sidebar.radio(
    "Choose a chain type",
    ("Expression Language Chain", "LLMChain"),
    help="Choose whether to use a vanilla LLMChain or an equivalent chain built using LangChain Expression Language.",
)

# Create Chain
if chain_type == "LLMChain":
    chain, memory = get_llm_chain(system_prompt)
else:
    chain, memory = get_expression_chain(system_prompt)


# Display chat messages from history on app rerun
def _get_openai_type(msg):
    if msg.type == "human":
        return "user"
    if msg.type == "ai":
        return "assistant"
    if msg.type == "chat":
        return msg.role
    return msg.type


for msg in st.session_state.messages:
    streamlit_type = _get_openai_type(msg)
    avatar = "🦜" if streamlit_type == "assistant" else None
    with st.chat_message(streamlit_type, avatar=avatar):
        st.markdown(msg.content)
    # Re-hydrate memory on app rerun
    memory.chat_memory.add_message(msg)


def send_feedback(run_id, score):
    client.create_feedback(run_id, "user_score", score=score)


run_collector = RunCollectorCallbackHandler()
runnable_config = RunnableConfig(
    callbacks=[run_collector],
    tags=["Streamlit Chat"],
)
if st.session_state.trace_link:
    st.sidebar.markdown(
        f'<a href="{st.session_state.trace_link}" target="_blank"><button>Latest Trace: 🛠️</button></a>',
        unsafe_allow_html=True,
    )

if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant", avatar="🦜"):
        message_placeholder = st.empty()
        full_response = ""
        if chain_type == "LLMChain":
            message_placeholder.markdown("thinking...")
            full_response = chain.invoke({"input": prompt}, config=runnable_config)[
                "text"
            ]
        else:
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
        with col3:
            # Requires langsmith >= 0.0.19
            url = client.share_run(run.id)
            # Or if you just want to use this internally
            # without sharing
            # url = client.read_run(run.id).url
            st.session_state.trace_link = url
            st.markdown(
                f'<a href="{url}" target="_blank"><button>🛠️</button></a>',
                unsafe_allow_html=True,
            )
