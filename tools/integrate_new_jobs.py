#!/usr/bin/env python3
"""Integrate all evaluated jobs from the past week into the tracker and update dashboard."""

import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"
riyadh_tz = timezone(timedelta(hours=3))
now = datetime.now(riyadh_tz)
now_str = now.strftime("%Y-%m-%d %I:%M %p").replace("AM", "ص").replace("PM", "م")
followup_date = (now + timedelta(days=3)).strftime("%Y-%m-%d")

# Read existing rows to get current count and verify duplicates
existing_ids = set()
existing_clean_urls = set()
with open(TRACKER_CSV, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

last_num = 0
for r in rows:
    if r and r[0].startswith("SA-"):
        try:
            num = int(r[0].replace("SA-", ""))
            if num > last_num:
                last_num = num
        except ValueError:
            pass
    if len(r) > 7:
        u = r[7].strip()
        if u:
            existing_clean_urls.add(re.sub(r'\?.*$', '', u).rstrip('/'))
            m = re.search(r'(\d{8,12})', u)
            if m:
                existing_ids.add(m.group(1))

print(f"Current highest ID: SA-{last_num:03d} (Total rows: {len(rows)})")

NEW_ENTRIES = [
    # --- Top Qualified Marketing Roles ---
    {
        "company": "Gathern | جاذر إن",
        "title": "Director of Growth",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4489633531",
        "fit": "97%",
        "status": "جاهز للتقديم",
        "contact": "Executive Talent Acquisition (Gathern)",
        "salary": "أساسي 25,000 / باكدج 32,000+",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "فرصة قيادية استثنائية: مدير النمو لقيادة الاستحواذ والتوسع بشركة جاذر إن (يونيكورن الضيافة السعودي المدعوم من صندوق الاستثمارات العامة - جولة 270 مليون ريال) - التقديم متاح يدوياً بنقرة واحدة عبر لينكد إن"
    },
    {
        "company": "evercare (إيفر كير)",
        "title": "Marketing Director",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4486683944",
        "fit": "96%",
        "status": "جاهز للتقديم",
        "contact": "Board & Executive Search",
        "salary": "أساسي 22,000 / باكدج 28,000+",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "شاغر مدير تسويق تنفيذي لقيادة استراتيجيات البراند والنمو والعمليات التسويقية للرعاية الصحية في الرياض - تقديم سريع Easy Apply"
    },
    {
        "company": "Lesha Capital",
        "title": "Vice President - Marketing & Communications",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4462290820",
        "fit": "95%",
        "status": "جاهز للتقديم",
        "contact": "Talent Acquisition Team",
        "salary": "أساسي 30,000 / باكدج 40,000+",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "منصب نائب رئيس التسويق والاتصال المؤسسي بشركة لشا كابيتال الاستثمارية بالرياض - شاغر تنفيذي رفيع بتقديم سريع عبر لينكد إن"
    },
    {
        "company": "Axelerated Solutions (AXS)",
        "title": "Marketing Manager (Head of Marketing)",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4488830406",
        "fit": "95%",
        "status": "جاهز للتقديم",
        "contact": "Leadership Hiring Team",
        "salary": "أساسي 18,000 / باكدج 24,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "قيادة وتأسيس قسم التسويق لشركة الحلول التقنية المتقدمة B2B بالرياض - متاح للتقديم اليدوي السريع"
    },
    {
        "company": "CEER Motors (سير للسيارات الكهربائية)",
        "title": "Senior Manager, Paid Media Performance and MarTech",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / CEER Careers",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487295354",
        "fit": "94%",
        "status": "جاهز للتقديم",
        "contact": "Ceer Talent Acquisition",
        "salary": "أساسي 22,000 / باكدج 28,000+",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "قيادة الأداء الإعلاني وتقنيات التسويق الرقمي MarTech لشركة السيارات الكهربائية السعودية الأولى (صندوق الاستثمارات العامة PIF)"
    },
    {
        "company": "دياري | Dyari (تحالف التطوير العقاري)",
        "title": "Marketing Manager",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4486640905",
        "fit": "94%",
        "status": "جاهز للتقديم",
        "contact": "Executive Management",
        "salary": "أساسي 16,000 / باكدج 20,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "إدارة التسويق لتحالف دياري العقاري بالرياض لدعم مشاريع رؤية 2030 - متاح للتقديم السريع المباشر"
    },
    {
        "company": "Canonical (كانونيكال - مطورو Ubuntu)",
        "title": "Senior Product Marketing Manager",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Canonical Careers",
        "city": "الرياض (عن بعد)",
        "url": "https://www.linkedin.com/jobs/view/4489634416",
        "fit": "93%",
        "status": "جاهز للتقديم",
        "contact": "Global Talent Acquisition",
        "salary": "أساسي 20,000 / باكدج 26,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "إدارة تسويق المنتجات التقنية وسحابة أوبونتو العالمية لشركة كانونيكال - الرياض مع مرونة كاملة للعمل عن بعد"
    },
    {
        "company": "Almarai - المراعي",
        "title": "Corporate E-Com Marketing Manager",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Almarai Careers",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487762253",
        "fit": "93%",
        "status": "جاهز للتقديم",
        "contact": "Almarai Recruitment",
        "salary": "أساسي 20,000 / باكدج 26,000+",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "قيادة تسويق التجارة الإلكترونية المؤسسية لشركة المراعي على مستوى منطقة الشرق الأوسط وشمال أفريقيا"
    },
    {
        "company": "WAFY (وافي)",
        "title": "Senior Marketing Manager",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487462915",
        "fit": "93%",
        "status": "جاهز للتقديم",
        "contact": "Talent Team WAFY",
        "salary": "أساسي 16,000 / باكدج 20,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "قيادة استراتيجيات التسويق والنمو الجماهيري لمنصة وافي الترفيهية والثقافية بالرياض - تقديم سريع Easy Apply"
    },
    {
        "company": "Canonical (كانونيكال)",
        "title": "Senior Marketing Automation Manager",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Canonical Careers",
        "city": "الرياض (عن بعد)",
        "url": "https://www.linkedin.com/jobs/view/4489648030",
        "fit": "92%",
        "status": "جاهز للتقديم",
        "contact": "Canonical Recruitment",
        "salary": "أساسي 18,000 / باكدج 24,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "قيادة أتمتة التسويق والعمليات الرقمية لمنظومة أوبونتو وحلول المؤسسات السحابية العالمية"
    },
    {
        "company": "Jobgether",
        "title": "Director of B2B Marketing",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "المملكة (عن بعد)",
        "url": "https://www.linkedin.com/jobs/view/4486955878",
        "fit": "93%",
        "status": "جاهز للتقديم",
        "contact": "Jobgether Global Hiring",
        "salary": "أساسي 22,000 / باكدج 28,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "مدير تسويق B2B لمنصة التوظيف والحلول الرقمية للشركات - وظيفة كاملة عن بعد داخل المملكة"
    },
    {
        "company": "Aramex (أرامكس)",
        "title": "Commercial Head - CEP",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Aramex Careers",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487276048",
        "fit": "92%",
        "status": "جاهز للتقديم",
        "contact": "Aramex HR KSA",
        "salary": "أساسي 20,000 / باكدج 25,000+",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "القيادة التجارية وتنمية الحصة السوقية لخدمات الشحن السريع والطرود السريعة لشركة أرامكس بالرياض"
    },
    {
        "company": "Qiddiya | القدية",
        "title": "Director Commercial and Partnerships - Film Studio",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Qiddiya Careers",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487644497",
        "fit": "91%",
        "status": "جاهز للتقديم",
        "contact": "Executive Talent Qiddiya",
        "salary": "أساسي 28,000 / باكدج 36,000+",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "قيادة الشراكات التجارية واستراتيجية الترويج واستقطاب الاستوديوهات العالمية لمشروع استوديو الأفلام بالقدية"
    },
    {
        "company": "Futu Holdings Limited (moomoo)",
        "title": "Strategic Partnerships & Influencer Lead - KSA",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4450451123",
        "fit": "91%",
        "status": "جاهز للتقديم",
        "contact": "MENA Talent Acquisition",
        "salary": "أساسي 18,000 / باكدج 24,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "قيادة استراتيجية الشراكات وصناع المحتوى والنمو لمنصة التداول والاستثمار الرقمي العالمية moomoo بالسعودية"
    },
    {
        "company": "Eli Lilly and Company (إيلي ليلي)",
        "title": "Brand Manager / Senior Brand Manager",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Workday",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4488142218",
        "fit": "90%",
        "status": "جاهز للتقديم",
        "contact": "Eli Lilly Talent Acquisition",
        "salary": "أساسي 18,000 / باكدج 24,000+",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "إدارة البراند والحملات التسويقية لشركة الأدوية العالمية إيلي ليلي في المملكة - التقديم عبر بوابة Workday"
    },
    {
        "company": "HAMS.AI | همس (للذكاء الاصطناعي)",
        "title": "Senior Marketing Specialist",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487145541",
        "fit": "90%",
        "status": "جاهز للتقديم",
        "contact": "HR Hams.AI",
        "salary": "أساسي 12,000 / باكدج 15,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "قيادة الحملات التسويقية الميدانية والرقمية لشركة الذكاء الاصطناعي السعودية بالرياض - تقديم سريع Easy Apply"
    },
    {
        "company": "AlKhalejiah | الخليجية للإعلان",
        "title": "Senior Marketing Specialist",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487459347",
        "fit": "90%",
        "status": "جاهز للتقديم",
        "contact": "Commercial Department",
        "salary": "أساسي 12,000 / باكدج 15,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "شاغر تسويقي متقدم بالقسم التجاري لدى الشركة الخليجية للإعلان والترويج بالرياض"
    },
    {
        "company": "Canonical (كانونيكال)",
        "title": "Senior Communications Manager - Analyst Relations",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Canonical Careers",
        "city": "الرياض (عن بعد)",
        "url": "https://www.linkedin.com/jobs/view/4489627906",
        "fit": "89%",
        "status": "جاهز للتقديم",
        "contact": "Canonical Communications",
        "salary": "أساسي 18,000 / باكدج 24,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "إدارة الاتصالات المؤسسية والعلاقات مع المحللين الدوليين لشركة كانونيكال - مرونة كاملة للعمل عن بعد"
    },
    {
        "company": "Jeeny (جيني)",
        "title": "Social Media & Communication Specialist",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4489438420",
        "fit": "88%",
        "status": "جاهز للتقديم",
        "contact": "Jeeny HR KSA",
        "salary": "أساسي 10,000 / باكدج 13,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "إدارة منصات التواصل الاجتماعي والاتصال التسويقي لتطبيق جيني للنقل الذكي بالرياض"
    },
    {
        "company": "Serva (سيرفا للتكنولوجيا)",
        "title": "Creative Marketing Specialist",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487498827",
        "fit": "88%",
        "status": "جاهز للتقديم",
        "contact": "Serva Hiring",
        "salary": "أساسي 10,000 / باكدج 13,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "أخصائي تسويق إبداعي وبناء الهوية لشركة تقنية سعودية ناشئة في الرياض"
    },
    {
        "company": "Omni Middle East Food Company (أومني)",
        "title": "Marketing Associate (Riyadh F&B Sector)",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4486684091",
        "fit": "87%",
        "status": "جاهز للتقديم",
        "contact": "F&B Marketing Lead",
        "salary": "أساسي 8,500 / باكدج 11,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "إدارة الحملات الميدانية والرقمية لقطاع المطاعم والأغذية بالرياض وشراكات تطبيقات التوصيل"
    },
    {
        "company": "TAWANTECH (توان تك للحلول المصرفية)",
        "title": "Marketing Specialist - Banking",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4488794099",
        "fit": "87%",
        "status": "جاهز للتقديم",
        "contact": "Fintech Talent Team",
        "salary": "أساسي 10,000 / باكدج 13,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تسويق الحلول المصرفية والمنتجات البنكية الرقمية لشركة توان تك بالرياض"
    },
    {
        "company": "AL Etihad Elevators (مصاعد الاتحاد)",
        "title": "Digital Marketing Specialist",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487471841",
        "fit": "86%",
        "status": "جاهز للتقديم",
        "contact": "Al Etihad HR",
        "salary": "أساسي 9,000 / باكدج 11,500",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "إدارة التسويق الرقمي وتوليد العملاء المحتملين B2B لشركة مصاعد الاتحاد بالرياض"
    },
    {
        "company": "Aleph (أليف - شريك X الإعلاني)",
        "title": "Client Solution Manager - X",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487347994",
        "fit": "87%",
        "status": "جاهز للتقديم",
        "contact": "Aleph Talent Group",
        "salary": "أساسي 12,000 / باكدج 16,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "إدارة الحلول الإعلانية والتسويقية لمنصة X (تويتر) لدى الشريك الإعلاني الرسمي أليف بالرياض"
    },
    {
        "company": "xma games (إكس إم إيه للألعاب)",
        "title": "Sales And Marketing Specialist",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487383187",
        "fit": "85%",
        "status": "جاهز للتقديم",
        "contact": "Hiring Manager",
        "salary": "أساسي 8,500 / باكدج 11,000",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تسويق الألعاب والمنتجات الترفيهية الرقمية بالرياض - تقديم سريع عبر لينكد إن"
    },

    # --- Disqualified Roles (Tracked for complete transparency) ---
    {
        "company": "Maskan | مسكن العقارية",
        "title": "Marketing Specialist - Content creator",
        "method": "✉️ ايميل مباشر (Email - آلي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487456983",
        "fit": "40%",
        "status": "تم التخطي",
        "contact": "amin@maskanre.sa",
        "salary": "مستبعد (شروط توطين)",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تم التخطي تلقائياً: يشترط صراحة في الإعلان الجنسية السعودية حصراً (Nationality: Saudi Citizen Male or Female)"
    },
    {
        "company": "Zid | زد (للتجارة الإلكترونية)",
        "title": "Lead, Sectors Growth",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4487718702",
        "fit": "50%",
        "status": "تم التخطي",
        "contact": "Growth Team (Zid)",
        "salary": "مستبعد (شروط توطين)",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تم التخطي تلقائياً: يشترط صراحة في متطلبات الوظيفة الجنسية السعودية (Saudi national, based in Riyadh)"
    },
    {
        "company": "Roche Diagnostics (روش الطبية)",
        "title": "Communications & Public Affairs Partner",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Roche Careers",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4488780210",
        "fit": "45%",
        "status": "تم التخطي",
        "contact": "Roche HR",
        "salary": "مستبعد (شروط توطين)",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تم التخطي تلقائياً: الإعلان مخصص حصرياً للمواطنين السعوديين (Open to Saudi nationals only)"
    },
    {
        "company": "TikTok (تيك توك)",
        "title": "Account Manager (Growth) - GBS",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / TikTok Careers",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4486528049",
        "fit": "45%",
        "status": "تم التخطي",
        "contact": "TikTok MENA Recruitment",
        "salary": "مستبعد (شروط توطين)",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تم التخطي تلقائياً: الوظيفة محددة للمواطنين السعوديين فقط (Only available to Saudi national citizens)"
    },
    {
        "company": "Potential HR Services & Consulting",
        "title": "Social Media Account Manager",
        "method": "⚡ ايزي ابلاي (Easy Apply - يدوي)",
        "platform": "LinkedIn Saudi Arabia",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4486913399",
        "fit": "45%",
        "status": "تم التخطي",
        "contact": "Recruiting Team",
        "salary": "مستبعد (شروط توطين)",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تم التخطي تلقائياً: يشترط صراحة الجنسية السعودية في الشروط (Saudi nationality is required)"
    },
    {
        "company": "Le Méridien Hotels & Resorts (ميريديان مكة)",
        "title": "Dir-Sales & Marketing-A",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Marriott Careers",
        "city": "مكة المكرمة (حضوري)",
        "url": "https://www.linkedin.com/jobs/view/4486788002",
        "fit": "60%",
        "status": "تم التخطي",
        "contact": "Marriott Careers",
        "salary": "خارج نطاق المدينة",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تم التخطي تلقائياً: دوام حضوري كامل خارج الرياض (مكة المكرمة) والمستهدف الرياض أو العمل عن بعد"
    },
    {
        "company": "Guerlain (جيرلان - LVMH)",
        "title": "Brand Marketing Manager",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / LVMH Careers",
        "city": "جدة (حضوري)",
        "url": "https://www.linkedin.com/jobs/view/4485065951",
        "fit": "60%",
        "status": "تم التخطي",
        "contact": "LVMH Talent Team",
        "salary": "خارج نطاق المدينة",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تم التخطي تلقائياً: دوام حضوري كامل خارج الرياض (جدة) والمستهدف الرياض أو العمل عن بعد"
    },
    {
        "company": "Visa",
        "title": "COOP Trainee (Students)",
        "method": "🌐 بوابة خارجية (ATS - آلي)",
        "platform": "LinkedIn / Visa Careers",
        "city": "الرياض",
        "url": "https://www.linkedin.com/jobs/view/4464024283",
        "fit": "20%",
        "status": "تم التخطي",
        "contact": "University Relations",
        "salary": "مستبعد (تدريب طلابي)",
        "cv": "cv/marketing-director-hsn.pdf",
        "notes": "تم التخطي تلقائياً: تدريب جامعي لطلاب السنة الأخيرة (COOP Trainee) ولا يناسب خبرتك كمدير تسويق تنفيذي"
    }
]

added_count = 0
for item in NEW_ENTRIES:
    u = item["url"].strip()
    clean_u = re.sub(r'\?.*$', '', u).rstrip('/')
    m = re.search(r'(\d{8,12})', u)
    jid = m.group(1) if m else None

    if clean_u in existing_clean_urls or (jid and jid in existing_ids):
        print(f"Skipping already existing: {item['company']} - {item['title']}")
        continue

    last_num += 1
    new_id = f"SA-{last_num:03d}"
    
    new_row = [
        new_id,
        now_str,
        item["company"],
        item["title"],
        item["method"],
        item["platform"],
        item["city"],
        item["url"],
        item["fit"],
        item["status"],
        item["contact"],
        item["salary"],
        item["cv"],
        followup_date,
        item["notes"]
    ]

    with open(TRACKER_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(new_row)

    existing_clean_urls.add(clean_u)
    if jid:
        existing_ids.add(jid)
    added_count += 1
    print(f"✓ Added [{new_id}] {item['company']} - {item['title']} ({item['status']})")

print(f"\nDone! Added {added_count} new entries to tracker. Total jobs is now {last_num}.")

