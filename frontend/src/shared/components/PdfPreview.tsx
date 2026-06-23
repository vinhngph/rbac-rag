import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { getKnowledgeFile } from "../../features/roles/services/role.service";
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react";

import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdn.jsdelivr.net/npm/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const options = {
  cMapUrl: "/cmaps/",
  cMapPacked: true,
  standardFontDataUrl: "/standard_fonts/",
};

interface PdfPreviewProps {
    readonly knowledgeId: string
}

function PdfPreview({ knowledgeId }: PdfPreviewProps) {
  const [numPages, setNumPages] = useState<number>();
  const [pageNumber, setPageNumber] = useState<number>(1);

  const [isControlVisible, setIsControlVisible] = useState<boolean>(true);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data: fileBlob, isLoading: isLoadingFile } = useQuery({
    queryKey: ["knowledge_file", knowledgeId],
    queryFn: () => getKnowledgeFile(knowledgeId).then((res) => res.data),
    enabled: !!knowledgeId
  });

  const resetTimer = () => {
    setIsControlVisible(true);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      setIsControlVisible(false);
    }, 2500);
  };

  useEffect(() => {
    timeoutRef.current = setTimeout(() => {
      setIsControlVisible(false);
    }, 2500);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setPageNumber(1);
  }

  const changePage = (offset: number) => {
    setPageNumber((prev) => Math.min(Math.max(1, prev + offset), numPages || 1));
  };

  if (isLoadingFile) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center text-emerald-400">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  if (fileBlob) {
    return (
      <div className="flex flex-col items-center h-full w-full relative bg-bg-prompt">
        {!!numPages && (numPages > 1) && (
          <div
            role="toolbar"
            tabIndex={0}
            className={`absolute bottom-6 z-10 flex items-center gap-4 bg-surface-active backdrop-blur-md px-4 py-2 rounded-full border border-border-subtle transition-all duration-500 ease-in-out ${
              isControlVisible ? "opacity-100 translate-y-0": "opacity-0 translate-y-2 pointer-events-none"
            }`}
            onMouseEnter={() => {
              if (timeoutRef.current) clearTimeout(timeoutRef.current);
              setIsControlVisible(true);
            }}
            onMouseLeave={resetTimer}
          >
            <button
              onClick={() => changePage(-1)}
              disabled={pageNumber <= 1}
              className="p-1.5 hover:bg-surface-hover rounded-full disabled:opacity-30 disabled:hover:bg-transparent transition-all cursor-pointer text-text"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <span className="text-sm font-medium text-text/90 min-w-22.5 text-center">Page {pageNumber} of {numPages}</span>

            <button
              onClick={() => changePage(1)}
              disabled={pageNumber >= numPages}
              className="p-1.5 hover:bg-surface-hover rounded-full disabled:opacity-30 disabled:hover:bg-transparent transition-all cursor-pointer text-text"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}

        <div
          className="flex-1 w-full overflow-y-auto custom-scrollbar p-6 flex justify-center"
          onScroll={resetTimer}
        >
          <Document
            file={fileBlob}
            onLoadSuccess={onDocumentLoadSuccess}
            loading={
              <div className="flex items-center justify-center p-10 text-emerald-400 mt-10">
                <Loader2 className="w-8 h-8 animate-spin" />
              </div>
            }
            error={
              <div className="p-10 text-text-muted text-center mt-10">
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
    <div className="w-full h-full flex flex-col items-center justify-center text-text-muted">
            Failed to fetch the docuemnt.
    </div>
  );
}

export default PdfPreview;
