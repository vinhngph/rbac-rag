import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { chatService } from "../services/chat.service";
import { FileText, Info, Loader2, SquareLibrary, X } from "lucide-react";
import PdfPreview from "../../../shared/components/PdfPreview";

interface MessageSourcesProps {
  isOpen: boolean
  onClose: () => void
  sessionId: string
  messageId: string
}

function MessageSources({ isOpen, onClose, sessionId, messageId }: Readonly<MessageSourcesProps>) {
  const { data: sourcesData, isLoading: isLoadingSources } = useQuery({
    queryKey: ["message_sources", sessionId, messageId],
    queryFn: () => chatService.getMessageSources(sessionId, messageId).then((res) => res.data),
    enabled: isOpen && !!sessionId && !!messageId
  });

  const [manualSelectedSource, setManualSelectedSource] = useState<string | null>(null);
  const selectedSource = manualSelectedSource ?? sourcesData?.[0].id ?? null;

  const renderContent = () => {
    if (isLoadingSources) {
      return (
        <div className="w-full h-full flex flex-col items-center justify-center gap-3 text-text-muted">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-400" />
        </div>
      );
    }

    if (sourcesData?.length === 0) {
      return (
        <div className="w-full h-full flex flex-col items-center justify-center gap-3 text-text-muted">
          <Info className="w-8 h-8" />
          <p>No sources available for this response.</p>
        </div>
      );
    }

    return (
      <>
        <div className="w-1/4 border-r border-border-subtle bg-bg-sidebar overflow-y-auto custom-scrollbar p-3 space-y-2">
          {sourcesData?.map((source) => (
            <button
              key={source.id}
              onClick={() => setManualSelectedSource(source.id)}
              className={`w-full p-3 rounded-xl cursor-pointer transition-all border ${selectedSource === source.id
                ? "bg-emerald-400/10 border-emerald-400/30 text-emerald-400"
                : "bg-transparent border-transparent hover:bg-white/5 text-text/70 hover:text-text"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <FileText className="w-4 h-4 shrink-0" />
                <span className="font-medium text-sm truncate">
                  {source.name}.{source.type}
                </span>
              </div>
            </button>
          ))}
        </div>

        <div className="w-3/4 overflow-y-auto custom-scrollbar bg-bg-prompt relative flex flex-col">
          {selectedSource
            ? (
              <PdfPreview knowledgeId={selectedSource} />
            )
            : (
              <div className="flex-1 flex items-center justify-center text-text-muted">
                Select a source from the left panel to preview its content.
              </div>
            )}
        </div>
      </>
    );
  };



  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-surface-active backdrop-blur-sm p-4">
      <div className="w-full max-w-7xl h-[95vh] bg-bg rounded-2xl border border-border-subtle flex flex-col overflow-hidden shadow-2xl duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-bg-modal">
          <h2 className="text-lg font-semibold text-text/80 flex items-center gap-2">
            <SquareLibrary className="w-5 h-5 text-emerald-400" />
            Response sources
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-surface-hover text-text/60 hover:text-text transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex flex-1 overflow-hidden">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default MessageSources;
