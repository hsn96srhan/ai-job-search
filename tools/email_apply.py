#!/usr/bin/env python3
"""Email Auto Submission Tool for Job Applications.

Enables automated and semi-automated job application submissions via email (SMTP/Gmail).
Supports 100% Arabic or 100% English formatting (never mixed).
Attaches tailored CV (PDF), formats professional email body with proper text direction (RTL/LTR),
and logs the submission to the job search tracker.
"""

import argparse
import csv
import mimetypes
import os
import re
import smtplib
import ssl
import sys
from datetime import date
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "job_search_tracker.csv"
DEFAULT_CV = REPO_ROOT / "cv" / "marketing-director-hsn.pdf"


def load_env_file():
    """Load configuration from .env, jobs.env, or jobs.env.txt if present."""
    for filename in [".env", "jobs.env", "jobs.env.txt"]:
        env_path = REPO_ROOT / filename
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                content = f.read().lstrip("\ufeff")
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if "PASS" in k.upper():
                            v = v.replace(" ", "")
                        if k not in os.environ:
                            os.environ[k] = v
                    elif len(line.replace(" ", "")) == 16 and "SMTP_PASSWORD" not in os.environ:
                        os.environ["SMTP_PASSWORD"] = line.replace(" ", "")


load_env_file()

# Configuration defaults
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "hsn96srhan@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", os.environ.get("GMAIL_APP_PASSWORD", "")).replace(" ", "")
CANDIDATE_NAME_EN = "Hassan Sarhan"
CANDIDATE_NAME_AR = "حسن سرحان"
CANDIDATE_PHONE = os.environ.get("CANDIDATE_PHONE", "+966 50 626 7542")
CANDIDATE_TITLE_EN = "HRSD-Accredited Marketing Director"
CANDIDATE_TITLE_AR = "مدير تسويق تنفيذي معتمد (HRSD)"
CANDIDATE_LOCATION_EN = "Riyadh, Saudi Arabia"
CANDIDATE_LOCATION_AR = "الرياض، المملكة العربية السعودية"
CANDIDATE_LINKEDIN = os.environ.get("CANDIDATE_LINKEDIN", "https://www.linkedin.com/in/srhan-jr/")
CANDIDATE_WEBSITE = os.environ.get("CANDIDATE_WEBSITE", "https://hsn96srhan.github.io/hsn/")


def detect_language(company, role, pitch=None):
    """Determine whether the email should be pure Arabic or pure English."""
    combined = f"{company} {role} {pitch or ''}"
    arabic_count = len(re.findall(r"[\u0600-\u06FF]", combined))
    return "ar" if arabic_count >= 8 else "en"


