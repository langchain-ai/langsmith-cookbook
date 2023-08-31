import { Client } from "langsmith";
import { getChain } from "../src/index";
import { expect } from "./jest_helper";
import { RunCollectorCallbackHandler } from "./collection_helper";

const client = new Client();

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

const examples = [
  {
    input: "I am a person named John.",
    output: {
      name: "John",
      type: "person",
    },
  },
  {
    input: "I am a person named John and I am 20 years old.",
    output: {
      name: "John",
      age: 20,
      entity: "person",
    },
  },
  {
    input:
      "I am a person named John and I am 20 years old. I live in New York.",
    output: {
      name: "John",
      age: 20,
      location: "New York",
    },
  },
  {
    input:
      "There once was a hero named Ragnar the Red who came riding to Whiterun from ole Rorikstead.",
    output: {
      hero: "Ragnar the Red",
      location: "Whiterun",
      origin: "Rorikstead",
    },
  },
];

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
      // Or you can use the example jest srapper in this recipe
      // The name feedback name is optional. An automatic name will be inferred
      // basd on the expectation method and object.
      expect(JSON.parse(pred), { runId, feedbackName: "to_equal_object" }).toEqual(
        example.output
      );
    }
  );
});
