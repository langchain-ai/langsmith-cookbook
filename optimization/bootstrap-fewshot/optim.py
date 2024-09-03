from collections import defaultdict
import itertools
from difflib import SequenceMatcher
from typing import Any, Callable, Iterable, Tuple

import langsmith as ls
import numpy as np
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langsmith.evaluation import EvaluationResult, EvaluationResults
from langsmith.evaluation._runner import ExperimentResultRow
from langsmith.schemas import Example, Run
from pydantic.v1 import BaseModel, Field, root_validator, ValidationError
from langchain_core.prompt_values import PromptValue
from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from rich.jupyter import print as richprint
from rich.panel import Panel


@ls.traceable
async def invoke_with_retries(
    prompt_value: PromptValue, model: BaseChatModel, schema: BaseModel
) -> BaseModel:
    model = model.with_structured_output(schema, include_raw=True)
    messages = prompt_value.to_messages()
    for _ in range(3):

        res = await model.ainvoke(messages)
        if res.get("parsing_error"):
            err = res.get("parsing_error")
            raw_message: AIMessage = res["raw"]
            messages = messages + [
                ToolMessage(
                    f"{repr(err)}\nRespond after fixing all validation errors.",
                    status="error",
                    tool_call_id=raw_message.tool_calls[0]["id"],
                )
            ]
        else:
            return res["parsed"]
    raise ValueError("Could not extract in sufficient steps")


async def run_optimizer(
    current_prompt: str, annotated_predictions: str, meta_prompt: str
):
    # Lazy way to get input variables
    input_variables = list(PromptTemplate.from_template(current_prompt).input_variables)

    class OptimizerOutput(BaseModel):
        """Think step-by-step, then write the optimized prompt."""

        task_objective: str = Field(
            description="What task is this prompt seeking to solve? What defines success here?"
        )
        brainstorm: str = Field(
            description="At least 3 bullet points brainstorming how to improve the prompt. Can focus on logical/correctness, style, or any other qualities that are salient, given the provided annotations."
        )
        plan: str = Field(
            description="Proposed edits and citations on which feedback will be improved."
        )
        improved_prompt: str = Field(
            description=f"The full text of the optimized prompt. Ensure that all the curly bracket {{variable_name}}'s are retained in the new prompt. These are: {input_variables}."
        )

        @root_validator
        def check_prompt_strings(cls, values):
            predicted_input_variables = list(
                PromptTemplate.from_template(
                    values.get("improved_prompt") or ""
                ).input_variables
            )
            missing = set(input_variables) - set(predicted_input_variables)
            extra = set(predicted_input_variables) - set(input_variables)
            if missing or extra:
                raise ValueError(
                    f"Unexpected variables included in output prompt. Expected {input_variables}. Got: {predicted_input_variables}.\nMissing: {missing}\nExtra: {extra}"
                )
            return values

    optim_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", meta_prompt),
            (
                "user",
                """Given the following annotated/evaluated predictions, optimize the provided prompt.
<annotated_predictions>
{annotated_predictions}
</annotated_predictions>

Remember to first brainstorm, then plan, and finally generate the optimized prompt. Remember to retain all bracketed variable placeholders.""",
            ),
        ]
    )

    model = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    val = optim_prompt.invoke(
        {
            "annotated_predictions": annotated_predictions,
            "current_prompt": current_prompt,
        }
    )
    return await invoke_with_retries(val, model, OptimizerOutput)


def format_evaluation_results(results: Iterable[ExperimentResultRow]):
    formatted = []
    for idx, res in enumerate(results):
        formatted.append(
            format_run_with_feedback(
                res["run"],
                res["example"],
                res.get("evaluation_results", {}).get("results") or [],
                idx,
            )
        )
    return formatted


@ls.traceable
async def run_optimizer_over_project(
    prompt: str, experiment_name: str, meta_prompt: str
) -> str:
    client = ls.Client()
    runs = list(
        client.list_runs(project_name=experiment_name, is_root=True, limit=100),
    )
    examples = {
        str(e.id): e
        for e in client.list_examples(
            example_ids=[r.reference_example_id for r in runs]
        )
    }
    feedback = defaultdict(list)
    for f in client.list_feedback(run_ids=[run.id for run in runs]):
        feedback[str(f.run_id)].append(f)
    joined = [
        {
            "run": run,
            "example": examples[str(run.reference_example_id)],
            "evaluation_results": {"results": feedback[str(run.id)]},
        }
        for run in runs
    ]
    formatted = format_evaluation_results(joined)
    updated = await run_optimizer(
        current_prompt=prompt,
        annotated_predictions="\n".join(formatted),
        meta_prompt=meta_prompt,
    )
    new_prompt = updated.improved_prompt
    print_rich_diff(prompt or "", new_prompt, "Prompt diff")
    return new_prompt


