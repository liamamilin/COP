export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function upstreamBaseUrl(): string {
  const configured = process.env.INTERNAL_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL;
  return configured?.startsWith("http") ? configured : "http://localhost:8000/api/v1";
}

/** The API's own origin: `/health` is not a versioned path. */
function upstreamOrigin(): string {
  return upstreamBaseUrl().replace(/\/api\/v1$/, "").replace(/\/$/, "");
}

export async function GET(): Promise<Response> {
  const base = upstreamOrigin();
  try {
    const response = await fetch(`${base}/health`, {
      headers: { accept: "application/json" },
      cache: "no-store",
    });
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: { "content-type": response.headers.get("content-type") ?? "application/json" },
    });
  } catch {
    return Response.json({ detail: "COP Studio API is unavailable." }, { status: 502 });
  }
}
