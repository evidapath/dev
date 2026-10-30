# Cloudflare deploy (staging now, evidapath.com later)

**Live staging (deployed 2026-10-30): https://evidapath-staging.evidapath.workers.dev** — workers.dev subdomain `evidapath`;
verified: all pages 200, live Sanity data (same as dev), sign-in + saved universities work, no console errors.

The app already builds as a Cloudflare Worker (`dist/server/server.js` + static files in `dist/client`).
Config: `deploy/cloudflare/wrangler.jsonc` — kept outside `evidapath-navigator/` so the GHL sync never ships it.
Tested 2026-10-30 in the local Workers runtime (`wrangler dev`): every page loads, live Sanity data shows,
identical to the dev server, no console errors.

## One-time setup (Subhan)
1. Log in to Cloudflare (opens a browser):
   `cd ~/Desktop/evidapath/deploy/cloudflare && npx wrangler@4 login`
2. Build and deploy the first time (this creates the Worker `evidapath-staging`):
   `(cd ../../evidapath-navigator && bun run build) && npx wrangler@4 deploy`
   It prints the URL, `https://evidapath-staging.evidapath.workers.dev`.
3. Add the Sanity **Viewer** token as a secret (paste it when asked; it is never stored in git):
   `npx wrangler@4 secret put SANITY_READ_TOKEN`
   Do **not** add `SANITY_PERSPECTIVE` — drafts must stay hidden.
4. Supabase → Authentication → URL Configuration → Redirect URLs: add
   `https://evidapath-staging.evidapath.workers.dev/**` (otherwise sign-in bounces to evidapath.com).

## Every later deploy
`cd ~/Desktop/evidapath/evidapath-navigator && bun run build && cd ../deploy/cloudflare && npx wrangler@4 deploy`

## Moving evidapath.com (after the Squarespace lock, ~2026-12-28)
1. Move DNS for evidapath.com to Cloudflare (or transfer the domain).
2. Workers → `evidapath-staging` (or a new `evidapath` worker) → Settings → Domains & Routes → add `evidapath.com`.
3. Add `https://evidapath.com/**` to Supabase redirect URLs (already there today).
4. GHL stays the CRM — the app keeps posting to GHL from any host.

## Notes
- `VITE_SITE_URL` (in `.env`) only sets SEO canonical links; leaving it as evidapath.com on staging is correct
  (search engines treat the staging copy as a duplicate of the real site).
- The Viewer token can be the same one GHL uses. Never use a write token here.
