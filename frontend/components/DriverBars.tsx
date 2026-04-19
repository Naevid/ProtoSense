import type { TopDriver } from "../lib/api";

export function DriverBars({ drivers }: { drivers: TopDriver[] }) {
  return (
    <div className="space-y-3">
      {drivers.map((driver) => (
        <div key={driver.feature}>
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className="font-medium text-[#111112]">{driver.feature.replaceAll("_", " ")}</span>
            <span className="text-[#63656a]">{driver.contribution_percent}%</span>
          </div>
          <div className="mt-1 h-2 rounded bg-[#e1e7e3]">
            <div
              className="h-2 rounded"
              style={{ width: `${Math.min(100, driver.contribution_percent)}%`, background: "linear-gradient(48deg, #0ba299 0%, #5fd8a8 100%)" }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
