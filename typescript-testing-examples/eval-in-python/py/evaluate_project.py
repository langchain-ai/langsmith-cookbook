"""An example script to evaluate an existing test project."""
import json
import os
from typing import Optional

from langchain.schema.runnable import RunnableLambda
from langchain.evaluation import load_evaluator
from langsmith import Client

from langsmith.evaluation import EvaluationResult, RunEvaluator
from langsmith.schemas import Example, Run


class JsonValueDistance(RunEvaluator):
    def __init__(self) -> None:
        super().__init__()
        self.distance_evaluator = load_evaluator("string_distance")
        self.eval_name = "json_string_similarity"

    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> EvaluationResult:
        """Evaluate an example."""
        if run.outputs is None:
            raise ValueError("Run outputs cannot be None")
        prediction = next(iter(run.outputs.values()))
        reference = next(iter(example.outputs.values()))
        if not reference:
            return EvaluationResult(
                key=self.eval_name, score=None, comment="No reference"
            )
        try:
            obj = json.loads(prediction)
        except Exception as e:
            return EvaluationResult(key=self.eval_name, score=0.0, comment=str(e))
        distances = []
        for key in reference:
            if key in obj:
                norm_distance = self.distance_evaluator.evaluate_strings(
                    prediction=str(obj[key]), reference=str(reference[key])
                )["score"]
            else:
                norm_distance = 1.0
            distances.append(norm_distance)
        return EvaluationResult(
            key=self.eval_name, score=1.0 - sum(distances) / len(distances)
        )


def evaluate_existing_project(project_name: str):
    client = Client()
    runs = client.list_runs(project_name=project_name, execution_order=1)
    evaluator = JsonValueDistance()
    batched_evaluator = RunnableLambda(
        lambda run: client.evaluate_run(run, evaluator=evaluator)
    )
    all_feedback = batched_evaluator.batch(list(runs))
    scores = [feedback.score for feedback in all_feedback if feedback.score is not None]
    print(f"Average score: {sum(scores) / len(scores)}")


if __name__ == "__main__":
    dataset_name = "Structured Output Example"
    project_name = os.environ.get("LANGCHAIN_PROJECT", "Unit Testing") + dataset_name
    evaluate_existing_project(project_name=project_name)
