import { useState } from "react";
import useDepartments from "../../features/departments/hooks/useDepartments";
import { useLocation, useNavigate } from "react-router";
import { Building2, PanelRightClose, PanelRightOpen, Plus } from "lucide-react";
import DepartmentItem from "../../features/departments/components/DepartmentItem";
import PromptModal from "../../shared/components/PromptModal";

function RightSidebar() {
  const [rightCollapsed, setRightCollapsed] = useState<boolean>(false);
  const [isAddingDepartment, setIsAddingDepartment] = useState<boolean>(false);
  const [newDepartmentName, setNewDepartmentName] = useState<string>("");
  const [renameTarget, setRenameTarget] = useState<{ id: string; name: string } | null>(null);

  const location = useLocation();
  const navigate = useNavigate();

  const { departments, checkedDepartments, handleAddDepartment, handleUpdateDepartment, handleDeleteDepartment, handleToggleCheck } = useDepartments();

  const handleAdd = async ()  =>{
    const name = newDepartmentName.trim();
    if (!name) return;

    handleAddDepartment(name);

    setNewDepartmentName("");
    setIsAddingDepartment(false);
  };

  const handleNewDepartmentNameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleAdd();
    if (e.key === "Escape") {
      setIsAddingDepartment(false);
      setNewDepartmentName("");
    }
  };

  const handleDepartmentNavigate = (id: string) => {
    if (location.pathname === `/department/${id}`) {
      navigate("/");
    } else {
      navigate(`/department/${id}`);
    }
  };

  const handleDelete = async (id: string) => {
    handleDeleteDepartment(id);

    if (location.pathname === `/department/${id}`)
      navigate("/");
  };

  const handleRenameConfirm = async (name: string) => {
    if (!renameTarget) return;

    handleUpdateDepartment(renameTarget.id, name);
    setRenameTarget(null);
  };
  return (
    <>
      <aside className={`flex flex-col transition-all duration-300 ease-in-out bg-bg-sidebar border-l border-white/5 ${rightCollapsed ? "w-15" : "w-72"}`}>
        {/* Header */}
        <div className="flex items-center h-13 px-3 border-b border-white/5 gap-2">
          <button
            onClick={() => setRightCollapsed(!rightCollapsed)}
            className="p-1.5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer shrink-0"
            title={rightCollapsed ? "Open departments" : "Close departments"}
          >
            {rightCollapsed
              ? <PanelRightOpen className="w-4 h-4 text-text/70" />
              : <PanelRightClose className="w-4 h-4 text-text/70" />}
          </button>

          {!rightCollapsed && (
            <>
              <Building2 className="w-4 h-4 text-text/40 shrink-0" />
              <span className="text-[12px] font-semibold text-text/50 tracking-widest uppercase flex-1">Departments</span>
              <button
                onClick={() => setIsAddingDepartment(true)}
                className="p-1.5 rounded-lg hover:bg-white/10 text-text/35 hover:text-text/75 transition-colors cursor-pointer"
                title="New department"
              >
                <Plus className="w-4 h-4" />
              </button>
            </>
          )}
        </div>

        {/* Collapsed icon strip */}
        {rightCollapsed && (
          <div className="flex flex-col items-center gap-1 px-2 pt-2">
            <button
              onClick={() => setRightCollapsed(false)}
              className="p-2 rounded-xl hover:bg-white/10 transition-colors cursor-pointer"
              title="Departments"
            >
              <Building2 className="w-4 h-4 text-text/40" />
            </button>
          </div>
        )}

        {!rightCollapsed && (
          <>
            {/* Add new department */}
            {isAddingDepartment && (
              <div className="px-3 py-2.5 border-b border-white/5">
                <input
                  autoFocus
                  type="text"
                  value={newDepartmentName}
                  onChange={(e) => setNewDepartmentName(e.target.value)}
                  onKeyDown={handleNewDepartmentNameKeyDown}
                  placeholder="Department name..."
                  className="w-full bg-white/5 border border-white/10 focus:border-emerald-400/40 rounded-xl px-3 py-2 text-sm text-text placeholder-text/25 outline-none transition-colors"
                />
                <div className="flex gap-1.5 mt-2">
                  <button
                    onClick={() => {
                      setIsAddingDepartment(false);
                      setNewDepartmentName("");
                    }}
                    className="flex-1 py-1.5 text-xs text-text/50 hover:text-text bg-white/5 hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAdd}
                    disabled={!newDepartmentName.trim()}
                    className="flex-1 py-1.5 text-xs text-text bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed"
                  >
                    Create
                  </button>
                </div>
              </div>
            )}

            {/* Knowledge context badge */}
            {(checkedDepartments.size > 0) && (
              <div className="mx-3 mt-2.5 px-2.5 py-1.5 bg-emerald-500/8 border border-emerald-500/15 rounded-xl">
                <p className="text-[11px] text-emerald-400/80 leading-snug">
                  Chat uses{" "}
                  <span className="font-semibold text-emerald-400">
                    {`${checkedDepartments.size} department${checkedDepartments.size > 1 ? "s" : ""}`}
                  </span>
                  {" "}
                  as context
                </p>
              </div>
            )}
            {/* List active departments */}
            <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5">
              {departments.length === 0
                ? <div className="flex flex-col items-center justify-center h-32 gap-2">
                  <Building2 className="w-7 h-7 text-text/10" />
                  <p className="text-xs text-text/25">No departments yet</p>
                  <button
                    onClick={() => setIsAddingDepartment(true)}
                    className="text-xs text-emerald-400/60 hover:text-emerald-400 transition-colors cursor-pointer"
                  >
                    + Create one
                  </button>
                </div>
                : (
                  departments.map((department) => (
                    <DepartmentItem
                      key={department.id}
                      department={department}
                      isActive={location.pathname === `/department/${department.id}`}
                      isChecked={checkedDepartments.has(department.id)}
                      onToggleCheck={handleToggleCheck}
                      onNavigate={handleDepartmentNavigate}
                      onRename={(id, name) => setRenameTarget({ id, name })}
                      onDelete={handleDelete}
                    />
                  ))
                )}
            </div>

            {/* Footer */}
            <div className="border-t border-white/5 px-4 py-2.5">
              <p className="text-[10px] text-text/20 leading-relaxed">
                ✓ Check department{"(s)"} to include in chat context
              </p>
            </div>
          </>
        )}
      </aside>

      {renameTarget && (
        <PromptModal
          title="Rename department"
          initialName={renameTarget.name}
          onConfirm={handleRenameConfirm}
          onCancel={() => setRenameTarget(null)}
        />
      )}
    </>
  );
}

export default RightSidebar;
