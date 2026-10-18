/**
 * Where the browser tests point.
 *
 * The API defaults to the same-origin proxy under BASE_URL rather than to a
 * fixed port, for two reasons.
 *
 * The browser reaches the API through that proxy, so a test that calls the
 * backend directly is exercising a path the product never uses.
 *
 * And a fixed port is actively wrong on this machine: 8000 is occupied by an
 * unrelated service, so `localhost:8000/api/v1/settings` returns that other
 * application's JSON. The read succeeds, the shape is wrong, and the failure
 * surfaces far from its cause.
 */
export const BASE_URL = process.env.E2E_BASE_URL ?? "http://localhost:3000";

export const API_URL = process.env.E2E_API_URL ?? `${BASE_URL}/api/v1`;
