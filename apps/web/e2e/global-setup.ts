import { forceMockProvider } from "./provider-guard";

import { BASE_URL } from "./endpoints";

/**
 * Probe the API through Next, not through a guessed port.
 *
 * `apps/web/app/health/route.ts` forwards the backend's real status, so a 502
 * here means the API is down while Next is fine. Deriving the origin from
 * BASE_URL keeps the check working whichever port the backend is on.
 */
const ORIGIN = BASE_URL.replace(/\/$/, "");

/**
 * Fail fast if the stack the suite needs is not up.
 *
 * Without this the first test fails with an opaque fetch error and the rest pile
 * up behind it. The E2E suite needs a running Worker, because its fixture
 * produces a real candidate through the Harness rather than posting a
 * hand-written artifact, so a missing Worker is a setup problem worth naming
 * clearly.
 */
export default async function globalSetup(): Promise<void> {
  try {
    const health = await fetch(`${ORIGIN}/health`);
    if (!health.ok) throw new Error(`health returned HTTP ${health.status}`);
  } catch (cause) {
    throw new Error(
      `The COP Studio API is not reachable at ${ORIGIN} (${String(cause)}). ` +
        "Start the stack first: make up, or POSTGRES_HOST_PORT=55432 make up. " +
        "A Worker must be running, since the E2E fixture generates a real candidate.",
    );
  }

  // Spec `19` requires the mock to carry the acceptance path, and CI has no
  // business reaching a paid model endpoint at all.
  await forceMockProvider();
}
