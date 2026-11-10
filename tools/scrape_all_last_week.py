#!/usr/bin/env python3
import json
import subprocess
import re
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUN_BIN = "/Users/saifalmutairi/.bun/bin/bun"
CLI_PATH = REPO_ROOT / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"

def extract_numeric_job_id(url_or_text):
    m = re.search(r'(\d{8,12})', str(url_or_text))
    return m.group(1) if m else None

def normalize_text_for_dedup(company, title):
    comp = str(company).lower()
    comp = re.sub(r'[\(\[\{].*?[\)\]\}]', '', comp)
    comp = re.sub(r'\b(llc|co|ltd|inc|group|holdings|company|corp|مقفلة|شركة|مؤسسة|مجموعة|القابضة|المحدودة)\b', '', comp, flags=re.IGNORECASE)
    comp = re.sub(r'[^\w\s]', '', comp).strip()
    tit = str(title).lower()
    tit = re.sub(r'[\(\[\{].*?[\)\]\}]', '', tit)
    tit = re.sub(r'[^\w\s]', '', tit).strip()
    return f"{comp}::{tit}"

# Load existing tracker
existing_ids = set()
existing_clean_urls = set()
existing_comp_titles = set()

if TRACKER_CSV.exists():
    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("رابط الوظيفة (Job URL)", "").strip()
            if url:
                clean_u = re.sub(r'\?.*$', '', url).rstrip('/')
                existing_clean_urls.add(clean_u)
                nid = extract_numeric_job_id(url)
                if nid:
                    existing_ids.add(nid)
            comp = row.get("اسم الشركة (Company)", "")
            tit = row.get("المسمى الوظيفي (Job Title)", "")
            if comp and tit:
                existing_comp_titles.add(normalize_text_for_dedup(comp, tit))

SEARCHES = [
    {"q": "Marketing Director", "l": "Riyadh, Saudi Arabia", "pages": [1, 2]},
    {"q": "Director of Marketing", "l": "Riyadh, Saudi Arabia", "pages": [1, 2]},
    {"q": "Director of Marketing", "l": "Saudi Arabia", "pages": [1, 2]},
    {"q": "Marketing Manager", "l": "Riyadh, Saudi Arabia", "pages": [1, 2, 3]},
    {"q": "Head of Marketing", "l": "Riyadh, Saudi Arabia", "pages": [1, 2]},
    {"q": "Chief Marketing Officer", "l": "Riyadh, Saudi Arabia", "pages": [1]},
    {"q": "Growth Marketing", "l": "Riyadh, Saudi Arabia", "pages": [1, 2]},
    {"q": "Digital Marketing Manager", "l": "Riyadh, Saudi Arabia", "pages": [1, 2]},
    {"q": "Brand Manager", "l": "Riyadh, Saudi Arabia", "pages": [1, 2]},
    {"q": "مدير تسويق", "l": "Riyadh, Saudi Arabia", "pages": [1, 2]},
    {"q": "Marketing", "l": "Saudi Arabia", "remote": "remote", "pages": [1, 2]},
]

all_found = {}

for s in SEARCHES:
    for page in s["pages"]:
        cmd = [
            BUN_BIN, "run", str(CLI_PATH), "search",
            "-q", s["q"],
            "-l", s["l"],
            "--jobage", "7",
            "--page", str(page),
            "--format", "json",
            "-n", "25"
        ]
        if "remote" in s:
            cmd.extend(["--remote", s["remote"]])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                results = data.get("results", data.get("jobs", []))
                for j in results:
                    jid = str(j.get("id", ""))
                    if not jid:
                        m = re.search(r'(\d{8,12})', j.get("url", ""))
                        jid = m.group(1) if m else j.get("url", "")
                    if jid and jid not in all_found:
                        all_found[jid] = j
        except Exception as e:
            print(f"Error in search {s['q']} p{page}: {e}")

print(f"Total raw jobs harvested from past week: {len(all_found)}")

# Filter against existing
new_jobs = []
for jid, job in all_found.items():
    url = job.get("url", "")
    clean_u = re.sub(r'\?.*$', '', url).rstrip('/')
    comp = job.get("company", "")
    tit = job.get("title", "")
    comp_tit = normalize_text_for_dedup(comp, tit)

    if jid in existing_ids:
        continue
    if clean_u in existing_clean_urls:
        continue
    if comp_tit in existing_comp_titles:
        continue

    new_jobs.append(job)

print(f"Total brand new jobs to process: {len(new_jobs)}")
out_p = REPO_ROOT / "new_jobs_to_process.json"
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(new_jobs, f, ensure_ascii=False, indent=2)

