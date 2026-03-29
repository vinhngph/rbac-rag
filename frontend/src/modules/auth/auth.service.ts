import { api } from "../../core/api/axios";

export const login = (data: {
  email: string,
  plain_text_password: string
}) => {
  return api.post("/auth/login", data);
};

export const register = (data: {
  email: string,
  name: string,
  avatar_url?: string | null,
  plain_text_password: string
}) => {
  return api.post("/auth/register", data);
};

export const getMe = () => {
  return api.get("/users/me");
};