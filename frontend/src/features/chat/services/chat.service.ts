import { api } from "../../../core/api/axios";
import type { KnowledgeRead } from "../../knowledge/services/knowledge.service";
import type { ChatMessage } from "../hooks/useChat";

export interface ChatSessionRead {
    id: string,
    title: string,
    department_ids: string[],
    user_id: string,
    updated_at: string
}

export const chatService = {
  getSessions: () =>
    api.get<ChatSessionRead[]>("/chat/sessions"),
  createSessions: (department_ids: string[], title?: string) =>
    api.post<ChatSessionRead>("/chat/sessions", { department_ids, title }),
  getMessages: (session_id: string) =>
    api.get<ChatMessage[]>(`/chat/sessions/${session_id}/messages`),
  getMessageSources: (session_id: string, message_id: string) =>
    api.get<KnowledgeRead[]>(`/chat/sessions/${session_id}/messages/${message_id}`)
};
