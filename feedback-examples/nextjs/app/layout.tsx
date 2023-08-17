import "./globals.css";
import { Public_Sans } from "next/font/google";

const publicSans = Public_Sans({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <title>LangSmith Feedback Example</title>
        <link rel="shortcut icon" href="/images/favicon.ico" />
        <meta
          name="description"
          content="Starter template showing how to use LangSmith in a Next.js project. See source code and deploy your own at https://github.com/langchain-ai/langsmith-cookbook!"
        />
        <meta property="og:title" content="LangSmith Feedback Example" />
        <meta
          property="og:description"
          content="Starter template showing how to use LangSmith in Next.js projects. See source code and deploy your own at https://github.com/langchain-ai/langsmith-cookbook!"
        />
        <meta property="og:image" content="/images/chat.png" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="LangSmith Feedback Example" />
        <meta
          name="twitter:description"
          content="Starter template showing how to use LangSmith in Next.js projects. See source code and deploy your own at https://github.com/langchain-ai/langsmith-cookbook!"
        />
        <meta name="twitter:image" content="/images/chat.png" />
      </head>
      <body className={publicSans.className}>
        <div className="flex flex-col p-4 md:p-12 h-[100vh]">{children}</div>
      </body>
    </html>
  );
}
