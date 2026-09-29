import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import { getAppSettings } from "../lib/api";

import "./globals.css";

export const metadata: Metadata = {
  title: "COP Studio",
  description: "Turn knowledge into a visible, learnable main process.",
};

export default async function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  const appearance = await getAppSettings()
    .then((settings) => settings.appearance)
    .catch(() => ({ theme: "system" as const, density: "comfortable" as const }));
  return (
    <html data-density={appearance.density} data-theme={appearance.theme} lang="zh-CN">
      <body>
        <a className="skip-link" href="#main-content">Skip to content</a>
        <header className="global-header">
          <Link className="brand" href="/">
            <span className="brand-mark" aria-hidden="true">C</span>
            <span>
              <strong>COP Studio</strong>
              <small>Operational knowledge workspace</small>
            </span>
          </Link>
          <div className="global-actions">
            <Link href="/settings">Settings</Link>
            <span className="build-badge">Local · v0.1</span>
          </div>
        </header>
        <div id="main-content" tabIndex={-1}>{children}</div>
      </body>
    </html>
  );
}
