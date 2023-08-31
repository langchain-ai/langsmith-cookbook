# Evaluating Existing Runs

This tutorial shows how to evaluate and tag runs after they've already been logged to a project. This is useful when:
- You have a new evaluator or version of an evaluator and want to add the eval metrics to existing test projects
- You want to use AI-assisted feedback within monitoring projects (non-test projects)
- Your model isn't defined in python or typescript but you want to add evaluation metrics

The typical steps are:

1. Select the runs you wish to evaluate (see the [run filtering](https://docs.smith.langchain.com/tracing/use-cases/export-runs/local) docs for more information)
2. Define the RunEvaluator
3. Call the `client.evaluate_run` method, which runs the evaluation and logs the results as feedback.

    - _alternatively, call `client.create_feedback` method directly, since evaluation results are logged as model feedback_
    

This is all you need to start logging eval feedback to an existing project.
Below, we will review how to list the runs to evaluate.

## 1. Select runs to evaluate

We will consider two scenarios:

    a. Evaluating a test project (a project created when calling the `run_on_dataset` function)
    b. Evaluating runs in a monitoring or debug project (all other projects)
    
In either case, once you have the project name or ID, you can list the runs to evaluate or add feedback to by calling the `list_runs` method on the client.
    
#### a. Test Projects

Each time you run call `run_on_dataset` to evaluate a model, a new "test project" is created containing the model's runs and the evaluator feedback. Each run contains the inputs and outputs to the component as well as a reference to the dataset example (row) it came from.


The easiest way to find the project name or ID is in the web app. Navigating to "Datasets & Testing", selecting a dataset, and then copying one of the project names from the test runs table. Below is an example of the Dataset & Testing page, with all the datasets listed out. We will select the "Chat Langchain Questions" dataset.

<img src="./img/datasets_and_testing.png" alt="Datasets & Testing Page" style="width:75%">

Once you've selected one of the datasets, a list of test projects will be displayed. You can copy the project name from the table directly.

<img src="./img/test_projects_page.png" alt="Test Projects" style="width:75%">

Or if you navigate to the test page, you can copy the project name from the title or the ID from the url.

<img src="./img/test_page.png" alt="Test Page" style="width:75%">


Then once you have the project name or ID, you can list the runs to evaluate by calling `list_runs`.


```python
from langsmith import Client

client = Client()

# Copy the project name or ID and paste it in the corresponding field below
runs = client.list_runs(
    project_name = "fedb3000a5be453b881bf3c4aa22b5cb-RetrievalQA",
    # Or by ID
    # project_id = "0fc4f999-bdd3-4a7e-b2d7-bdf837d57cd9",
    execution_order = 1,
)
```

Since this is a test project, each run will have a reference to the dataset example, meaning you can apply a labeled evaluator such as the [cot_qa](https://api.python.langchain.com/en/latest/evaluation/langchain.evaluation.qa.eval_chain.CotQAEvalChain.html#langchain.evaluation.qa.eval_chain.CotQAEvalChain) evaluator to these runs.

#### b. Monitoring and Debug Projects

For all other projects, you can find the project name or ID directly in the "[Projects](https://smith.langchain.com/projects)" page for your organization. 

When applying feedback to a monitoring project, you may want to filter by time or other criteria. For instance, to fetch today's traces in the `default` project, you 
can use the following query:


```python
import datetime

midnight = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
runs = client.list_runs(
    project_name="default",
    execution_order=1,
    start_time = midnight
)
```

For information on more advanced filtering techniques, check out the [run filtering docs](https://docs.smith.langchain.com/tracing/use-cases/export-runs/local).
Since these projects are not typically associated with a dataset, you will have to use 'reference-free' evaluators [Criteria evaluator](https://docs.smith.langchain.com/evaluation/evaluator-implementations#no-labels-criteria-evaluation) to create evaluation feedback without reference labels.

Once you've decided the runs you want to evaluate, it's time to define the evaluator.

## 2. Define Evaluator

You may already know what you want to test to ensure you application is functioning as expected. In that case, you can easily add that logic to a custom evaluator to get started.
You can also configure one of LangChain's off-the-shelf evaluators to use to test for things like correctness, helpfulness, embedding or string distance, or other metrics.
For more information on some of the existing open source evaluators, check out the [documentation](https://python.langchain.com/docs/guides/evaluation).

### Custom Evaluator

You can add automated/algorithmic feedback to existing runs using just the SDK in two steps:
1. Subclassing the RunEvaluator class and implementing the evaluate_run method
2. Calling the `evaluate_run` method directly on the client

The `evaluate_run` method loads a reference example if present, applies the evaluator to the run and optional example, and then logs the feedback to LangSmith.
Below, create a custom evaluator that checks for any digits in the prediction.


```python
from typing import Optional

from evaluate import load
from langsmith.evaluation import EvaluationResult, RunEvaluator
from langsmith.schemas import Example, Run


class ContainsDigits(RunEvaluator):

    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> EvaluationResult:
        if run.outputs is None:
            raise ValueError("Run outputs cannot be None")
        prediction = str(next(iter(run.outputs.values())))
        contains_digits = any(c.isdigit() for c in prediction)
        return EvaluationResult(key="Contains Digits", score=contains_digits)
```

Our custom evaluator is a simple reference-free check for boolean presence of digits in the output. In your case you may want to check for PII, assert the result conforms to some schema, or even parse and compare generated code.

The logic fetching the prediction above assumes your chain only returns one value, meaning the `run.outputs` dictionary will have only one key. If there are multiple keys in your outputs, you will have to select whichever key(s) you wish to evaluate or test the whole outputs dictionary directly as a string. For more information on creating a custom evaluator, check out the [docs](https://docs.smith.langchain.com/evaluation/custom-evaluators).

Below, apply the evaluator to all runs in the "My Test" project.


```python
project_name="LangSmith Retrieval QA Project"
evaluator = ContainsDigits()
runs = client.list_runs(
    project_name=project_name,
    execution_order=1,
)

for run in runs:
    feedback = client.evaluate_run(run, evaluator)
```

The evaluation results will all be saved as feedback to the run trace. LangSmith aggregates the feedback over the project for you asynchronously, so after some time you will be
able to see the feedback results directly on the project stats.


```python
# Updating the aggregate stats is async, but after some time, the "Contains Digits" feedback will be available
client.read_project(project_name=project_name).feedback_stats
```




    {'Perplexity': {'n': 3, 'avg': 20.9166269302368, 'mode': 12.5060758590698},
     'Contains Digits': {'n': 7, 'avg': 0.42857142857142855, 'mode': 0},
     'sufficient_code': {'n': 7, 'avg': 0.5714285714285714, 'mode': 1},
     'LangSmith Category': {'n': 21, 'avg': None, 'mode': None},
     'COT Contextual Accuracy': {'n': 7, 'avg': 0.7142857142857143, 'mode': 1}}



### LangChain evaluators

LangChain has a number of evaluators you can  use off-the-shelf or modify to suit your needs. An easy way to use these is to modify the code above and apply the evaluator directly to the run. For more information on available LangChain evaluators, check out the [open source documentation](https://python.langchain.com/docs/guides/evaluation).

Below, we will demonstrate this by using the criteria evaluator, which instructs an LLM to check that the prediction against the described criteria. 
In this case, we will check that the responses contain both a python and typescript example, if needed, since LangSmith's SDK supports both languages.


```python
from langchain import evaluation, callbacks

class SufficientCodeEvaluator(RunEvaluator):
    
    def __init__(self):
        criteria_description=(
            "If the submission contains code, does it contain both a python and typescript example?"
            " Y if no code is needed or if both languages are present, N if response is only in one language"
        )
        self.evaluator = evaluation.load_evaluator("criteria", 
                                      criteria={
                                          "sufficient_code": criteria_description
                                      })
    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> EvaluationResult:
        question = next(iter(run.inputs.values()))
        prediction = str(next(iter(run.outputs.values())))
        with callbacks.collect_runs() as cb:
            result = self.evaluator.evaluate_strings(input=question, prediction=prediction)
            run_id = cb.traced_runs[0].id
        return EvaluationResult(key="sufficient_code", evaluator_info={"__run": {"run_id": run_id}}, **result)

```


```python
runs = client.list_runs(
    project_name=project_name,
    execution_order=1,
)
evaluator = SufficientCodeEvaluator()
for run in runs:
    feedback = client.evaluate_run(run, evaluator)
```

### (advanced) Using a custom chain

In LangSmith, evaluation results are feedback. The `Evaluator` abstractions help to orchestrate this, but you can also choose to save any computed values as feedback on the run.
This is especially easy when using LangChain runnables. 

Let's make an example that tags each run's input using an LLM. You could apply this to a sample of production runs to further categorize them.

In the example below, we will use LangChain's runnable lambda to conveniently batch calls, and use a runnable chain to perform the tagging.


```python
from langchain import chat_models, prompts, callbacks, schema

chain = (
    prompts.ChatPromptTemplate.from_template(
    "The following is a user question:\n<question>\n{question}</question>\n\n"
    "Categorize it into 1 of the following categories:\n"
    "- API\n- Tracing\n- Evaluation\n- Off-Topic\n- Other\n\nCategory:")
    | chat_models.ChatOpenAI()
    | schema.output_parser.StrOutputParser()
)

def evaluate_run(run: Run, config: dict):
    # You can get the run ID using the collect_runs callback manager
    with callbacks.collect_runs() as cb:
        result = chain.invoke({"question": next(iter(run.inputs.values()))}, config)
        feedback = client.create_feedback(
            run.id,
            key="LangSmith Category",
            value=result,
            source_run_id=cb.traced_runs[0].id,
            feedback_source_type="model",
        )
    return feedback

wrapped_function = schema.runnable.RunnableLambda(evaluate_run)
```

Here, we are using the `collect_runs` callback handler to easily fetch the run ID from the evaluation run. By adding it as the `source_run_id`, the feedback will retain a link from the evaluated run to the source run so you can see why the tag was generated. Below, we will log feedback to all the traces in the specified project.


```python
runs = client.list_runs(
    project_name=project_name,
    execution_order=1,
)
all_feedback = wrapped_function.batch([run for run in runs], return_errors=True)

# Example of the first feedback example
all_feedback[0]
```

Check out the target project to see the feedback appear as the runs are tagged.

### Evaluating the whole trace

For all the examples above, we've been working with individual runs. By default, LangSmith will not return all the nested run spans in the trace. 
For some evaluations, however, you may want to consider information contained across different child runs. You can do this by setting the `load_child_runs` argument to `True` when calling `evaluate_run`.

An example of when this is useful is if you want to evaluate an agent's trajectory of actions. Below, we will create an agent trajectory evaluator to do this. The main steps are:

Within the evaluator:
- Select the `tool` child runs to represent the agents actions
- Use an LLM to grade the action choices based on the responses at each turn and the final answer

And then for accessing the data:
- Query the project for runs by name to select the agent executor
- Specify `load_child_runs=True` to direct the client to load the other child runs in the trace before evaluating


```python
from langchain import evaluation, callbacks, agents

class AgentTrajectoryEvaluator(RunEvaluator):
    
    def __init__(self):
        self.evaluator = evaluation.load_evaluator("trajectory")
        
    @staticmethod
    def construct_trajectory(run: Run):
        trajectory = []
        for run in (run.child_runs or []):
            if run.run_type == "tool":
                action = agents.agent.AgentAction(tool=run.name, tool_input=run.inputs['input'], log='')
                trajectory.append((action, run.outputs['output']))
        return trajectory
        
    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> EvaluationResult:
        if run.outputs is None:
            return EvaluationResult(key="trajectory", score=None)
        question = next(iter(run.inputs.values()))
        prediction = str(next(iter(run.outputs.values())))
        trajectory = self.construct_trajectory(run)
        with callbacks.collect_runs() as cb:
            try:
                result = self.evaluator.evaluate_agent_trajectory(input=question,
                                                                  prediction=prediction,
                                                                  agent_trajectory=trajectory)
            except:
                # If the evaluation fails, we can log a null score
                return EvaluationResult(key="trajectory", score=None)
            run_id = cb.traced_runs[0].id
        return EvaluationResult(key="trajectory", evaluator_info={"__run": {"run_id": run_id}}, **result)

```

The `construct_trajectory` method extracts the tool runs from amongst the trace's child runs and then passes them to the evaluator.

Below, we will select runs by the "AgentExecutor" name to be sure we are appropriately applying our evaluator, then we will
evaluate, remembering to set `load_child_runs=True`.


```python
project_name = "My Project"
runs = client.list_runs(
    project_name=project_name,
    execution_order=1,
    filter='eq(name, "AgentExecutor")',
)

evaluator = AgentTrajectoryEvaluator()
for run in runs:
    feedback = client.evaluate_run(run.id, evaluator, load_child_runs=True)
```

## Conclusion

Congrats! You've run evals on an existing project and logged feedback to the traces. Now, all the feedback results are aggregated on the project page and can be monitored through the monitoring dashboard.

You can use the examples in this notebook to help evaluate, tag, and organize your traces as needed. If you have other related questions, feel free to create an issue in this repo!


```python

```
