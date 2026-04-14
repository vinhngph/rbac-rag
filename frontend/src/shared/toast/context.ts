import { createContext } from "react";

export type ToastType = "success" | "error" | "info"

interface ToastContextType {
    toast: (message: string, type?: ToastType) => void
    success: (message: string) => void
    error: (message: string) => void
}

export const ToastContext = createContext<ToastContextType | null>(null);
