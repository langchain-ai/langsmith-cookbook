import uuid
from typing import Any, Callable, Optional

import langsmith
import pytest
from langchain.callbacks import tracers
from langchain.callbacks.tracers import run_collector
from langsmith import schemas

_CLIENT: Optional[langsmith.Client] = None
# Shared unique ID for an entire run of a pytest suite
_INVOCATION_UID = uuid.uuid4().hex


def _get_client() -> langsmith.Client:
    """Get the client."""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = langsmith.Client()
    return _CLIENT


def langsmith_unit_test(
    dataset_name: str,
    client: Optional[langsmith.Client] = None,
    project_name: Optional[str] = None,
) -> Callable:
    client_ = client or _get_client()
    examples = client_.list_examples(dataset_name=dataset_name)
    params = [
        (
            example,
            {
                "callbacks": [
                    tracers.LangChainTracer(
                        example_id=example.id, project_name=project_name
                    ),
                    run_collector.RunCollectorCallbackHandler(),
                ],
                "tags": ["pytest", _INVOCATION_UID],
            },
        )
        for example in examples
    ]

    def decorator(test_func: Callable):
        @pytest.mark.parametrize("example,config", params)
        def wrapper(
            request: Any,
            example: schemas.Example,
            config: dict,
            *args: Any,
            **kwargs: Any,
        ):
            func_name: str = test_func.__name__
            description = test_func.__doc__
            # TODO: Just specify a run ID once pr lands for LCEL
            run_collector_: run_collector.RunCollectorCallbackHandler = config[
                "callbacks"
            ][1]
            tracer: tracers.LangChainTracer = config["callbacks"][0]
            if project_name is None:
                tracer.project_name = f"{func_name}-{_INVOCATION_UID}"

            # Get any other non-langsmith fixtures for the unit test
            func_arg_names = test_func.__code__.co_varnames[
                : test_func.__code__.co_argcount
            ]
            fixture_values = {
                name: request.getfixturevalue(name)
                for name in func_arg_names
                if name not in ("example", "config")
            }
            try:
                test_func(
                    *args, example=example, config=config, **fixture_values, **kwargs
                )
                if run_collector_.traced_runs:
                    run = run_collector_.traced_runs[0]
                    tracer.wait_for_futures()
                    client_.create_feedback(
                        run_id=run.id,
                        key=func_name,
                        score=True,
                        value="Pass",
                        comment=description,
                    )
            except Exception as e:
                if run_collector_.traced_runs:
                    run = run_collector_.traced_runs[0]
                    tracer.wait_for_futures()
                    client_.create_feedback(
                        run_id=run.id,
                        key=func_name,
                        score=False,
                        value="Fail",
                        comment=f"Failed with error {e}\n{description}",
                    )

                raise e

        return wrapper

    return decorator
