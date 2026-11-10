#!/usr/bin/env python3
import json
import subprocess
import re
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUN_BIN = "/Users/saifalmutairi/.bun/bin/bun"
CLI_PATH = REPO_ROOT / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"

with open(REPO_ROOT / "new_jobs_to_process.json") as f:
    jobs = json.load(f)

print(f"Loaded {len(jobs)} jobs to analyze...")

detailed_jobs = []

for idx, job in enumerate(jobs, 1):
    jid = job.get("id")
    title = job.get("title", "")
    comp = job.get("company", "")
    loc = job.get("location", "")
    url = job.get("url", "")
    
    print(f"[{idx}/{len(jobs)}] Fetching {jid}: {title} @ {comp}...")
    
    cmd = [BUN_BIN, "run", str(CLI_PATH), "detail", str(jid), "--format", "json"]
    desc = ""
    apply_url = ""
    posted_date = job.get("date", "")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if res.returncode == 0:
            d_data = json.loads(res.stdout)
            desc = d_data.get("description", "")
            apply_url = d_data.get("applyUrl", "")
            posted_date = d_data.get("date", posted_date)
    except Exception as e:
        print(f"  Error fetching detail for {jid}: {e}")

    job_data = {
        "id": jid,
        "title": title,
        "company": comp,
        "location": loc,
        "url": url,
        "applyUrl": apply_url,
        "date": posted_date,
        "description": desc
    }
    detailed_jobs.append(job_data)
    time.sleep(0.1)

out_file = REPO_ROOT / "detailed_candidate_jobs.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(detailed_jobs, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(detailed_jobs)} detailed jobs to {out_file}")

