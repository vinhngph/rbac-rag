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
  api.get<DepartmentRead[]>("/user/departments");

export const getDepartment = (id: string) =>
  api.get<DepartmentRead>(`/user/departments/${id}`);

export const createDepartment = (data: DepartmentCreate) =>
  api.post<DepartmentRead>("/user/departments", data);

export const updateDepartment = (id: string, data: DepartmentUpdate) =>
  api.patch<DepartmentRead>(`/user/departments/${id}`, data);

export const deleteDepartment = (id: string) =>
  api.delete(`/user/departments/${id}`);