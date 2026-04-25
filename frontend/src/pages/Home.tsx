import { memo, useEffect, useRef, useState } from "react";
import { Bot, Check, Copy, Send, SquareLibrary } from "lucide-react";

import { APP_CONFIG } from "../core/config";
import useChat, { type ChatMessage } from "../features/chat/hooks/useChat";
import { useLocation, useNavigate } from "react-router";
import useChatSessions from "../features/chat/hooks/useChatSessions";
import { useDepartmentStore } from "../features/departments/store/department.store";
import UserAvatar from "../shared/components/UserAvatar";
import { useAuth } from "../features/auth/hooks/useAuth";
import MarkdownRenderer from "../shared/components/MarkdownRenderer";
import type { User } from "../features/auth/context/auth.context";
import MessageSources from "../features/chat/components/MessageSources";
import { useToast } from "../shared/toast";

const MessageItem = memo(({ msg, user, onOpenSources }: { msg: ChatMessage, user: User, onOpenSources: (msgId: string) => void }) => {
  const [isCopied, setIsCopied] = useState(false);
  const { success, error } = useToast();

  const handleCopy = async (textToCopy: string) => {
    if (!textToCopy) return;

    try {
      await navigator.clipboard.writeText(textToCopy);

      setIsCopied(true);
      success("Copied the answer.");

      setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    } catch {
      error("Failed to copy.");
    }
  };

  return (
    <div className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
      {msg.role === "assistant" && (
        <div className="w-8 h-8 rounded-full bg-linear-to-br from-emerald-400/20 to-cyan-500/20 border border-emerald-400/20 flex items-center justify-center shrink-0 mt-0.5">
          <Bot className="w-4 h-4 text-emerald-400" />
        </div>
      )}

      <div className={`${msg.role === "user" ? "max-w-[75%]" : "flex-1 min-w-0"}`}>
        {msg.role === "user"
          ? <div className="bg-surface-active rounded-[20px] rounded-br-md px-4 py-2.5 text-text leading-relaxed">
            {msg.content}
          </div>
          : <div>
            <div className="prose dark:prose-invert max-w-none text-text prose-strong:text-text">
              <MarkdownRenderer content={msg.content} />
            </div>
            {/* Action buttons */}
            <div className="flex items-center gap-1 mt-2">
              <button
                onClick={() => handleCopy(msg.content)}
                className="flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-surface-hover text-text-muted hover:text-text/70 transition-colors cursor-pointer"
                title={isCopied ? "Copied" : "Copy"}
              >
                {isCopied ? (
                  <Check className="w-3.5 h-3.5 text-emerald-500" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
              <button
                onClick={() => onOpenSources(msg.id)}
                className="flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-surface-hover text-text-muted hover:text-text/70 transition-colors cursor-pointer"
                title="Sources"
              >
                {msg.knowledge_ids && msg.knowledge_ids.length >= 1 && (
                  <>
                    <SquareLibrary className="w-3.5 h-3.5" />
                    <span className="text-xs font-medium">Sources {"(" + msg.knowledge_ids?.length + ")"}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        }
      </div>

      {msg.role === "user" && (
        <UserAvatar avatar_url={user?.avatar_url} name={user?.name ?? ""} />
      )}
    </div>
  );
});

function Home() {
  const [input, setInput] = useState<string>("");
  const [sourceModalData, setSourceModalData] = useState<{ sessionId: string, messageId: string } | null>(null);
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
      bottomRef.current.scrollIntoView({ behavior: "auto" });
    }
  }, [messages, isLoading]);

  useEffect(() => {
    if (activeChatId && location.state?.pendingPrompt) {
      const prompt = location.state.pendingPrompt;
      navigate(location.pathname, { replace: true, state: {} });

      sendMessage(prompt, activeChatId);
    }
  }, [activeChatId, location.pathname, location.state, navigate, sendMessage]);

  const autoResize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  };

  const handleSend = async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || isLoading) return;

    const targetSessionId = activeChatId;

    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    try {
      if (!targetSessionId) {
        const deptIds = Array.from(checkedDepartments);
        const chatTitle = content.length > 40 ? content.slice(0, 40) + "..." : content;

        const newSession = await handleCreateSession({
          department_ids: deptIds,
          title: chatTitle
        });

        navigate(`/chat/${newSession.id}`, { state: { pendingPrompt: content } });

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
      {sourceModalData && (
        <MessageSources isOpen={true} sessionId={sourceModalData.sessionId} messageId={sourceModalData.messageId} onClose={() => setSourceModalData(null)} />
      )}

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
              <p className="text-sm text-text-muted text-center max-w-md">
                An AI assistant with role-based document search capabilities.
              </p>
            </div>
          </div>
          :
          // CHAT MESSAGES
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
            {user && messages.map((msg) => (
              <MessageItem key={msg.id} msg={msg} user={user} onOpenSources={(msgId) => {
                if (activeChatId) {
                  setSourceModalData({ sessionId: activeChatId, messageId: msgId });
                }
              }} />
            ))}

            {/* Loading indicator */}
            {isLoading && messages.at(-1)?.role !== "assistant" && (
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
          <div className="relative bg-bg-prompt rounded-3xl border border-border-subtle hover:border-border-subtle/15 focus-within:border-border-subtle/20 transition-colors shadow-lg">
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
              className="w-full bg-transparent text-sm text-text placeholder:text-text/30 resize-none outline-none pl-5 pr-12 py-3.5 max-h-50 leading-relaxed"
            />

            {/* Bottom toolbar */}
            <div className="absolute right-2.5 bottom-2.5">
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${input.trim() && !isLoading
                  ? "bg-text text-bg hover:opacity-80 cursor-pointer"
                  : "bg-surface-active text-text-muted opacity-50 cursor-not-allowed"
                }`}
              >
                <Send className="w-3.5 h-3.5" />
              </button>
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
