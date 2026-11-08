#!/usr/bin/env python3
"""Comprehensively audit and fix Platform/Source and Application Methods for all 59 jobs."""

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"

# True External ATS Portals (specifically verified offsite ATS):
TRUE_EXTERNAL_ATS = {
    "SA-021": ("Hilton", "LinkedIn / Oracle HCM", "تم التقديم بنجاح عبر بوابة Oracle HCM Cloud بعد التحقق الذاتي من كود OTP المستلم على الإيميل (411037)"),
    "SA-026": ("qlub", "LinkedIn / Ashby ATS", "تم التقديم آلياً بنجاح عبر بوابة Ashby الدولية للتوظيف مع إرفاق السيرة الذاتية ورابط لينكد إن"),
    "SA-027": ("AstraZeneca", "LinkedIn / Eightfold AI", "تم فحص بوابة Eightfold التابعة لأسترازينيكا وتبيّن إغلاق الشاغر رسمياً من جهة العمل وعدم قبول طلبات جديدة"),
    "SA-052": ("Mumzworld.com", "LinkedIn / Teamtailor", "تم التقديم آلياً بنجاح عبر بوابة Teamtailor وإكمال استبيان الإفصاح وتحميل السيرة الذاتية (App ID: b86179e9-9376-47e2-95be-f3d1f831ddc9)"),
    "SA-005": ("Savills Middle East", "LinkedIn / Career Portal", "بوابة توظيف خارجية لمجموعة سافيلز العقارية"),
    "SA-008": ("Red Sea Global", "LinkedIn / Career Portal", "بوابة توظيف خارجية لشركة البحر الأحمر الدولية"),
    "SA-013": ("IHG Hotels & Resorts", "LinkedIn / IHG Careers", "بوابة توظيف خارجية لمجموعة فنادق إنتركونتيننتال"),
    "SA-025": ("Calo Inc.", "LinkedIn / Calo ATS", "بوابة توظيف خارجية لشركة كالو"),
    "SA-028": ("Red Sea Global", "LinkedIn / Career Portal", "بوابة توظيف خارجية لشركة البحر الأحمر الدولية"),
    "SA-029": ("IHG Hotels & Resorts", "LinkedIn / IHG Careers", "بوابة توظيف خارجية لمجموعة فنادق إنتركونتيننتال"),
    "SA-031": ("IHG Hotels & Resorts", "LinkedIn / IHG Careers", "بوابة توظيف خارجية لمجموعة فنادق إنتركونتيننتال"),
    "SA-034": ("Novotel Hotels", "LinkedIn / Accor Careers", "تم التخطي تلقائياً: الشاغر يشترط الجنسية السعودية فقط عبر بوابة Accor"),
    "SA-038": ("dentsu", "LinkedIn / SmartRecruiters", "بوابة توظيف خارجية لشبكة دينتسو العالمية"),
    "SA-042": ("dentsu", "LinkedIn / SmartRecruiters", "بوابة توظيف خارجية لشبكة دينتسو العالمية"),
    "SA-047": ("dentsu", "LinkedIn / SmartRecruiters", "بوابة توظيف خارجية لشبكة دينتسو العالمية"),
    "SA-048": ("Fragomen", "LinkedIn / Workday", "بوابة توظيف خارجية لمجموعة فراغومين الدولية"),
    "SA-051": ("PepsiCo", "LinkedIn / PepsiCo Careers", "بوابة توظيف خارجية لشركة بيبسيكو العالمية"),
    "SA-053": ("Shangri-La Group", "LinkedIn / Shangri-La Careers", "تم التخطي تلقائياً: دوام حضوري خارج الرياض (جدة)")
}

