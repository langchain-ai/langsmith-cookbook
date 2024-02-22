import { NextRequest, NextResponse } from "next/server";
import { ChatWindowMessage } from "@/schema/ChatWindowMessage";

import { ChatOpenAI } from "langchain/chat_models/openai";
import { BytesOutputParser } from "langchain/schema/output_parser";
import { PromptTemplate } from "langchain/prompts";

export const runtime = "edge";

const formatMessage = (message: ChatWindowMessage) => {
  let prefix;
  if (message.role === "human") {
    prefix = "Human:";
  } else {
    prefix = "Assistant:";
  }
  return `${prefix} ${message.content}`;
};

const TEMPLATE = `You are William Shakespeare. Respond to the following query. All responses must be in period-appropriate iambic pentameter.

Current conversation:
{chat_history}

Query: {input}`;

/**
 * This handler initializes and calls a simple chain with a prompt,
 * chat model, and output parser. See the docs for more information:
 *
 * https://js.langchain.com/docs/expression_language/cookbook#prompttemplate--llm--outputparser
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const messages = body.messages ?? [];
    const formattedPreviousMessages = messages.slice(0, -1).map(formatMessage);
    const currentMessageContent = messages[messages.length - 1].content;
    const prompt = PromptTemplate.fromTemplate<{
      chat_history: string;
      input: string;
    }>(TEMPLATE);

    /**
     * You can also try e.g.:
     *
     * import { ChatAnthropic } from "langchain/chat_models/anthropic";
     * const model = new ChatAnthropic({});
     *
     * See a full list of supported models at:
     * https://js.langchain.com/docs/modules/model_io/models/
     */
    const model = new ChatOpenAI({
      temperature: 0.8,
    });

    /**
     * This output parser converts streaming output chunks into the correct format.
     */
    const outputParser = new BytesOutputParser();

    /**
     * Can also initialize as:
     *
     * import { RunnableSequence } from "langchain/schema/runnable";
     * const chain = RunnableSequence.from([prompt, model, outputParser]);
     */
    const chain = prompt.pipe(model).pipe(outputParser);

    /**
     * Wait for a run id to be generated.
     */
    let chainRunId;
    const stream: ReadableStream = await new Promise((resolve) => {
      const chainStream = chain.stream(
        {
          chat_history: formattedPreviousMessages.join("\n"),
          input: currentMessageContent,
        },
        {
          callbacks: [
            {
              handleChainStart(_llm, _prompts, runId) {
                chainRunId = runId;
                resolve(chainStream);
              },
            },
          ],
        },
      );
    });

    return new Response(stream, {
      headers: {
        "x-langsmith-run-id": chainRunId ?? "",
      },
    });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
