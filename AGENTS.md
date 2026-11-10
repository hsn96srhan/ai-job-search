---
framework_version: 1.0.0
---

# Agent Guidelines: AI Job Search

This workspace is structured to manage job search activities, scraper tools, CVs, cover letters, and interview preparation.

## Thin-Pointer Design (Single Source of Truth)

To prevent duplication and configuration drift across different AI agent frameworks (Claude Code, Google Antigravity, Codex, Cursor, Gemini CLI, etc.), this workspace uses a unified thin-pointer design. All agent runtimes should load the canonical specifications and candidate profiles from the files and directories below:

1. **Personal Candidate Profile:**
   - The candidate profile, contact details, education, and target preferences are defined in [CLAUDE.md](CLAUDE.md) and the individual profile methodology files under [.claude/skills/job-application-assistant/](.claude/skills/job-application-assistant/) (specifically `01-*.md` etc.).
2. **Canonical Workflow Specifications:**
   - The step-by-step instructions and triggers for tasks (setup, scrape, rank, apply, upskill, interview) are defined in the [.claude/](.claude/) directory (specifically under `.claude/skills/` and `.claude/commands/`).
   - Do not duplicate these rules or specifications. Treat `.claude/` files as the single source of truth.
3. **Portal Search Skills:**
   - Job-portal search CLIs live under [.agents/skills/](.agents/skills/) in the portable Agent Skills format (with a `SKILL.md` per portal). Codex and Antigravity discover these automatically; the `/scrape` workflow in [.claude/skills/job-scraper/](.claude/skills/job-scraper/) orchestrates them.

## Language Purity Rule for Applications & Emails

- **Arabic Postings:** When a job description, company name, or role is in Arabic, the entire submission email (Subject, Salutation, Pitch, Executive Highlights, and Sign-off) must be **100% pure Arabic** with proper RTL formatting.
- **English Postings:** When a job description or role is in English, the entire submission email must be **100% pure English** with proper LTR formatting.
- **Strict Rule:** Never produce or send mixed-language emails (e.g. Arabic pitch with English greeting or bullet points). Every communication must be linguistically unified and culturally appropriate.

## LinkedIn Integrity & No-Follow Rule

- **Strictly Preserve Settings:** Never touch, navigate to, or modify any LinkedIn account settings, profile preferences, or privacy options.
- **Always Uncheck "Follow Company":** During LinkedIn Easy Apply submissions, LinkedIn checks "Follow [Company]" by default on the Review screen. You MUST ALWAYS explicitly uncheck/disable this checkbox before submitting so that the candidate never follows any company during application.

## Legal Requirements, Sponsorship & Benefits Rule

- **Legal Status:** Candidate resides in Riyadh with a valid Transferable Iqama (رقم الإقامة: 2644162360 - إقامة عمل نظامية سارية قابلة للتحويل الفوري عبر منصة قوى). Currently on current employer's sponsorship (على كفالة الشركة الحالية في الرياض). Holds a valid Saudi Driving License (رخصة قيادة سعودية سارية).
- **Education:** Bachelor of Journalism & Media (بكالوريوس إعلام قسم صحافة) - Akhbar El Yom Academy (أكاديمية أخبار اليوم).
- **Official Accreditation:** Accredited Marketing Manager by HRSD (الاعتماد المهني كمدير تسويق من وزارة الموارد البشرية والتنمية الاجتماعية).
- **Mandatory Employer Coverage:** Any offer/application must account for:
  1. **Housing Allowance (بدل سكن نقدي):** 3 months of basic salary annually (25% cash housing allowance, strictly paid as cash allowance and NOT company-provided housing).
  2. **Sponsorship Transfer (نقل كفالة / نقل خدمات):** Executed via Qiwa with legal transfer fees borne by the employer.
  3. **Work Permit (كرت عمل / رخصة عمل):** Statutory issuance and annual renewal borne by the employer.
  4. **Medical Insurance (تأمين طبي تعاوني CCHI):** Comprehensive medical insurance coverage.
  5. **All Statutory Procedures:** Full legal adherence under the Saudi Labor Law.
- **Sponsorship Questions:** When an application asks *"Will you require sponsorship for employment visa / work authorization?"*, select **Yes** (نعم), since the candidate requires official in-kingdom sponsorship transfer (نقل كفالة) to the new employer. In free-text fields, explain: *"Transferable Iqama: 2644162360 in Riyadh. Requires standard sponsorship transfer via Qiwa (نقل كفالة عبر قوى), work permit issuance (كرت العمل), and medical insurance according to Saudi Labor Law."*
- **Compensation & Benefits Fields:** State Basic: 8,000 - 9,000 SAR | Cash Housing Allowance: 3 months basic salary annually (25%) | Total package: 10,000 - 12,000+ SAR + sponsorship transfer fees, work permit, medical insurance, and annual flight tickets.


