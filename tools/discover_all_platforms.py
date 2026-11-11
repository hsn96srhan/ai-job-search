#!/usr/bin/env python3
"""
اكتشاف كل منصات التوظيف في السعودية والخليج وتسجيلها على الداشبورد.

يبحث عن وظائف مدير تسويق / Marketing Director على كل منصة
ويحدث ملف platforms_registry.json و الداشبورد.
"""

import json
import csv
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ───────────────────────────────────────────────
RIYADH = timezone(timedelta(hours=3))
NOW = datetime.now(RIYADH)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M")
REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"
PLATFORMS_JSON = REPO_ROOT / "platforms_registry.json"
BUN_BIN = "/Users/saifalmutairi/.bun/bin/bun"
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"

# ───────────────────────────────────────────────
# الكتالوج الشامل لكل منصات التوظيف
# ───────────────────────────────────────────────
ALL_PLATFORMS = [
    # ─── منصات مفعّلة عبر CLI ───
    {
        "id": "linkedin",
        "name_ar": "لينكد إن",
        "name_en": "LinkedIn",
        "url": "https://www.linkedin.com/jobs/",
        "scope": "عالمي / السعودية / الخليج",
        "category": "عالمي",
        "profile_status": "⏭️ محجوب بطلب المستخدم",
        "profile_url": "https://www.linkedin.com/in/srhan-jr/",
        "search_active": True,
        "cli": "linkedin-search",
        "region": "Saudi Arabia",
        "notes": "تم تخطيه بأمر المستخدم — يتطلب تقديم يدوي",
    },
    {
        "id": "bayt",
        "name_ar": "بيت.كوم",
        "name_en": "Bayt.com",
        "url": "https://www.bayt.com/ar/",
        "scope": "السعودية / الخليج / الشرق الأوسط",
        "category": "خليجي",
        "profile_status": "🟡 87% — ينتظر رمز SMS",
        "profile_url": "https://www.bayt.com/ar/mycvs/?cv_id=98683664",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "تحديث الملف مكتمل إلا التحقق من الجوال (+8%)",
    },
    {
        "id": "naukrigulf",
        "name_ar": "نوكري غلف",
        "name_en": "Naukrigulf",
        "url": "https://arabic.naukrigulf.com/",
        "scope": "الخليج والسعودية",
        "category": "خليجي",
        "profile_status": "✅ 100% مكتمل",
        "profile_url": "https://arabic.naukrigulf.com/",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "الملف مكتمل 100%",
    },
    {
        "id": "tanqeeb",
        "name_ar": "تنقيب",
        "name_en": "Tanqeeb",
        "url": "https://saudi.tanqeeb.com/ar/",
        "scope": "السعودية والخليج",
        "category": "خليجي",
        "profile_status": "✅ 100% مكتمل",
        "profile_url": "https://saudi.tanqeeb.com/ar/profile/70204357",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "الملف مكتمل 100% — التحقق من الإيميل تم",
    },
    # ─── منصات مهمة — تحتاج تسجيل ───
    {
        "id": "gulftalent",
        "name_ar": "غلف تالنت",
        "name_en": "GulfTalent",
        "url": "https://www.gulftalent.com/",
        "scope": "الخليج والشرق الأوسط",
        "category": "خليجي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة تنفيذية — مهمة لمدراء التسويق",
    },
    {
        "id": "indeed_sa",
        "name_ar": "إنديد السعودية",
        "name_en": "Indeed KSA",
        "url": "https://sa.indeed.com/",
        "scope": "السعودية",
        "category": "عالمي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "أكبر محرك بحث وظائف عالمي — يدعم السعودية",
    },
    {
        "id": "glassdoor_sa",
        "name_ar": "جلاسدور السعودية",
        "name_en": "Glassdoor Saudi Arabia",
        "url": "https://www.glassdoor.com/Job/saudi-arabia-marketing-director-jobs",
        "scope": "السعودية",
        "category": "عالمي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "يتضمن تقييمات الشركات ورواتب السوق",
    },
    {
        "id": "jadarat",
        "name_ar": "جدارات",
        "name_en": "Jadarat (جدارات)",
        "url": "https://jadarat.sa/",
        "scope": "السعودية — رسمي",
        "category": "حكومي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة وزارة الموارد البشرية الرسمية للقطاع الخاص",
    },
    {
        "id": "qiwa",
        "name_ar": "قوى",
        "name_en": "Qiwa (قوى)",
        "url": "https://www.qiwa.sa/en/",
        "scope": "السعودية — رسمي",
        "category": "حكومي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة وزارة الموارد البشرية — نقل الكفالة والوظائف",
    },
    {
        "id": "linkedin_sa_jobs",
        "name_ar": "وظائف السعودية على لينكد إن",
        "name_en": "LinkedIn Saudi Arabia Jobs",
        "url": "https://www.linkedin.com/jobs/search/?location=Saudi%20Arabia",
        "scope": "السعودية",
        "category": "عالمي",
        "profile_status": "⏭️ يدوي فقط",
        "profile_url": "https://www.linkedin.com/in/srhan-jr/",
        "search_active": True,
        "cli": "linkedin-search",
        "region": "Saudi Arabia",
        "notes": "يستخدم CLI للبحث فقط — التقديم يدوي",
    },
    {
        "id": "wuzzuf",
        "name_ar": "وظف",
        "name_en": "Wuzzuf",
        "url": "https://wuzzuf.net/",
        "scope": "مصر والشرق الأوسط",
        "category": "إقليمي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "الأكبر في مصر — يقبل سكان الخليج",
    },
    {
        "id": "forasna",
        "name_ar": "فرصتنا",
        "name_en": "Forasna",
        "url": "https://www.forasna.com/",
        "scope": "السعودية والخليج",
        "category": "خليجي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة وظائف عربية",
    },
    {
        "id": "drjobs",
        "name_ar": "دي آر جوبز",
        "name_en": "DrJobs",
        "url": "https://ae.drjobs.com/",
        "scope": "الإمارات والخليج والسعودية",
        "category": "خليجي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة وظائف خليجية — قوية في KSA",
    },
    {
        "id": "rozee_pk",
        "name_ar": "روزي",
        "name_en": "Rozee.pk / GCC",
        "url": "https://www.rozee.pk/",
        "scope": "الخليج وباكستان",
        "category": "إقليمي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة وظائف جنوب آسيا والخليج",
    },
    {
        "id": "hire_success",
        "name_ar": "هاير سكسس",
        "name_en": "HireSuccess",
        "url": "https://www.hiresuccess.me/",
        "scope": "الخليج",
        "category": "خليجي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة وظائف تنفيذية خليجية",
    },
    {
        "id": "gulfiad",
        "name_ar": "خليجياد",
        "name_en": "Gulfiad",
        "url": "https://www.gulfiad.com/",
        "scope": "الخليج",
        "category": "خليجي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة وظائف خليجية",
    },
    {
        "id": "careers_ksa",
        "name_ar": "وظائف السعودية",
        "name_en": "Careers.sa",
        "url": "https://www.careers.sa/",
        "scope": "السعودية",
        "category": "خليجي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة وظائف سعودية محلية",
    },
    {
        "id": "mustakbal",
        "name_ar": "مستقبل",
        "name_en": "Mustakbal",
        "url": "https://mustakbal.sa/",
        "scope": "السعودية",
        "category": "خليجي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة توظيف سعودية",
    },
    {
        "id": "jooble_sa",
        "name_ar": "جوبل السعودية",
        "name_en": "Jooble KSA",
        "url": "https://sa.jooble.org/",
        "scope": "السعودية",
        "category": "عالمي",
        "profile_status": "لا يحتاج ملف",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "محرك بحث وظائف — يجمع من مصادر متعددة",
    },
    {
        "id": "adzuna_sa",
        "name_ar": "أدزونا السعودية",
        "name_en": "Adzuna KSA",
        "url": "https://www.adzuna.com/search?q=marketing+director&loc=saudi+arabia",
        "scope": "السعودية",
        "category": "عالمي",
        "profile_status": "لا يحتاج ملف",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "محرك تجميعي — لا يحتاج ملف شخصي",
    },
    {
        "id": "freehire",
        "name_ar": "فري هاير",
        "name_en": "Freehire (ATS Aggregator)",
        "url": "https://freehire.me/",
        "scope": "عالمي / خليجي",
        "category": "عالمي",
        "profile_status": "لا يحتاج ملف",
        "profile_url": "",
        "search_active": True,
        "cli": "freehire-search",
        "region": "Saudi Arabia",
        "notes": "يجمع من 50+ نظام ATS — مفيد جداً",
    },
    {
        "id": "linkedin_easy_apply",
        "name_ar": "لينكد إن إيزي أبلاي",
        "name_en": "LinkedIn Easy Apply",
        "url": "https://www.linkedin.com/jobs/",
        "scope": "السعودية / عالمي",
        "category": "عالمي",
        "profile_status": "⏭️ يدوي فقط",
        "profile_url": "https://www.linkedin.com/in/srhan-jr/",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "نقل الكفالة (Iqama) مطلوب — يدوي فقط",
    },
    {
        "id": "salary_sa",
        "name_ar": "وظائف السعودية (Salary.sa)",
        "name_en": "Salary.sa Jobs",
        "url": "https://salary.sa/jobs",
        "scope": "السعودية",
        "category": "خليجي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة رواتب ووظائف سعودية",
    },
    {
        "id": "masdarak",
        "name_ar": "مصدرك",
        "name_en": "Masdarak",
        "url": "https://masdarak.com/",
        "scope": "السعودية",
        "category": "خليجي",
        "profile_status": "❌ لم يبدأ",
        "profile_url": "",
        "search_active": False,
        "cli": None,
        "region": "Saudi Arabia",
        "notes": "منصة توظيف سعودية",
    },
]

