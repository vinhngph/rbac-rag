import { useNavigate } from "react-router";
import useRoles from "../../roles/hooks/useRoles";
import { useState } from "react";
import { ChevronRight, Folder, Plus, X } from "lucide-react";

interface DepartmentModalProps {
    readonly id: string
}

function DepartmentModal({ id }: DepartmentModalProps) {
  const navigate = useNavigate();

  const handleClose = () => { navigate("/"); };

  // const [loading, setLoading] = useState(true);
  // const [departmentName, setDepartmentName] = useState<string>("");


  const { currentRole, childRoles, breadcrumb, rootRole, isRoot, loadingRoles, handleNavigateRole } = useRoles(id);

  const [showNewRole, setShowNewRole] = useState(false);

  const handleNavigate = (roleId: string) => {
    handleNavigateRole(roleId);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      {/* Backdrop */}
      <button
        type="button"
        className="absolute inset-0 bg-black/55 backdrop-blur-md"
        onClick={handleClose}
        aria-label="Close"
      />

      {/* Modal box */}
      <div className="relative z-10 w-full max-w-6xl h-[88vh] bg-[#161616] border border-white/10 rounded-2xl shadow-2xl shadow-black/70 flex flex-col overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center gap-3 px-5 py-3.5 border-b border-white/6 shrink-0 bg-[#111]/60">
          {/* Breadcrumb */}
          <div className="flex items-center gap-1 flex-1 min-w-0 overflow-hidden">
            <button
              onClick={() => handleNavigateRole(rootRole?.id?? null) }
              className="text-sm font-semibold text-emerald-400/90 hover:text-emerald-400 transition-colors shrink-0 cursor-pointer"
            >
              {rootRole?.name}
            </button>
            {breadcrumb.slice(1).map((role) => (
              <span key={role.id} className="flex items-center gap-1 shrink-0">
                <ChevronRight className="w-3.5 h-3.5 text-text/20" />
                <button
                  onClick={() => handleNavigate(role.id)}
                  className={`text-sm transition-colors cursor-pointer ${role.id === currentRole?.id ? "text-white font-medium": "text-text/50 hover:text-text/80"}`}
                >
                  {role.name}
                </button>
              </span>
            ))}
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {!loadingRoles && !isRoot && (
              <button
                onClick={() => setShowNewRole(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/6 hover:bg-white/10 text-text/60 hover:text-text text-xs transition-colors cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" /> New role
              </button>
            )}
            <button
              onClick={handleClose}
              className="p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/80 transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex flex-1 overflow-hidden">
          {/* Left: Roles Tree */}
          <div className="w-64 shrink-0 border-r border-white/6 flex flex-col bg-[#0f0f0f]/40">
            <div className="px-3 py-2.5 border-b border-white/5">
              <p className="text-[10px] font-semibold text-text/30 uppercase tracking-widest">Roles</p>
            </div>
            <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5">
              {!loadingRoles && childRoles.length === 0 && !showNewRole && (
                <div className="flex flex-col items-center justify-center h-24 gap-1.5">
                  <Folder className="w-7 h-7 text-text/10" />
                  <p className="text-xs text-text/20">No child roles</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DepartmentModal;
