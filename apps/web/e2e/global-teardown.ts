import { rmSync } from "node:fs";

import { PROVIDER_SNAPSHOT, readProviderSnapshot } from "./provider-guard";

import { API_URL } from "./endpoints";

/**
 * Put the developer's provider settings back.
 *
 * `globalSetup` switches the app to the Mock Provider for the duration of the
 * run, because leaving that to individual specs made correctness depend on spec
 * ordering. The flip side is that the override is still sitting there
 * afterwards, pointed at whichever endpoint the developer normally uses -- so it
 * has to be undone, or the next `make up` quietly keeps generating COPs through a
 * paid API that the person running the tests never asked for.
 *
 * A failure here is warned about rather than raised: teardown runs after the
 * results are already in, and a provider-restore problem must not turn a green
 * suite red.
 */
export default async function globalTeardown(): Promise<void> {
  const snapshot = readProviderSnapshot();
  try {
    if (snapshot) {
      const response = await fetch(`${API_URL}/settings`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: snapshot.provider }),
      });
      if (!response.ok) {
        console.warn(
          `E2E teardown could not restore provider settings: HTTP ${response.status}`,
        );
        return;
      }
      // Read the settings back and confirm the developer's endpoint is really
      // back. A restore that silently half-succeeds is worse than one that
      // reports itself: the Settings screen would claim a live provider is
      // configured while generation quietly went somewhere else.
      const now = await fetch(`${API_URL}/settings`).then((r) => r.json());
      const expected = snapshot.provider;
      const current = now.provider ?? {};
      if (current.type !== expected.type || current.base_url !== expected.base_url) {
        console.warn(
          "E2E teardown did not fully restore the provider. " +
            `Expected type=${expected.type} base_url=${expected.base_url}, ` +
            `found type=${current.type} base_url=${current.base_url}. ` +
            "Re-select your provider in Settings before generating.",
        );
      }
    }
  } catch (cause) {
    console.warn(`E2E teardown could not restore provider settings: ${String(cause)}`);
  } finally {
    rmSync(PROVIDER_SNAPSHOT, { force: true });
  }
}
