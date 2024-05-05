import { NextRequest, NextResponse } from "next/server";

import { Client } from "langsmith";

export const runtime = "edge";

const langsmithClient = new Client();

/**
 * This handler creates feedback for a LangSmith trace.
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const runId = body.run_id;
    const score = body.score;
    if (!runId || isNaN(score)) {
      return NextResponse.json(
        { error: "You must provide a run id and a score." },
        { status: 400 }
      );
    }
    const feedback = await langsmithClient.createFeedback(runId, "user_score", {
      score,
    });
    return NextResponse.json({ feedback }, { status: 200 });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}

/**
 * This handler updates feedback for a LangSmith trace.
 */
export async function PUT(req: NextRequest) {
  try {
    const body = await req.json();
    const feedbackId = body.id;
    const score = body.score;
    if (!feedbackId) {
      return NextResponse.json(
        { error: "You must provide a feedback id" },
        { status: 400 }
      );
    }
    let correction;
    let comment;
    if (score === 1) {
      comment = body.comment;
    } else {
      correction = { desired: body.comment };
    }
    await langsmithClient.updateFeedback(feedbackId, {
      score,
      comment,
      correction,
    });
    return NextResponse.json({}, { status: 200 });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
