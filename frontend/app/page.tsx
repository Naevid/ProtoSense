import Link from "next/link";
import { AppShell } from "../components/AppShell";

export default function HomePage() {
  return (
    <AppShell active="home">
      <section className="grid min-h-[68vh] items-center gap-10 py-8 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <p className="text-sm font-semibold text-[#0ba299]">Protocol feasibility infrastructure</p>
          <h1 className="mt-5 max-w-4xl text-5xl font-semibold leading-tight text-[#111112] md:text-7xl">
            Turn protocol data into launch-ready operational insight
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-[#313235]">
            Connect protocol text to structured feasibility features, traceable evidence, deterministic risk scoring, and redesign simulations before trial startup.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link className="focus-ring rounded-md bg-[#111112] px-5 py-3 text-sm font-semibold text-white" href="/upload">
              Start building
            </Link>
            <a className="focus-ring rounded-md border border-[#dfe5e1] bg-white px-5 py-3 text-sm font-semibold text-[#111112]" href="#network">
              See the network
            </a>
          </div>
        </div>

        <div className="relative">
          <div className="absolute inset-0 translate-x-6 translate-y-6 rounded-lg" style={{ background: "linear-gradient(48deg, #CDF5FD 0%, #D8FEF3 48%, #E8FED7 100%)" }} />
          <div className="relative overflow-hidden rounded-lg border border-[#dfe5e1] bg-white shadow-soft">
            <div className="border-b border-[#e8ece9] px-5 py-4">
              <p className="text-sm font-semibold text-[#111112]">Protocol intelligence graph</p>
            </div>
            <div className="grid gap-3 p-5">
              {[
                ["Protocol PDF", "Uploaded source with page-level text"],
                ["Section map", "Objectives, endpoints, criteria, procedures"],
                ["Feature schema", "Visits, sites, countries, vendors, burden"],
                ["Risk engine", "Weighted startup, enrollment, site, amendment scores"],
                ["Simulation", "Before/after redesign deltas"]
              ].map(([title, detail], index) => (
                <div key={title} className="flex items-center gap-4 rounded-lg border border-[#e8ece9] bg-[#fbfcfb] p-4">
                  <span className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-[#111112] text-sm font-semibold text-white">{index + 1}</span>
                  <span>
                    <span className="block text-sm font-semibold text-[#111112]">{title}</span>
                    <span className="block text-sm text-[#63656a]">{detail}</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 border-y border-[#e8ece9] py-8 md:grid-cols-4" id="network">
        {[
          ["5", "risk dimensions"],
          ["70+", "canonical fields"],
          ["11", "simulator inputs"],
          ["0", "black-box scores"]
        ].map(([value, label]) => (
          <div key={label}>
            <p className="text-5xl font-semibold text-[#111112]">{value}</p>
            <p className="mt-2 text-sm text-[#63656a]">{label}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-5 py-10 lg:grid-cols-3">
        {[
          ["Extract", "Protocol-specific schema captures evidence, confidence, page, section, and extraction method."],
          ["Assess", "Transparent weighted scoring converts features into operational complexity signals."],
          ["Redesign", "Mapped recommendations and what-if simulations show how design changes move risk."]
        ].map(([title, copy]) => (
          <article key={title} className="rounded-lg border border-[#e1e7e3] bg-white p-6 shadow-soft">
            <div className="mb-6 h-2 rounded-md" style={{ background: "linear-gradient(48deg, #CDF5FD 0%, #D8FEF3 50%, #E8FED7 100%)" }} />
            <h2 className="text-2xl font-semibold text-[#111112]">{title}</h2>
            <p className="mt-4 text-sm leading-6 text-[#63656a]">{copy}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-5 rounded-lg bg-[#111112] p-6 text-white lg:grid-cols-[0.8fr_1.2fr]">
        <div>
          <p className="text-sm font-semibold text-[#8ff1dc]">Developer-ready logic</p>
          <h2 className="mt-3 text-3xl font-semibold leading-tight">The score belongs to the product, not the prompt.</h2>
          <p className="mt-4 text-sm leading-6 text-white/70">
            Gemini supports semantic extraction. The feasibility model, recommendations, traceability, and simulator remain explicit product logic.
          </p>
        </div>
        <pre className="overflow-x-auto rounded-lg bg-black/35 p-5 text-sm leading-7 text-[#d8fef3]">
{`risk = weighted_score({
  eligibility_restrictiveness_level: "high",
  biomarker_requirement: true,
  total_visit_count: 13,
  multiple_vendor_dependencies: true
})

return evidence_backed_assessment(risk)`}
        </pre>
      </section>
    </AppShell>
  );
}
