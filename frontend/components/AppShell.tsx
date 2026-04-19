import Link from "next/link";
import Image from "next/image";

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
            <Image src="/protosenselogo.png" alt="ProtoSense" width={96} height={96} className="h-16 w-16" />
            <span className="text-base font-semibold text-[#111112]">ProtoSense</span>
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
