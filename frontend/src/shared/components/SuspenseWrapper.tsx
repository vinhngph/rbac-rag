import { Suspense, type ReactNode } from "react";

interface SuspenseWrapperProps {
    readonly children: ReactNode
}

function SuspenseWrapper({ children }: SuspenseWrapperProps) {
  return (
    <Suspense fallback={<h1>Loading...</h1>}>
      {children}
    </Suspense>
  );
}

export default SuspenseWrapper;
