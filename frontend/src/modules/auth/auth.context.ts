import { createContext } from "react";

export interface User {
    id: string,
    email: string,
    name: string,
    avatar_url?: string
}

interface AuthContextType {
    user: User | null,
    loading: boolean,
    setUser: (user: User | null) => void
}

export const AuthContext = createContext<AuthContextType | null>(null);