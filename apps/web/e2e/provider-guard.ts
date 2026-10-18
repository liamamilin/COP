import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

/**
 * Making the Mock Provider the state the whole E2E run runs against.
 *
 * The provider is *global* application state, and it used to be switched on and
 * off by an individual spec's cleanup. That made the suite's correctness depend
 * on spec ordering: the spec that touched the provider restored the developer's
 * real OpenAI-compatible endpoint, and every spec that ran afterwards made live
 * model calls, produced no candidate, and failed in a way that looked like a
 * product regression rather than a test-harness one.
 *
 * So the override is a suite-level precondition with a matching teardown, and no
 * spec is allowed to restore it on its own.
 *
 * The snapshot path is resolved from the working directory rather than from
 * `import.meta`, because the package is CommonJS and `import.meta` is not
 * available in the Playwright config's module loader. Playwright runs with the
 * config's directory as the working directory, so `e2e/` here is stable.
 */

export const PROVIDER_SNAPSHOT = join(process.cwd(), "e2e", ".provider-snapshot.json");

export interface ProviderSettings {
  type: string;
  base_url: string;
  model: string;
  timeout: number;
  max_retries: number;
  mock_scenario: string;
}

export interface ProviderSnapshot {
  provider: ProviderSettings;
}

import { API_URL } from "./endpoints";

/**
 * Record the current provider, then select the Mock Provider.
 *
 * A no-op when the mock is already selected, so a second run in a row does not
 * overwrite the snapshot with the mock and then "restore" the mock forever.
 */
export async function forceMockProvider(): Promise<void> {
  const current = await fetch(`${API_URL}/settings`).then((response) => {
    if (!response.ok) {
      throw new Error(`could not read app settings: HTTP ${response.status}`);
    }
    return response.json() as Promise<{ provider: ProviderSettings }>;
  });

  if (current.provider.type === "mock" && current.provider.mock_scenario === "success") {
    return;
  }

  mkdirSync(join(process.cwd(), "e2e"), { recursive: true });
  writeFileSync(PROVIDER_SNAPSHOT, JSON.stringify({ provider: current.provider }), "utf8");

  const applied = await fetch(`${API_URL}/settings`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider: { type: "mock", mock_scenario: "success" } }),
  });
  if (!applied.ok) {
    throw new Error(`could not select the Mock Provider: HTTP ${applied.status}`);
  }
}

export function readProviderSnapshot(): ProviderSnapshot | null {
  try {
    return JSON.parse(readFileSync(PROVIDER_SNAPSHOT, "utf8")) as ProviderSnapshot;
  } catch {
    return null;
  }
}
