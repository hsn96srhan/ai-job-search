#!/usr/bin/env python3
"""
Search & Apply Engine - 24 Hours
يبحث عن كل الوظائف المنشورة خلال ٢٤ ساعة ويقدم عليها تلقائياً
"""

import json
import subprocess
import re
import csv
import os
import sys
import smtplib
import email.mime.multipart
import email.mime.base
import email.mime.text
from email import encoders
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
BUN_BIN = "/Users/saifalmutairi/.bun/bin/bun"
CLI_PATH = REPO_ROOT / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"
CV_PATH = REPO_ROOT / "cv" / "marketing-director-hsn.pdf"

# Load environment
def load_env():
    for fn in [".env", "jobs.env", "jobs.env.txt"]:
        p = REPO_ROOT / fn
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("\"'")
                    if "PASS" in k.upper(): v = v.replace(" ", "")
                    if k not in os.environ: os.environ[k] = v

load_env()
SMTP_USER = os.environ.get("SMTP_USER", "hsn96srhan@gmail.com")
SMTP_PASS = os.environ.get("SMTP_PASSWORD", os.environ.get("GMAIL_APP_PASSWORD", "")).replace(" ", "")

# --- Candidate Info ---
CANDIDATE = {
    "name": "Hassan Sarhan | حسن سرحان",
    "name_ar": "حسن سرحان",
    "name_en": "Hassan Sarhan",
    "phone": "+966506267542",
    "email": SMTP_USER,
    "portfolio": "https://hsn96srhan.github.io/hsn/",
    "linkedin": "https://www.linkedin.com/in/srhan-jr/",
    "title": "Marketing Director | مدير تسويق",
    "iqama": "2644162360",
}

# --- Search Queries (24-hour window) ---
QUERIES = [
    {"q": "Marketing Director", "l": "Riyadh, Saudi Arabia"},
    {"q": "Marketing Manager", "l": "Riyadh, Saudi Arabia"},
    {"q": "Head of Marketing", "l": "Riyadh, Saudi Arabia"},
    {"q": "Chief Marketing Officer", "l": "Riyadh, Saudi Arabia"},
    {"q": "Growth Marketing Manager", "l": "Riyadh, Saudi Arabia"},
    {"q": "Digital Marketing Director", "l": "Riyadh, Saudi Arabia"},
    {"q": "VP Marketing", "l": "Riyadh, Saudi Arabia"},
    {"q": "Brand Director", "l": "Riyadh, Saudi Arabia"},
    {"q": "E-commerce Director", "l": "Riyadh, Saudi Arabia"},
    {"q": "Marketing Director", "l": "Saudi Arabia", "extra": ["--remote", "remote"]},
    {"q": "Marketing Manager", "l": "Saudi Arabia", "extra": ["--remote", "remote"]},
]

