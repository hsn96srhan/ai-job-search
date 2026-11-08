#!/usr/bin/env python3
"""Unified Multi-Portal Job Search Orchestrator.

Aggregates job searches across 6 portal skills under .agents/skills/:
1. linkedin-search (Global, MENA, KSA, Egypt, Remote)
2. freehire-search (Global Tech, EMEA, Remote, 50+ ATS aggregators)
3. jobindex-search (Denmark & Nordics)
4. jobnet-search (STAR Danish Labour Agency)
5. jobbank-search (Akademikernes Jobbank)
6. jobdanmark-search (Jobdanmark.dk Regional & Corporate)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUN_BIN = "/Users/saifalmutairi/.bun/bin/bun"
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"


PORTALS = {
    "linkedin-search": {
        "name": "LinkedIn Jobs",
        "scope": "Global, MENA, Saudi Arabia, Egypt, Remote",
        "cli_path": SKILLS_DIR / "linkedin-search" / "cli" / "src" / "cli.ts",
        "arg_type": "linkedin",
    },
    "freehire-search": {
        "name": "Freehire ATS Aggregator",
        "scope": "Global Tech, EMEA, Remote (50+ ATS systems)",
        "cli_path": SKILLS_DIR / "freehire-search" / "cli" / "src" / "cli.ts",
        "arg_type": "freehire",
    },
    "jobindex-search": {
        "name": "Jobindex.dk",
        "scope": "Denmark & Nordics",
        "cli_path": SKILLS_DIR / "jobindex-search" / "cli" / "src" / "cli.ts",
        "arg_type": "jobindex",
    },
    "jobnet-search": {
        "name": "Jobnet (STAR Agency)",
        "scope": "Denmark Public & Private",
        "cli_path": SKILLS_DIR / "jobnet-search" / "cli" / "src" / "cli.ts",
        "arg_type": "jobnet",
    },
    "jobbank-search": {
        "name": "Jobbank.dk",
        "scope": "Denmark Academic & Graduate",
        "cli_path": SKILLS_DIR / "jobbank-search" / "cli" / "src" / "cli.ts",
        "arg_type": "jobbank",
    },
    "jobdanmark-search": {
        "name": "Jobdanmark.dk",
        "scope": "Denmark Regional & Municipal",
        "cli_path": SKILLS_DIR / "jobdanmark-search" / "cli" / "src" / "cli.ts",
        "arg_type": "jobdanmark",
    },
}


def build_command(portal_key, query, location=None, limit=10):
    cfg = PORTALS[portal_key]
    cli = str(cfg["cli_path"])
    arg_type = cfg["arg_type"]

    cmd = [BUN_BIN, "run", cli, "search"]

    if arg_type == "linkedin":
        cmd += ["-q", query, "-l", location or "Riyadh, Saudi Arabia", "--limit", str(limit), "--format", "json"]
    elif arg_type == "freehire":
        cmd += ["-q", query, "--limit", str(limit), "--format", "json"]
    elif arg_type == "jobindex":
        cmd += ["--query", query, "--limit", str(limit), "--format", "json"]
    elif arg_type == "jobnet":
        cmd += ["--search-string", query, "--limit", str(limit), "--format", "json"]
    elif arg_type == "jobbank":
        cmd += ["--key", query, "--limit", str(limit), "--format", "json"]
    elif arg_type == "jobdanmark":
        cmd += ["--text", query, "--limit", str(limit), "--format", "json"]

    return cmd


def normalize_result(portal_key, item):
    """Normalize fields across different portal schemas."""
    title = item.get("title") or item.get("jobTitle") or "Untitled"
    company = item.get("company") or item.get("companyName") or item.get("hiringOrgName") or "Unknown"
    location = item.get("location") or item.get("companyAddress") or item.get("municipality") or ""
    url = item.get("url") or item.get("jobAdUrl") or item.get("applyUrl") or ""
    date_val = item.get("date") or item.get("publishedDate") or item.get("publicationDate") or ""
    deadline = item.get("deadline") or item.get("applicationDeadline") or ""

    return {
        "portal": PORTALS[portal_key]["name"],
        "portal_key": portal_key,
        "title": title,
        "company": company,
        "location": location,
        "url": url,
        "date": str(date_val)[:10] if date_val else "",
        "deadline": str(deadline)[:10] if deadline else "",
    }


def search_portal(portal_key, query, location=None, limit=10):
    cmd = build_command(portal_key, query, location, limit)
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if res.returncode != 0 and not res.stdout:
            return {"ok": False, "portal": portal_key, "error": res.stderr.strip() or "Process exited with error"}

        data = json.loads(res.stdout)
        raw_items = data.get("results") or []
        items = [normalize_result(portal_key, it) for it in raw_items]
        return {"ok": True, "portal": portal_key, "count": len(items), "results": items}
    except Exception as e:
        return {"ok": False, "portal": portal_key, "error": str(e)}


def search_all(channels, query, location=None, limit=10):
    results = {}
    aggregated = []
    for ch in channels:
        if ch not in PORTALS:
            continue
        print(f"Searching {PORTALS[ch]['name']}...", file=sys.stderr)
        resp = search_portal(ch, query, location, limit)
        results[ch] = resp
        if resp.get("ok"):
            aggregated.extend(resp.get("results", []))
    return {"aggregated": aggregated, "portals": results}


def main():
    parser = argparse.ArgumentParser(description="Multi-Portal Job Search Orchestrator")
    parser.add_argument("-q", "--query", default="Marketing Director", help="Job search query")
    parser.add_argument("-l", "--location", default="Riyadh, Saudi Arabia", help="Location (primarily for LinkedIn)")
    parser.add_argument("-c", "--channels", default="all", help="Comma-separated portal keys or 'all' or 'mena' or 'nordic'")
    parser.add_argument("-n", "--limit", type=int, default=5, help="Limit per portal")
    parser.add_argument("--format", choices=["json", "table"], default="table", help="Output format")

    args = parser.parse_args()

    if args.channels == "all":
        selected_channels = list(PORTALS.keys())
    elif args.channels == "mena":
        selected_channels = ["linkedin-search", "freehire-search"]
    elif args.channels == "nordic":
        selected_channels = ["jobindex-search", "jobnet-search", "jobbank-search", "jobdanmark-search"]
    else:
        selected_channels = [c.strip() for c in args.channels.split(",") if c.strip() in PORTALS]

    data = search_all(selected_channels, args.query, args.location, args.limit)

    if args.format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("\n" + "=" * 80)
        print(f"SEARCH RESULTS FOR: '{args.query}' across {len(selected_channels)} channels")
        print("=" * 80)
        items = data["aggregated"]
        if not items:
            print("No jobs found matching criteria.")
        for idx, it in enumerate(items, 1):
            print(f"[{idx}] {it['title']} @ {it['company']}")
            print(f"    Portal: {it['portal']} | Location: {it['location']} | Date: {it['date']}")
            print(f"    URL: {it['url']}")
            print("-" * 80)

        print("\nCHANNELS STATUS SUMMARY:")
        for ch in selected_channels:
            p_data = data["portals"].get(ch, {})
            status = f"✓ Found {p_data.get('count', 0)} jobs" if p_data.get("ok") else f"⚠️ Error: {p_data.get('error')}"
            print(f"• {PORTALS[ch]['name']}: {status}")


if __name__ == "__main__":
    main()

