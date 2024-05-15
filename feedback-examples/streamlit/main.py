import streamlit as st
from langchain import memory as lc_memory
from langsmith import Client
from streamlit_feedback import streamlit_feedback
from expression_chain import get_expression_chain
from langchain_core.tracers.context import collect_runs

client = Client()

st.set_page_config(
    page_title="Capturing User Feedback",
    page_icon="🦜️️🛠️",
)

st.subheader("🦜🛠️ Chatbot with Feedback in LangSmith")

st.sidebar.info(
    """
         
An example of a Streamlit Chat UI capturing user feedback.

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- Streamlit's [chat elements Documentation](https://docs.streamlit.io/library/api-reference/chat)
- Trubrics' [Streamlit-Feedback](https://github.com/trubrics/streamlit-feedback) component
         
"""
)

# Add a button to choose between llmchain and expression chain
_DEFAULT_SYSTEM_PROMPT = (
    "You are a funky parrot pal. You are not an AI. You are a parrot."
    " You love poetry, reading, funk music, and friendship!"
)
system_prompt = st.sidebar.text_area(
    "Custom Instructions",
    _DEFAULT_SYSTEM_PROMPT,
    help="Custom instructions to provide the language model to determine "
    "style, personality, etc.",
)
system_prompt = system_prompt.strip().replace("{", "{{").replace("}", "}}")

memory = lc_memory.ConversationBufferMemory(
    chat_memory=lc_memory.StreamlitChatMessageHistory(key="langchain_messages"),
    return_messages=True,
    memory_key="chat_history",
)

# Create Chain
chain = get_expression_chain(system_prompt, memory)

st.sidebar.markdown("## Feedback Scale")
feedback_option = (
    "thumbs" if st.sidebar.toggle(label="`Faces` ⇄ `Thumbs`", value=False) else "faces"
)

if st.sidebar.button("Clear message history"):
    print("Clearing message history")
    memory.clear()

for msg in st.session_state.langchain_messages:
    avatar = "🦜" if msg.type == "ai" else None
    with st.chat_message(msg.type, avatar=avatar):
        st.markdown(msg.content)


if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant", avatar="🦜"):
        message_placeholder = st.empty()
        full_response = ""
        # Define the basic input structure for the chains
        input_dict = {"input": prompt}

        with collect_runs() as cb:
            for chunk in chain.stream(input_dict, config={"tags": ["Streamlit Chat"]}):
                full_response += chunk.content
                message_placeholder.markdown(full_response + "▌")
            memory.save_context(input_dict, {"output": full_response})
            st.session_state.run_id = cb.traced_runs[0].id
        message_placeholder.markdown(full_response)

if st.session_state.get("run_id"):
    run_id = st.session_state.run_id
    feedback = streamlit_feedback(
        feedback_type=feedback_option,
        optional_text_label="[Optional] Please provide an explanation",
        key=f"feedback_{run_id}",
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
            # Formulate feedback type string incorporating the feedback option
            # and score value
            feedback_type_str = f"{feedback_option} {feedback['score']}"

            # Record the feedback with the formulated feedback type string
            # and optional comment
            feedback_record = client.create_feedback(
                run_id,
                feedback_type_str,
                score=score,
                comment=feedback.get("text"),
            )
            st.session_state.feedback = {
                "feedback_id": str(feedback_record.id),
                "score": score,
            }
        else:
            st.warning("Invalid feedback score.")