# --- Load already-applied tracker ---
def load_applied_ids():
    applied = set()
    if TRACKER_CSV.exists():
        with open(TRACKER_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                jid = row.get("job_id", row.get("Job ID", "")).strip()
                url = row.get("url", row.get("URL", row.get("Apply Link", ""))).strip()
                if jid: applied.add(jid)
                m = re.search(r"(\d{8,12})", url)
                if m: applied.add(m.group(1))
    return applied

# --- Search ---
def search_jobs_24h():
    all_jobs = []
    seen_ids = set()
    for q in QUERIES:
        cmd = [
            BUN_BIN, "run", str(CLI_PATH), "search",
            "-q", q["q"],
            "-l", q["l"],
            "--jobage", "1",
            "--format", "json",
            "-n", "25"
        ]
        if "extra" in q:
            cmd.extend(q["extra"])
        print(f"🔍 Searching: {q['q']} @ {q['l']} ...")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                jobs = data.get("results", data.get("jobs", []))
                new = 0
                for job in jobs:
                    jid = str(job.get("id", ""))
                    if not jid:
                        m = re.search(r"(\d{8,12})", job.get("url", ""))
                        jid = m.group(1) if m else job.get("url", "")
                    if jid and jid not in seen_ids:
                        seen_ids.add(jid)
                        job["job_id"] = jid
                        all_jobs.append(job)
                        new += 1
                print(f"  → {len(jobs)} found, {new} new unique")
            else:
                print(f"  → Error: {res.stderr[:100]}")
        except Exception as e:
            print(f"  → Exception: {e}")
    return all_jobs

# --- Fetch job detail & check email ---
def get_job_detail(job_id):
    cmd = [BUN_BIN, "run", str(CLI_PATH), "detail", str(job_id), "--format", "json"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            return json.loads(res.stdout)
    except Exception:
        pass
    return {}

def extract_email_from_detail(detail):
    text = json.dumps(detail)
    emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return emails[0] if emails else None

# --- Email Application ---
EMAIL_SUBJECT_EN = "Application: Marketing Director | Hassan Sarhan | Iqama 2644162360 (Transferable)"
EMAIL_SUBJECT_AR = "تقديم وظيفة: مدير تسويق | حسن سرحان | إقامة قابلة للتحويل 2644162360"

COVER_EN = """\
Dear Hiring Manager,

I am writing to express my strong interest in the Marketing Director role at your organization.

I am Hassan Sarhan, a Marketing Director and officially Accredited Marketing Manager by the Saudi Ministry of Human Resources and Social Development (HRSD), currently based in Riyadh with 8+ years of proven leadership in performance marketing, e-commerce growth, and brand strategy across Saudi Arabia and the GCC.

Currently serving as Marketing Director at FLUX Ads (Riyadh) managing 30+ enterprise clients. Previously led marketing for Arabeva Group, Fantazzia Bed, and co-founded VLEX Logistics.

Key highlights:
• HRSD-Accredited Marketing Manager (وزارة الموارد البشرية)
• 8+ years experience | Riyadh-based with Transferable Iqama (2644162360)
• Managed multi-million SAR budgets — ROAS achieved: 5x to 25x
• Expert in Meta, Google, TikTok, Snapchat paid advertising
• E-commerce & D2C growth specialist (Saudi market)

Portfolio: https://hsn96srhan.github.io/hsn/
LinkedIn: https://www.linkedin.com/in/srhan-jr/
Phone/WhatsApp: +966506267542

Compensation expectations: 10,000–12,000+ SAR total package (Basic: 8,000–9,000 SAR + 25% cash housing allowance). I require standard Iqama transfer (نقل كفالة via Qiwa), work permit, and CCHI medical insurance per Saudi Labor Law.

My CV is attached. I would welcome the opportunity to discuss how I can drive growth for your brand.

Best regards,
Hassan Sarhan | حسن سرحان
Marketing Director | +966506267542
"""

COVER_AR = """\
السادة المحترمين،

أتقدم بكل ثقة للانضمام إلى فريقكم في منصب مدير تسويق.

اسمي حسن سرحان، مدير تسويق معتمد من وزارة الموارد البشرية والتنمية الاجتماعية بالمملكة العربية السعودية، مقيم في الرياض بإقامة عمل نظامية قابلة للتحويل الفوري رقمها 2644162360، وأمتلك خبرة تزيد عن ٨ سنوات في قيادة استراتيجيات النمو والتسويق الرقمي والأداء وإدارة التجارة الإلكترونية في السوق السعودي.

أعمل حالياً مديراً للتسويق في شركة فلوكس آدز بالرياض، وسبق لي الإشراف على التسويق في مجموعة أرابيفا وشركة فانتازيا بيد وتأسيس شركة فليكس للشحن.

**أبرز المؤهلات:**
• اعتماد مهني كمدير تسويق من وزارة الموارد البشرية والتنمية الاجتماعية (HRSD)
• خبرة +٨ سنوات | مقيم بالرياض | إقامة قابلة للتحويل (٢٦٤٤١٦٢٣٦٠)
• إدارة ميزانيات إعلانية بملايين الريالات مع تحقيق ROAS يصل إلى 25x
• خبرة واسعة في Google Ads، Meta، TikTok، Snapchat، وإعلانات نجوم
• متخصص في التجارة الإلكترونية D2C وتوسع العلامات التجارية في السوق السعودي

البورتفوليو: https://hsn96srhan.github.io/hsn/
لينكد إن: https://www.linkedin.com/in/srhan-jr/
الجوال/واتساب: +966506267542

**التوقعات المادية:** الراتب الأساسي 8,000–9,000 ريال + بدل سكن نقدي 25% + نقل كفالة + كرت عمل + تأمين طبي وفق نظام العمل السعودي.

السيرة الذاتية مرفقة. يسعدني مناقشة كيف أُضيف قيمة حقيقية لعلامتكم التجارية.

مع تقديري،
حسن سرحان
مدير تسويق | +966506267542
"""

def detect_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text or ""))

