#!/usr/bin/env python3
"""Automate Cloudflare Pages setup via API."""

import os
import subprocess
import sys
import json
from pathlib import Path

def setup_cloudflare():
    """Complete Cloudflare Pages setup automation."""

    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not api_token:
        print("ERROR: Set CLOUDFLARE_API_TOKEN environment variable")
        print("")
        print("To get your token:")
        print("  1. Go to https://dash.cloudflare.com/profile/api-tokens")
        print("  2. Create token: 'Edit Cloudflare Workers' (or custom with Accounts.Manage)")
        print("  3. Copy the token")
        print("  4. Run: export CLOUDFLARE_API_TOKEN='your-token-here'")
        print("  5. Re-run this script")
        sys.exit(1)

    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    if not account_id:
        print("ERROR: Set CLOUDFLARE_ACCOUNT_ID")
        print("")
        print("Find your Account ID:")
        print("  1. https://dash.cloudflare.com/")
        print("  2. Right sidebar, 'Account ID' — copy it")
        print("  3. Run: export CLOUDFLARE_ACCOUNT_ID='your-id-here'")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    print("🔧 Setting up Cloudflare Pages...")
    print(f"   Account: {account_id}")
    print("")

    # 1. Create Pages project
    print("1️⃣  Creating Pages project...")
    project_name = "ofone-blog"

    create_project = {
        "name": project_name,
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
        [
            "curl", "-s", "-X", "POST",
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects",
            "-H", f"Authorization: Bearer {api_token}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(create_project)
        ],
        capture_output=True,
        text=True
    )

    response = json.loads(result.stdout)

    if not response.get("success"):
        error = response.get("errors", [{}])[0].get("message", "Unknown error")
        if "already exists" in error.lower():
            print(f"   ✓ Project already exists")
        else:
            print(f"   ✗ Failed: {error}")
            print(f"\n   Raw response: {json.dumps(response, indent=2)}")
            sys.exit(1)
    else:
        print(f"   ✓ Project created")

    # 2. Add custom domain
    print("2️⃣  Adding custom domain (blog.ofone.dev)...")

    add_domain = {
        "domain": "blog.ofone.dev"
    }

    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST",
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project_name}/domains",
            "-H", f"Authorization: Bearer {api_token}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(add_domain)
        ],
        capture_output=True,
        text=True
    )

    response = json.loads(result.stdout)

    if not response.get("success"):
        error = response.get("errors", [{}])[0].get("message", "Unknown error")
        if "already" in error.lower():
            print(f"   ✓ Domain already configured")
        else:
            print(f"   ⚠️  Domain setup: {error}")
    else:
        print(f"   ✓ Domain added (verify DNS in CF dashboard)")

    # 3. Trigger first deployment
    print("3️⃣  Triggering initial build...")

    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST",
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project_name}/deployments",
            "-H", f"Authorization: Bearer {api_token}",
            "-H", "Content-Type: application/json"
        ],
        capture_output=True,
        text=True
    )

    response = json.loads(result.stdout)

    if response.get("success"):
        print(f"   ✓ Build triggered")
    else:
        error = response.get("errors", [{}])[0].get("message", "Unknown error")
        print(f"   ℹ️  {error}")

    print("")
    print("✅ Cloudflare Pages setup complete!")
    print("")
    print("Next steps:")
    print("  1. Visit https://dash.cloudflare.com/")
    print("  2. Pages → ofone-blog → Deployments (wait ~2min for build)")
    print("  3. Verify: https://blog.ofone.dev/")
    print("")
    print("Once live, integrate with your scheduled task:")
    print("  See Code/ofone-blog/INTEGRATION.md")

if __name__ == "__main__":
    setup_cloudflare()
