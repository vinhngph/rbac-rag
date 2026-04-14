interface PermissionBadgeProps {
    readonly label: string
    readonly active: boolean
    readonly disabled: boolean
    readonly onClick: () => void
}

function PermissionBadge({ label, active, disabled, onClick }: PermissionBadgeProps) {
  const badgeStyle = () => {
    if (active ) {
      if (label === "edit") {
        return "bg-violet-500/20 border-violet-500/40 text-violet-300";
      } else {
        return "bg-emerald-500/20 border-emerald-500/40 text-emerald-300";
      }
    } else {
      return "bg-transparent border-white/10 text-text/25 hover:border-white/25 hover:text-text/50";
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={disabled ? "Member must have at least one permission": undefined}
      className={`px-2 py-0.5 rounded-md text-[11px] font-medium tracking-wide border transition-all cursor-pointer disabled:cursor-not-allowed ${badgeStyle()}`}
    >
      {label}
    </button>
  );
}

export default PermissionBadge;
