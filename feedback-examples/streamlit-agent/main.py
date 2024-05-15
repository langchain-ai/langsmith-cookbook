"""Example implementation of a LangChain Agent."""
import logging
from datetime import datetime
from functools import partial

import streamlit as st
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers.openai_functions import (
    OpenAIFunctionsAgentOutputParser,
)
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.pydantic_v1 import BaseModel, Field
from langsmith import Client
from streamlit_feedback import streamlit_feedback
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tracers.context import tracing_v2_enabled
from langchain_core.utils.function_calling import format_tool_to_openai_function
from langchain_openai import ChatOpenAI

st.set_page_config(
    page_title="Streamlit Agent with LangSmith",
    page_icon="🦜️️🛠️",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Client()

st.subheader("🦜🛠️ Ask the bot some questions")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


class DDGInput(BaseModel):
    query: str = Field(description="search query to look up")


tools = [
    DuckDuckGoSearchResults(
        name="duck_duck_go", args_schema=DDGInput
    ),  # General internet search using DuckDuckGo
]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Current date: {time}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
).partial(time=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))

MEMORY = ConversationBufferMemory(
    chat_memory=StreamlitChatMessageHistory(key="langchain_messages"),
    return_messages=True,
    memory_key="chat_history",
)
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_functions(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x.get("chat_history") or [],
    }
    | prompt
    | llm.bind_functions(functions=[format_tool_to_openai_function(t) for t in tools])
    | OpenAIFunctionsAgentOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)


def _submit_feedback(user_response: dict, emoji=None, run_id=None):
    score = {"👍": 1, "👎": 0}.get(user_response.get("score"))
    client.create_feedback(
        run_id=run_id,
        key=user_response["type"],
        score=score,
        comment=user_response.get("text"),
        value=user_response.get("score"),
    )
    return user_response


if st.sidebar.button("Clear message history"):
    MEMORY.clear()

feedback_kwargs = {
    "feedback_type": "thumbs",
    "optional_text_label": "Rate this response in LangSmith",
}
if "feedback_key" not in st.session_state:
    st.session_state.feedback_key = 0

messages = st.session_state.get("langchain_messages", [])
for i, msg in enumerate(messages):
    avatar = "🦜" if msg.type == "ai" else None
    with st.chat_message(msg.type, avatar=avatar):
        st.markdown(msg.content)
    if msg.type == "ai":
        feedback_key = f"feedback_{int(i/2)}"

        if feedback_key not in st.session_state:
            st.session_state[feedback_key] = None

        disable_with_score = (
            st.session_state[feedback_key].get("score")
            if st.session_state[feedback_key]
            else None
        )
        # This actually commits the feedback
        streamlit_feedback(
            **feedback_kwargs,
            key=feedback_key,
            disable_with_score=disable_with_score,
            on_submit=partial(
                _submit_feedback, run_id=st.session_state[f"run_{int(i/2)}"]
            ),
        )


if st.session_state.get("run_url"):
    st.markdown(
        f"View trace in [🦜🛠️ LangSmith]({st.session_state.run_url})",
        unsafe_allow_html=True,
    )
if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant", avatar="🦜"):
        message_placeholder = st.empty()
        full_response = ""
        # Define the basic input structure for the chains
        input_dict = {
            "input": prompt,
        }
        input_dict.update(MEMORY.load_memory_variables({"query": prompt}))
        st_callback = StreamlitCallbackHandler(st.container())
        with tracing_v2_enabled("langsmith-streamlit-agent") as cb:
            for chunk in agent_executor.stream(
                input_dict,
                config={"tags": ["Streamlit Agent"], "callbacks": [st_callback]},
            ):
                full_response += chunk["output"]
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            feedback_kwargs = {
                "feedback_type": "thumbs",
                "optional_text_label": "Please provide extra information",
                "on_submit": _submit_feedback,
            }
            run = cb.latest_run
            MEMORY.save_context(input_dict, {"output": full_response})
            feedback_index = int(
                (len(st.session_state.get("langchain_messages", [])) - 1) / 2
            )
            st.session_state[f"run_{feedback_index}"] = run.id
            # This displays the feedback widget and saves to session state
            # It will be logged on next render
            streamlit_feedback(**feedback_kwargs, key=f"feedback_{feedback_index}")
            try:
                url = cb.get_run_url()
                st.session_state.run_url = url
                st.markdown(
                    f"View trace in [🦜🛠️ LangSmith]({url})",
                    unsafe_allow_html=True,
                )
            except Exception:
                logger.exception("Failed to get run URL.")
