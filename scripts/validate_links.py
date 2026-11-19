#!/usr/bin/env python3
"""Validate relative Markdown links without external dependencies."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
errors = []
checked = 0

for document in sorted(ROOT.rglob("*.md")):
    if ".git" in document.parts or "node_modules" in document.parts:
        continue
    text = document.read_text(encoding="utf-8")
    fence = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        fence_match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
            continue
        if fence is not None:
            continue
        for match in LINK_PATTERN.finditer(line):
            target = match.group(1).strip().strip("<>")
            if target.split()[0].startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split()[0].split("#", 1)[0]
            if not target:
                continue
            checked += 1
            resolved = (document.parent / unquote(target)).resolve()
            if not resolved.exists():
                relative = document.relative_to(ROOT)
                errors.append(f"{relative}:{line_number}: missing target {target}")

if errors:
    print("Broken relative Markdown links:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    sys.exit(1)

print(f"Validated {checked} relative Markdown links successfully.")
