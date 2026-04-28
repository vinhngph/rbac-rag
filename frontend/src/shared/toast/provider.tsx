import { useCallback, useMemo, useState, type ReactNode } from "react";
import { ToastContext, type ToastType } from "./context";
import { AlertCircle, CheckCircle2, Info, X } from "lucide-react";

interface ToastMessage {
    id: string
    message: string
    type: ToastType
}

function ToastProvider({ children }: {readonly children: ReactNode}) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback((message: string, type: ToastType = "info") => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      removeToast(id);
    }, 3000);
  }, [removeToast]);

  const success = useCallback((message: string) => toast(message, "success"), [toast]);
  const error = useCallback((message: string) => toast(message, "error"), [toast]);

  const getIcon = (type: ToastType) => {
    switch (type) {
    case "success": return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
    case "error": return <AlertCircle className="w-5 h-5 text-red-400" />;
    default: return <Info className="w-5 h-5 text-blue-400" />;
    }
  };

  const contextValue = useMemo(() => (
    { toast, success, error }
  ), [toast, success, error]);

  return (
    <ToastContext.Provider value={contextValue}>
      {children}

      <div className="fixed bottom-5 left-5 z-100 flex flex-col gap-3 pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className="pointer-events-auto flex items-center gap-3 min-w-62.5 max-w-sm px-4 py-3 bg-bg-modal border border-border-subtle rounded-xl shadow-2xl shadow-black/50 animate-in slide-in-from-right-8 fade-in duration-300"
          >
            <div className="shrink-0">{getIcon(t.type)}</div>
            <p className="flex-1 text-sm text-text/90 leading-snug">{t.message}</p>
            <button
              onClick={() => removeToast(t.id)}
              className="shrink-0 p-1 rounded-md text-text-muted hover:text-text/80 hover:bg-surface-hover transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}


export default ToastProvider;
