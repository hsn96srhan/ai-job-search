#!/usr/bin/env python3
"""Strictly reclassify all 59 jobs with exact verified application method."""

import csv
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"

# Verified classifications:
# 1. EMAIL JOBS (7):
EMAIL_IDS = {"SA-003", "SA-009", "SA-012", "SA-040", "SA-045", "SA-046", "SA-056"}

# 2. EXTERNAL ATS PORTAL JOBS (19):
ATS_IDS = {
    "SA-005", # Savills Middle East (Taleo/Careers Portal)
    "SA-008", # Red Sea Global (RSG Portal)
    "SA-013", # IHG Hotels & Resorts (IHG Careers)
    "SA-014", # Qureos (Offsite ATS link)
    "SA-021", # Hilton (Oracle HCM Cloud - Applied)
    "SA-025", # Calo Inc. (Calo Careers / Greenhouse)
    "SA-026", # qlub (Ashby ATS - Applied)
    "SA-027", # AstraZeneca (Eightfold AI - Closed)
    "SA-028", # Red Sea Global (RSG Portal)
    "SA-029", # IHG Hotels & Resorts (IHG Careers)
    "SA-031", # IHG Hotels & Resorts (IHG Careers)
    "SA-034", # Novotel Hotels (Accor Careers - Skipped: Saudi Only)
    "SA-038", # dentsu (SmartRecruiters)
    "SA-042", # dentsu (SmartRecruiters)
    "SA-047", # dentsu (SmartRecruiters)
    "SA-048", # Fragomen (Workday)
    "SA-051", # PepsiCo (PepsiCo Jobs)
    "SA-052", # Mumzworld.com (Teamtailor ATS - Applied)
    "SA-053", # Shangri-La Group (Careers Portal - Skipped: Jeddah)
}

# 3. All remaining are EASY APPLY (33):
# Includes Qiddiya (SA-004, SA-037), webook.com (SA-023), Red Sea Global (SA-022),
# Elfaleh (SA-001, SA-035), HungerStation (SA-002), Setup.sa (SA-006, SA-044), etc.

def run():
    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    fieldnames = [
        "ID",
        "وقت وتاريخ الإضافة (Added Time)",
        "اسم الشركة (Company)",
        "المسمى الوظيفي (Job Title)",
        "طريقة التقديم (Application Method)",
        "المنصة / المصدر (Platform)",
        "المدينة (City)",
        "رابط الوظيفة (Job URL)",
        "نسبة التوافق (Fit Score %)",
        "حالة التقديم (Status)",
        "مسؤول التوظيف / جهة الاتصال (Contact)",
        "الراتب المستهدف (Salary)",
        "نسخة السيرة الذاتية (CV File)",
        "تاريخ المتابعة (Next Follow-up)",
        "ملاحظات وتأكيد التقديم (Notes)"
    ]

    updated_rows = []
    c_easy = 0
    c_email = 0
    c_ats = 0

    for r in reader:
        jid = r["ID"]
        comp = r["اسم الشركة (Company)"]
        title = r["المسمى الوظيفي (Job Title)"]
        status = r["حالة التقديم (Status)"]
        notes = r["ملاحظات وتأكيد التقديم (Notes)"]

        if jid in EMAIL_IDS:
            method = "✉️ ايميل مباشر (Email - آلي)"
            c_email += 1
        elif jid in ATS_IDS:
            method = "🌐 بوابة خارجية (ATS - آلي)"
            c_ats += 1
        else:
            method = "⚡ ايزي ابلاي (Easy Apply - يدوي)"
            c_easy += 1

        # Refine notes for precision
        if method == "⚡ ايزي ابلاي (Easy Apply - يدوي)":
            if "تم التخطي" not in status:
                notes = "شاغر تقديم سريع (LinkedIn Easy Apply) مخصص لتقديمك اليدوي بضغطة زر دون تدخل البوت"
        elif method == "🌐 بوابة خارجية (ATS - آلي)":
            if jid == "SA-021":
                notes = "تم التقديم بنجاح عبر بوابة Oracle HCM Cloud بعد التحقق الذاتي من كود OTP المستلم على الإيميل (411037)"
            elif jid == "SA-026":
                notes = "تم التقديم آلياً بنجاح عبر بوابة Ashby الدولية للتوظيف مع إرفاق السيرة الذاتية PDF لحسن سرحان"
            elif jid == "SA-052":
                notes = "تم التقديم آلياً بنجاح عبر بوابة Teamtailor وتحميل السيرة الذاتية (App ID: b86179e9-9376-47e2-95be-f3d1f831ddc9)"
            elif jid == "SA-027":
                notes = "تم فحص بوابة Eightfold التابعة لأسترازينيكا وتبيّن إغلاق الشاغر رسمياً من جهة العمل وعدم قبول طلبات جديدة"
            elif jid == "SA-034":
                notes = "تم التخطي تلقائياً: الشاغر يشترط الجنسية السعودية فقط عبر بوابة توظيف Accor"
            elif jid == "SA-053":
                notes = "تم التخطي تلقائياً: دوام حضوري خارج الرياض (جدة) عبر بوابة توظيف Shangri-La"
            else:
                notes = "بوابة توظيف خارجية ومطابقة لمعاييرك، مدرجة في طابور محرك التقديم الآلي بالمتصفح"

        r["طريقة التقديم (Application Method)"] = method
        r["ملاحظات وتأكيد التقديم (Notes)"] = notes
        updated_rows.append(r)

    with open(TRACKER_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"✓ تم تحديث وتدقيق تصنيف الـ 59 شاغر بنجاح:")
    print(f"  - ⚡ ايزي ابلاي (Easy Apply - يدوي): {c_easy}")
    print(f"  - ✉️ ايميل مباشر (Email - آلي): {c_email}")
    print(f"  - 🌐 بوابة خارجية (ATS - آلي): {c_ats}")

if __name__ == "__main__":
    run()