def build_email_content_arabic(company, role, custom_pitch=None):
    """Generate 100% Arabic email subject, plain text, and RTL HTML."""
    subject = f"طلب تقديم: {role} - {CANDIDATE_NAME_AR} ({CANDIDATE_TITLE_AR})"

    default_pitch = (
        f"يسرني التقدم لشغل منصب {role} لدى {company}.\n\n"
        f"بصفتي مدير تسويق تنفيذي معتمد من وزارة الموارد البشرية والتنمية الاجتماعية (HRSD) في الرياض وبخبرة تتجاوز 8 سنوات، "
        f"قمت بتوجيه وإدارة ميزانيات إعلانية تفوق 7,000,000 ريال سعودي عبر كبرى منصات الأداء الرقمي، محققاً عوائد إنفاق إعلاني (ROAS) "
        f"تصل إلى 25x مع خفض تكلفة الاستحواذ بنسبة 32% وبناء مسارات نمو المبيعات والتجارة الإلكترونية لتصل إلى 10,000,000 ريال شهرياً. "
        f"كما أشرفت على قيادة فرق عمل تنفيذية متعددة التخصصات تضم أكثر من 20 محترفاً في التسويق الرقمي والمبيعات وصناعة المحتوى الإبداعي.\n\n"
        f"يسعدني تسخير هذه الخبرة الميدانية واستراتيجيات النمو لدفع الخطط التوسعية لـ {company} وتحقيق مستهدفاتها البيعية والتسويقية."
    )

    pitch = custom_pitch.replace('\\n', '\n').strip() if custom_pitch else default_pitch

    plain_body = f"""السادة / فريق التوظيف في {company} المحترمين،

السلام عليكم ورحمة الله وبركاته،

{pitch}

أبرز المؤهلات والخبرات التنفيذية:
• الموقع والجاهزية: {CANDIDATE_LOCATION_AR} (جاهزية تامة للمباشرة)
• الاعتماد المهني: مدير تسويق معتمد من وزارة الموارد البشرية والتنمية الاجتماعية (HRSD)
• الأثر التجاري والمالي: إدارة ميزانيات تفوق 7,000,000 ريال | عوائد إعلانية (ROAS) تصل إلى 25x | بناء منظومات مبيعات حتى 10 مليون شهرياً
• قيادة الفرق: إدارة وتدريب فرق متعددة التخصصات تضم 20+ محترفاً عبر 4 أقسام

تجدون برفقة هذا البريد السيرة الذاتية المهنية للاطلاع، وأتطلع للتواصل معكم ومناقشة تفاصيل الفرصة.

وتفضلوا بقبول فائق التقدير والاحترام،

{CANDIDATE_NAME_AR} ({CANDIDATE_NAME_EN})
{CANDIDATE_TITLE_AR}
{CANDIDATE_LOCATION_AR}
جوال: {CANDIDATE_PHONE}
بريد إلكتروني: {SMTP_USER}
موقع ومعرض الأعمال: {CANDIDATE_WEBSITE}
لينكدإن: {CANDIDATE_LINKEDIN}
"""

    html_paragraphs = "".join(f"<p>{p.strip()}</p>" for p in pitch.split("\n\n") if p.strip())

    html_body = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"></head>
<body style="font-family: system-ui, -apple-system, 'Segoe UI', Tahoma, Arial, sans-serif; color: #1e293b; line-height: 1.8; font-size: 15px; text-align: right; direction: rtl;">
  <p>السادة / فريق التوظيف في <strong>{company}</strong> المحترمين،</p>
  <p>السلام عليكم ورحمة الله وبركاته،</p>
  
  {html_paragraphs}
  
  <div style="background-color: #f8fafc; border-right: 4px solid #16a34a; padding: 14px 18px; margin: 18px 0; border-radius: 6px; text-align: right; direction: rtl;">
    <strong style="color: #0f172a; display: block; margin-bottom: 8px;">أبرز المؤهلات والخبرات التنفيذية:</strong>
    <ul style="margin: 0; padding-right: 20px; color: #334155; list-style-type: disc;">
      <li><strong>الموقع والجاهزية:</strong> {CANDIDATE_LOCATION_AR} (جاهزية تامة للمباشرة)</li>
      <li><strong>الاعتماد المهني:</strong> مدير تسويق معتمد من وزارة الموارد البشرية والتنمية الاجتماعية (HRSD)</li>
      <li><strong>الأثر التجاري والمالي:</strong> إدارة ميزانيات تفوق 7,000,000 ريال · عوائد إعلانية (ROAS) تصل إلى 25x · بناء منظومات نمو ومبيعات حتى 10 مليون شهرياً</li>
      <li><strong>قيادة الفرق:</strong> إدارة وتدريب فرق متعددة التخصصات تضم 20+ محترفاً في التسويق والمبيعات والتقنية</li>
    </ul>
  </div>

  <p>تجدون برفقة هذا البريد السيرة الذاتية المهنية للاطلاع، وأتطلع للتواصل معكم ومناقشة تفاصيل الفرصة.</p>

  <p style="margin-top: 24px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
    وتفضلوا بقبول فائق التقدير والاحترام،<br>
    <strong>{CANDIDATE_NAME_AR} ({CANDIDATE_NAME_EN})</strong><br>
    <span style="color: #64748b;">{CANDIDATE_TITLE_AR}</span><br>
    <span style="color: #64748b;">{CANDIDATE_LOCATION_AR}</span><br>
    <span style="color: #2563eb;">📞 {CANDIDATE_PHONE}</span> · <span style="color: #2563eb;">✉️ {SMTP_USER}</span><br>
    <a href="{CANDIDATE_WEBSITE}" style="color: #2563eb; text-decoration: none; font-weight: bold;">🌐 الموقع الشخصي ومعرض الأعمال (Portfolio)</a> · <a href="{CANDIDATE_LINKEDIN}" style="color: #0284c7; text-decoration: none;">🔗 ملف لينكدإن المهني (LinkedIn)</a>
  </p>
