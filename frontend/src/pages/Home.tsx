import { useRef, useState } from "react";
import { BookOpen, Bot, Code2, Copy, Globe, Lightbulb, Mic, Paperclip, RotateCcw, Send, ThumbsDown, ThumbsUp } from "lucide-react";

import { APP_CONFIG } from "../config";

type Message = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
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
  const [input, setInput] = useState<string>("");

  // AI thinking...
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const autoResize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  };

  const handleSend = (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || isLoading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    setIsLoading(true);


    // Simulate AI response
    setTimeout(() => {
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `Demo reply from ${APP_CONFIG.APP_NAME}. ${content}.`,
        timestamp: new Date()
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setIsLoading(false);
    }, 1200);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key == "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

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
                  onClick={() => handleSend(s.prompt)}
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
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
            {messages.map(msg => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-linear-to-br from-emerald-400/20 to-cyan-500/20 border border-emerald-400/20 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-4 h-4 text-emerald-400" />
                  </div>
                )}

                <div className={`${msg.role === "user" ? "max-w-[75%]" : "flex-1 min-w-0"}`}>
                  {msg.role === "user"
                    ? <div className="bg-bg-prompt rounded-[20px] rounded-br-md px-4 py-2.5 text-sm text-text leading-relaxed">
                      {msg.content}
                    </div>
                    : <div>
                      <p className="text-sm text-text/90 leading-relaxed whitespace-pre-wrap">
                        {msg.content}
                      </p>
                      {/* Action buttons */}
                      <div className="flex items-center gap-1 mt-2">
                        <button className="p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors">
                          <Copy className="w-3.5 h-3.5" />
                        </button>
                        <button className="p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors">
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button className="p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors">
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                        <button className="p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors">
                          <RotateCcw className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  }
                </div>

                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-linear-to-br from-violet-500 to-purple-600 flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold text-text">
                    V
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-linear-to-br from-emerald-400/20 to-cyan-500/20 border border-emerald-400/20 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="flex items-center gap-1 pt-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400/60 animate-bounce [animation-delay:0ms]"></span>
                  <span className="w-2 h-2 rounded-full bg-emerald-400/60 animate-bounce [animation-delay:150ms]"></span>
                  <span className="w-2 h-2 rounded-full bg-emerald-400/60 animate-bounce [animation-delay:300ms]"></span>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        }
      </div>

      {/* INPUT AREA */}
      <div className="px-4 pb-2 pt-2">
        <div className="max-w-3xl mx-auto">
          <div className="relative bg-bg-prompt rounded-3xl border border-white/8 hover:border-white/15 focus-within:border-white/20 transition-colors shadow-lg">
            {/* Textarea */}
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                autoResize();
              }}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything"
              rows={1}
              className="w-full bg-transparent text-sm text-text placeholder:text-text/30 resize-none outline-none px-4 pt-3.5 pb-2 max-h-50 leading-relaxed"
            />

            {/* Bottom toolbar */}
            <div className="flex items-center justify-between px-3 pb-2.5">
              <div className="flex items-center gap-1">
                <button className="cursor-pointer p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors" title="Add files">
                  <Paperclip className="w-4 h-4" />
                </button>
                <button className="cursor-pointer flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors text-xs" title="Web search">
                  <Globe className="w-3.5 h-3.5" />
                  <span>Web search</span>
                </button>
                <button className="cursor-pointer flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors text-xs" title="Web search">
                  <Lightbulb className="w-3.5 h-3.5" />
                  <span>Thinking</span>
                </button>
              </div>

              <div className="flex items-center gap-1">
                <button className="cursor-pointer p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors" title="Voice">
                  <Mic className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isLoading}
                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${input.trim() && !isLoading
                    ? "bg-white text-bg hover:bg-white/90 cursor-pointer"
                    : "bg-white/10 text-text/20 cursor-not-allowed"
                  }`}
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          <p className="text-center text-[11px] text-text/25 mt-2">
            {APP_CONFIG.APP_NAME} can make mistakes.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Home;