CATEGORIES = {
    "حكومي": "🏛️ حكومي / رسمي",
    "خليجي": "🌍 خليجي / إقليمي",
    "عالمي": "🌐 عالمي",
    "إقليمي": "🗺️ إقليمي",
}


def save_platforms_registry():
    """حفظ كتالوج المنصات في ملف JSON"""
    registry = {
        "last_updated": NOW_STR,
        "total_platforms": len(ALL_PLATFORMS),
        "platforms": ALL_PLATFORMS,
    }
    with open(PLATFORMS_JSON, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print(f"✅ حُفظ كتالوج {len(ALL_PLATFORMS)} منصة في: {PLATFORMS_JSON}")


def search_linkedin_24h():
    """البحث على LinkedIn عن وظائف مدير تسويق في السعودية"""
    cli_path = SKILLS_DIR / "linkedin-search" / "cli" / "src" / "cli.ts"
    if not cli_path.exists():
        print("⚠️  LinkedIn CLI غير موجود — تخطي")
        return []

    print("\n🔍 جارٍ البحث على LinkedIn (مدير تسويق / الرياض)...")
    try:
        result = subprocess.run(
            [
                BUN_BIN, "run", str(cli_path),
                "--query", "مدير تسويق OR Marketing Director",
                "--location", "Saudi Arabia",
                "--jobage", "7",
                "--format", "json",
                "-n", "25",
            ],
            capture_output=True, text=True, timeout=90, cwd=str(REPO_ROOT),
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            jobs = data if isinstance(data, list) else data.get("jobs", [])
            print(f"   LinkedIn: وجدت {len(jobs)} وظيفة")
            return jobs
    except Exception as e:
        print(f"   LinkedIn: خطأ — {e}")
    return []


def search_freehire():
    """البحث على Freehire عن وظائف مدير تسويق"""
    cli_path = SKILLS_DIR / "freehire-search" / "cli" / "src" / "cli.ts"
    if not cli_path.exists():
        print("⚠️  Freehire CLI غير موجود — تخطي")
        return []

    print("\n🔍 جارٍ البحث على Freehire (مدير تسويق / الخليج)...")
    try:
        result = subprocess.run(
            [
                BUN_BIN, "run", str(cli_path),
                "--query", "Marketing Director",
                "--location", "Saudi Arabia",
                "--format", "json",
                "-n", "15",
            ],
            capture_output=True, text=True, timeout=90, cwd=str(REPO_ROOT),
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            jobs = data if isinstance(data, list) else data.get("jobs", [])
            print(f"   Freehire: وجدت {len(jobs)} وظيفة")
            return jobs
    except Exception as e:
        print(f"   Freehire: خطأ — {e}")
    return []


def load_existing_ids():
    """تحميل معرّفات الوظائف الموجودة لتجنب التكرار"""
    ids = set()
    urls = set()
    if TRACKER_CSV.exists():
        with open(TRACKER_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ids.add(row.get("ID", "").strip())
                url = row.get("رابط الوظيفة (Job URL)", "").strip()
                if url:
                    urls.add(url)
    return ids, urls


def get_next_id(existing_ids):
    """توليد معرّف وظيفة جديد SA-XXX"""
    nums = []
    for eid in existing_ids:
        if eid.startswith("SA-") and eid[3:].isdigit():
            nums.append(int(eid[3:]))
    next_num = max(nums, default=0) + 1
    return f"SA-{next_num:03d}"


def add_jobs_to_tracker(new_jobs_raw, platform_name, existing_ids, existing_urls):
    """إضافة وظائف جديدة إلى الـ CSV"""
    added = 0
    new_rows = []

    for job in new_jobs_raw:
        url = (job.get("url") or job.get("link") or job.get("job_url") or "").strip()
        if not url or url in existing_urls:
            continue

        title = (
            job.get("title") or job.get("job_title") or job.get("position") or "Marketing Director"
        ).strip()
        company = (job.get("company") or job.get("company_name") or "").strip()
        location = (job.get("location") or job.get("city") or "الرياض").strip()
        if not company:
            continue

        job_id = get_next_id(existing_ids)
        existing_ids.add(job_id)
        existing_urls.add(url)

        new_rows.append({
            "ID": job_id,
            "وقت وتاريخ الإضافة (Added Time)": NOW_STR,
            "اسم الشركة (Company)": company,
            "المسمى الوظيفي (Job Title)": title,
            "طريقة التقديم (Application Method)": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
            "المنصة / المصدر (Platform)": platform_name,
            "المدينة (City)": location if "رياض" in location.lower() or "riyadh" in location.lower() else location,
            "رابط الوظيفة (Job URL)": url,
            "نسبة التوافق (Fit Score %)": "80%",
            "حالة التقديم (Status)": "جاهز للتقديم",
            "مسؤول التوظيف / جهة الاتصال (Contact)": "",
            "الراتب المستهدف (Salary)": "أساسي 8,000 / باكدج 10,000",
            "نسخة السيرة الذاتية (CV File)": "cv/marketing-director-hsn.pdf",
            "تاريخ المتابعة (Next Follow-up)": "",
            "ملاحظات وتأكيد التقديم (Notes)": f"وظيفة مكتشفة تلقائياً من {platform_name} بتاريخ {NOW_STR}",
        })
        added += 1

    if new_rows:
        fieldnames = [
            "ID", "وقت وتاريخ الإضافة (Added Time)", "اسم الشركة (Company)",
            "المسمى الوظيفي (Job Title)", "طريقة التقديم (Application Method)",
            "المنصة / المصدر (Platform)", "المدينة (City)", "رابط الوظيفة (Job URL)",
            "نسبة التوافق (Fit Score %)", "حالة التقديم (Status)",
            "مسؤول التوظيف / جهة الاتصال (Contact)", "الراتب المستهدف (Salary)",
            "نسخة السيرة الذاتية (CV File)", "تاريخ المتابعة (Next Follow-up)",
            "ملاحظات وتأكيد التقديم (Notes)",
        ]
        with open(TRACKER_CSV, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for row in new_rows:
                writer.writerow(row)
        print(f"   ✅ أُضيف {added} وظيفة جديدة إلى الـ tracker")
    else:
        print("   ℹ️  لا توجد وظائف جديدة لإضافتها (كلها موجودة أو بدون رابط)")

    return added


def rebuild_dashboard():
    """إعادة بناء الداشبورد"""
    build_script = REPO_ROOT / "tools" / "build_online_dashboard.py"
    if build_script.exists():
        print("\n🔨 جارٍ إعادة بناء الداشبورد...")
        result = subprocess.run(
            [sys.executable, str(build_script)],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            print("   ✅ الداشبورد مُحدَّث بنجاح")
        else:
            print(f"   ⚠️  خطأ في الداشبورد: {result.stderr[:300]}")
    else:
        print("   ⚠️  build_online_dashboard.py غير موجود")


def git_push():
    """رفع التحديثات على GitHub"""
    print("\n📤 جارٍ رفع التحديثات على GitHub...")
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(REPO_ROOT), check=True,
                       capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"🌐 اكتشاف منصات + تحديث داشبورد — {NOW_STR}"],
            cwd=str(REPO_ROOT), check=True, capture_output=True,
        )
        subprocess.run(["git", "push"], cwd=str(REPO_ROOT), check=True,
                       capture_output=True)
        print("   ✅ تم الرفع بنجاح على GitHub Pages")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  خطأ في git: {e}")


def print_summary(total_added):
    """طباعة ملخص التقرير"""
    print("\n" + "=" * 60)
    print("📊 ملخص اكتشاف المنصات")
    print("=" * 60)

    by_cat = {}
    for p in ALL_PLATFORMS:
        cat = CATEGORIES.get(p["category"], p["category"])
        by_cat.setdefault(cat, []).append(p)

    for cat, platforms in sorted(by_cat.items()):
        print(f"\n{cat}:")
        for p in platforms:
            status = p["profile_status"]
            print(f"  • {p['name_ar']:20s} ({p['name_en']:25s}) — {status}")

    print(f"\n📌 إجمالي المنصات المكتشفة: {len(ALL_PLATFORMS)}")
    print(f"✅ منصات مكتملة 100%: {sum(1 for p in ALL_PLATFORMS if '100%' in p['profile_status'])}")
    print(f"🟡 منصات جزئية: {sum(1 for p in ALL_PLATFORMS if '87%' in p['profile_status'])}")
    print(f"❌ منصات لم تُبدأ: {sum(1 for p in ALL_PLATFORMS if 'لم يبدأ' in p['profile_status'])}")
    print(f"➕ وظائف مُضافة جديدة: {total_added}")
    print(f"\n🔗 الداشبورد: https://hsn96srhan.github.io/ai-job-search/")
    print("=" * 60)


def main():
    print("🚀 بدء اكتشاف كل منصات التوظيف في السعودية والخليج")
    print(f"🕐 الوقت: {NOW_STR} (الرياض)\n")

    # 1. حفظ كتالوج المنصات
    save_platforms_registry()

    # 2. تحميل الوظائف الموجودة
    existing_ids, existing_urls = load_existing_ids()
    print(f"\n📋 الوظائف الموجودة في الـ tracker: {len(existing_ids)}")

    total_added = 0

    # 3. بحث LinkedIn
    linkedin_jobs = search_linkedin_24h()
    if linkedin_jobs:
        added = add_jobs_to_tracker(
            linkedin_jobs, "LinkedIn (لينكد إن السعودية)",
            existing_ids, existing_urls
        )
        total_added += added

    # 4. بحث Freehire
    freehire_jobs = search_freehire()
    if freehire_jobs:
        added = add_jobs_to_tracker(
            freehire_jobs, "Freehire (ATS Aggregator)",
            existing_ids, existing_urls
        )
        total_added += added

    # 5. إعادة بناء الداشبورد
    rebuild_dashboard()

    # 6. رفع على GitHub
    git_push()

    # 7. طباعة الملخص
    print_summary(total_added)


if __name__ == "__main__":
    main()
