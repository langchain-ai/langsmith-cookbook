import functools
from typing import Optional
import uuid
import streamlit as st
from streamlit_feedback import streamlit_feedback
from langsmith import Client
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import re
import random
from langchain import hub

DATASET_NAME = "Tweet Critic"

client = Client()

st.set_page_config(
    page_title="Prompt Optimization with Feedback",
    page_icon="🦜️️🛠️",
)


## Get few-shot examples from 👍 examples
def _format_example(example):
    return f"""<example>
    <original>
    {example.inputs['input']}
    </original>
    <tweet>
    {example.outputs['output']}
    </tweet>
</example>"""


def few_shot_examples():
    if client.has_dataset(dataset_name=DATASET_NAME):
        # TODO: Update to randomize
        examples = list(client.list_examples(dataset_name=DATASET_NAME))
        if not examples:
            return ""
        examples = random.sample(examples, min(len(examples), 10))
        e_str = "\n".join([_format_example(e) for e in examples])

        return f"""

Approved Examples:
{e_str}
"""
    return ""


if st.session_state.get("few_shots"):
    few_shots = st.session_state.get("few_shots")
else:
    few_shots = few_shot_examples()
    st.session_state["few_shots"] = few_shots


# Create the chat bot
prompt = hub.pull("wfh/tweet-critic-fewshot")
prompt = prompt.partial(examples=few_shots)
llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=1)

tweet_critic = prompt | llm | StrOutputParser()

# Render the messages


def parse_tweet(response: str, turn: int, box=None):
    match = re.search(r"(.*?)<tweet>(.*?)</tweet>(.*?)", response.strip(), re.DOTALL)
    box = box or st
    pre, tweet, post = match.groups() if match else (response, None, None)
    if pre:
        box.markdown(pre)
    if tweet is not None:
        tweet = st.text_area(
            "Edit this to save your refined tweet",
            tweet,
            key=f"tweet_{turn}",
            height=500,
        )
    if post:
        box.markdown(post)
    return tweet


def log_feedback(
    value: dict,
    *args,
    presigned_url: str,
    original_tweet: Optional[str] = None,
    txt: Optional[str] = None,
    **kwargs,
):
    score = {"👍": 1, "👎": 0}.get(value["score"]) or 0
    comment = value.get("text")
    client.create_feedback_from_token(presigned_url, score=int(score), comment=comment)

    if score and original_tweet and txt:
        # If the input/output pairs are provided, you can log them to a few-shot dataset.
        try:
            client.create_example(
                inputs={"input": original_tweet},
                outputs={"output": txt},
                dataset_name=DATASET_NAME,
            )
        except:  # noqa: E722
            client.create_dataset(dataset_name=DATASET_NAME)
            client.create_example(
                inputs={"input": original_tweet},
                outputs={"output": txt},
                dataset_name=DATASET_NAME,
            )


messages = st.session_state.get("langchain_messages", [])
original_tweet = messages[0][1] if messages else None
for i, msg in enumerate(messages):
    with st.chat_message(msg[0]):
        if len(msg) == 3:
            updated = parse_tweet(msg[1], i)
            presigned_url = msg[2]
            feedback = streamlit_feedback(
                feedback_type="thumbs",
                optional_text_label="[Optional] Please provide an explanation",
                on_submit=functools.partial(
                    log_feedback,
                    presigned_url=presigned_url,
                    original_tweet=original_tweet,
                    txt=updated,
                ),
                key=f"fb_{i}",
            )
        else:
            updated = None
            st.markdown(msg[1])
            presigned_url = None


# Run the chat conversation
run_id = uuid.uuid4()
presigned = client.create_presigned_feedback_token(
    run_id, feedback_key="tweet_critique_quality"
)

if prompt := st.chat_input(placeholder="What's the tweet about?"):
    st.chat_message("user").write(prompt)
    original_tweet = prompt
    messages.append(("user", prompt))
    with st.chat_message("assistant", avatar="🦜"):
        write_stream = tweet_critic.stream(
            {"messages": [tuple(msg[:2]) for msg in messages]},
            config={"run_id": run_id},
        )
        message_placeholder = st.empty()
        full_response = ""
        for chunk in write_stream:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown("")
        tweet_txt = parse_tweet(full_response, len(messages), message_placeholder)
        messages.append(("assistant", full_response, presigned.url))
    st.session_state["langchain_messages"] = messages
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Optional] Please provide an explanation",
        on_submit=functools.partial(
            log_feedback,
            presigned_url=presigned.url,
            original_tweet=original_tweet,
            txt=tweet_txt,
        ),
        key=f"fb_{len(messages) - 1}",
    )
