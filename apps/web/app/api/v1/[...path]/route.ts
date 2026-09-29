import { type NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const BODY_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

function upstreamBaseUrl(): string {
  const configured = process.env.INTERNAL_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL;
  // A relative public base is for the browser-facing proxy itself. It is not a
  // valid target for fetch, so local development falls back to the host API.
  return configured?.startsWith("http") ? configured : "http://localhost:8000/api/v1";
}

async function proxy(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const base = upstreamBaseUrl().replace(/\/$/, "");
  const upstreamUrl = `${base}/${path.map((segment) => encodeURIComponent(segment)).join("/")}${request.nextUrl.search}`;
  const headers = new Headers(request.headers);
  headers.delete("content-length");
  headers.delete("connection");
  headers.delete("host");

  try {
    const response = await fetch(upstreamUrl, {
      method: request.method,
      headers,
      body: BODY_METHODS.has(request.method) ? await request.arrayBuffer() : undefined,
      cache: "no-store",
      redirect: "manual",
    });
    const responseHeaders = new Headers(response.headers);
    // The runtime may transparently decompress an upstream response. Let the
    // Next response calculate framing and encoding for the streamed body.
    responseHeaders.delete("content-length");
    responseHeaders.delete("content-encoding");
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch {
    return Response.json(
      { detail: "COP Studio API is unavailable. Check the API service and try again." },
      { status: 502 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
