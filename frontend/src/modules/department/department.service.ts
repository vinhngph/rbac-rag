import { api } from "../../core/api/axios";

export interface DepartmentRead {
  id: string;
  name: string
  status: boolean
}

export interface DepartmentCreate {
  name: string
}

export interface DepartmentUpdate {
  name: string | null
}

export const getDepartments = () =>
  api.get<DepartmentRead[]>("/departments");

export const getDepartment = (id: string) =>
  api.get<DepartmentRead>(`/departments/${id}`);

export const createDepartment = (data: DepartmentCreate) =>
  api.post<DepartmentRead>("/departments", data);

export const updateDepartment = (id: string, data: DepartmentUpdate) =>
  api.patch<DepartmentRead>(`/departments/${id}`, data);

export const deleteDepartment = (id: string) =>
  api.delete(`/departments/${id}`);