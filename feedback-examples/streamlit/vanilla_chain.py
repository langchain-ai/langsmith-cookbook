from datetime import datetime
from typing import Tuple
from langchain import LLMChain

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_llm_chain(
    system_prompt: str,
) -> Tuple[LLMChain, ConversationBufferMemory]:
    """Return a basic LLMChain with memory."""
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt + "\nIt's currently {time}.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    ).partial(time=lambda: str(datetime.now()))
    llm = ChatOpenAI(temperature=0.7)
    chain = LLMChain(prompt=prompt, llm=llm, memory=memory)
    return chain, memory


if __name__ == "__main__":
    chain, _ = get_llm_chain()
    print(chain.invoke({"input": "Hi there, I'm a human!"})["text"])
    print(chain.invoke({"input": "What's your name?"})["text"])
