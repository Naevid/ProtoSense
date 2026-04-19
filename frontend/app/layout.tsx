import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Protocol Feasibility Copilot",
  description: "Evidence-backed protocol feasibility and operational complexity assessment."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