</body>
</html>
"""
    return subject, plain_body, html_body


def build_email_content_english(company, role, custom_pitch=None):
    """Generate 100% English email subject, plain text, and LTR HTML."""
    subject = f"Application: {role} - {CANDIDATE_NAME_EN} ({CANDIDATE_TITLE_EN})"

    default_pitch = (
        f"I am writing to express my strong interest in the {role} position at {company}.\n\n"
        f"As an HRSD-accredited Marketing Director based in Riyadh with over 8 years of executive leadership, "
        f"I have directed more than 7,000,000 SAR in performance advertising budgets across Saudi Arabia and the GCC, "
        f"consistently delivering Return on Ad Spend (ROAS) up to 25x while reducing customer acquisition costs by 32%. "
        f"I have successfully led multidisciplinary teams of 20+ professionals across brand strategy, paid performance, "
        f"creative production, and e-commerce revenue engines.\n\n"
        f"Given {company}'s market expansion, I would welcome the opportunity to discuss how my hands-on growth methodology, "
        f"budget discipline, and deep knowledge of the Saudi market can accelerate your commercial goals."
    )

    pitch = custom_pitch.replace('\\n', '\n').strip() if custom_pitch else default_pitch

    plain_body = f"""Dear Hiring Team at {company},

{pitch}

Key Qualifications Overview:
- Location & Availability: {CANDIDATE_LOCATION_EN} (Immediate on-site availability)
- Ministry Accreditation: HRSD Certified Marketing Manager (Kingdom of Saudi Arabia)
- Commercial Impact: +7M SAR Ad Spend Directed | 5x-25x ROAS | Scaled D2C Revenue to 10M/Month
- Team Leadership: Supervised multidisciplinary teams of 20+ professionals across 4 divisions
- Direct Contact: {CANDIDATE_PHONE} | {SMTP_USER}

My complete tailored Executive CV is attached for your review. I look forward to speaking with your team.

Warm regards,

