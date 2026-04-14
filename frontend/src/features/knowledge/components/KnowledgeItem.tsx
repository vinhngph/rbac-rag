import { AlertCircle, CheckCircle2, FileImage, FileScan, FileText, Loader2, MoreHorizontal, Pencil, Trash2, Zap } from "lucide-react";
import type { KnowledgeRead } from "../services/knowledge.service";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { APP_CONFIG } from "../../../core/config";
import InlineRename from "../../../shared/components/InlineRename";
import ContextMenu from "../../../shared/components/ContextMenu";

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

interface KnowledgeItemProps{
    readonly knowledge: KnowledgeRead
    readonly roleId: string
    readonly isRenaming: boolean
    readonly isContextOpen: boolean
    readonly onSetRenaming: () => void
    readonly onSetContextOpen: () => void
    readonly onCloseContext: () => void
    readonly onRename: (id: string, newName: string) => Promise<void>
    readonly onDelete: (id: string) => void
}

function KnowledgeItem({ knowledge, roleId, isRenaming, isContextOpen, onSetRenaming, onSetContextOpen, onCloseContext, onRename, onDelete }: KnowledgeItemProps) {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (["completed", "failed"].includes(knowledge.status)) return;

    const sse = new EventSource(`${APP_CONFIG.APP_BE_API}/knowledges/${knowledge.id}/status`, {
      withCredentials: true
    });

    const updateKnowledgeStatus = (oldData: KnowledgeRead[] | undefined, newStatus: string) => {
      if (!oldData) return oldData;

      return oldData.map((k) => {
        if (k.id === knowledge.id) {
          return { ...k, status: newStatus };
        } else {
          return k;
        }
      });
    };
    sse.addEventListener("status_update", (event) => {
      const newStatus = JSON.parse(JSON.parse(event.data)).status.toLowerCase();

      queryClient.setQueryData(["role_knowledges", roleId], (oldData: KnowledgeRead[] | undefined) => {
        return updateKnowledgeStatus(oldData, newStatus);
      });

      if (["completed", "failed"].includes(newStatus)) {
        sse.close();
      }
    });

    sse.onerror = () => {
      sse.close();
    };

    return () => sse.close();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [knowledge.id, roleId, queryClient]);

  const sc = STATUS_CONFIG[knowledge.status] ?? STATUS_CONFIG.scanning;

  return (
    <div
      key={knowledge.id}
      className="group flex items-center gap-2.5 py-2 px-2.5 rounded-xl hover:bg-white/4 transition-colors cursor-pointer"
    >
      {fileIcon(knowledge.type)}
      <div className="flex-1 min-w-0">
        {isRenaming
          ? (
            <InlineRename
              value={knowledge.name}
              onConfirm={async (n) => {
                await onRename(knowledge.id, n);
              }}
              onCancel={onCloseContext}
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
            onSetContextOpen();
          }}
          className={`p-1 rounded-md transition-colors cursor-pointer ${
            isContextOpen ? "text-text/70 bg-white/8" : "text-transparent group-hover:text-text/30 hover:text-text/60!"
          }`}
        >
          <MoreHorizontal className="w-3.5 h-3.5" />
        </button>
        {isContextOpen && (
          <ContextMenu
            onClose={onCloseContext}
            items={[
              { label: "Rename", icon: <Pencil className="w-3.5 h-3.5" />, onClick: onSetRenaming },
              { label: "Delete", icon: <Trash2 className="w-3.5 h-3.5" />, danger: true, onClick: () => onDelete(knowledge.id) }
            ]}
          />
        )}
      </div>
    </div>
  );
}

export default KnowledgeItem;
