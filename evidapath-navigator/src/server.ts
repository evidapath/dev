import "./lib/error-capture";

import { consumeLastCapturedError } from "./lib/error-capture";
import { renderErrorPage } from "./lib/error-page";

type ServerEntry = {
  fetch: (request: Request, env: unknown, ctx: unknown) => Promise<Response> | Response;
};

let serverEntryPromise: Promise<ServerEntry> | undefined;

async function getServerEntry(): Promise<ServerEntry> {
  if (!serverEntryPromise) {
    serverEntryPromise = import("@tanstack/react-start/server-entry").then(
      (m) => (m.default ?? m) as ServerEntry,
    );
  }
  return serverEntryPromise;
}

// h3 swallows in-handler throws into a normal 500 Response with body
// {"unhandled":true,"message":"HTTPError"} — try/catch alone never fires for those.
async function normalizeCatastrophicSsrResponse(response: Response): Promise<Response> {
  if (response.status < 500) return response;
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) return response;

  const body = await response.clone().text();
  if (!isH3SwallowedErrorBody(body)) return response;

  console.error(consumeLastCapturedError() ?? new Error(`h3 swallowed SSR error: ${body}`));
  return new Response(renderErrorPage(), {
    status: 500,
    headers: { "content-type": "text/html; charset=utf-8" },
  });
}

function isH3SwallowedErrorBody(body: string): boolean {
  try {
    const payload = JSON.parse(body) as { unhandled?: unknown; message?: unknown };
    return payload.unhandled === true && payload.message === "HTTPError";
  } catch {
    return false;
  }
}

// TanStack Start answers page requests whose Accept header names neither text/html nor */*
// (e.g. an AI tool asking for text/markdown) with a 500 "Only HTML requests are supported
// here". Serve those clients the HTML page instead. Server functions keep their own header.
function acceptHtml(request: Request): Request {
  if (request.method !== "GET" && request.method !== "HEAD") return request;
  if (new URL(request.url).pathname.startsWith("/_serverFn/")) return request;
  const accept = request.headers.get("Accept");
  if (!accept || /text\/html|\*\/\*/.test(accept)) return request;
  const headers = new Headers(request.headers);
  headers.set("Accept", `text/html, ${accept}`);
  return new Request(request, { headers });
}

// The staging copy (*.workers.dev) must not compete with evidapath.com in search results.
// Plus baseline security headers on every response the worker builds. No X-Frame-Options or
// frame-ancestors: the site is previewed inside other tools (AI Studio). HSTS only on the
// real domain, without includeSubDomains, so other subdomains aren't forced onto HTTPS.
function finalHeaders(request: Request, response: Response): Response {
  const host = new URL(request.url).hostname;
  const out = new Response(response.body, response);
  out.headers.set("X-Content-Type-Options", "nosniff");
  out.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  out.headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()");
  if (host === "evidapath.com") out.headers.set("Strict-Transport-Security", "max-age=31536000");
  if (host.endsWith(".workers.dev")) out.headers.set("X-Robots-Tag", "noindex, nofollow");
  return out;
}

export default {
  async fetch(request: Request, env: unknown, ctx: unknown) {
    try {
      const handler = await getServerEntry();
      const req = acceptHtml(request);
      const response = await handler.fetch(req, env, ctx);
      return finalHeaders(req, await normalizeCatastrophicSsrResponse(response));
    } catch (error) {
      console.error(error);
      return new Response(renderErrorPage(), {
        status: 500,
        headers: { "content-type": "text/html; charset=utf-8" },
      });
    }
  },
};
