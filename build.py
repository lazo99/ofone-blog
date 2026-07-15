#!/usr/bin/env python3
"""Build markdown posts into static HTML site."""
import os
import re
from pathlib import Path
from datetime import datetime
import yaml
import markdown

POSTS_DIR = Path("posts")
OUTPUT_DIR = Path("public")
TEMPLATE_DIR = Path("templates")


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown."""
    if not content.startswith("---"):
        return {}, content

    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not match:
        return {}, content

    frontmatter = yaml.safe_load(match.group(1))
    body = match.group(2)
    return frontmatter or {}, body


def build_posts():
    """Convert markdown posts to HTML."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    posts_output = OUTPUT_DIR / "posts"
    posts_output.mkdir(exist_ok=True)

    posts = []

    for md_file in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        with open(md_file) as f:
            content = f.read()

        frontmatter, body = parse_frontmatter(content)
        html_content = markdown.markdown(body, extensions=['extra', 'tables'])

        post = {
            "slug": md_file.stem,
            "title": frontmatter.get("title", md_file.stem),
            "date": frontmatter.get("date", ""),
            "html": html_content,
        }
        posts.append(post)

        # Write individual post HTML
        post_html = render_post_template(post)
        output_file = posts_output / f"{md_file.stem}.html"
        with open(output_file, "w") as f:
            f.write(post_html)

    # Write index
    index_html = render_index_template(posts)
    with open(OUTPUT_DIR / "index.html", "w") as f:
        f.write(index_html)

    print(f"✓ Built {len(posts)} posts to {OUTPUT_DIR}/")


def render_post_template(post):
    """Render individual post HTML."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{post['title']} | Cannabis-AI Digest</title>
    <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1><a href="/">Cannabis-AI Digest</a></h1>
            <p>Daily intersections between cannabis industry and AI</p>
        </div>
    </header>

    <main class="container">
        <article>
            <h2>{post['title']}</h2>
            <time>{post['date']}</time>
            <div class="content">
                {post['html']}
            </div>
        </article>
        <nav>
            <a href="/">← Back to all posts</a>
        </nav>
    </main>

    <footer>
        <p>© 2026 ofOne. Posted daily via Claude automation.</p>
    </footer>
</body>
</html>"""


def render_index_template(posts):
    """Render index page listing all posts."""
    posts_list = "".join([
        f'<li><a href="posts/{post["slug"]}.html">{post["title"]}</a> <span class="date">{post["date"]}</span></li>'
        for post in posts
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Cannabis-AI Digest</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>Cannabis-AI Digest</h1>
            <p>Daily intersections between cannabis industry and AI</p>
        </div>
    </header>

    <main class="container">
        <section class="posts">
            <h2>Latest posts</h2>
            <ul>
                {posts_list}
            </ul>
        </section>
    </main>

    <footer>
        <p>© 2026 ofOne. Posted daily via Claude automation.</p>
    </footer>
</body>
</html>"""


if __name__ == "__main__":
    build_posts()
