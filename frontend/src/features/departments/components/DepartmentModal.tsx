import React, { useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import { AlertCircle, CheckCircle2, ChevronRight, FileImage, FileScan, FileText, FolderOpen, House, Loader2, MoreHorizontal, Pencil, Plus, RefreshCcw, Trash2, Upload, UserPlus, Users, X, Zap } from "lucide-react";

import { useAuth } from "../../auth/hooks/useAuth";
import useRoles from "../../roles/hooks/useRoles";
import InlineRename from "../../../shared/components/InlineRename";
import ContextMenu from "../../../shared/components/ContextMenu";
import RequestButton from "../../../shared/components/RequestButton";
import useRoleMembers from "../../roles/hooks/useRoleMembers";
import useRoleKnowledges from "../../roles/hooks/useRoleKnowledges";
import UserAvatar from "../../../shared/components/UserAvatar";
import PermissionBadge from "../../../shared/components/PermissionBadge";
import AddMemberPanel from "./AddMemberPanel";

const STATUS_CONFIG: Record<string, {label: string, color: string, icon: React.ReactNode}> = {
  scanning: { label: "Scanning", color: "text-yellow-400", icon: <FileScan className="w-3 h-3" /> },
  safe: { label: "Safe", color:"text-blue-400", icon:<CheckCircle2 className="w-3 h-3"/> },
  extracting: { label: "Extracting", color: "text-orange-400", icon: <Loader2 className="w-3 h-3 animate-spin" /> },
  chunking: { label: "Chunking", color: "text-purple-400", icon: <Loader2 className="w-3 h-3 animate-spin" /> },
  embedding: { label: "Embedding", color: "text-cyan-400", icon: <Zap className="w-3 h-3 animate-spin" /> },
  completed: { label: "Ready", color: "text-emerald-400", icon: <CheckCircle2 className="w-3 h-3" /> },
  failed: { label: "Failed", color: "text-red-400", icon: <AlertCircle className="w-3 h-3" /> },
};

function fileIcon(type: string) {
  if (["png", "jpg", "jpeg"].includes(type))
    return <FileImage className="w-5 h-5 text-sky-400/80" />;
  return <FileText className="w-5 h-5 text-rose-400/80" />;
}

interface DepartmentModalProps {
    readonly id: string
}

function DepartmentModal({ id }: DepartmentModalProps) {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  // Data
  const { user } = useAuth();
  const { currentRole, childRoles, breadcrumb, rootRole, isRoot, isLoadingRoles, navigateRole, handleCreateRole, handleRenameRole, handleDeleteRole } = useRoles(id);
  const { roleMembers, handleTogglePermission, handleRemoveMember } = useRoleMembers(currentRole?.id);
  const { roleKnowledges, isUploading, handleUpload, handleRenameKnowledge, handleDeleteKnowledge } = useRoleKnowledges(currentRole?.id);

  // UI States
  const [contextRole, setContextRole] = useState<string | null>(null);
  const [contextMember, setContextMember] = useState<string | null>(null);
  const [contextKnowledge, setContextKnowledge] = useState<string | null>(null);
  const [renamingRole, setRenamingRole] = useState<string | null>(null);
  const [renamingKnowledge, setRenamingKnowledge] = useState<string | null>(null);
  const [newRoleName, setNewRoleName] = useState("");
  const [showNewRole, setShowNewRole] = useState(false);
  const [showAddMember, setShowAddMember] = useState(false);

  const isMany = (n: number) => {
    return n > 1 ? "s": "";
  };

  const handleClose = () => { navigate("/"); };

  const handleNewRoleCreate = async () => {
    const name = newRoleName.trim();
    if (!name || !currentRole) return;

    handleCreateRole(name);
    setNewRoleName("");
    setShowNewRole(false);
  };

  if (isLoadingRoles) {
    return (
      <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
      </div>
    );
  }

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
              onClick={() => navigateRole(rootRole?.id?? null) }
              className="text-sm font-semibold text-emerald-400/90 hover:text-emerald-400 transition-colors shrink-0 cursor-pointer"
            >
              {rootRole?.name}
            </button>
            {breadcrumb.slice(1).map((role) => (
              <span key={role.id} className="flex items-center gap-1 shrink-0">
                <ChevronRight className="w-3.5 h-3.5 text-text/20" />
                <button
                  onClick={() => navigateRole(role.id)}
                  className={`text-sm transition-colors cursor-pointer ${role.id === currentRole?.id ? "text-white font-medium": "text-text/50 hover:text-text/80"}`}
                >
                  {role.name}
                </button>
              </span>
            ))}
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {!isLoadingRoles && (
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
              {!isLoadingRoles && childRoles.length === 0 && !showNewRole && (
                <div className="flex flex-col items-center justify-center h-24 gap-1.5">
                  <House className="w-7 h-7 text-text/10" />
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
                    onDoubleClick={() => navigateRole(role.id)}
                  />
                  <House className="w-4 h-4 text-amber-400/70 shrink-0" />
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
                          { label: "Open", icon: <FolderOpen className="w-3.5 h-3.5" />, onClick: () => navigateRole(role.id) },
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
                      isLoading={isLoadingRoles}
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
          <div className="flex-1 overflow-hidden flex flex-col">
            {isLoadingRoles
              ? <div className="flex-1 flex items-center justify-center">
                <Loader2 className="w-6 h-6 text-emerald-400/50 animate-spin" />
              </div>
              :(
                <div className="flex-1 overflow-y-auto">
                  {/* Current role banner */}
                  <div className="px-6 py-4 border-b border-white/5 flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-amber-400/10 border border-amber-400/20 flex items-center justify-center">
                      <House className="w-4.5 h-4.5 text-amber-400" />
                    </div>
                    <div>
                      <h2 className="text-base font-semibold text-white leading-tight">{currentRole?.name}</h2>
                      <p className="text-[11px] text-text/35 mt-0.5">{`${roleMembers.length} member${isMany(roleMembers.length)} • ${roleKnowledges.length} file${isMany(roleKnowledges.length)}`}</p>
                    </div>
                    <div className="ml-auto flex items-center gap-1.5">
                      <button
                        onClick={() => {
                          queryClient.invalidateQueries({ queryKey: ["role_members", currentRole?.id] });
                          queryClient.invalidateQueries({ queryKey: ["role_knowledges", currentRole?.id] });
                        }}
                        className="p-1.5 rounded-lg hover:bg-white/10 text-text/30 hover:text-text/70 transition-colors cursor-pointer"
                      >
                        <RefreshCcw className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-0 divide-x divide-white/5 flex-1">
                    {/* Member section */}
                    <div className="px-5 py-4 space-y-3">
                      <div className="flex items-center gap-2">
                        <Users className="w-3.5 h-3.5 text-text/40" />
                        <span className="text-[11px] font-semibold text-text/40 uppercase tracking-widest">Members</span>
                        <span className="ml-auto text-[11px] text-text/25 bg-white/4 px-2 py-0.5 rounded-full">{roleMembers.length}</span>
                        {!isRoot && (
                          <button
                            onClick={() => setShowAddMember(!showAddMember)}
                            className="p-1 rounded-lg hover:bg-white/10 text-text/30 hover:text-text/70 transition-colors cursor-pointer"
                          >
                            <UserPlus className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>

                      <div className="space-y-1">
                        {/* Member list */}
                        {roleMembers.length === 0 && (
                          <p className="text-xs text-text/20 py-4 text-center">No members</p>
                        )}
                        {roleMembers.map((member) => (
                          <div
                            key={member.id}
                            className="group flex items-center gap-2.5 px-2.5 py-2 rounded-xl hover:bg-white/4 transition-colors cursor-pointer"
                          >
                            <UserAvatar avatar_url={member.avatar_url} name={member.name} />
                            {/* Info */}
                            <div className="flex-1 min-w-0">
                              <p className="text-sm text-text/85 truncate leading-tight">
                                {member.name}
                                {(member.id === user?.id) && (
                                  <span className="ml-1.5 text-[10px] text-emerald-400/60">(you)</span>
                                )}
                              </p>
                              <p className="text-[11px] text-text/35 truncate">{member.email}</p>
                            </div>
                            {/* Permissions */}
                            <div className="flex items-center gap-1 shrink-0">
                              {(["view", "edit"] as const).map((p) => (
                                <PermissionBadge
                                  key={p}
                                  label={p}
                                  active={member.permissions?.includes(p) ?? false}
                                  disabled={
                                    (member.permissions?.includes(p) && (member.permissions.length ?? 0) === 1) ?? true
                                  }
                                  onClick={() => handleTogglePermission(member, p)}
                                />
                              ))}
                            </div>
                            {/* Remove */}
                            {member.permissions && (
                              <div className="relative">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setContextMember(contextMember === member.id ? null : member.id);
                                  }}
                                  className={`p-1 rounded-md transition-colors cursor-pointer ${
                                    contextMember === member.id ? "text-text/70 bg-white/8" : "text-transparent group-hover:text-text/30 hover:text-text/60!"
                                  }`}
                                >
                                  <MoreHorizontal className="w-3.5 h-3.5" />
                                </button>
                                {contextMember === member.id && (
                                  <ContextMenu
                                    onClose={() => setContextMember(null)}
                                    items={[
                                      { label: "Remove", icon: <Trash2 className="w-3.5 h-3.5" />, danger: true, onClick: () => handleRemoveMember(member.id) }
                                    ]}
                                  />
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                      {/* Add member panel */}
                      {showAddMember && currentRole && (
                        <AddMemberPanel
                          roleId={currentRole.id}
                          onClose={() => setShowAddMember(false)}
                        />
                      )}

                      {isRoot && (
                        <div className="flex items-center gap-1.5 px-2.5 py-2 rounded-xl bg-amber-500/6 border border-amber-500/15">
                          <AlertCircle className="w-3 h-3 text-amber-400/70 shrink-0" />
                          <p className="text-[11px] text-amber-400/60">Root role members cannot be edited.</p>
                        </div>
                      )}
                    </div>

                    {/* Knowledge section */}
                    <div className="px-5 py-4 space-y-3">
                      <div className="flex items-center gap-2">
                        <FileText className="w-3.5 h-3.5 text-text/40" />
                        <span className="text-[11px] font-semibold text-text/40 uppercase tracking-widest">
                      Knowledges
                        </span>
                        <span className="ml-auto text-[11px] text-text/25 bg-white/4 px-2 py-0.5 rounded-full">
                          {roleKnowledges.length}
                        </span>
                        {/* Upload */}
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          disabled={isUploading}
                          className="p-1 rounded-lg hover:bg-white/10 text-text/30 hover:text-text/70 transition-colors cursor-pointer disabled:opacity-40"
                          title="Upload file"
                        >
                          {isUploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Upload className="w-3.5 h-3.5" />}
                        </button>
                        <input
                          type="file"
                          ref={fileInputRef}
                          accept=".pdf,.png,.jpg,.jpeg"
                          className="hidden"
                          onChange={(e) =>  handleUpload(e, fileInputRef)}
                        />
                      </div>

                      <div className="space-y-1">
                        {roleKnowledges.length === 0 && (
                          <div className="flex flex-col items-center justify-center py-8 gap-2">
                            <div className="w-10 h-10 rounded-xl bg-white/4 flex items-center justify-center">
                              <Upload className="w-5 h-5 text-text/15" />
                            </div>
                            <p className="text-xs text-text/20">No files uploaded</p>
                            <button
                              onClick={() => fileInputRef.current?.click()}
                              className="text-xs text-emerald-400/60 hover:text-emerald-400 transition-colors cursor-pointer"
                            >
                            Upload PDF or image
                            </button>
                          </div>
                        )}
                        {roleKnowledges.map((knowledge) => {
                          const sc = STATUS_CONFIG[knowledge.status] ?? STATUS_CONFIG.scanning;
                          return (
                            <div
                              key={knowledge.id}
                              className="group flex items-center gap-2.5 py-2 px-2.5 rounded-xl hover:bg-white/4 transition-colors cursor-pointer"
                            >
                              {fileIcon(knowledge.type)}
                              <div className="flex-1 min-w-0">
                                {renamingKnowledge === knowledge.id
                                  ? (
                                    <InlineRename
                                      value={knowledge.name}
                                      onConfirm={async (n) => {
                                        await handleRenameKnowledge(knowledge.id, n);
                                        setRenamingKnowledge(null);
                                      }}
                                      onCancel={() => setRenamingKnowledge(null)}
                                    />
                                  )
                                  : (
                                    <>
                                      <p className="text-sm text-text/85 truncate leading-tight">{`${knowledge.name}.${knowledge.type}`}</p>
                                      <div className="flex items-center gap-1 mt-0.5">
                                        <span className={`flex items-center gap-1 text-[10px] ${sc.color}`}>
                                          {sc.icon} {sc.label}
                                        </span>
                                        <span className="text-[10px] text-text/20">•</span>
                                        <span className="text-[10px] text-text/25 uppercase">{knowledge.type}</span>
                                      </div>
                                    </>
                                  )}
                              </div>
                              <div className="relative">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setContextKnowledge(contextKnowledge === knowledge.id? null: knowledge.id);
                                  }}
                                  className={`p-1 rounded-md transition-colors cursor-pointer ${
                                    contextKnowledge === knowledge.id ? "text-text/70 bg-white/8" : "text-transparent group-hover:text-text/30 hover:text-text/60!"
                                  }`}
                                >
                                  <MoreHorizontal className="w-3.5 h-3.5" />
                                </button>
                                {contextKnowledge === knowledge.id && (
                                  <ContextMenu
                                    onClose={() => setContextKnowledge(null)}
                                    items={[
                                      { label: "Rename", icon: <Pencil className="w-3.5 h-3.5" />, onClick: () =>setRenamingKnowledge(knowledge.id) },
                                      { label: "Delete", icon: <Trash2 className="w-3.5 h-3.5" />, danger: true, onClick: () =>handleDeleteKnowledge(knowledge.id) }
                                    ]}
                                  />
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )
            }
          </div>
        </div>
      </div>
    </div>
  );
}

export default DepartmentModal;
