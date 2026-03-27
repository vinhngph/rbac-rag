import { useState } from "react";
import { BookOpen, Bot, Code2, Globe, Lightbulb } from "lucide-react";

type Message = {
  id: number;
  role: "user" | "assistant";
  contet: string;
  timestamp: Date;
}

const SUGGESTIONS = [
  {
    icon: <Lightbulb className="w-4 h-4" />,
    label: "Explain RAG",
    prompt: "Explain what Retrieval-Augmented Generation (RAG) is and how it works?"
  },
  {
    icon: <Code2 className="w-4 h-4" />,
    label: "What is RBAC?",
    prompt: "How does Role-Based Access Control (RBAC) work within a system?"
  },
  {
    icon: <Globe className="w-4 h-4" />,
    label: "Vector search",
    prompt: "How to optimize vector search with embedding models?"
  },
  {
    icon: <BookOpen className="w-4 h-4" />,
    label: "FastAPI + JWT",
    prompt: "Guide to implementing JWT authentication with FastAPI"
  }
];

function Home() {
  const [messages, setMessages] = useState<Message[]>([]);

  return (
    <div className="flex flex-col h-full bg-bg">
      {/* MESSAGES AREA */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0
          // Empty state
          ?
          <div className="flex flex-col items-center justify-center h-full px-4 pb-32">
            {/* Logo */}
            <div className="mb-6 flex flex-col items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-linear-to-br from-emerald-400/20 to-cyan-500/20 border border-emerald-400/20 flex items-center justify-center">
                <Bot className="w-6 h-6 text-emerald-400" />
              </div>
              <h1 className="text-2xl font-semibold text-text tracking-tight">
                How may I help you?
              </h1>
              <p className="text-sm text-text/40 text-center max-w-md">
                An AI assistant with role-based document search capabilities.
              </p>
            </div>

            {/* Suggestions */}
            <div className="grid grid-cols-2 gap-2 w-full max-w-xl">
              {SUGGESTIONS.map(s => (
                <button
                  key={s.label}
                  className="flex items-start cursor-pointer gap-3 p-3.5 rounded-2xl bg-bg-prompt hover:bg-bg-prompt/30 border border-white/5 hover:border-white/10 transition-all text-left group "
                >
                  <span className="mt-0.5 text-emerald-400/70 group-hover:text-emerald-400 transition-colors shrink-0">
                    {s.icon}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-text/90">{s.label}</p>
                    <p className="text-xs text-text/40 mt-0.5 line-clamp-2">{s.prompt}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
          :
          // CHAT MESSAGES
          <div></div>
        }
      </div>
    </div>
  );
}

export default Home;