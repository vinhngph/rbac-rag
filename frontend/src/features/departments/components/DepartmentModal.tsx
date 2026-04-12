import { useNavigate } from "react-router";

interface DepartmentModalProps {
    readonly id: string
}

function DepartmentModal({ id }: DepartmentModalProps) {
  const navigate = useNavigate();

  const handleClose = () => { navigate("/"); };


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
            >

            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DepartmentModal;
