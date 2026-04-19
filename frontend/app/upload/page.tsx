"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { AppShell } from "../../components/AppShell";
import { runPipeline, uploadProtocol } from "../../lib/api";

const steps = ["Upload PDF", "Map sections", "Extract features", "Score feasibility"];

export default function UploadPage() {
  const router = useRouter();
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleFile(file: File) {
    setBusy(true);
    setError(null);
    try {
      setActiveStep(0);
      const uploaded = await uploadProtocol(file);
      setActiveStep(1);
      await runPipeline(uploaded.protocol_id);
      setActiveStep(3);
      router.push(`/protocols/${uploaded.protocol_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to process protocol");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell active="upload" eyebrow="Protocol Intake" title="Connect a protocol to the feasibility network">
      <div className="grid gap-8 lg:grid-cols-[0.85fr_1.15fr]">
        <section>
          <p className="text-sm font-semibold text-[#0ba299]">From document to structured signals</p>
          <h2 className="mt-4 text-3xl font-semibold leading-tight text-[#111112]">Upload once. Inspect every downstream assumption.</h2>
          <p className="mt-4 text-sm leading-6 text-[#63656a]">
            The pipeline preserves page-level source text, detects clinical sections, extracts canonical feasibility features, and calculates deterministic risk dimensions.
          </p>
          <div className="mt-8 space-y-3">
            {steps.map((step, index) => (
              <div key={step} className="flex items-center gap-4 rounded-lg border border-[#e1e7e3] bg-white p-4 shadow-soft">
                <span className={`h-3 w-3 rounded-full ${index <= activeStep ? "bg-[#0ba299]" : "bg-[#dfe5e1]"}`} />
                <span className="text-sm font-medium text-[#313235]">{step}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="relative">
          <div className="absolute inset-0 translate-x-5 translate-y-5 rounded-lg" style={{ background: "linear-gradient(48deg, #CDF5FD 0%, #D8FEF3 48%, #E8FED7 100%)" }} />
          <div className="relative rounded-lg border border-[#dfe5e1] bg-white p-6 shadow-soft">
            <label className="focus-within:ring-4 focus-within:ring-[#0ba299]/20 block rounded-lg border border-dashed border-[#0ba299] bg-[#f7fffb] p-10 text-center">
              <span className="block text-2xl font-semibold text-[#111112]">Add a protocol PDF</span>
              <span className="mt-3 block text-sm leading-6 text-[#63656a]">PDF and text files are supported for the MVP parser.</span>
              <input
                className="sr-only"
                type="file"
                accept=".pdf,.txt,application/pdf,text/plain"
                disabled={busy}
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) void handleFile(file);
                }}
              />
            </label>

            <div className="mt-6 overflow-hidden rounded-lg border border-[#e1e7e3]">
              <div className="grid grid-cols-3 bg-[#fbfcfb] px-4 py-3 text-xs font-semibold text-[#63656a]">
                <span>Output</span>
                <span>Status</span>
                <span>Method</span>
              </div>
              {[
                ["Section map", "Rule-first + Gemini fill"],
                ["Feature schema", "Validated Pydantic model"],
                ["Risk scores", "Weighted backend config"],
                ["Recommendations", "Mapped driver logic"]
              ].map(([item, method]) => (
                <div key={item} className="grid grid-cols-3 border-t border-[#e1e7e3] px-4 py-4 text-sm">
                  <span className="font-semibold text-[#111112]">{item}</span>
                  <span className="text-[#63656a]">{busy ? "Running" : "Ready"}</span>
                  <span className="text-[#63656a]">{method}</span>
                </div>
              ))}
            </div>

            {busy ? <p className="mt-5 text-sm font-medium text-[#0ba299]">Analyzing protocol structure...</p> : null}
            {error ? <p className="mt-5 text-sm text-coral">{error}</p> : null}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
