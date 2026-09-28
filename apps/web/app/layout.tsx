import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "COP Studio",
  description: "Turn knowledge into a visible, learnable main process.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>
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
        {children}
      </body>
    </html>
  );
}
