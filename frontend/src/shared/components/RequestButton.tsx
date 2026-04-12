import { Loader2 } from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

interface RequestButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    isLoading?: boolean
    children: ReactNode
}

function RequestButton({ isLoading = false, children, className="", disabled, ...props }: Readonly<RequestButtonProps>) {
  return (
    <button
      disabled={isLoading || disabled}
      className={`flex items-center justify-center gap-2 transition-all ${className} ${(isLoading || disabled) ? "cursor-not-allowed opacity-70": "cursor-pointer"}`}
      {...props}
    >
      {isLoading && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}

      {children}
    </button>
  );
}

export default RequestButton;
