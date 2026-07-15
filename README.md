# ofOne Cannabis-AI Digest Blog

Daily blog posting pipeline for the Cannabis-AI Digest. Markdown posts → Static HTML → Cloudflare Pages.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create GitHub repo
```bash
gh repo create ofone-blog --public --source=. --remote=origin --push
```

### 3. Deploy to Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select "Pages" → "Connect to Git"
3. Authorize GitHub and select `ofone-blog`
4. Build settings:
   - **Framework preset**: None
   - **Build command**: `python build.py`
   - **Build output directory**: `public`
5. Set custom domain: `blog.ofone.dev`

### 4. Point DNS to Cloudflare
In your domain registrar, set nameservers to Cloudflare's or create a CNAME:
```
blog  CNAME  ofone-blog.pages.dev
```

## Usage

### Post a new digest
```python
from post_digest import post_digest

digest = {
    "date": "July 15, 2026",
    "intersects": [
        {
            "title": "Article Title",
            "url": "https://example.com",
            "description": "Brief summary."
        }
    ],
    "doesnt_intersect": [
        {
            "title": "Article Title",
            "url": "https://example.com",
            "description": "Brief summary."
        }
    ],
    "sources": [
        {
            "title": "Source Title",
            "url": "https://example.com"
        }
    ],
    "run_summary": "Found X articles..."
}

blog_url = post_digest(digest)
print(f"Posted to: {blog_url}")
```

### Manual build
```bash
python build.py
```

Outputs static HTML to `public/`.

## Structure

```
ofone-blog/
├── posts/               # Markdown blog posts
│   └── *.md
├── public/              # Generated static site (Cloudflare Pages serves this)
│   ├── index.html
│   └── posts/
│       └── *.html
├── assets/
│   └── css/
│       └── style.css
├── build.py             # Markdown → HTML converter
├── post_digest.py       # Post & commit digest
└── README.md
```

## Scheduling

Integrate `post_digest.py` into the Claude Desktop scheduled task that runs the daily digest.

The digest runner should:
1. Generate digest data (web search, summarization)
2. Call `post_digest(digest_data)`
3. Return the blog URL in the output

## Notes

- Posts are stored as markdown with YAML frontmatter
- Static HTML is regenerated on every new post
- Cloudflare Pages auto-deploys on git push
- No CMS or database needed—pure git-based workflow