def format_feedback(single_feedback: EvaluationResult):
    if single_feedback.score is None:
        if single_feedback.value is not None:
            val = f"Value: {single_feedback.value}"
        else:
            val = ""
    else:
        val = f"\nScore:[{single_feedback.score}]"
    comment = f"\n{single_feedback.comment}" if single_feedback.comment else ""
    return f"""<feedback key={single_feedback.key}>{val}{comment}
</feedback>"""


def format_run_with_feedback(
    run: Run, example: Example, feedback: EvaluationResults, id: int
):
    all_feedback = "\n".join([format_feedback(f) for f in feedback])
    return f"""<example id={id}>
<input>
{str(run.inputs)[:400]}
</input>
<prediction>
{run.outputs}
</prediction>
<label>
{example.outputs}
</label>
<annotations>
{all_feedback}
</annotations>
</example>"""


## For if you're doing multiple loops/ non-user feedback
def step(
    construct_chain: Callable[[str], Callable[[dict], Any]],
    prompt: str,
    train_examples: list[Example],
    evaluators: list[Callable],
    step_idx: int,
) -> str:
    # TODO: Batching to speed it up
    chain = construct_chain(prompt)
    results = ls.evaluate(
        chain, data=train_examples[:15], evaluators=evaluators, blocking=False
    )
    formatted = format_evaluation_results(results)
    updated = run_optimizer(
        current_prompt=prompt, annotated_predictions="\n".join(formatted)
    )
    new_prompt = updated.improved_prompt
    print_rich_diff(prompt or "", new_prompt, f"Prompt diff at step {step_idx}")
    return new_prompt


def get_eval_score(eval_dataset, system, evaluators, step_n) -> float:
    """Compute the metrics on the validation dataset."""
    dev_results = ls.evaluate(
        system,
        # TODO: do whole
        data=itertools.islice(
            ls.Client().list_examples(dataset_name=eval_dataset), 0, 15
        ),
        evaluators=evaluators,
        metadata={
            "step": step_n,
        },
    )
    scores = []
    for res in dev_results:
        scores.append(res["evaluation_results"]["results"][0].score)
    # Assume single metric rn ha
    return np.mean(scores)


def train(
    chain_constructor: Callable[[str], Callable[[dict], Any]],
    original: str,
    train_dataset: str,
    eval_dataset: str,
    evaluators: list,
    steps: int = 5,
) -> list[Tuple[float, str]]:
    """Run the full training loop"""
    best_score = get_eval_score(
        eval_dataset, chain_constructor(original), evaluators, 0
    )
    best_step = 0
    scores = [(best_score, [])]
    train_examples = list(ls.Client().list_examples(dataset_name=train_dataset))
    updated = original
    for step_number in range(steps):
        updated = step(
            chain_constructor, updated, train_examples, evaluators, step_idx=step_number
        )
        updated_chain = chain_constructor(updated)
        updated_score = get_eval_score(
            eval_dataset, updated_chain, evaluators, step_number + 1
        )
        scores.append((updated_score, updated))

        if updated_score > best_score:
            print(
                f"New best score {updated_score} > {best_score}. Updating selected examples."
            )
            best_score = updated_score
            best_step = step_number + 1
        else:
            print(f"Underperformed ({updated_score} < {best_score}). Continuing")
    print("Best overall score: ", best_score)
    print("Best step: ", best_step)
    return sorted(scores, key=lambda x: x[0], reverse=True)


# Formating utils


# Random Utils:


def colorize_diff(diff):
    for op, i1, i2, j1, j2 in diff.get_opcodes():
        if op == "equal":
            yield diff.a[i1:i2]
        elif op == "insert":
            yield f"[green]{diff.b[j1:j2]}[/green]"
        elif op == "delete":
            yield f"[red]{diff.a[i1:i2]}[/red]"
        elif op == "replace":
            yield f"[red]{diff.a[i1:i2]}[/red][green]{diff.b[j1:j2]}[/green]"


def print_rich_diff(original, updated, title: str = ""):
    diff = SequenceMatcher(None, original, updated)
    colorized_diff = "".join(colorize_diff(diff))
    panel = Panel(
        colorized_diff, title=title or "Prompt Diff", expand=False, border_style="bold"
    )

    richprint(panel)
