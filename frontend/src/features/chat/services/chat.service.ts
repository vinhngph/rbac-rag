import { api } from "../../../core/api/axios";

export interface ChatSessionRead {
    id: string,
    title: string,
    department_ids: string[],
    user_id: string,
    updated_at: string
}

export interface ChatMessageRead {
    id: string,
    session_id: string,
    role: "user" | "assistant",
    content: string
}

export const chatService = {
  getSessions: () =>
    api.get<ChatSessionRead[]>("/chat/sessions"),
  createSessions: (department_ids: string[], title?: string) =>
    api.post<ChatSessionRead>("/chat/sessions", { department_ids, title }),
  getMessages: (session_id: string) =>
    api.get<ChatMessageRead[]>(`/chat/sessions/${session_id}/messages`)
};
