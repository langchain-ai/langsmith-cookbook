import { NextRequest, NextResponse } from "next/server";

import { Client } from "langsmith";

export const runtime = "edge";

const langsmithClient = new Client();

/**
 * This handler retrieves a LangSmith trace URL for the given run.
 * It isn't used by default, but if you'd like to turn it on, set
 * "showTraceUrls" to true in app/page.tsx.
 * Note that currently (2023/08/18) this will raise an error if the
 * run is still waiting to be committed to the database.
 * @param {NextRequest} req
 * @returns {Promise<NextResponse>}
 **/
export async function GET(req: NextRequest) {
  try {
    const runId = req.nextUrl.searchParams.get("run_id");
    if (!runId) {
      return NextResponse.json(
        { error: "You must provide a run id." },
        { status: 400 }
      );
    }
    const traceUrl = await langsmithClient.shareRun(runId);
    // Uncomment if you don't want to share run by default
    // const traceUrl = chainRunId ? await langsmithClient.readRun(chainRunId) : "";
    console.log(traceUrl);
    return NextResponse.json({ url: traceUrl }, { status: 200 });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
