#!/usr/bin/env bash
# Copy evidapath-navigator/ from this monorepo (evidapath/dev) into the repo that
# GHL AI Studio is connected to (sub7an/evidapath-navigator, app at the root).
#
#   scripts/sync-ghl.sh          dry run: show what would change, push nothing
#   scripts/sync-ghl.sh --push   commit and push to the GHL repo
#
# The monorepo is the source of truth. The script only ever adds a commit on top
# of the GHL repo's main (never force-pushes). If GHL AI Studio has made commits
# since the last sync, it stops: port those into the monorepo first, so they are
# not silently overwritten.
#
# Note: GHL has "Pull from GitHub" switched on, so a push replaces the files in
# the GHL project. Check whether GHL then republishes evidapath.com on its own.
set -euo pipefail

GHL_REPO="${GHL_REPO:-https://github.com/sub7an/evidapath-navigator.git}"
PREFIX="evidapath-navigator"
MARK="Sync from evidapath/dev@"

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

if [[ -n "$(git status --porcelain -- "$PREFIX")" ]]; then
  echo "Uncommitted changes in $PREFIX/. Commit (and push to evidapath/dev) first." >&2
  exit 1
fi
SHA="$(git rev-parse --short HEAD)"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
git clone -q "$GHL_REPO" "$WORK/ghl"
cd "$WORK/ghl"

# Commits made in GHL since our last sync (on the first sync: everything after "Initial sync").
LAST="$(git log --grep="^$MARK" --format=%H -1 || true)"
if [[ -n "$LAST" ]]; then RANGE="$LAST..HEAD"; else RANGE="$(git rev-list --max-parents=0 HEAD)..HEAD"; fi
FOREIGN="$(git log --format='%h %an: %s' "$RANGE" --invert-grep --grep="^$MARK")"
if [[ -n "$FOREIGN" && "${ALLOW_OVERWRITE:-}" != "1" ]]; then
  echo "GHL repo has commits not yet in the monorepo:" >&2
  echo "$FOREIGN" >&2
  echo "Port them into $PREFIX/ first (see docs/ghl-sync.md), then re-run." >&2
  echo "If they are already ported, re-run with ALLOW_OVERWRITE=1." >&2
  exit 2
fi

# Replace the GHL repo's tree with the committed monorepo folder (tracked files only,
# so .env.local, .dev.vars and other ignored files never leave this machine).
git rm -rq --ignore-unmatch . >/dev/null
git -C "$ROOT" archive HEAD "$PREFIX" | tar -x --strip-components=1 -C .
# .env (publishable VITE_ Supabase URL/anon key) is tracked only in the GHL repo; the
# browser bundle needs it at build time, so keep GHL's copy.
git checkout HEAD -- .env 2>/dev/null || true
git add -A

if git diff --cached --quiet; then
  echo "GHL repo already matches evidapath/dev@$SHA. Nothing to do."
  exit 0
fi
git diff --cached --stat | tail -25

if [[ "${1:-}" != "--push" ]]; then
  echo
  echo "Dry run only. Re-run with --push to commit and push to $GHL_REPO."
  exit 0
fi
git commit -q -m "$MARK$SHA"
git push -q origin HEAD:main
echo "Pushed $MARK$SHA to $GHL_REPO"
