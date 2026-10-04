#!/bin/bash
# SessionStart hook for Claude Code cloud sessions: make sure the CV build
# (cv/build_cvs.py -> HTML + PDF) can run. It only needs python3 (stdlib) and
# a Chromium binary for --print-to-pdf.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

command -v python3 >/dev/null || { echo "session-start: python3 not found" >&2; exit 1; }

chrome=""
for c in "${CHROME:-}" /opt/pw-browsers/chromium-*/chrome-linux/chrome \
         "$(command -v chromium || true)" "$(command -v google-chrome || true)"; do
  if [ -n "$c" ] && [ -x "$c" ]; then chrome="$c"; break; fi
done
[ -n "$chrome" ] || { echo "session-start: no Chromium found for PDF export" >&2; exit 1; }

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export CHROME=\"$chrome\"" >> "$CLAUDE_ENV_FILE"
fi
echo "session-start: python3 $(python3 -c 'import platform;print(platform.python_version())'), CHROME=$chrome" >&2
