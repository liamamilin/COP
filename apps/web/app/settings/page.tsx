import Link from "next/link";

import { AppSettingsForm } from "../../components/app-settings-form";
import { getAppSettings } from "../../lib/api";

export default async function SettingsPage() {
  const settings = await getAppSettings();
  return <main className="app-settings-page"><div className="settings-heading"><Link className="back-link" href="/">← All projects</Link><p className="eyebrow">APPLICATION SETTINGS</p><h1>Quiet defaults,<br />explicit control.</h1><p>Configure the model once, then override only what a particular COP or generation run needs.</p></div><AppSettingsForm initial={settings} /></main>;
}
