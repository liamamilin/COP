import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import SettingsPage from "../app/settings/page";
import { AppSettingsView } from "../components/app-settings-view";
import { type AppSettings, getAppSettings } from "../lib/api";
import fixture from "./fixtures/app-settings.json";

vi.mock("../lib/api", async (original) => ({
  ...await original<typeof import("../lib/api")>(), getAppSettings: vi.fn(),
}));
const initial = fixture as AppSettings;
function render(settings = initial) {
  return renderToStaticMarkup(createElement(AppSettingsView, { initial: settings }));
}

describe("app settings presentation", () => {
  it("uses a functional page heading instead of a marketing-sized hero", async () => {
    vi.mocked(getAppSettings).mockResolvedValue(initial);
    const html = renderToStaticMarkup(await SettingsPage());
    expect(html).toContain("<h1>Settings</h1>");
    expect(html).not.toContain("Quiet defaults");
    expect(html).not.toContain("explicit control");
    expect(html).not.toContain('class="app-settings-page"');
    expect(html).toContain('href="/"');
  });

  it("provides section navigation with matching stable destinations", () => {
    const html = render();
    expect(html).toContain('aria-label="Settings sections"');
    for (const section of ["provider", "generation", "appearance"]) {
      expect(html).toContain(`href="#settings-${section}"`);
      expect(html).toContain(`id="settings-${section}"`);
      expect(html).toContain(`aria-labelledby="settings-${section}-heading"`);
    }
  });

  it("keeps all editable settings and unchanged bounds inside one explicit-save form", () => {
    const html = render();
    for (const name of ["provider_type", "base_url", "api_key", "model", "mock_scenario",
      "timeout", "max_retries", "language", "generation_depth", "learner_level",
      "detail_density", "practice_mode", "evidence_density", "theme", "density"]) {
      expect(html).toContain(`name="${name}"`);
    }
    expect(html.match(/<form/g)).toHaveLength(1);
    expect(html.match(/type="submit"/g)).toHaveLength(1);
    expect(html).toContain('min="5" max="600"');
    expect(html).toContain('min="0" max="5"');
    expect(html).toContain("Save settings");
  });

  it("collapses advanced options without unmounting their values", () => {
    const html = render();
    expect(html.match(/<details/g)).toHaveLength(2);
    expect(html).not.toContain(" open=");
    expect(html).toContain("Advanced connection settings");
    expect(html).toContain("More generation options");
    expect(html).toContain('value="90"');
    expect(html).toContain('value="2"');
    expect(html).toContain('value="all" selected=""');
    expect(html).toContain('value="high" selected=""');
    expect(html).toContain("run → project → app → built-in default");
  });

  it("labels each visible field explicitly, separate from hints and masked key state", () => {
    const html = render();
    const labels = [...html.matchAll(/<label for="([^"]+)">([^<]+)<\/label>/g)];
    expect(labels.length).toBe(14);
    for (const [, id] of labels) expect(html).toContain(`id="${id}"`);
    expect(labels.map(([, , label]) => label)).toContain("API key");
    expect(html).toContain('type="password"');
    expect(html).not.toContain('value="••••demo"');
    expect(html).toContain("Leave blank to keep it.");
    expect(html).toContain("Key stored");
    expect(html).not.toContain("connection succeeded");
  });

  it("shows only mock-specific connection fields in mock mode", () => {
    const html = render({ ...initial, provider: { ...initial.provider, type: "mock" } });
    expect(html).toContain("Mock scenario");
    expect(html).toContain("Mock mode");
    expect(html).not.toContain('type="password"');
    expect(html).not.toContain("Load available models");
    expect(html).toContain("Test connection");
  });

  it("does not mutate settings or pretend to save, test or connect during rendering", () => {
    const before = JSON.stringify(initial);
    const html = render();
    expect(JSON.stringify(initial)).toBe(before);
    expect(html).toContain("Changes apply when you save.");
    expect(html).not.toContain("Settings saved.");
    expect(html).not.toContain("connection succeeded");
  });
});
