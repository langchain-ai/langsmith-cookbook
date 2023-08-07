import { NextApiResponse } from "next";
import { NextRequest } from "next/server";
import { StreamingTextResponse } from "ai";

import { ChatOpenAI } from "langchain/chat_models/openai";
import { ChatMessage } from "langchain/schema";
import { BytesOutputParser } from "langchain/schema/output_parser";
import { PromptTemplate } from "langchain/prompts";
import { RunnableSequence } from "langchain/schema/runnable";

export const runtime = "edge";

const formatMessage = (message: ChatMessage) => {
  return `${message.role}: ${message.content}`;
};


function getChain() {
  const TEMPLATE = `You are a funky parrot pal. You are not an AI. You are a parrot.
  You love poetry, reading, funk music, friendship, and squawking!
  It's currently ${new Date().toLocaleTimeString()}.

  {chat_history}

  User: {input}
  AI:`;

  const model = new ChatOpenAI({});
  const prompt = PromptTemplate.fromTemplate(TEMPLATE);
  const outputParser = new BytesOutputParser();
  return RunnableSequence.from([
    prompt,
    model,
    outputParser,
  ]);
}

async function POSTFeedback(req: NextRequest, res: NextApiResponse) {
  const { runId, score } = await req.json();
  // Log the feedback using the runId and score
  console.log(`Feedback for Run ID ${runId}: ${score}`);
  res.status(200).end();
}


export async function POST(req: NextRequest, res: NextApiResponse) {
  const body = await req.json();
  if (body.action === "feedback") {
    // Handle feedback request
    return POSTFeedback(req, res);
  }
  const messages = body.messages;
  const chatHistory = messages.slice(0, -1).map(formatMessage);
  
  const chain = getChain();

  const stream = await chain.stream({
    chat_history: chatHistory,
    input: messages[messages.length - 1].content,
  });

  return new StreamingTextResponse(stream);
}

