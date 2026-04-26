import { useCallback, useEffect, useState } from "react";
import { APP_CONFIG } from "../../../core/config";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { chatService } from "../services/chat.service";
import useChatSessions from "./useChatSessions";
import { useDepartmentStore } from "../../departments/store/department.store";

export interface ChatMessage {
  id: string,
  role: "user" | "assistant",
  content: string,
  session_id: string,
  knowledge_ids?: string[]
}

function useChat(sessionId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const [prevSessionId, setPrevSessionId] = useState<string | null>(sessionId);

  if (sessionId !== prevSessionId) {
    setPrevSessionId(sessionId);
    setMessages([]);
  }

  const { sessions } = useChatSessions();
  const { setDepartments, clearDepartments } = useDepartmentStore();

  useEffect(() => {
    if (!sessionId) {
      clearDepartments();
      return;
    };

    const currentSession = sessions.find(s => s.id === sessionId);
    if (currentSession?.department_ids) {
      setDepartments(currentSession.department_ids);
    }

    const fetchHistory = async () => {
      try {
        const res = await chatService.getMessages(sessionId);
        setMessages((prev) => {
          if (prev.length > 0) return prev;
          return res.data;
        });
      } catch (err) {
        console.error(err);
      }
    };
    fetchHistory();
  }, [sessionId]);

  const sendMessage = useCallback(async (content: string, overrideSessionId: string | null) => {
    const targetSessionId = overrideSessionId || sessionId;

    if (!content.trim() || isLoading || !targetSessionId) return;

    setIsLoading(true);

    try {
      await fetchEventSource(`${APP_CONFIG.APP_BE_API}/chat/sessions/${targetSessionId}/messages`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "Accept": "text/event-stream"
        },
        body: JSON.stringify({
          role: "user",
          content: content
        }),
        async onopen(response) {
          if (response.ok) return;
          throw new Error("Failed to connect stream");
        },
        onmessage(event) {
          if (!event.data) return;

          const chunkData = JSON.parse(event.data);

          const msgId = chunkData.id;
          const msgContent = chunkData.content || "";
          const msgRole = chunkData.role;
          const msgSessionId = chunkData.session_id;
          const msgKnowledgeids = chunkData.knowledge_ids;

          const newMsg: ChatMessage = {
            id: msgId,
            role: msgRole,
            content: msgContent,
            session_id: msgSessionId,
            knowledge_ids: msgKnowledgeids
          };

          setMessages((prev) => {
            const msgIndex = prev.findIndex((m) => m.id === msgId);

            if (msgIndex === -1) {
              // New message
              return [...prev, newMsg];
            } else {
              const updated = [...prev];
              updated[msgIndex] = {
                ...updated[msgIndex],
                content: updated[msgIndex].content + msgContent
              };
              return updated;
            }
          });
        },
        onclose() {
          setIsLoading(false);
        },
        onerror(err) {
          setIsLoading(false);
          throw err;
        }
      });
    } catch (error) {
      setIsLoading(false);
      console.error(error);
    }
  }, [sessionId, isLoading]);

  return { messages, setMessages, isLoading, sendMessage };
}

export default useChat;
