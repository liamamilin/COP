import { AppSettingsView } from "../../components/app-settings-view";
import { getAppSettings } from "../../lib/api";

export default async function SettingsPage() {
  const settings = await getAppSettings();
  return <AppSettingsView initial={settings} />;
}
