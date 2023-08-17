## LangSmith Next.js Chat UI Example

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Flangchain-ai%2Flangsmith-cookbook%2Ffeedback-examples%2Fnextjs)

This template demonstrates how to use LangSmith tracing and feedback collection in a serverless TypeScript environment. It has only one page - a chat interface that streams messages and allows you to rate and comment on LLM responses.

![Chat UI](public/images/chat.png)

Specifically, you'll be able to save user feedback as simple 👍/👎 scores attributed to traced runs, which you can then view in the LangSmith UI. Feedback can benefit LLM applications by providing signal for few-shot examples, model fine-tuning, evaluations, personalized user experiences, and improved application observability.

You can try out a live version of this repo here: https://langsmith-cookbook.vercel.app/

## Setup

After cloning this repo, copy the `.env.example` file into a new `.env.local` file and populate the following environment variables:

```
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="YOUR_LANGSMITH_API_KEY_HERE"
LANGCHAIN_SESSION="YOUR_SESSION_HERE"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
```

Next, you'll need to install required dependencies by running e.g. `yarn` or `pnpm install` with your favorite package manger.

And that's it! Run `yarn dev` to start the app locally.

## Learn More

To learn more about LangSmith, check out [the documentation](https://docs.smith.langchain.com).

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out the [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details.
