"use client";

import { FormEvent, useState } from "react";
import { askProtocol, type ChatResponse } from "../lib/api";

type Message = {
  role: "user" | "assistant";
  text: string;
  response?: ChatResponse;
};

const suggestedPrompts = [
  "Why is enrollment risk elevated?",
  "What evidence supports site burden?",
  "How can we reduce participant burden?"
];

export function ChatAssistant({ protocolId }: { protocolId: string }) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Ask about this feasibility assessment. I can explain risk drivers, evidence, and redesign options without creating new risk scores."
    }
  ]);

  async function sendMessage(message: string) {
    const trimmed = message.trim();
    if (!trimmed || busy) return;
    setInput("");
    setBusy(true);
    setMessages((current) => [...current, { role: "user", text: trimmed }]);
    try {
      const response = await askProtocol(protocolId, trimmed);
      setMessages((current) => [...current, { role: "assistant", text: response.answer, response }]);
    } catch (error) {
      const text = error instanceof Error ? error.message : "The assistant could not answer right now.";
      setMessages((current) => [...current, { role: "assistant", text }]);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage(input);
  }

  return (
    <div className="fixed bottom-5 right-5 z-40 flex flex-col items-end gap-3">
      {open ? (
        <section className="flex h-[min(42rem,calc(100vh-2.5rem))] w-[min(26rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-lg border border-[#e1e7e3] bg-white shadow-soft">
          <div className="flex shrink-0 items-start justify-between gap-3 border-b border-[#e1e7e3] bg-[#fbfcfb] p-4">
            <div>
              <p className="text-sm font-semibold text-[#111112]">Feasibility Assistant</p>
              <p className="mt-1 text-xs leading-5 text-[#63656a]">Grounded in assessment evidence and scoring outputs.</p>
            </div>
            <button className="focus-ring rounded-md border border-[#e1e7e3] bg-white px-2 py-1 text-xs" onClick={() => setOpen(false)}>
              Close
            </button>
          </div>

          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
            {messages.map((message, index) => (
              <article
                key={index}
                className={`rounded-lg px-3 py-2 text-sm leading-6 ${
                  message.role === "user" ? "ml-8 bg-[#111112] text-white" : "mr-8 border border-[#e1e7e3] bg-white text-[#313235]"
                }`}
              >
                <p>{message.text}</p>
                {message.response?.cited_evidence?.length ? (
                  <div className="mt-3 space-y-2 border-t border-[#e1e7e3] pt-3">
                    {message.response.cited_evidence.slice(0, 3).map((item, evidenceIndex) => (
                      <div key={`${item.feature}-${evidenceIndex}`} className="text-xs leading-5 text-[#63656a]">
                        <strong className="text-[#111112]">{item.feature.replaceAll("_", " ")}</strong>
                        <span> · page {item.page ?? "n/a"} · {item.method}</span>
                        <p className="mt-1">{item.snippet || "No snippet captured."}</p>
                      </div>
                    ))}
                  </div>
                ) : null}
                {message.response ? (
                  <p className="mt-2 text-[11px] leading-4 text-[#63656a]">
                    Method: {message.response.method}. {message.response.caveat}
                  </p>
                ) : null}
              </article>
            ))}
            {busy ? <p className="text-sm text-[#0ba299]">Thinking through the assessment...</p> : null}
          </div>

          <div className="shrink-0 border-t border-[#e1e7e3] bg-white p-4">
            <div className="mb-3 flex flex-wrap gap-2">
              {suggestedPrompts.map((prompt) => (
                <button
                  key={prompt}
                  className="focus-ring rounded-md border border-[#e1e7e3] px-2 py-1 text-xs text-[#313235]"
                  onClick={() => void sendMessage(prompt)}
                  disabled={busy}
                >
                  {prompt}
                </button>
              ))}
            </div>
            <form className="flex gap-2" onSubmit={onSubmit}>
              <input
                className="focus-ring min-w-0 flex-1 rounded-md border border-[#e1e7e3] px-3 py-2 text-sm"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask about risk drivers..."
              />
              <button className="focus-ring shrink-0 rounded-md bg-[#111112] px-3 py-2 text-sm font-semibold text-white" disabled={busy}>
                Ask
              </button>
            </form>
          </div>
        </section>
      ) : null}

      {!open ? (
        <button className="focus-ring rounded-md bg-[#111112] px-5 py-3 text-sm font-semibold text-white shadow-soft" onClick={() => setOpen(true)}>
          Ask about this assessment
        </button>
      ) : null}
    </div>
  );
}
