# Deploying to GHL AI Studio (interim hosting)

GHL AI Studio can only sync with a repo it creates itself, with the app at the repo root
(see help.gohighlevel.com "How to Use Git Sync in AI Studio"). So:

```
evidapath/dev (source of truth)
   └─ scripts/sync-ghl.sh --push ─► sub7an/evidapath-navigator (GHL's repo, private)
                                       └─ GHL auto-pull ─► new PREVIEW in AI Studio
                                                             └─ someone clicks Publish ─► evidapath.com
```

## Each release
1. Commit and push the change to `evidapath/dev`.
2. `scripts/sync-ghl.sh` (dry run: shows what would change), then `scripts/sync-ghl.sh --push`.
3. In GHL, open the project's preview and check: Discover lists universities, sign up / sign in work,
   saving to My Path works, Scholarships loads.
4. Only then click **Publish** in GHL.

## Rules
- **Don't edit the app in GHL** (AI chat, code editor or visual edits). Those edits land only in GHL's repo.
  The script refuses to sync if GHL has commits it hasn't seen; port them into `evidapath-navigator/`, then
  re-run with `ALLOW_OVERWRITE=1`.
- If GHL shows the branch as **diverged**, don't choose **Force push** (that overwrites GitHub with GHL's copy).
- GHL's repo tracks `.env` (publishable Supabase URL/anon key, needed at build time); the script keeps it.
- Server secrets live in GHL → More → Cloud → Secrets: `SANITY_READ_TOKEN` (a **Viewer** token).
  Do **not** set `SANITY_PERSPECTIVE` there, so only published Sanity content is shown, never drafts.
  Project ID and dataset default to `jxwrtsiz` / `staging` in `src/lib/sanity.server.ts`.
