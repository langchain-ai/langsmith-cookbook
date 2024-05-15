import uuid
from operator import itemgetter

import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain.chains import RetrievalQA
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableParallel
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings


@st.cache_resource
def get_retriever() -> BaseRetriever:
    # In a real application, this would be run once than indexed on a schedule
    # See other techniques for more sophisticated retrieveal methods
    # https://python.langchain.com/docs/modules/data_connection/
    api_loader = RecursiveUrlLoader("https://docs.smith.langchain.com")
    text_splitter = TokenTextSplitter(
        model_name="gpt-3.5-turbo",
        chunk_size=2000,
        chunk_overlap=200,
    )
    doc_transformer = Html2TextTransformer()
    raw_documents = api_loader.load()
    transformed = doc_transformer.transform_documents(raw_documents)
    docs = text_splitter.split_documents(transformed)
    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(
        collection_name="full_documents", embedding_function=OpenAIEmbeddings()
    )
    # The storage layer for the parent documents
    store = InMemoryStore()
    id_key = "doc_id"
    # The retriever (empty to start)
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )

    doc_ids = [str(uuid.uuid4()) for _ in docs]
    # The splitter to use to create smaller chunks
    child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
    sub_docs = []
    for i, doc in enumerate(docs):
        _id = doc_ids[i]
        _sub_docs = child_text_splitter.split_documents([doc])
        for _doc in _sub_docs:
            _doc.metadata[id_key] = _id
        sub_docs.extend(_sub_docs)

    retriever.vectorstore.add_documents(sub_docs)
    retriever.docstore.mset(list(zip(doc_ids, docs)))
    return retriever


MEMORY = ConversationBufferMemory(
    chat_memory=StreamlitChatMessageHistory(key="langchain_messages"),
    return_messages=True,
    memory_key="chat_history",
)

RETRIEVER = get_retriever()


def get_chain(chain_type: str):
    if chain_type == "runnable":
        return (
            RunnableParallel(
                {
                    "documents": itemgetter("query")
                    | RETRIEVER
                    | (lambda docs: "\n\n".join(doc.page_content for doc in docs)),
                    "query": itemgetter("query"),
                    "chat_history": itemgetter("chat_history"),
                }
            ).with_config(run_name="RetrieveDocs")
            | ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a helpful assistant. Respond to the user question using the"
                        " following retrieved documents:\n<DOCUMENTS>\n{documents}</DOCUMENTS>\n"
                        "If you do not know the answer, you can say 'I don't know'"
                        " or 'I'm not sure",
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("user", "{query}"),
                ]
            )
            | ChatAnthropic(model="claude-instant-1.2", temperature=1)
            | StrOutputParser()
        )
    elif chain_type == "RetrievalQA":
        return RetrievalQA.from_chain_type(
            llm=ChatAnthropic(model="claude-instant-1.2", temperature=1),
            chain_type="stuff",
            retriever=RETRIEVER,
            memory=MEMORY,
        ) | (lambda x: x["result"])
    else:
        raise NotImplementedError(
            f"Chain type {chain_type} not implemented. Try 'runnable' or 'RetrievalQA'"
        )
