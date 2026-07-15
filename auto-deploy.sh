#!/bin/bash
set -e

echo "🚀 Blog Auto-Deploy"
echo ""

# Credentials from env or prompt
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "Need your Cloudflare API token (get it in 30s):"
    echo "  https://dash.cloudflare.com/profile/api-tokens"
    echo "  → Create Token (use 'Edit Cloudflare Workers' preset)"
    echo ""
    read -sp "Paste token: " CF_TOKEN
    echo ""
else
    CF_TOKEN="$CLOUDFLARE_API_TOKEN"
fi

if [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
    echo "Need your Account ID:"
    echo "  https://dash.cloudflare.com/"
    echo "  → Right sidebar, copy 'Account ID'"
    echo ""
    read -p "Paste Account ID: " CF_ACCOUNT
    echo ""
else
    CF_ACCOUNT="$CLOUDFLARE_ACCOUNT_ID"
fi

# Validate
if [ -z "$CF_TOKEN" ] || [ -z "$CF_ACCOUNT" ]; then
    echo "❌ Missing credentials"
    exit 1
fi

# Deploy
cd "$(dirname "$0")"
export CLOUDFLARE_API_TOKEN="$CF_TOKEN"
export CLOUDFLARE_ACCOUNT_ID="$CF_ACCOUNT"

python deploy-cf.py

echo ""
echo "✅ Done. Blog is live at https://blog.ofone.dev/"
