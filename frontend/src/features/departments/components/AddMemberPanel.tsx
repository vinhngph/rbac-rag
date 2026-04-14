import { useState } from "react";
import useRoleMembers from "../../roles/hooks/useRoleMembers";
import PermissionBadge from "../../../shared/components/PermissionBadge";
import RequestButton from "../../../shared/components/RequestButton";

interface AddMemberPanelProps {
    readonly roleId: string
    readonly onClose: () => void
}

function AddMemberPanel({ roleId, onClose }: AddMemberPanelProps) {
  const [email,  setEmail] = useState("");
  const [perms, setPerms] = useState<("view"| "edit")[]>(["view"]);

  const { isLoadingMembers, handleAddMember } = useRoleMembers(roleId);

  const togglePerm = (p: "view" | "edit") => {
    setPerms((prev) => {
      if (prev.includes(p)) {
        if (prev.length === 1) return prev;
        return prev.filter((x) => x !== p);
      }
      return [...prev, p];
    });
  };

  const handleAdd = async () => {
    if (!email.trim()) return;

    await handleAddMember({ email: email.trim(), permissions: perms });
    onClose();
  };

  return (
    <div className="border-t border-white/5 bg-white/2 px-4 py-3 space-y-2">
      <p className="text-[11px] font-semibold text-text/40 uppercase tracking-wider">Add member</p>
      <input
        type="email"
        autoFocus
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleAdd()}
        placeholder="user@example.com"
        className="w-full bg-white/5 border border-white/10 focus:border-emerald-400/40 rounded-xl px-3 py-2 text-sm text-white placeholder-text/25 outline-none transition-colors"
      />
      <div className="flex items-center gap-2">
        <span className="text-[11px] text-text/40">Permissions:</span>
        {(["view", "edit"] as const).map((p) => (
          <PermissionBadge
            key={p}
            label={p}
            active={perms.includes(p)}
            disabled={perms.includes(p) && perms.length === 1}
            onClick={() => togglePerm(p)}
          />
        ))}
      </div>
      <div className="flex gap-1.5">
        <button
          onClick={onClose}
          className="flex-1 py-1.5 text-xs text-text/50 bg-white/5 hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
        >Cancel
        </button>
        <RequestButton
          onClick={handleAdd}
          className="flex-1 py-1.5 text-xs text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-1"
          disabled={!email.trim() || isLoadingMembers}
        >
            Add
        </RequestButton>
      </div>
    </div>
  );
}

export default AddMemberPanel;
