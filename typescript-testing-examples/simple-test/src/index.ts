import {
  ChatPromptTemplate,
  HumanMessagePromptTemplate,
  SystemMessagePromptTemplate,
} from "langchain/prompts";

import { ChatOpenAI } from "langchain/chat_models/openai";
import { StringOutputParser } from "langchain/schema/output_parser";

/**
 * Returns a chain that prompts the user to write a rap battle response.
 * @returns {import("langchain/schema/chain").Chain<string>} A chain that prompts the user to write a rap battle response.
 */
export function getChain() {
  const prompt = ChatPromptTemplate.fromPromptMessages([
    SystemMessagePromptTemplate.fromTemplate(
      "You are an extraction agent tasked with generating structured JSON."
    ),
    HumanMessagePromptTemplate.fromTemplate(
      "Extract all entity information as keys and values in a json blob" +
        " from the following:\n\n{input}"
    ),
    SystemMessagePromptTemplate.fromTemplate("Respond only in valid json."),
  ]);
  const model = new ChatOpenAI({ temperature: 0 });
  return prompt.pipe(model).pipe(new StringOutputParser());
}

/**
 * Extract entities from text.
 * @param {string} txt The text to extract entities from.
 * @returns {object} The extracted entities.
 */
export function extract(txt: string): object {
  const chain = getChain();
  return chain.pipe(JSON.parse).invoke({ input: txt });
}
