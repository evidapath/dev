#!/bin/sh
# Install the secret-scan pre-commit hook into this clone's .git/hooks (git hooks aren't versioned).
ROOT=$(git rev-parse --show-toplevel) && cp "$ROOT/scripts/hooks/pre-commit" "$ROOT/.git/hooks/pre-commit" && chmod +x "$ROOT/.git/hooks/pre-commit" && echo "pre-commit hook installed"
