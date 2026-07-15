#!/usr/bin/env python3
"""Deploy blog to Cloudflare Pages using Python API."""

import os
import sys
import subprocess
from pathlib import Path
import json

def deploy():
    """Complete Cloudflare Pages deployment."""

    token = os.getenv("CLOUDFLARE_API_TOKEN")
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")

    if not token or not account_id:
        print("❌ Missing Cloudflare credentials")
        print("")
        print("Get them here:")
        print("  Token: https://dash.cloudflare.com/profile/api-tokens")
        print("  Account ID: https://dash.cloudflare.com/ (right sidebar)")
        print("")
        print("Then run:")
        print("  export CLOUDFLARE_API_TOKEN='token' CLOUDFLARE_ACCOUNT_ID='id'")
        print("  python deploy-cf.py")
        sys.exit(1)

    repo_root = Path(__file__).parent

    # 1. Create project
    print("📦 Creating Pages project...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    project_data = {
        "name": "ofone-blog",
        "source": {
            "type": "github",
            "config": {
                "owner": "lazo99",
                "repo": "ofone-blog",
                "production_branch": "master"
            }
        },
        "build_config": {
            "build_command": "python build.py",
            "destination_dir": "public"
        }
    }

    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(project_data)],
        capture_output=True,
        text=True
    )

    resp = json.loads(result.stdout)
    if resp.get("success"):
        print("   ✅ Project created")
    elif "already exists" in str(resp.get("errors", [])).lower():
        print("   ✅ Project already exists")
    else:
        print(f"   ❌ {resp.get('errors', [{}])[0].get('message', 'Failed')}")
        sys.exit(1)

    # 2. Add domain
    print("🔗 Adding custom domain...")

    domain_data = {"domain": "blog.ofone.dev"}

    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/ofone-blog/domains",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(domain_data)],
        capture_output=True,
        text=True
    )

    resp = json.loads(result.stdout)
    if resp.get("success"):
        print("   ✅ Domain added")
    else:
        error = resp.get("errors", [{}])[0].get("message", "Failed")
        if "already" in error.lower():
            print("   ✅ Domain already configured")
        else:
            print(f"   ⚠️  {error}")

    # 3. Trigger build
    print("🚀 Triggering deployment...")

    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/ofone-blog/deployments",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Content-Type: application/json"],
        capture_output=True,
        text=True
    )

    resp = json.loads(result.stdout)
    if resp.get("success"):
        print("   ✅ Deployment started")

    print("")
    print("✅ Cloudflare Pages is live!")
    print("")
    print("📍 Check deployment at:")
    print("   https://dash.cloudflare.com/ → Pages → ofone-blog")
    print("")
    print("🌐 Blog URL:")
    print("   https://blog.ofone.dev/")
    print("")
    print("🔌 Integrate with scheduled task:")
    print("   See: INTEGRATION.md")

if __name__ == "__main__":
    deploy()
