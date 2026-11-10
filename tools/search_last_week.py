#!/usr/bin/env python3
import json
import subprocess
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUN_BIN = "/Users/saifalmutairi/.bun/bin/bun"
CLI_PATH = REPO_ROOT / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"

QUERIES = [
    {"q": "Marketing Director", "l": "Riyadh, Saudi Arabia"},
    {"q": "Marketing Manager", "l": "Riyadh, Saudi Arabia"},
    {"q": "Head of Marketing", "l": "Riyadh, Saudi Arabia"},
    {"q": "Chief Marketing Officer", "l": "Riyadh, Saudi Arabia"},
    {"q": "Growth Marketing", "l": "Riyadh, Saudi Arabia"},
    {"q": "Digital Marketing", "l": "Riyadh, Saudi Arabia"},
    {"q": "Brand Manager", "l": "Riyadh, Saudi Arabia"},
    {"q": "Marketing", "l": "Saudi Arabia", "remote": "remote"},
]

def run_query(q_dict):
    cmd = [
        BUN_BIN, "run", str(CLI_PATH), "search",
        "-q", q_dict["q"],
        "-l", q_dict["l"],
        "--jobage", "7",
        "--format", "json",
        "-n", "25"
    ]
    if "remote" in q_dict:
        cmd.extend(["--remote", q_dict["remote"]])

    print(f"Running search: {q_dict} ...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            jobs = data.get("results", data.get("jobs", []))
            print(f"  -> Found {len(jobs)} jobs")
            return jobs
        else:
            print(f"  -> Error (code {res.returncode}): {res.stderr}")
            return []
    except Exception as e:
        print(f"  -> Exception: {e}")
        return []

def main():
    all_jobs = []
    seen_ids = set()

    for q in QUERIES:
        jobs = run_query(q)
        for job in jobs:
            jid = str(job.get("id", ""))
            if not jid:
                m = re.search(r'(\d{8,12})', job.get("url", ""))
                jid = m.group(1) if m else job.get("url", "")
            if jid and jid not in seen_ids:
                seen_ids.add(jid)
                all_jobs.append(job)

    print(f"\nTotal unique jobs found across all queries: {len(all_jobs)}")
    out_file = REPO_ROOT / "last_week_search_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out_file}")

if __name__ == "__main__":
    main()

