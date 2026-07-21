#!/usr/bin/env python3
"""Daily coding-journal publisher: pull last 24h of Open Brain thoughts,
synthesize into a real wins/losses post via Zen, and publish only if there's
something substantive to say. Runs entirely on the VM (systemd timer).

Unlike make_diary_draft.py (which only ever writes an editable draft), this
writes directly to posts/, rebuilds the site, and pushes to git. No human
review gate -- if you want one back, revert to make_diary_draft.py.
"""
import datetime
import json
import os
import pathlib
import subprocess
import sys
import urllib.request

import psycopg
from psycopg.rows import dict_row

REPO_ROOT = pathlib.Path("/opt/ofone-blog")
POSTS_DIR = REPO_ROOT / "posts"
ZEN_URL = "https://opencode.ai/zen/v1/chat/completions"
ZEN_MODEL = "grok-4.5"
DB = os.environ["DATABASE_URL"]

today = datetime.date.today()
post_path = POSTS_DIR / f"{today.isoformat()}-journal.md"


def fetch_thoughts():
    with psycopg.connect(DB, row_factory=dict_row) as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT content, metadata, created_at FROM thoughts
               WHERE GREATEST(created_at, updated_at) > now() - interval '24 hours'
               ORDER BY created_at"""
        )
        return cur.fetchall()


def synthesize_post(rows, api_key):
    bullets = []
    for r in rows:
        meta = r["metadata"] or {}
        tag = f" ({meta.get('project')})" if meta.get("project") else ""
        bullets.append(f"- {r['content']}{tag}")
    raw = "\n".join(bullets)

    prompt = f"""You are writing a daily developer journal / blog post for ofOne
(Andrew's personal dev brand). Below are raw thought-log entries captured
automatically over the last 24 hours. Turn them into a genuine, readable
diary-style blog post -- NOT a bullet dump of the raw log. Write real prose
under "## Wins" and "## Losses" sections (a short paragraph or a few tight
bullets each, whichever fits the material), skip anything that's clearly just
noise/housekeeping with no real story, and keep the voice first-person casual
technical (like a builder writing to future-self / other builders), not
corporate. If there is truly nothing worth a Wins or Losses entry, write
"Nothing notable today." under that heading rather than padding it out.

Output ONLY the markdown body (no frontmatter, no title heading -- those are
added separately). Start directly with "## Wins".

Raw log:
{raw}
"""

    req = urllib.request.Request(
        ZEN_URL,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "curl/8.5.0",
        },
        data=json.dumps({
            "model": ZEN_MODEL,
            "max_tokens": 900,
            "messages": [{"role": "user", "content": prompt}],
        }).encode(),
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def main():
    if post_path.exists():
        print(f"{post_path} already exists, not overwriting")
        return 0

    rows = fetch_thoughts()
    if not rows:
        print("Nothing captured in Open Brain today -- skipping post")
        return 0

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set, cannot synthesize post", file=sys.stderr)
        return 1

    body = synthesize_post(rows, api_key)

    title = f"Coding Journal — {today.strftime('%B %d, %Y')}"
    frontmatter = f"---\ntitle: {title}\ndate: {today.strftime('%B %d, %Y')}\n---\n\n"
    post_path.write_text(frontmatter + body + "\n")
    print(f"wrote {post_path} ({len(rows)} raw thoughts synthesized)")

    os.chdir(REPO_ROOT)
    # build.py needs markdown+PyYAML, which live in system python3, not the
    # open-brain-mcp venv this script runs under.
    build = subprocess.run(["/usr/bin/python3", "build.py"], capture_output=True, text=True)
    if build.returncode != 0:
        print(f"build.py failed: {build.stderr}", file=sys.stderr)
        return 1
    print(build.stdout.strip())

    subprocess.run(["git", "add", str(post_path.relative_to(REPO_ROOT)), "public/"],
                    cwd=REPO_ROOT, check=True)
    commit = subprocess.run(
        ["git", "commit", "-m", f"Journal: {today.isoformat()}"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if commit.returncode != 0:
        print(f"git commit failed (maybe nothing changed): {commit.stderr}", file=sys.stderr)
        return 1
    subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True)

    url = f"https://blog.ofone.dev/posts/{post_path.stem}.html"
    print(f"published: {url}")

    try:
        hermes_venv_python = pathlib.Path.home() / ".hermes" / "hermes-agent" / "venv" / "bin" / "python"
        subprocess.run(
            [str(hermes_venv_python), "-m", "hermes_cli.main", "send", "--to", "discord",
             f"📝 Published today's coding journal: {url}"],
            cwd=str(pathlib.Path.home() / ".hermes" / "hermes-agent"),
            check=False, capture_output=True, text=True,
        )
    except Exception as exc:
        print(f"notify failed (non-fatal): {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
