import { Loader2 } from "lucide-react";
import { Suspense, type ReactNode } from "react";

interface SuspenseWrapperProps {
    readonly children: ReactNode
}

function SuspenseWrapper({ children }: SuspenseWrapperProps) {
  const fallbackUI = (
    <div className="flex w-full h-full flex-col items-center justify-center p-8">
      <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
    </div>
  );
  return (
    <Suspense fallback={fallbackUI}>
      {children}
    </Suspense>
  );
}

export default SuspenseWrapper;
