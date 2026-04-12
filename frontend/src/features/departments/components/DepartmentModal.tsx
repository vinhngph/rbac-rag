import { useNavigate } from "react-router";
import useRoles from "../../roles/hooks/useRoles";
import { useState } from "react";
import { ChevronRight, Folder, FolderOpen, MoreHorizontal, Pencil, Plus, Trash2, X } from "lucide-react";
import InlineRename from "../../../shared/components/InlineRename";
import ContextMenu from "../../../shared/components/ContextMenu";
import RequestButton from "../../../shared/components/RequestButton";

interface DepartmentModalProps {
    readonly id: string
}

function DepartmentModal({ id }: DepartmentModalProps) {
  const navigate = useNavigate();

  const handleClose = () => { navigate("/"); };

  // const [loading, setLoading] = useState(true);
  // const [departmentName, setDepartmentName] = useState<string>("");

  const [contextRole, setContextRole] = useState<string | null>(null);
  const [renamingRole, setRenamingRole] = useState<string | null>(null);
  const [newRoleName, setNewRoleName] = useState("");


  const { currentRole, childRoles, breadcrumb, rootRole, isRoot, loadingRoles, handleCreateRole, handleNavigateRole, handleRenameRole, handleDeleteRole } = useRoles(id);

  const [showNewRole, setShowNewRole] = useState(false);

  const handleNavigate = (roleId: string) => {
    handleNavigateRole(roleId);
  };

  const handleNewRoleCreate = async () => {
    const name = newRoleName.trim();
    if (!name || !currentRole) return;

    handleCreateRole(name);
    setNewRoleName("");
    setShowNewRole(false);
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
              {childRoles.map((role) => (
                <div
                  key={role.id}
                  className="group relative flex items-center gap-2 px-2.5 py-2 rounded-xl hover:bg-white/6 transition-colors"
                >
                  <button
                    type="button"
                    className="absolute inset-0 w-full h-full z-10 rounded-xl cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-white/20 bg-transparent border-none"
                    onDoubleClick={() => handleNavigate(role.id)}
                  />
                  <FolderOpen className="w-4 h-4 text-amber-400/70 shrink-0" />
                  <div className="flex-1 min-w-0">
                    {renamingRole === role.id
                      ?
                      <div className="relative z-20">
                        <InlineRename
                          value={role.name}
                          onConfirm={(n) => {handleRenameRole(role.id, n); setRenamingRole(null);}}
                          onCancel={() => setRenamingRole(null)}
                        />
                      </div>
                      :<span className="text-sm text-text/80 truncate block">{role.name}</span>
                    }
                  </div>
                  <div className="relative z-20">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setContextRole(contextRole === role.id? null: role.id);
                      }}
                      className={`p-0.5 rounded-md transition-colors cursor-pointer ${contextRole == role.id ? "text-text/70 bg-white/8": "text-transparent group-hover:text-text/35 hover:text-text/60!"}`}
                    >
                      <MoreHorizontal className="w-3.5 h-3.5" />
                    </button>
                    {contextRole === role.id && (
                      <ContextMenu
                        onClose={() => setContextRole(null)}
                        items={[
                          { label: "Open", icon: <FolderOpen className="w-3.5 h-3.5" />, onClick: () => handleNavigate(role.id) },
                          { label: "Rename", icon: <Pencil className="w-3.5 h-3.5" />, onClick: () => setRenamingRole(role.id) },
                          { label: "Delete", icon: <Trash2 className="w-3.5 h-3.5" />, danger: true, onClick: () => handleDeleteRole(role.id) }
                        ]}
                      />
                    )}
                  </div>
                </div>
              ))}
              {showNewRole && (
                <div className="px-2 py-1.5 space-y-1.5">
                  <input
                    type="text"
                    autoFocus
                    value={newRoleName}
                    onChange={(e) => setNewRoleName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleNewRoleCreate();
                      if (e.key === "Escape") {
                        setShowNewRole(false);
                        setNewRoleName("");
                      }
                    }}
                    placeholder="Role name..."
                    className="w-full bg-white/5 border border-white/10 focus:border-emerald-400/40 rounded-lg px-2.5 py-1.5 text-sm text-white placeholder-text/25 outline-none transition-colors"
                  />
                  <div className="flex gap-1">
                    <button
                      onClick={() => {setShowNewRole(false); setNewRoleName("");}}
                      className="flex-1 text-xs text-text/40 hover:text-text/70 bg-white/4 hover:bg-white/8 rounded-lg cursor-pointer transition-colors"
                    >
                      Cancel
                    </button>
                    <RequestButton
                      type="button"
                      onClick={handleNewRoleCreate}
                      isLoading={loadingRoles}
                      disabled={!newRoleName.trim()}
                      className="flex-1 py-1 text-xs text-white bg-emerald-700 hover:bg-emerald-600 disabled:opacity-40 rounded-lg cursor-pointer transition-colors"
                    >
                      Create
                    </RequestButton>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Role Context */}

        </div>
      </div>
    </div>
  );
}

export default DepartmentModal;