def send_email_application(to_email, job_title, company, job_url, is_arabic=False):
    if not SMTP_PASS:
        print(f"  ⚠️ No SMTP password configured — skipping email to {to_email}")
        return False
    try:
        msg = email.mime.multipart.MIMEMultipart()
        msg["From"] = f"Hassan Sarhan <{SMTP_USER}>"
        msg["To"] = to_email
        msg["Subject"] = EMAIL_SUBJECT_AR if is_arabic else EMAIL_SUBJECT_EN
        
        body = (COVER_AR if is_arabic else COVER_EN) + f"\n\nJob Reference: {job_url}"
        msg.attach(email.mime.text.MIMEText(body, "plain", "utf-8"))
        
        # Attach CV
        if CV_PATH.exists():
            with open(CV_PATH, "rb") as f:
                part = email.mime.base.MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="marketing-director-hsn.pdf"')
                msg.attach(part)
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        
        print(f"  ✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"  ❌ Email error: {e}")
        return False

# --- Update Tracker ---
def update_tracker(job, status, method="email"):
    rows = []
    headers = []
    if TRACKER_CSV.exists():
        with open(TRACKER_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            rows = list(reader)
    
    if not headers:
        headers = ["job_id", "title", "company", "location", "url", "date_found", "status", "method", "applied_at"]
    
    new_row = {
        "job_id": job.get("job_id", ""),
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "location": job.get("location", ""),
        "url": job.get("url", ""),
        "date_found": job.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "status": status,
        "method": method,
        "applied_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    
    # Check if job already tracked
    for row in rows:
        existing_id = row.get("job_id", "")
        existing_url = row.get("url", row.get("Apply Link", ""))
        m = re.search(r"(\d{8,12})", existing_url)
        if existing_id == new_row["job_id"] or (m and m.group(1) == new_row["job_id"]):
            row.update(new_row)
            break
    else:
        rows.append(new_row)
    
    with open(TRACKER_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 65)
    print("🚀 بحث ٢٤ ساعة + التقديم التلقائي | 24-Hour Job Search & Apply")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    # 1. Load already-applied jobs
    applied_ids = load_applied_ids()
    print(f"\n📋 Jobs already in tracker: {len(applied_ids)}")

    # 2. Search for new jobs in last 24h
    print("\n🔍 Searching all portals for jobs posted in last 24 hours...\n")
    new_jobs = search_jobs_24h()
    print(f"\n✅ Total unique new jobs found: {len(new_jobs)}")

    # 3. Filter out already-applied
    to_apply = [j for j in new_jobs if j.get("job_id", "") not in applied_ids]
    print(f"📌 New (not yet applied): {len(to_apply)}")

    if not to_apply:
        print("\n✔️ No new jobs to apply to. All caught up!")
        return

    # 4. For each job, fetch detail, find email, apply
    applied_count = 0
    linkedin_manual = []
    results_summary = []

    print("\n" + "=" * 65)
    print("📧 Starting Applications...")
    print("=" * 65)

    for idx, job in enumerate(to_apply, 1):
        jid = job.get("job_id", "")
        title = job.get("title", "")
        company = job.get("company", "")
        url = job.get("url", "")
        location = job.get("location", "")
        date = job.get("date", "")

        print(f"\n[{idx}/{len(to_apply)}] {title} @ {company}")
        print(f"  📍 {location} | 📅 {date}")
        print(f"  🔗 {url}")

        # Fetch detail
        detail = get_job_detail(jid)
        apply_email = extract_email_from_detail(detail)
        
        # Check if job description is Arabic
        desc_text = detail.get("description", "") or detail.get("title", "")
        is_arabic_job = detect_arabic(company + " " + desc_text)

        if apply_email:
            print(f"  📧 Found email: {apply_email}")
            sent = send_email_application(apply_email, title, company, url, is_arabic_job)
            if sent:
                applied_count += 1
                update_tracker(job, "applied_email", "email")
                results_summary.append(f"✅ {title} @ {company} → {apply_email}")
            else:
                update_tracker(job, "email_failed", "email_error")
                results_summary.append(f"❌ {title} @ {company} → email failed")
        else:
            # No email found — mark as LinkedIn / manual
            print(f"  ℹ️ No email found — marked as LinkedIn (manual apply)")
            linkedin_manual.append(job)
            update_tracker(job, "جاهز للتقديم", "linkedin_manual")
            results_summary.append(f"🔵 {title} @ {company} → LinkedIn (يدوي)")

    # 5. Summary
    print("\n" + "=" * 65)
    print("📊 ملخص التقديمات | Application Summary")
    print("=" * 65)
    print(f"✅ Applied via Email:  {applied_count}")
    print(f"🔵 LinkedIn Manual:    {len(linkedin_manual)}")
    print(f"📋 Total Processed:   {len(to_apply)}")
    print()
    for r in results_summary:
        print(f"  {r}")

    # 6. Show LinkedIn manual list
    if linkedin_manual:
        print("\n" + "=" * 65)
        print("🔵 وظائف LinkedIn جاهزة للتقديم اليدوي (سيب إنت تقدم عليها):")
        print("=" * 65)
        for j in linkedin_manual:
            print(f"  • {j.get('title')} @ {j.get('company')}")
            print(f"    {j.get('url')}")

    print("\n✅ Done!")

if __name__ == "__main__":
    main()