{CANDIDATE_NAME_EN}
{CANDIDATE_TITLE_EN}
{CANDIDATE_LOCATION_EN}
Phone: {CANDIDATE_PHONE}
Email: {SMTP_USER}
Portfolio / Website: {CANDIDATE_WEBSITE}
LinkedIn: {CANDIDATE_LINKEDIN}
"""

    html_paragraphs = "".join(f"<p>{p.strip()}</p>" for p in pitch.split("\n\n") if p.strip())

    html_body = f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.6; font-size: 15px; text-align: left; direction: ltr;">
  <p>Dear Hiring Team at <strong>{company}</strong>,</p>
  
  {html_paragraphs}
  
  <div style="background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 14px 18px; margin: 18px 0; border-radius: 6px; text-align: left; direction: ltr;">
    <strong style="color: #0f172a; display: block; margin-bottom: 6px;">Executive Qualifications Overview:</strong>
    <ul style="margin: 0; padding-left: 20px; color: #334155; list-style-type: disc;">
      <li><strong>Location & Status:</strong> {CANDIDATE_LOCATION_EN} (Immediate on-site availability)</li>
      <li><strong>Accreditation:</strong> HRSD Certified Marketing Manager (Ministry of Human Resources & Social Development)</li>
      <li><strong>Commercial Impact:</strong> +7,000,000 SAR Ad Spend Managed · Up to 25x ROAS · Scaled 10M/Mo Revenue</li>
      <li><strong>Team Leadership:</strong> Supervised cross-functional teams of 20+ across media buying, creative, and tech</li>
    </ul>
  </div>

  <p>My tailored Executive CV is attached to this email for your comprehensive review. I would welcome the opportunity to discuss how my expertise aligns with your strategic mandates.</p>

  <p style="margin-top: 24px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
    Warm regards,<br>
    <strong>{CANDIDATE_NAME_EN}</strong><br>
    <span style="color: #64748b;">{CANDIDATE_TITLE_EN}</span><br>
    <span style="color: #64748b;">{CANDIDATE_LOCATION_EN}</span><br>
    <span style="color: #2563eb;">📞 {CANDIDATE_PHONE}</span> · <span style="color: #2563eb;">✉️ {SMTP_USER}</span><br>
    <a href="{CANDIDATE_WEBSITE}" style="color: #2563eb; text-decoration: none; font-weight: bold;">🌐 Portfolio & Website</a> · <a href="{CANDIDATE_LINKEDIN}" style="color: #0284c7; text-decoration: none;">🔗 LinkedIn Profile</a>
  </p>
</body>
</html>
"""
    return subject, plain_body, html_body


def build_email_content(company, role, custom_pitch=None, lang="auto"):
    """Route to 100% Arabic or 100% English email builder."""
    resolved_lang = detect_language(company, role, custom_pitch) if lang == "auto" else lang
    if resolved_lang == "ar":
        return build_email_content_arabic(company, role, custom_pitch)
    else:
        return build_email_content_english(company, role, custom_pitch)


def create_message(to_email, company, role, cv_path, custom_pitch=None, lang="auto"):
    """Construct MIME message with attachments."""
    subject, plain_body, html_body = build_email_content(company, role, custom_pitch, lang)

    msg = MIMEMultipart("mixed")
    msg["From"] = f"{CANDIDATE_NAME_EN} <{SMTP_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Reply-To"] = SMTP_USER

    # Alternative part for text/plain and text/html
    msg_alt = MIMEMultipart("alternative")
    msg_alt.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg_alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(msg_alt)

    # Attach CV
    cv_file = Path(cv_path) if cv_path else DEFAULT_CV
    if cv_file.exists():
        ctype, encoding = mimetypes.guess_type(str(cv_file))
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        with open(cv_file, "rb") as fp:
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
        encoders.encode_base64(attachment)
        filename = f"CV - {CANDIDATE_NAME_EN} - {role}.pdf"
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(attachment)
    else:
        print(f"Warning: CV attachment not found at {cv_file}", file=sys.stderr)

    return msg


def send_email_smtp(to_email, company, role, cv_path=None, custom_pitch=None, lang="auto", dry_run=False):
    """Send the email via secure SMTP or simulate in dry-run mode."""
    msg = create_message(to_email, company, role, cv_path, custom_pitch, lang)

    if dry_run:
        print("\n" + "=" * 60)
        print(f"DRY RUN MODE: Email would be sent ({lang.upper()} format):")
        print("=" * 60)
        print(f"From: {msg['From']}")
        print(f"To: {msg['To']}")
        print(f"Subject: {msg['Subject']}")
        print(f"Attachment: {cv_path or DEFAULT_CV}")
        print("-" * 60)
        print("PLAIN TEXT BODY PREVIEW:")
        print("-" * 60)
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                print(part.get_payload(decode=True).decode("utf-8"))
                break
        print("=" * 60 + "\n")
        return True

    if not SMTP_PASSWORD:
        print("\n❌ Error: SMTP_PASSWORD is not configured.", file=sys.stderr)
        return False

    try:
        print(f"Connecting to {SMTP_HOST}:{SMTP_PORT} via SSL...")
        context = ssl.create_default_context()
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, [to_email], msg.as_string())

        print(f"✓ Application email sent successfully to {to_email} ({company} - {role})!")
        record_submission_in_tracker(company, role, to_email)
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}", file=sys.stderr)
        return False


