import jestExpect from "expect";
import { Client } from "langsmith";

const client = new Client();

/**
 * A wrapper for jest's expect to include LangSmith logging.
 * @param actual - Actual value to be expected
 * @param options - An object containing the following properties:
 *  - `runId` (string): Run ID from LangSmith
 *  - `feedbackName` (optional string): A custom name for the feedback
 * @returns An object that has all the jest's expect methods
 * @template T - The type of the actual value
 */
export function expect(
  actual: any,
  { runId, feedbackName }: { runId: string; feedbackName?: string }
): any {
  const jestExpectInstance = jestExpect(actual);

  // Iterate through all keys in the jestExpect instance
  Object.keys(jestExpectInstance).forEach((key: string) => {
    // Wrap each method to include LangSmith logging
    const originalMethod = (jestExpectInstance as any)[key];
    (jestExpectInstance as any)[key] = function (...args: any[]) {
      const feedbackName_ = feedbackName ?? `${key}_${args.join("_")}`;
      try {
        originalMethod.apply(this, args);
        client.createFeedback(runId, feedbackName_, { score: 1 });
      } catch (e) {
        const errorMessage = (e as Error)?.message ?? "";
        client.createFeedback(runId, feedbackName_, {
          score: 0,
          comment: errorMessage,
        });
        throw e;
      }
    };
  });

  return jestExpectInstance;
}
