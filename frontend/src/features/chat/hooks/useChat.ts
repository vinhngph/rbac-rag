import { useState } from "react";
import { APP_CONFIG } from "../../../core/config";

type Message = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
}

function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  // AI thinking...
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const sendMessage = (text: string) => {
    const content = text.trim();
    if (!content || isLoading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMsg]);
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

  return { messages, isLoading, sendMessage };
}

export default useChat;
