from datetime import datetime

from langchain import chat_models
from langchain import prompts 
from langchain.schema import runnable 
from langchain import memory


def get_expression_chain(
    system_prompt: str, memory: memory.ConversationBufferMemory
) -> runnable.Runnable:
    """Return a chain defined primarily in LangChain Expression Language"""
    ingress = runnable.RunnableMap(
        {
            "input": lambda x: x["input"],
            "chat_history": lambda x: memory.load_memory_variables(x)["chat_history"],
            "time": lambda _: str(datetime.now()),
        }
    )
    prompt = prompts.ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt + "\nIt's currently {time}.",
            ),
            prompts.MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )
    llm = chat_models.ChatOpenAI(temperature=0.7)
    return ingress | prompt | llm


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