def record_submission_in_tracker(company, role, to_email):
    """Update or append submission in job_search_tracker.csv."""
    if not TRACKER_CSV.exists():
        return

    today_str = date.today().isoformat()
    rows = []
    matched = False

    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            if company.lower() in r["company"].lower() or r["company"].lower() in company.lower():
                r["status"] = "applied"
                r["channel"] = "email"
                note_addition = f"{today_str} email-auto-submit: sent to {to_email}"
                r["notes"] = f"{r.get('notes', '')} | {note_addition}".strip(" |")
                matched = True
            rows.append(r)

    if not matched:
        new_row = {
            "date": today_str,
            "company": company,
            "sector": "Commercial",
            "role": role,
            "role_type": "Marketing Leadership",
            "channel": "email",
            "status": "applied",
            "contact_person": to_email,
            "fit_rating": "90",
            "notes": f"{today_str} email-auto-submit: sent to {to_email}",
            "cv_file": str(DEFAULT_CV.relative_to(REPO_ROOT)),
            "cover_letter_file": "",
            "source": f"mailto:{to_email}",
            "deadline": "",
        }
        rows.append(new_row)

    with open(TRACKER_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✓ Tracker updated: {company} marked as 'applied' (channel: email).")


def generate_mailto_link(to_email, company, role, lang="auto"):
    """Generate a 1-click mailto: URL with pre-filled subject and body."""
    subject, plain_body, _ = build_email_content(company, role, lang=lang)
    mailto_url = f"mailto:{to_email}?subject={quote(subject)}&body={quote(plain_body)}"
    return mailto_url


def main():
    parser = argparse.ArgumentParser(description="Automated Email Submission Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Send command
    send_parser = subparsers.add_parser("send", help="Send an application email")
    send_parser.add_argument("--to", required=True, help="Recipient email (e.g. hr@company.com)")
    send_parser.add_argument("--company", required=True, help="Company name")
    send_parser.add_argument("--role", required=True, help="Job title")
    send_parser.add_argument("--cv", help="Path to tailored CV PDF (optional)")
    send_parser.add_argument("--pitch", help="Custom pitch text (optional)")
    send_parser.add_argument("--lang", choices=["auto", "ar", "en"], default="auto", help="Force language (auto/ar/en)")
    send_parser.add_argument("--dry-run", action="store_true", help="Preview email without sending")

    # Mailto command
    mailto_parser = subparsers.add_parser("mailto", help="Generate 1-click mailto URL")
    mailto_parser.add_argument("--to", required=True, help="Recipient email")
    mailto_parser.add_argument("--company", required=True, help="Company name")
    mailto_parser.add_argument("--role", required=True, help="Job title")
    mailto_parser.add_argument("--lang", choices=["auto", "ar", "en"], default="auto")

    # Test connection command
    test_parser = subparsers.add_parser("test", help="Test SMTP connection")

    args = parser.parse_args()

    if args.command == "send":
        success = send_email_smtp(
            to_email=args.to,
            company=args.company,
            role=args.role,
            cv_path=args.cv,
            custom_pitch=args.pitch,
            lang=args.lang,
            dry_run=args.dry_run,
        )
        sys.exit(0 if success else 1)

    elif args.command == "mailto":
        url = generate_mailto_link(args.to, args.company, args.role, lang=args.lang)
        print(url)

    elif args.command == "test":
        print(f"Testing SMTP credentials for {SMTP_USER} on {SMTP_HOST}:{SMTP_PORT}...")
        if not SMTP_PASSWORD:
            print("❌ SMTP_PASSWORD is not set.", file=sys.stderr)
            sys.exit(1)
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
            print("✓ SMTP Authentication Successful! Email auto-submission is ready to fire.")
        except Exception as e:
            print(f"❌ SMTP Connection failed: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
