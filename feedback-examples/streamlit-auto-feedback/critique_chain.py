from datetime import datetime
import operator

from langchain import chat_models
from langchain import prompts
from langchain.schema import runnable
from langchain import memory
import langsmith
from langchain.output_parsers import openai_functions


def get_critique_chain(
    memory: memory.ConversationBufferMemory, client: langsmith.Client
) -> runnable.Runnable:
    """Return a functions chain that critiques the prediction given the user's next response."""
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
                "You are a QA assurance agent shadowing a colleague. Review the following"
                " conversation and score the quality of "
                " the AI assistant's last response, taking the user's next response into account."
                " for instance, if the user corrects the AI saying 'no' or seems frustrated, "
                " you should score the AI's last response poorly."
                "\nIt's currently {time}.\n\n<TRANSCRIPT>",
            ),
            prompts.MessagesPlaceholder(variable_name="chat_history"),
            # TODO: Could fetch previous feedback from this user / store in DB
            # to provide few-shot examples of good and bad responses for this user.
            ("human", "{input}"),
            (
                "system",
                "</TRANSCRIPT>\nBased on the previous messages, how would you "
                "rate the AI's last response? Use the critique function.",
            ),
        ]
    ).partial(time=lambda: str(datetime.now()))

    schema = {
        "name": "critique",
        "description": "Save critique for later review.",
        "parameters": {
            "type": "object",
            "properties": {
                "score": {
                    "type": "integer",
                    "description": "The numeric grade (from 1 to 10) stating how well your colleague's"
                    " response satisfied the user's need.",
                    "minimum": 1,
                    "maximum": 10,
                },
                "comment": {
                    "type": "string",
                    "description": "Step-by-step reasoning or explanation for the score.",
                },
                "correction": {
                    "type": "object",
                    "description": "What would a more appropriate response have been?",
                },
            },
        },
    }

    llm = chat_models.ChatOpenAI(temperature=0.7).bind(functions=[schema])
    chain = ingress | prompt | llm | openai_functions.JsonOutputFunctionsParser()

    feedback_chain = runnable.RunnableMap(
        {
            "result": (lambda x: {"input": x["input"]}) | chain,
            "run_id": operator.itemgetter("run_id"),
        }
    ) | (
        lambda x: client.create_feedback(
            run_id=x["run_id"], key="ai_score", **x["result"]
        )
    )

    return feedback_chain
