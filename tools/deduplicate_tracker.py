#!/usr/bin/env python3
"""Deduplicate tracker CSV by LinkedIn job ID and ensure 1:1 truth with reality."""

import csv
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"

def extract_job_id(url):
    m = re.search(r"(\d{8,12})", url)
    return m.group(1) if m else url

def deduplicate():
    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    seen_job_ids = set()
    unique_rows = []

    for r in reader:
        url = r["رابط الوظيفة (Job URL)"]
        jid_key = extract_job_id(url)

        if jid_key in seen_job_ids:
            print(f"Removing duplicate: {r['ID']} - {r['اسم الشركة (Company)']} ({jid_key})")
            continue

        seen_job_ids.add(jid_key)
        unique_rows.append(r)

    # Renumber IDs sequentially
    for idx, r in enumerate(unique_rows, 1):
        r["ID"] = f"SA-{idx:03d}"

    fieldnames = list(unique_rows[0].keys())

    with open(TRACKER_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"\n✓ Deduplication complete. Total unique jobs: {len(unique_rows)}")
    
    # Audit counts
    c_easy = sum(1 for r in unique_rows if "ايزي" in r["طريقة التقديم (Application Method)"])
    c_email = sum(1 for r in unique_rows if "ايميل" in r["طريقة التقديم (Application Method)"])
    c_ats = sum(1 for r in unique_rows if "بوابة" in r["طريقة التقديم (Application Method)"])
    print(f"  - ⚡ ايزي ابلاي: {c_easy}")
    print(f"  - ✉️ ايميل مباشر: {c_email}")
    print(f"  - 🌐 بوابة خارجية: {c_ats}")

if __name__ == "__main__":
    deduplicate()
