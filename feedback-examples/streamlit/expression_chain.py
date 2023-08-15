from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import Runnable, RunnableMap
from langchain.memory import ConversationBufferMemory


def get_expression_chain(
    system_prompt: str, memory: ConversationBufferMemory
) -> Runnable:
    """Return a chain defined primarily in LangChain Expression Language"""
    ingress = RunnableMap(
        {
            "input": lambda x: x["input"],
            "chat_history": lambda x: memory.load_memory_variables(x)["chat_history"],
            "time": lambda _: str(datetime.now()),
        }
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt + "\nIt's currently {time}.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )
    llm = ChatOpenAI(temperature=0.7)
    chain = ingress | prompt | llm
    return chain


if __name__ == "__main__":
    chain, _ = get_expression_chain()
    in_ = "Hi there, I'm a human!"
    print(in_)
    for chunk in chain.stream({"input": in_}):
        print(chunk.content, end="", flush=True)
    in_ = "What's your name?"
    print()
    print(in_)
    for chunk in chain.stream({"input": in_}):
        print(chunk.content, end="", flush=True)
