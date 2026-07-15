#!/bin/bash
set -e

# One command to finish setup
# Run: bash Code/ofone-blog/setup.sh

REPO="$HOME/Code/ofone-blog"
cd "$REPO"

echo "🚀 Finishing blog setup..."

# Dependencies
pip install -q markdown pyyaml >/dev/null 2>&1 || true

# Test build locally
python build.py >/dev/null 2>&1

# Check git is ready
git log -1 --oneline >/dev/null

echo ""
echo "✅ Blog repo ready: https://github.com/lazo99/ofone-blog"
echo ""
echo "📍 Cloudflare setup (do this ONCE):"
echo ""
echo "   Option A: Fast (automatic)"
echo "   ────────────────────────"
echo "   Get credentials from: https://dash.cloudflare.com/profile/api-tokens"
echo "   Then run:"
echo ""
echo "   export CF_API_TOKEN='your-token' && \\
export CF_ACCOUNT_ID='your-id' && \\
python $REPO/setup-cloudflare.py"
echo ""
echo "   Option B: Manual (2 min, simple)"
echo "   ──────────────────────────────"
echo "   1. https://dash.cloudflare.com → Pages"
echo "   2. Connect to Git → Select lazo99/ofone-blog"
echo "   3. Build: python build.py | Output: public"
echo "   4. Custom domain: blog.ofone.dev"
echo ""
echo "🔌 Then integrate with your scheduled task:"
echo "   See: Code/ofone-blog/INTEGRATION.md"
echo ""
