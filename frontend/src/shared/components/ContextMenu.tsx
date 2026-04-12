import { useEffect, useRef, type ReactNode } from "react";

interface ContextMenuItem {
    label: string
    icon: ReactNode
    danger?: boolean
    onClick: () => void
}

interface ContextMenuProps {
    readonly items: ContextMenuItem[]
    readonly onClose: () => void
}

function ContextMenu({ items, onClose }: ContextMenuProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node))
        onClose();
    };
    document.addEventListener("mousedown", h);

    return () => document.removeEventListener("mousedown", h);
  }, [onClose]);

  return (
    <div
      ref={ref}
      className="absolute right-0 top-full mt-1 z-50 bg-[#1a1a1a] border border-white/10 rounded-xl shadow-2xl overflow-hidden"
    >
      {items.map((item) => (
        <button
          key={item.label}
          onClick={() => {
            item.onClick();
            onClose();
          }}
          className={`w-full flex items-center gap-2.5 px-3.5 py-2.5 text-sm transition-colors cursor-pointer ${
            item.danger
              ? "text-red-400 hover:bg-red-500/10"
              : "text-text/80 hover:bg-white/6 hover:text-text"
          }`}
        >
          {item.icon}
          {item.label}
        </button>
      ))}
    </div>
  );
}

export default ContextMenu;
