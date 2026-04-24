import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { chatService } from "../services/chat.service";
import { ChevronLeft, ChevronRight, FileText, Info, Loader2, SquareLibrary, X } from "lucide-react";
import { getKnowledgeFile } from "../../roles/services/role.service";

import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

const options = {
  cMapUrl: "/cmaps/",
  standardFontDataUrl: "/standard_fonts/",
  wasmUrl: "/wasm/"
};

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

  const { data: fileBlob, isLoading: isLoadingFile } = useQuery({
    queryKey: ["knowledge_file", selectedSource],
    queryFn: () => getKnowledgeFile(selectedSource ?? "").then((res) => res.data),
    enabled: !!selectedSource
  });

  const [numPages, setNumPages] = useState<number>();
  const [pageNumber, setPageNumber] = useState<number>(1);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setPageNumber(1);
  }

  const changePage = (offset: number) => {
    setPageNumber((prev) => Math.min(Math.max(1, prev + offset), numPages || 1));
  };

  const renderPreview = () => {
    if (!selectedSource) {
      return (
        <div className="h-full flex items-center justify-center text-text/40">
          Select a source from the left panel to preview its content.
        </div>
      );
    }

    if (isLoadingFile) {
      return (
        <div className="w-full h-full flex flex-col items-center justify-center text-emerald-400">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      );
    }

    if (fileBlob) {
      return (
        <div className="flex flex-col items-center h-full w-full relative">
          {numPages && (
            <div className="absolute bottom-2 z-10 flex items-center gap-4 bg-black/60 backdrop-blur-md px-4 py-2 rounded-full shadow-xl border border-white/10 transition-opacity hover:bg-black/80">
              <button
                onClick={() => changePage(-1)}
                disabled={pageNumber <= 1}
                className="p-1.5 hover:bg-white/20 rounded-full disabled:opacity-30 disabled:hover:bg-transparent transition-all cursor-pointer text-white"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              <span className="text-sm font-medium text-white/90 min-w-22.5 text-center">Page {pageNumber} of {numPages}</span>

              <button
                onClick={() => changePage(1)}
                disabled={pageNumber >= numPages}
                className="p-1.5 hover:bg-white/20 rounded-full disabled:opacity-30 disabled:hover:bg-transparent transition-all cursor-pointer text-white"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}

          <div className="flex-1 w-full overflow-y-auto custom-scrollbar flex justify-center">
            <Document
              file={fileBlob}
              onLoadSuccess={onDocumentLoadSuccess}
              loading={
                <div className="flex items-center justify-center p-10 text-emerald-400 mt-10">
                  <Loader2 className="w-8 h-8 animate-spin" />
                </div>
              }
              error={
                <div className="p-10 text-text/40 text-center mt-10">
                  Failed to load the PDF document.
                </div>
              }
              options={options}
            >
              <Page
                key={`page_${pageNumber}`}
                pageNumber={pageNumber}
                className="shadow-2xl overflow-hidden"
                renderTextLayer={true}
                renderAnnotationLayer={true}
                width={800}
              />
            </Document>
          </div>
        </div>
      );
    }

    return (
      <div className="w-full h-full flex flex-col items-center justify-center text-text/40">
        Failed to fetch the docuemnt.
      </div>
    );
  };

  const renderContent = () => {
    if (isLoadingSources) {
      return (
        <div className="w-full h-full flex flex-col items-center justify-center gap-3 text-text/50">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-400" />
        </div>
      );
    }

    if (sourcesData?.length === 0) {
      return (
        <div className="w-full h-full flex flex-col items-center justify-center gap-3 text-text/50">
          <Info className="w-8 h-8" />
          <p>No sources available for this response.</p>
        </div>
      );
    }

    return (
      <>
        <div className="w-1/4 border-r border-white/10 bg-white/1 overflow-y-auto custom-scrollbar p-3 space-y-2">
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

        <div className="w-3/4 overflow-y-auto custom-scrollbar bg-bg-prompt">
          {renderPreview()}
        </div>
      </>
    );
  };



  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-7xl h-[95vh] bg-bg rounded-2xl border border-white/10 flex flex-col overflow-hidden shadow-2xl duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/2">
          <h2 className="text-lg font-semibold text-text/80 flex items-center gap-2">
            <SquareLibrary className="w-5 h-5 text-emerald-400" />
            Response sources
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/10 text-text/60 hover:text-text transition-colors cursor-pointer"
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
