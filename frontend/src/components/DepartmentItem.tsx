import { useRef, useState } from "react";
import { Check, ChevronRight, Ellipsis, Pencil, Trash2 } from "lucide-react";

import { type DepartmentRead } from "../modules/department/department.service";

interface DepartmentItemProps {
  readonly department: DepartmentRead
  readonly isActive: boolean
  readonly isChecked: boolean
  readonly onToggleCheck: (id: string) => void
  readonly onNavigate: (id: string) => void
  readonly onRename: (id: string, name: string) => void
  readonly onDelete: (id: string) => void
}

function DepartmentItem({ department, isActive, isChecked, onToggleCheck, onNavigate, onRename, onDelete }: DepartmentItemProps) {

  const [menuOpen, setMenuOpen] = useState<boolean>(false);
  const menuRef = useRef<HTMLDivElement>(null);

  return (
    <div className={`group flex items-center gap-2 px-2 py-2 rounded-xl transition-colors ${isActive ? "bg-white/10" : "hover:bg-white/6"
    }`}>
      {/* Checkbox */}
      <button
        onClick={() => onToggleCheck(department.id)}
        className="shrink-0 cursor-pointer"
        title="Use this department's knowledge in chat"
      >
        <div className={`w-4 h-4 rounded flex items-center justify-center border transition-all ${isChecked
          ? "bg-emerald-500 border-emerald-500"
          : "border-white/20 hover:border-white/40"
        }`}>
          {isChecked && (
            <Check className="w-2.5 h-2.5 text-text" strokeWidth={1.8} />
          )}
        </div>
      </button>

      {/* Name */}
      <button
        onClick={() => onNavigate(department.id)}
        className="cursor-pointer flex-1 min-w-0 text-left flex items-center gap-1"
        title={isActive ? "Back to chat" : `Open ${department.name} dashboard`}
      >
        <span
          className={`text-sm truncate transition-colors ${isActive ? "text-text font-medium" : "text-text/70 group-hover:text-text/90"
          }`}
        >
          {department.name}
        </span>
        {isActive && <ChevronRight className="w-3 h-3 text-text/40 shrink-0" />}
      </button>

      {/* Menu */}
      <div className="relative shrink-0" ref={menuRef}>
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className={`p-1 rounded-lg transition-colors cursor-pointer ${menuOpen
            ? "bg-white/10 text-text/80"
            : "text-transparent group-hover:text-text/40 hover:text-text/70! hover:bg-white/10"
          }`}
        >
          <Ellipsis className="w-3.5 h-3.5" />
        </button>

        {menuOpen && (
          <div className="absolute right-0 top-full mt-1 z-50 min-w-35 bg-bg-menu border border-white/10 rounded-xl shadow-xl overflow-hidden">
            <button
              onClick={() => {
                setMenuOpen(false);
                onRename(department.id, department.name);
              }}
              className="w-full flex items-center gap-2.5 px-3 py-2.5 text-sm text-text/80 hover:bg-white/8 hover:text-text transition-colors cursor-pointer"
            >
              <Pencil className="w-3.5 h-3.5 text-text/50" />
              Edit name
            </button>
            <div className="h-px bg-white/5 mx-2" />
            <button
              onClick={() => {
                setMenuOpen(false);
                onDelete(department.id);
              }}
              className="w-full flex items-center gap-2.5 px-3 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors cursor-pointer"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default DepartmentItem;