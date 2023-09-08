import { Client } from "langsmith";
import { Example } from "langsmith/schemas";
import { LangChainTracer } from "langchain/callbacks";
import { getChain } from "../src/index";

function getConfigs(examples: Example[], projectName?: string) {
  return examples.map((example) => {
    return {
      callbacks: [new LangChainTracer({ exampleId: example.id, projectName })],
    };
  });
}

const datasetName = "Structured Output Example";
test(`"Test run on ${datasetName}`, async () => {
  const client = new Client();
  const chain = getChain();
  const examples: Example[] = [];
  for await (const example of client.listExamples({ datasetName })) {
    examples.push(example);
  }
  // You can pick a useful name for your project here that is easy to
  // use when evaluating in python
  const projectName =
    (process.env.LANGCHAIN_PROJECT ?? "Unit Testing") + datasetName;
  const configs = getConfigs(examples, projectName);
  const chainInputs = examples.map((example) => example.inputs);
  await chain.batch(chainInputs, configs);
}, 300_000);
