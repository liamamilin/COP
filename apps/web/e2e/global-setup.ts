/**
 * Fail fast if the stack the suite needs is not up.
 *
 * Without this the first test fails with an opaque fetch error and the rest pile
 * up behind it. The E2E suite needs a running Worker, because its fixture
 * produces a real candidate through the Harness rather than posting a
 * hand-written artifact, so a missing Worker is a setup problem worth naming
 * clearly.
 */
const API_URL = process.env.E2E_API_URL ?? "http://localhost:8000/api/v1";
const ORIGIN = API_URL.replace(/\/api\/v1$/, "");

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
}
