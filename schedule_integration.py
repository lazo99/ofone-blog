#!/usr/bin/env python3
"""
Integration for Claude Desktop scheduled digest task.

Usage in your scheduled task:
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path.home() / "Code/ofone-blog"))
    from schedule_integration import post_daily_digest

    # After generating digest data, call:
    blog_url = post_daily_digest(digest_data)
    print(f"Blog posted: {blog_url}")
"""

from pathlib import Path
from datetime import datetime
import subprocess
import sys
import re


BLOG_REPO = Path.home() / "Code/ofone-blog"


def post_daily_digest(digest_data):
    """
    Post digest to blog and return URL.

    Args:
        digest_data (dict): Digest with keys:
            - date: "July 15, 2026"
            - intersects: [{"title": str, "url": str, "description": str}]
            - doesnt_intersect: [{"title": str, "url": str, "description": str}]
            - sources: [{"title": str, "url": str}]
            - run_summary: str

    Returns:
        str: Blog URL if posted, None if failed
    """
    if not BLOG_REPO.exists():
        print(f"✗ Blog repo not found: {BLOG_REPO}")
        return None

    # Date slug: "July 15, 2026" → "July-15-2026"
    date_str = digest_data["date"].replace(" ", "-").replace(",", "")
    post_path = BLOG_REPO / "posts" / f"{date_str}.md"

    if post_path.exists():
        print(f"✗ Post already exists: {post_path.name}")
        return None

    # Format markdown
    markdown_content = _format_markdown(digest_data)
    post_path.write_text(markdown_content)
    print(f"✓ Created: {post_path.name}")

    # Build
    if not _build_site():
        return None

    # Commit & push
    if not _commit_and_push(date_str):
        return None

    blog_url = f"https://blog.ofone.dev/posts/{date_str}.html"
    print(f"✓ Live: {blog_url}")
    return blog_url


def _format_markdown(digest_data):
    """Format digest to markdown with frontmatter."""
    title = f"Cannabis-AI Digest — {digest_data['date']}"

    # Intersects
    intersects = "\n\n".join([
        f"{i+1}. **[{item['title']}]({item['url']})** — {item['description']}"
        for i, item in enumerate(digest_data.get("intersects", []))
    ])

    # Doesn't intersect
    doesnt_intersect = "\n\n".join([
        f"{i+1}. **[{item['title']}]({item['url']})** — {item['description']}"
        for i, item in enumerate(digest_data.get("doesnt_intersect", []))
    ])

    # Sources
    sources = "\n".join([
        f"- [{item['title']}]({item['url']})"
        for item in digest_data.get("sources", [])
    ])

    return f"""---
title: {title}
date: {digest_data['date']}
---

## Intersects

{intersects}

## Doesn't Intersect / Barriers

{doesnt_intersect}

---

## Sources

{sources}

---

**Run Summary:** {digest_data.get('run_summary', 'Daily digest generated.')}
"""


def _build_site():
    """Run build.py to generate static HTML."""
    try:
        result = subprocess.run(
            [sys.executable, "build.py"],
            cwd=BLOG_REPO,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print(f"✗ Build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False


def _commit_and_push(date_str):
    """Commit post and public files, then push."""
    try:
        subprocess.run(
            ["git", "add", f"posts/{date_str}.md", "public/"],
            cwd=BLOG_REPO,
            check=True,
            capture_output=True
        )

        subprocess.run(
            ["git", "commit", "-m", f"Post digest: {date_str}"],
            cwd=BLOG_REPO,
            check=True,
            capture_output=True
        )

        subprocess.run(
            ["git", "push"],
            cwd=BLOG_REPO,
            check=True,
            capture_output=True
        )

        print(f"✓ Pushed: {date_str}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Git failed: {e.stderr if hasattr(e, 'stderr') else e}")
        return False


if __name__ == "__main__":
    # Test
    test_digest = {
        "date": "July 15, 2026",
        "intersects": [
            {
                "title": "Test Intersect",
                "url": "https://example.com",
                "description": "Test description."
            }
        ],
        "doesnt_intersect": [
            {
                "title": "Test Barrier",
                "url": "https://example.com",
                "description": "Test description."
            }
        ],
        "sources": [
            {
                "title": "Test Source",
                "url": "https://example.com"
            }
        ],
        "run_summary": "Test run."
    }

    url = post_daily_digest(test_digest)
    if url:
        print(f"\n🎉 Success: {url}")
