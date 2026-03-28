import { createContext } from "react";

interface AuthContextType {
    user: unknown,
    loading: boolean,
    setUser: (user: unknown) => void
}

export const AuthContext = createContext<AuthContextType | null>(null);