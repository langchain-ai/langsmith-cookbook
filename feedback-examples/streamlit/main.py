import streamlit as st
from langchain.callbacks.tracers.run_collector import RunCollectorCallbackHandler
from langchain.memory import StreamlitChatMessageHistory, ConversationBufferMemory
from langchain.schema.runnable import RunnableConfig
from langsmith import Client
from streamlit_feedback import streamlit_feedback
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from expression_chain import get_expression_chain
from vanilla_chain import get_llm_chain

client = Client()

st.set_page_config(
    page_title="Chatbot with user feedback collection to LangSmith",
    page_icon="🦜",
)

st.subheader("🦜🛠️ Chatbot with user feedback collection to LangSmith")

st.sidebar.info('''
         
An example of a Streamlit Chat UI that features the Trubrics Feedback component and sends that feedback data to LangSmith.

- [Streamlit's chat elements Documentation](https://docs.streamlit.io/library/api-reference/chat)
- [Trubrics' Streamlit-Feedback](https://github.com/trubrics/streamlit-feedback)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
         
''')

st.subheader("")

# Initialize State
if "trace_link" not in st.session_state:
    st.session_state.trace_link = None
if "run_id" not in st.session_state:
    st.session_state.run_id = None

# Add a button to choose between llmchain and expression chain
_DEFAULT_SYSTEM_PROMPT = (
    "You are a funky parrot pal. You are not an AI. You are a parrot."
    " You love poetry, reading, funk music, and friendship!"
)
system_prompt = st.sidebar.text_area(
    "Custom Instructions",
    _DEFAULT_SYSTEM_PROMPT,
    help="Custom instructions to provide the language model to determine style, personality, etc.",
)
system_prompt = system_prompt.strip().replace("{", "{{").replace("}", "}}")

chain_type = st.sidebar.radio(
    "Choose a chain type",
    ("LLMChain", "Expression Chain"),
    help="Choose whether to use a vanilla LLMChain or an equivalent chain built using LangChain Expression Language.",
)

memory = ConversationBufferMemory(
    chat_memory=StreamlitChatMessageHistory(key="langchain_messages"),
    return_messages=True,
    memory_key="chat_history",
)

# Create Chain
if chain_type == "LLMChain":
    chain = get_llm_chain(system_prompt, memory)
else:
    chain = get_expression_chain(system_prompt, memory)

if st.sidebar.button("Clear message history"):
    print("Clearing message history")
    memory.clear()
    st.session_state.trace_link = None
    st.session_state.run_id = None

# Display chat messages from history on app rerun
def _get_openai_type(msg):
    if msg.type == "human":
        return "user"
    if msg.type == "ai":
        return "assistant"
    if msg.type == "chat":
        return msg.role
    return msg.type

for msg in st.session_state.langchain_messages:
    streamlit_type = _get_openai_type(msg)
    avatar = "🦜" if streamlit_type == "assistant" else None
    with st.chat_message(streamlit_type, avatar=avatar):
        st.markdown(msg.content)

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

def _reset_feedback():
    st.session_state.feedback_update = None
    st.session_state.feedback = None

if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)
    _reset_feedback()
    with st.chat_message("assistant", avatar="🦜"):
        message_placeholder = st.empty()
        full_response = ""

        # Define the basic input structure for the chains
        input_structure = {"input": prompt}

        # Handle LLMChain separately as it uses the invoke method
        if chain_type == "LLMChain":
            message_placeholder.markdown("thinking...")
            full_response = chain.invoke(input_structure, config=runnable_config)["text"]
        else:
            for chunk in chain.stream({"input": prompt}, config=runnable_config):
                full_response += chunk.content
                message_placeholder.markdown(full_response + "▌")
            memory.save_context({"input": prompt}, {"output": full_response})

        message_placeholder.markdown(full_response)

        run = run_collector.traced_runs[0]
        run_collector.traced_runs = []
        st.session_state.run_id = run.id
        wait_for_all_tracers()
        url = client.share_run(run.id)
        st.session_state.trace_link = url

# Check if there are chat messages in the session state before displaying the toggle
if st.session_state.get("langchain_messages"):
    feedback_option = "faces" if st.toggle(label="`Thumbs` ⇄ `Faces`", value=False) else "thumbs"
else:
    feedback_option = "thumbs"  # Default value

if st.session_state.get("run_id") and st.session_state.get("langchain_messages"):
    feedback = streamlit_feedback(
        feedback_type=feedback_option,
        optional_text_label="[Optional] Please provide an explanation",
        key=f"feedback_{st.session_state.run_id}",
    )

    # Define score mappings for both "thumbs" and "faces" feedback systems
    score_mappings = {
        "thumbs": {"👍": 1, "👎": 0},
        "faces": {"😀": 1, "🙂": 0.75, "😐": 0.5, "🙁": 0.25, "😞": 0},
    }

    # Get the score mapping based on the selected feedback option
    scores = score_mappings[feedback_option]

    if feedback:
        # Get the score from the selected feedback option's score mapping
        score = scores.get(feedback["score"])

        if score is not None:
            # Formulate feedback type string incorporating the feedback option and score value
            feedback_type_str = f"{feedback_option} {feedback['score']}"

            # Record the feedback with the formulated feedback type string and optional comment
            feedback_record = client.create_feedback(
                st.session_state.run_id, 
                feedback_type_str,
                score=score, 
                comment=feedback.get("text")
            )
            st.session_state.feedback = {"feedback_id": str(feedback_record.id), "score": score}
        else:
            st.warning("Invalid feedback score.")
