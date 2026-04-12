import React, { useRef, useState } from "react";

interface PromptModalProps {
  readonly title: string
  readonly initialName: string
  readonly onConfirm: (n: string) => void
  readonly onCancel: () => void
}


function PromptModal({ title, initialName, onConfirm, onCancel }: PromptModalProps) {
  const [name, setName] = useState(initialName);
  const nameRef = useRef<HTMLInputElement>(null);

  const handleNameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && name.trim())
      onConfirm(name.trim());
    if (e.key === "Escape")
      onCancel();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Button - Blur overlay */}
      <button
        className="absolute inset-0 bg-black/60 backdrop-blur-sm w-full h-full border-none"
        onClick={onCancel}
      />

      {/* Modal card */}
      <div className="relative z-10 w-full max-w-xs mx-4 bg-bg-modal border border-white/10 rounded-2xl shadow-2xl p-5">
        <h3 className="text-sm font-semibold text-text mb-3">{title}</h3>
        <input
          ref={nameRef}
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={handleNameKeyDown}
          className="w-full bg-white/5 border border-white/10 focus:border-emerald-400/40 rounded-xl px-3.5 py-2.5 text-sm text-text outline-none transition-colors"
        />
        <div className="flex gap-2 mt-3">
          <button
            onClick={onCancel}
            className="flex-1 py-2 text-sm text-text/60 hover:text-text bg-white/5 hover:bg-white/10 rounded-xl transition-colors cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={() => name.trim() && onConfirm(name.trim())}
            disabled={!name.trim()}
            className="flex-1 py-2 text-sm text-text bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 rounded-xl transition-colors cursor-pointer disabled:cursor-not-allowed"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

export default PromptModal;
