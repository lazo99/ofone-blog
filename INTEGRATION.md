# Scheduled Task Integration

Your daily digest task should call `post_daily_digest()` after generating the digest data.

## One-time Cloudflare Setup

```bash
bash cloudflare-setup.sh
```

Then visit https://dash.cloudflare.com/ and follow the 8 steps shown.

## Integrate with Your Scheduled Digest Task

In your scheduled digest runner (wherever it generates the digest), add this at the end:

```python
from pathlib import Path
import sys

# Add blog repo to path
sys.path.insert(0, str(Path.home() / "Code/ofone-blog"))
from schedule_integration import post_daily_digest

# After you generate digest_data dict with:
# - date: "July 15, 2026"
# - intersects: [{"title": str, "url": str, "description": str}, ...]
# - doesnt_intersect: [{"title": str, "url": str, "description": str}, ...]
# - sources: [{"title": str, "url": str}, ...]
# - run_summary: str

blog_url = post_daily_digest(digest_data)

if blog_url:
    # Append to digest output
    digest_output += f"\n\n🎉 **Blog post:** {blog_url}"
else:
    # Post failed (maybe already posted today, or git error)
    digest_output += "\n\n⚠️ Blog post failed to post (already posted today?)"
```

## Testing

Test locally without committing:

```bash
cd Code/ofone-blog
pip install -q markdown pyyaml
python schedule_integration.py
```

This will:
1. Create a test post
2. Build the site
3. Commit & push to GitHub
4. Cloudflare auto-rebuilds and deploys

Check the live site at: https://blog.ofone.dev/

## Digest Data Format

Your digest task must produce a dict with this structure:

```python
digest_data = {
    "date": "July 15, 2026",  # Human-readable date
    "intersects": [
        {
            "title": "Article Title",
            "url": "https://example.com/article",
            "description": "2-3 sentence summary explaining the intersection."
        },
        # ... more items
    ],
    "doesnt_intersect": [
        {
            "title": "Article Title",
            "url": "https://example.com/article",
            "description": "2-3 sentence summary explaining the barrier."
        },
        # ... more items
    ],
    "sources": [
        {
            "title": "Source Name",
            "url": "https://example.com/article"
        },
        # ... more sources
    ],
    "run_summary": "Found X articles about Y, highlighting Z trends."
}
```

## Pipeline

```
Scheduled Task Runs
    ↓
Generate digest data
    ↓
Call post_daily_digest(digest_data)
    ↓
Creates markdown post
    ↓
Builds static HTML (build.py)
    ↓
Commits to git
    ↓
Pushes to GitHub
    ↓
Cloudflare auto-deploys
    ↓
Post live at blog.ofone.dev
```

## Troubleshooting

**Post already exists:** Task ran twice same day. Safe—just skipped.

**Git push fails:** Check SSH key is set up: `ssh -T git@github.com`

**Build fails:** Check markdown/PyYAML installed: `pip install -q markdown pyyaml`

**Cloudflare not building:** Check Pages settings in dashboard match build command/output.
