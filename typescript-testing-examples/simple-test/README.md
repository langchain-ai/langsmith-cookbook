# Logging Assertions as Feedback

[![Open In GitHub](https://img.shields.io/badge/GitHub-View%20source-green.svg)](https://github.com/langchain-ai/langsmith-cookbook/blob/master/./typescript-testing-examples/simple-test/README.md)


This walkthrough shows a lightweight way to begin using LangSmith feedback in TypeScript, without having to change many lines of code
in your existing tests. It does not incorporate LangSmith datasets, and so you do not get the benefits of row-level comparisons, performance and chain tracking over a dataset, or other future analytical functionality. For information on how to evaluate your JS chains over a dataset, check out the [Evaluating JS Chains in Python](../eval-in-python/) walkthrough in this repo.

This recipe works by wrapping your testing assertions of your existing JavaScript tests and logging them as evaluation feedback.

We don't (yet) have full benchmarking functionality natively written in TypeScript, and you may already have some tests using
familiar testing harnesses like Jest or Mocha. You can still track your tests in LangSmith in a lightweight manner using the tactics presented in this recipe.

The basic steps are:

1. Run your chain on example data, capturing the run IDs for each run.
2. Perform your assertions, catching and logging the result.

For our example, we have defined a chain meant to generate structured json objects based on the input text. You can check out the chain definition in [index.ts](./src/index.ts), or proceed with the walkthrough. Let's dive in!

## Prerequisites

This example assumes you have your Langsmith account and organizational API key available:

```bash
export LANGCHAIN_API_KEY=<your-api-key>
```

To run the tests, install the requirements in the [package.json](./package.json) file with the following command:

```bash
npm install --include=dev
```

## Run Tests

The tests are run using `jest`. You can execute them with the command `npm test`. We recommend creating a new test project each time CI is run. One pattern that makes it easier to organize your projects in a meaningful way is to include the git hash in the name. The following command accomplishes this:

```bash
LANGCHAIN_PROJECT="UnitTests-$(git rev-parse --short HEAD)" npm test
```

Once you've run the tests, a new test project will be created. You can find this by navigating to LangSmith, clicking on the 'Projects' page, and the looking for the "UnitTests-<hash>" project (e.g., "UnitTests-21e914b"). The results should look something like the image below:

![Unit Test Project](img/resulting_project.png)

You can view traces from this unit test along with the assertion feedback. Aggregate feedback and other statistics are visible at the top of the page.

Now let's review the code!

## Code Walkthrough

Let's start with the test file in [index.test.ts](./tests/index.test.ts). In this file, we define a list of example inputs and expected outputs and then use
jest to define a test suite called "Test chain outputs", which iterates through each example as a test case. The code is defined below:


```typescript
import { expect } from "./jest_helper";

describe("Test chain outputs", () => {
  it.each(examples)(
    "produces expected json for example: %s",
    async (example) => {
      const chain = getChain();
      const runCollector = new RunCollectorCallbackHandler();
      const pred = await chain.invoke(
        { input: example.input },
        {
          callbacks: [runCollector],
        }
      );
      const runId = runCollector.tracedRuns[0].id;
      // If you're not using jest, you can manually catch and log
      parseAndLog(runId, pred);
      // Or you can use the example jest wrapper in this recipe
      // The name feedback name is optional. An automatic name will be inferred
      // basd on the expectation method and object.
      expect(JSON.parse(pred), { runId, feedbackName: "to_equal_object" }).toEqual(
        example.output
      );
    }
  );
});

```

At a high level, the test:

1. Runs the chain on the example input.
2. Asserts that the result can be parsed as json in `parseAndLog` (see explanation below)
3. Asserts that the prediction is equivalent to the expected output using the wrapped `expect` statement.

When running the chain, we use the "runCollector" callback to collect each traced run in a list so that we can
easily recover the run's ID to associate feedback with it. This callback handler is available in langchain versions `>=0.0.139`.

We demonstrate two ways to log and assert in one line. The first is the manual `parseAndLog` function, reproduced below:

```typescript
function parseAndLog(runId: string, actual: any): void {
  try {
    JSON.parse(actual);
    client.createFeedback(runId, "validJson", { score: 1 });
  } catch (e) {
    const errorMessage = e?.toString() ?? "";
    client.createFeedback(runId, "validJson", {
      score: 0,
      comment: errorMessage,
    });
    throw e;
  }
}
```

This manually tries to parse the predicted value and then logs feedback in either the passing or failing cases. If you aren't using Jest assertions, this is a relatively easy pattern to apply to your checks, though it can get verbose.

You can also wrap Jest or other expect() calls directly so that you can add feedback logging to your existing test suite with a single line replacement.
The syntax is identical to a regular Jest assertion except for the required `runId` needed to specify which run to associate the feedback with. The
wrapper also accepts an optional `feedbackName` argument for you to customize the resulting metric to be logged to LangSmith. This way you can create more
readable names than those inferred by the Jest syntax. 

While we won't reproduce the full wrapper code here, you can check out its implementation in [jest_helper.ts](./tests/jest_helper.ts) to see how it works.

## Conclusion

Congratulations! You've added LangSmith feedback logging to your existing JS test suite. This is a lightweight way to incorporate tracing and other LangSmith functionality
in your practice so you can track changes in your chain as you application evolves. While the technique presented in this recipe does not support rowwise comparisons on a dataset,
it is an easy way to get started and incorporate tracing in CI.

For a recipe that DOES let you evaluate your JS chains on datasets, check out the [Evaluating JS Chains in Python](../eval-in-python/) walkthrough in this repo.