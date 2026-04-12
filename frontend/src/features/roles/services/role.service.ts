import { api } from "../../../core/api/axios";
import type { KnowledgeRead } from "../../knowledge/services/knowledge.service";

export interface RoleRead {
    id: string
    name: string
    parent_id: string | null
    original_parent_id: string | null
}

export interface RoleCreate {
    name: string
    parent_id: string
}

export interface RoleUpdate {
    name?: string | null
    parent_id?: string | null
}

export interface MemberCreate {
    email: string,
    permissions: ("view" | "edit")[]
}

export interface MemberRead {
    id: string
    email: string
    name: string
    avatar_url?: string | null
    permissions?: ("view" | "edit")[] | null
}

export interface MemberUpdate {
    id: string
    permissions: ("view" | "edit")[]
}

export const createRole = (data: RoleCreate) =>
  api.post<RoleRead>("/roles/", data);

export const updateRole = (roleId: string, data: RoleUpdate) =>
  api.patch<RoleRead>(`/roles/${roleId}`, data);

export const getRoleKnowledges = (roleId: string) =>
  api.get<KnowledgeRead[]>(`/roles/${roleId}/knowledges`);

export const deleteRole = (roleId: string) =>
  api.delete(`/roles/${roleId}`);

export const uploadKnowledge = (roleId: string, file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post(`/roles/${roleId}/knowledges`, form, {
    headers: { "Content-Type": "multipart/form-dataI" }
  });
};

export const getRoleMembers = (roleId: string) =>
  api.get<MemberRead[]>(`/roles/${roleId}/members`);

export const addMember = (roleId: string, data: MemberCreate) =>
  api.post<MemberRead>(`/roles/${roleId}/members`, data);

export const removeMember = (roleId: string, memberId: string) =>
  api.delete(`/roles/${roleId}/members/${memberId}`);

export const updateMemberRolePermissions = (roleId: string, data: MemberUpdate) =>
  api.patch<MemberRead>(`/roles/${roleId}/members`, data);
