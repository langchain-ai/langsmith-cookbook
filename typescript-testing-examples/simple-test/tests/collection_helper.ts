import { BaseRun, Run } from "langsmith/schemas";
import { BaseTracer } from "langchain/callbacks";

// Todo: Remove in next JS release
export class RunCollectorCallbackHandler extends BaseTracer {
  name = "run_collector";
  exampleId?: string;
  tracedRuns: Run[];

  constructor({ exampleId }: { exampleId?: string } = {}) {
    super();
    this.exampleId = exampleId;
    this.tracedRuns = [];
  }

  protected async persistRun(run: BaseRun): Promise<void> {
    const run_ = { ...run } as Run;
    run_.reference_example_id = this.exampleId;
    this.tracedRuns.push(run_);
  }
}
