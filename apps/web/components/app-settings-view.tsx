import Link from "next/link";

import type { AppSettings } from "../lib/api";
import { AppSettingsForm } from "./app-settings-form";
import styles from "./app-settings.module.css";

/** Layout only: app settings transport and editable values stay in the form. */
export function AppSettingsView({ initial }: { initial: AppSettings }) {
  return <main className={styles.page}>
    <header className={styles.heading}>
      <Link className={styles.back} href="/">← All projects</Link>
      <h1>Settings</h1>
      <p>Model connection, generation defaults, and appearance.</p>
    </header>
    <div className={styles.layout}>
      <nav className={styles.navigation} aria-label="Settings sections">
        <a href="#settings-provider">Model provider</a>
        <a href="#settings-generation">Generation</a>
        <a href="#settings-appearance">Appearance</a>
      </nav>
      <AppSettingsForm initial={initial} />
    </div>
  </main>;
}
