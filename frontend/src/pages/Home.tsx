import { useEffect, useRef, useState } from "react";
import { Bot, Copy, RotateCcw, Send, ThumbsDown, ThumbsUp } from "lucide-react";

import { APP_CONFIG } from "../core/config";
import useChat from "../features/chat/hooks/useChat";
import { useLocation, useNavigate } from "react-router";
import useChatSessions from "../features/chat/hooks/useChatSessions";
import { useDepartmentStore } from "../features/departments/store/department.store";
import UserAvatar from "../shared/components/UserAvatar";
import { useAuth } from "../features/auth/hooks/useAuth";
import MarkdownRenderer from "../shared/components/MarkdownRenderer";

function Home() {
  const [input, setInput] = useState<string>("");
  const navigate = useNavigate();

  const location = useLocation();
  const activeChatId = location.pathname.startsWith("/chat/") ? location.pathname.split("/")[2] : null;
  const { messages, isLoading, sendMessage } = useChat(activeChatId);
  const { user } = useAuth();

  const { checkedDepartments } = useDepartmentStore();

  const { handleCreateSession } = useChatSessions();

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior:"smooth" });
    }
  }, [messages, isLoading]);

  const autoResize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  };

  const handleSend =  async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || isLoading) return;

    const targetSessionId = activeChatId;

    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    try {
      if (!targetSessionId) {
        const deptIds = Array.from(checkedDepartments);
        const chatTitle = content.length > 40 ? content.slice(0, 40) + "...": content;

        const newSession = await handleCreateSession({
          department_ids: deptIds,
          title: chatTitle
        });

        navigate(`/chat/${newSession.id}`);

        await sendMessage(content, newSession.id);

        return;
      }

      await sendMessage(content, targetSessionId);
    } catch (error) {
      console.error(error);
    }
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
      <div className="flex-1 overflow-y-auto custom-scrollbar">
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
                      <div className="prose prose-invert max-w-none">
                        <MarkdownRenderer content={msg.content}/>
                      </div>
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
                  <UserAvatar avatar_url={user?.avatar_url} name={user?.name ?? ""}/>
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
                {/* <button className="cursor-pointer p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors" title="Add files">
                  <Paperclip className="w-4 h-4" />
                </button>
                <button className="cursor-pointer flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors text-xs" title="Web search">
                  <Globe className="w-3.5 h-3.5" />
                  <span>Web search</span>
                </button>
                <button className="cursor-pointer flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors text-xs" title="Web search">
                  <Lightbulb className="w-3.5 h-3.5" />
                  <span>Thinking</span>
                </button> */}
              </div>

              <div className="flex items-center gap-1">
                {/* <button className="cursor-pointer p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors" title="Voice">
                  <Mic className="w-4 h-4" />
                </button> */}
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