# Direct Email jobs (7 entries, verified SMTP submissions):
EMAIL_JOBS = {
    "SA-003": ("Sharaf DG (شرف دي جي)", "LinkedIn / إيميل مباشر", "recruitment@sharafdg.com", "تم التقديم بنجاح عبر الإيميل الرسمي للتوظيف recruitment@sharafdg.com مع إرفاق السيرة الذاتية PDF وتأكيد الاستلام"),
    "SA-009": ("شركة سحاب الجنوب العقارية", "LinkedIn / إيميل مباشر", "sscc-ksa@hotmail.com", "تم إرسال بريد التقديم الرسمي آلياً عبر SMTP إلى sscc-ksa@hotmail.com مع السيرة الذاتية المعتمدة"),
    "SA-012": ("RAM Systems Company", "LinkedIn / إيميل مباشر", "jobs@ramsys.com.sa", "تم إرسال بريد التقديم الرسمي آلياً عبر SMTP إلى jobs@ramsys.com.sa مع إرفاق السيرة الذاتية وتأكيد التسليم"),
    "SA-040": ("Mars SA", "LinkedIn / إيميل مباشر", "info@mars.sa", "تم التقديم بنجاح عبر الإيميل الرسمي للتوظيف info@mars.sa مع إرفاق السيرة الذاتية التنفيذية لحسن سرحان"),
    "SA-045": ("Corebridge Financial", "LinkedIn / إيميل مباشر", "TalentandInclusion@corebridgefinancial.com", "تم التقديم آلياً عبر الإيميل الرسمي TalentandInclusion@corebridgefinancial.com مع إرفاق السيرة الذاتية PDF"),
    "SA-046": ("Sharaf DG", "LinkedIn / إيميل مباشر", "recruitment@sharafdg.com", "تم التقديم بنجاح عبر الإيميل الرسمي للتوظيف recruitment@sharafdg.com مع إرفاق السيرة الذاتية وتأكيد الرد الآلي"),
    "SA-056": ("Astek Middle East", "LinkedIn / إيميل مباشر", "contact-astekme@astek-international.com", "تم التقديم آلياً عبر الإيميل الرسمي contact-astekme@astek-international.com بالسيرة الذاتية وخطاب التقديم")
}

def clean_all():
    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

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

    c_easy = 0
    c_email = 0
    c_ats = 0

    cleaned = []
    for r in rows:
        jid = r["ID"]
        comp = r["اسم الشركة (Company)"]
        title = r["المسمى الوظيفي (Job Title)"]
        stat = r["حالة التقديم (Status)"]
        url = r["رابط الوظيفة (Job URL)"]

        if jid in EMAIL_JOBS:
            method = "✉️ ايميل مباشر (Email - آلي)"
            platform = EMAIL_JOBS[jid][1]
            contact = EMAIL_JOBS[jid][2]
            notes = EMAIL_JOBS[jid][3]
            c_email += 1
        elif jid in TRUE_EXTERNAL_ATS:
            method = "🌐 بوابة خارجية (ATS - آلي)"
            platform = TRUE_EXTERNAL_ATS[jid][1]
            notes = TRUE_EXTERNAL_ATS[jid][2]
            contact = r.get("مسؤول التوظيف / جهة الاتصال (Contact)", "مسؤول التوظيف")
            c_ats += 1
        else:
            method = "⚡ ايزي ابلاي (Easy Apply - يدوي)"
            platform = "LinkedIn (لينكد إن السعودية)"
            contact = r.get("مسؤول التوظيف / جهة الاتصال (Contact)", "مسؤول التوظيف")
            if "تم التخطي" in stat:
                notes = r.get("ملاحظات وتأكيد التقديم (Notes)", "تم التخطي لمعايير الموقع أو الجنسية")
            else:
                notes = "شاغر تقديم سريع (LinkedIn Easy Apply) مخصص لتقديمك اليدوي بضغطة زر واحدة دون تدخل البوت"
            c_easy += 1

        r["طريقة التقديم (Application Method)"] = method
        r["المنصة / المصدر (Platform)"] = platform
        r["مسؤول التوظيف / جهة الاتصال (Contact)"] = contact
        r["ملاحظات وتأكيد التقديم (Notes)"] = notes
        cleaned.append(r)

    with open(TRACKER_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned)

    print(f"✓ تم تنظيف وتصحيح المنصة وطريقة التقديم لجميع الـ 59 شاغر:")
    print(f"  - ⚡ ايزي ابلاي (Easy Apply - يدوي): {c_easy}")
    print(f"  - ✉️ ايميل مباشر (Email - آلي): {c_email}")
    print(f"  - 🌐 بوابة خارجية (ATS - آلي): {c_ats}")

if __name__ == "__main__":
    clean_all()
