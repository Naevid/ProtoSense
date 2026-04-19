import Link from "next/link";

type AppShellProps = {
  children: React.ReactNode;
  active?: "home" | "upload" | "dashboard";
  title?: string;
  eyebrow?: string;
  actions?: React.ReactNode;
};

export function AppShell({ children, active = "home", title, eyebrow, actions }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#fbfcfb] text-[#111112]">
      <header className="sticky top-0 z-30 border-b border-[#e8ece9] bg-white/95 backdrop-blur">
        <div className="mx-auto flex min-h-20 max-w-7xl items-center gap-6 px-4 lg:px-6">
          <Link href="/" className="flex shrink-0 items-center gap-3">
            <span className="relative grid h-9 w-9 place-items-center overflow-hidden rounded-md bg-[#111112] text-sm font-bold text-white">
              <span className="absolute inset-0 opacity-50" style={{ background: "linear-gradient(48deg, #CDF5FD 0%, #D8FEF3 50%, #E8FED7 100%)" }} />
              <span className="relative text-[#111112]">PF</span>
            </span>
            <span className="text-base font-semibold text-[#111112]">ProtocolRisk</span>
          </Link>

          <div className="flex-1" />

          <div className="ml-auto flex items-center gap-3">
            {actions}
            <Link href="/upload" className="focus-ring rounded-md bg-[#111112] px-4 py-2 text-sm font-semibold text-white">
              Start analysis
            </Link>
          </div>
        </div>
      </header>

      <main>
        {title ? (
          <section className="border-b border-[#e8ece9] bg-white">
            <div className="mx-auto max-w-7xl px-4 py-10 lg:px-6">
              {eyebrow ? <p className="text-xs font-semibold uppercase text-[#0ba299]">{eyebrow}</p> : null}
              <h1 className="mt-3 max-w-4xl text-4xl font-semibold leading-tight text-[#111112] md:text-5xl">{title}</h1>
            </div>
          </section>
        ) : null}
        <div className="mx-auto max-w-7xl px-4 py-8 lg:px-6">{children}</div>
      </main>
    </div>
  );
}
