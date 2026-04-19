"use client";

import { useState } from "react";
import type { Evidence } from "../lib/api";

export function EvidenceDrawer({ evidence }: { evidence: Evidence[] }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        className="focus-ring rounded-md border border-line bg-white px-4 py-2 text-sm font-semibold text-ink shadow-soft"
        onClick={() => setOpen(true)}
      >
        View evidence
      </button>
      {open ? (
        <div className="fixed inset-0 z-50 bg-ink/30" onClick={() => setOpen(false)}>
          <aside
            className="ml-auto h-full w-full max-w-xl overflow-y-auto bg-white p-6 shadow-soft"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase text-teal">Traceability</p>
                <h2 className="mt-2 text-2xl font-semibold text-ink">Protocol evidence</h2>
              </div>
              <button className="focus-ring rounded-md border border-line px-3 py-2 text-sm" onClick={() => setOpen(false)}>
                Close
              </button>
            </div>
            <div className="mt-6 space-y-4">
              {evidence.map((item, index) => (
                <article key={`${item.feature}-${index}`} className="rounded-lg border border-line p-4">
                  <div className="flex flex-wrap items-center gap-2 text-xs text-graphite">
                    <span className="font-semibold text-ink">{item.feature.replaceAll("_", " ")}</span>
                    <span>Page {item.page ?? "n/a"}</span>
                    <span>{item.section ?? "Unmapped section"}</span>
                    <span>{Math.round(item.confidence * 100)}% confidence</span>
                    <span>{item.method}</span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-graphite">{item.snippet || "No snippet captured for this inferred feature."}</p>
                </article>
              ))}
            </div>
          </aside>
        </div>
      ) : null}
    </>
  );
}
