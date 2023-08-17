import { ChatWindow } from "@/components/ChatWindow";

export default function Home() {
  const InfoCard = (
    <div className="p-4 md:p-8 rounded bg-[#25252d] w-full max-h-[85%] overflow-hidden">
      <h1 className="text-3xl md:text-4xl mb-4">
        ⚒️ LangSmith + Next.js Feedback Example 🦜🔗
      </h1>
      <ul>
        <li className="text-l">
          🔎
          <span className="ml-2">
            This template shows how to use LangSmith to collect feedback on your{" "}
            <a href="https://js.langchain.com/" target="_blank">
              LangChain.js
            </a>{" "}
            run outputs in a{" "}
            <a href="https://nextjs.org/" target="_blank">
              Next.js
            </a>{" "}
            project.
          </span>
        </li>
        <li className="text-l">
          ⚒️
          <span className="ml-2">
            You&apos;ll want to ensure you have{" "}
            <a href="https://docs.smith.langchain.com" target="_blank">
              LangSmith
            </a>{" "}
            correctly configured first.
          </span>
        </li>
        <li>
          👨‍🎨
          <span className="ml-2">
            By default, the bot is pretending to be William Shakespeare, but you
            can change the prompt to whatever you want!
          </span>
        </li>
        <li className="hidden text-l md:block">
          🎨
          <span className="ml-2">
            The main frontend logic is found in <code>app/page.tsx</code>.
          </span>
        </li>
        <li className="text-l">
          🐙
          <span className="ml-2">
            This template is open source - you can see the source code and
            deploy your own version{" "}
            <a
              href="https://github.com/langchain-ai/langsmith-cookbook"
              target="_blank"
            >
              from the GitHub repo
            </a>
            !
          </span>
        </li>
        <li className="text-l">
          👇
          <span className="ml-2">
            Try asking e.g. <code>What is your favorite play?</code> below,
            giving some feedback, and checking out your run in{" "}
            <a href="https://smith.langchain.com" target="_blank">
              LangSmith
            </a>
            !
          </span>
        </li>
      </ul>
    </div>
  );
  return (
    <ChatWindow
      endpoint="api/chat"
      emoji="👨‍🎨"
      titleText="Wi-LLM-iam Shakespeare"
      placeholder="I'm an LLM pretending to be William Shakespeare! Ask me anything!"
      emptyStateComponent={InfoCard}
      showTraceUrls={false}
    ></ChatWindow>
  );
}
