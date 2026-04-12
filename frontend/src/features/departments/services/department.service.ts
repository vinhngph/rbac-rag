import { api } from "../../../core/api/axios";
import type { RoleRead } from "../../roles/services/role.service";

export interface DepartmentRead {
  id: string
  name: string
}

export interface DepartmentCreate {
  name: string
}

export interface DepartmentUpdate {
  name: string | null
}

export const getDepartments = () =>
  api.get<DepartmentRead[]>("/departments/");

export const getDepartmentRoles = (id: string) =>
  api.get<RoleRead[]>(`/departments/${id}`);

export const createDepartment = (data: DepartmentCreate) =>
  api.post<DepartmentRead>("/departments/", data);

export const updateDepartment = (id: string, data: DepartmentUpdate) =>
  api.patch<DepartmentRead>(`/departments/${id}`, data);

export const deleteDepartment = (id: string) =>
  api.delete(`/departments/${id}`);
