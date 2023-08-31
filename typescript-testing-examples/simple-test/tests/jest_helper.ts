import jestExpect from "expect";
import { Client } from "langsmith";

const client = new Client();

/**
 * A wrapper for jest's expect to include LangSmith logging.
 * @param {string} runId - Run ID from LangSmith
 * @param {any} actual - Actual value to be expected
 * @returns {any} - Returns an object that has all the jest's expect methods
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
