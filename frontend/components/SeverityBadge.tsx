export function SeverityBadge({ label }: { label: "Low" | "Medium" | "High" }) {
  const classes = {
    Low: "border-emerald-200 bg-emerald-50 text-emerald-700",
    Medium: "border-amber-200 bg-amber-50 text-amber-800",
    High: "border-coral/25 bg-red-50 text-coral"
  };
  return <span className={`rounded-md border px-2.5 py-1 text-xs font-semibold ${classes[label]}`}>{label}</span>;
}
