#!/usr/bin/env python3
"""Post daily digest to blog and commit."""
import os
import subprocess
from pathlib import Path
from datetime import datetime
import sys

REPO_ROOT = Path(__file__).parent


def format_digest_markdown(digest_data):
    """Convert digest dict to markdown with YAML frontmatter."""
    title = f"Cannabis-AI Digest — {digest_data['date']}"

    frontmatter = f"""---
title: {title}
date: {digest_data['date']}
---

"""

    # Intersects section
    intersects = "\n\n".join([
        f"{i+1}. **[{item['title']}]({item['url']})** — {item['description']}"
        for i, item in enumerate(digest_data.get('intersects', []))
    ])

    # Doesn't intersect section
    doesnt_intersect = "\n\n".join([
        f"{i+1}. **[{item['title']}]({item['url']})** — {item['description']}"
        for i, item in enumerate(digest_data.get('doesnt_intersect', []))
    ])

    # Sources
    sources = "\n".join([
        f"- [{item['title']}]({item['url']})"
        for item in digest_data.get('sources', [])
    ])

    body = f"""## Intersects

{intersects}

## Doesn't Intersect / Barriers

{doesnt_intersect}

---

## Sources

{sources}

---

**Run Summary:** {digest_data.get('run_summary', 'Daily digest generated.')}
"""

    return frontmatter + body


def post_digest(digest_data):
    """Create post file, commit, and push."""
    date_str = digest_data['date'].replace(' ', '-').replace(',', '')  # "July-15-2026"
    post_filename = f"posts/{date_str}.md"
    post_path = REPO_ROOT / post_filename

    # Check if already posted today
    if post_path.exists():
        print(f"✗ Post already exists: {post_filename}")
        return None

    # Write markdown post
    content = format_digest_markdown(digest_data)
    post_path.write_text(content)
    print(f"✓ Created post: {post_filename}")

    # Build static site
    os.chdir(REPO_ROOT)
    result = subprocess.run(
        [sys.executable, "build.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"✗ Build failed: {result.stderr}")
        return None
    print(result.stdout.strip())

    # Commit and push
    try:
        subprocess.run(
            ["git", "add", post_filename, "public/"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True
        )

        commit_msg = f"Post digest: {date_str}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True
        )

        subprocess.run(
            ["git", "push"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True
        )
        print(f"✓ Committed and pushed: {commit_msg}")

        # Return blog URL
        blog_url = f"https://blog.ofone.dev/posts/{date_str}.html"
        return blog_url

    except subprocess.CalledProcessError as e:
        print(f"✗ Git operation failed: {e.stderr}")
        return None


if __name__ == "__main__":
    # Example usage
    digest = {
        "date": "July 15, 2026",
        "intersects": [
            {
                "title": "5W PR Releases Cannabis AI Visibility Index 2026",
                "url": "https://www.trendhunter.com/trends/cannabis-ai-visibility",
                "description": "Curaleaf, Trulieve, and Green Thumb Industries now compete for prominence in AI platform citations."
            }
        ],
        "doesnt_intersect": [
            {
                "title": "Platform Ads Remain Restricted",
                "url": "https://www.cannabisregulations.ai/...",
                "description": "AI-powered ad targeting unavailable; Meta, TikTok, Google restrictions persist."
            }
        ],
        "sources": [
            {
                "title": "5W Public Relations Cannabis AI Visibility Index",
                "url": "https://www.trendhunter.com/trends/cannabis-ai-visibility"
            }
        ],
        "run_summary": "Daily digest generated."
    }

    blog_url = post_digest(digest)
    if blog_url:
        print(f"\n🎉 Blog post live: {blog_url}")
