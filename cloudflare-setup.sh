#!/bin/bash
# One-time Cloudflare Pages setup for blog.ofone.dev
# After running: gh repo push completes, wait ~2min, then visit Cloudflare dashboard

set -e

REPO="ofone-blog"
GITHUB_REPO="lazo99/${REPO}"

echo "📋 Cloudflare Pages Setup for blog.ofone.dev"
echo "=============================================="
echo ""
echo "✓ GitHub repo ready: https://github.com/${GITHUB_REPO}"
echo ""
echo "Next: Visit https://dash.cloudflare.com/"
echo ""
echo "Steps:"
echo "  1. Click 'Pages' (left sidebar)"
echo "  2. Click 'Connect to Git'"
echo "  3. Authorize & select: ${GITHUB_REPO}"
echo "  4. Build Settings:"
echo "     - Build command: python build.py"
echo "     - Build output directory: public"
echo "     - (Root directory: / is fine)"
echo "  5. Environment variables: (leave empty)"
echo "  6. Click 'Save and Deploy'"
echo "  7. Once deployed, go to 'Custom domains'"
echo "  8. Add custom domain: blog.ofone.dev"
echo ""
echo "That's it! CF will auto-rebuild on every git push."
echo ""
echo "─────────────────────────────────────────"
echo "Verify locally first:"
echo "  pip install -q markdown pyyaml"
echo "  python build.py"
echo "  # Check public/index.html exists"
