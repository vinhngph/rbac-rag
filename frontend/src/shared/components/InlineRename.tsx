import { useEffect, useRef, useState } from "react";

interface InlineRenameProps {
    readonly value: string
    readonly onConfirm: (v: string) => void
    readonly onCancel: () => void
}

function InlineRename({ value, onConfirm, onCancel }: InlineRenameProps) {
  const [v, setV] = useState(value);
  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => { ref.current?.select();}, []);

  return (
    <input
      ref={ref}
      value={v}
      onChange={(e) => setV(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === "Enter" && v.trim()) onConfirm(v.trim());
        if (e.key === "Escape") onCancel();
      }}
      onBlur={() => v.trim() ? onConfirm(v.trim()) : onCancel()}
      onClick={(e) => e.stopPropagation()}
      className="w-full bg-white/8 border border-emerald-400/40 rounded-lg px-2 py-0.5 text-sm text-white outline-none"
    />
  );
}

export default InlineRename;
