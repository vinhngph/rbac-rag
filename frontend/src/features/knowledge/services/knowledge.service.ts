import { api } from "../../../core/api/axios";

export type FileType = "pdf" | "png" | "jpg" | "jpeg"

export type KnowledgeStatus = "scanning" | "safe" | "extracting" | "chunking" | "embedding" | "completed" | "failed"

export interface KnowledgeRead {
    id: string
    name: string
    type: FileType
    status: KnowledgeStatus
    role_id: string
    original_role_id?: string | null
    author_id: string
    created_at: string
}

export interface KnowledgeUpdate {
    name?: string | null
    role_id?: string | null
}

export const updateKnowledge = (knowledgeId: string, data: KnowledgeUpdate) =>
  api.patch<KnowledgeRead>(`/knowledges/${knowledgeId}`, data);

export const deleteKnowledge = (knowledgeId: string) =>
  api.delete(`knowledges/${knowledgeId}`);
