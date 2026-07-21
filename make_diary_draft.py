#!/usr/bin/env python3
"""Nightly AI-diary draft: pull the last 24h of Open Brain thoughts into a
wins/losses post skeleton in drafts/. Never publishes anything by itself —
review, edit, move into posts/, and run build.py to go live."""
import datetime
import os
import pathlib

import psycopg
from psycopg.rows import dict_row

DB = os.environ["DATABASE_URL"]
DRAFTS = pathlib.Path("/opt/ofone-blog/drafts")

today = datetime.date.today()
out = DRAFTS / f"{today.isoformat()}-diary.md"
if out.exists():
    raise SystemExit(f"{out} already exists, not overwriting")

with psycopg.connect(DB, row_factory=dict_row) as conn, conn.cursor() as cur:
    cur.execute(
        """SELECT content, metadata, created_at FROM thoughts
           WHERE GREATEST(created_at, updated_at) > now() - interval '24 hours'
           ORDER BY created_at"""
    )
    rows = cur.fetchall()

lines = [
    f"# AI Diary — {today.strftime('%B %d, %Y')}",
    "",
    "## Wins",
    "",
    "- ",
    "",
    "## Losses",
    "",
    "- ",
    "",
    "## Raw thoughts captured today",
    "",
]
if rows:
    for r in rows:
        meta = r["metadata"] or {}
        tag = f" _({meta.get('project')})_" if meta.get("project") else ""
        lines.append(f"- {r['content']}{tag}")
else:
    lines.append("_(nothing captured in Open Brain today)_")
lines += ["", "<!-- draft generated automatically; edit, move to posts/, run build.py -->", ""]

out.write_text("\n".join(lines))
print(f"wrote {out} ({len(rows)} thoughts)")
