# Search Queries for Job Scraper

<!-- SETUP: Customize these queries based on your skills, target roles, and location -->

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search`; Danish demos and any skill you add with `/add-portal` are included the same way. You do **not** need a matching `site:` line below for those CLIs to run.

The `site:` query templates in this file are the **WebSearch fallback** — for portals without a CLI, company career pages, or when a CLI fails.

**Language scope:** write every query category in every language listed in your CLAUDE.md Languages table (typically 1-2, sometimes more). A posting requiring a language you have *not* declared, as a job condition, is excluded before scoring; a posting requiring a *higher level* than you declared in a language you *do* work in is flagged for your own judgment, not excluded — see `04-job-evaluation.md`'s Language Gate, the single source of truth for this rule. Translate each category's keywords rather than machine-translating word-for-word (e.g. "Frontend Developer" -> "Desarrollador Frontend", not a literal word-for-word translation) if you work in more than one language.

# Search Queries for Job Scraper

## Installed portal CLIs (primary for `/scrape`)
`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search`.

The `site:` query templates in this file are the **WebSearch fallback** — for portals without a CLI, company career pages, or when a CLI fails.

## Search Sites
Primary:
- **linkedin.com/jobs** - LinkedIn job listings (Location: Riyadh, Saudi Arabia / GCC / Remote)
- **bayt.com** - Leading regional job portal across Saudi Arabia & Gulf
- **tanqeeb.com** - Major aggregator in Saudi Arabia
- **gulftalent.com** - Executive & senior roles in GCC

Secondary:
- Direct Google searches with `site:` filters for leading tech scale-ups and agencies in Saudi Arabia (Jahez, HungerStation, Nana, Floward, Tamara, Tabby, Salla, Zid, etc.)

## Query Categories

### Priority 1: Marketing Leadership (Director / Head of Marketing / CMO)
English:
```
site:linkedin.com/jobs "Marketing Director" "Riyadh"
site:linkedin.com/jobs "Head of Marketing" "Riyadh"
site:linkedin.com/jobs "Chief Marketing Officer" "Saudi Arabia"
site:linkedin.com/jobs "VP Marketing" "Riyadh"
```
Arabic:
```
site:linkedin.com/jobs "مدير تسويق" "الرياض"
site:linkedin.com/jobs "رئيس قطاع التسويق" "السعودية"
site:bayt.com/ar/saudi-arabia/jobs "مدير تسويق" "الرياض"
```

### Priority 2: Performance Marketing & Growth Leadership
English:
```
site:linkedin.com/jobs "Performance Marketing Director" "Riyadh"
site:linkedin.com/jobs "Head of Performance Marketing" "Saudi Arabia"
site:linkedin.com/jobs "Head of Growth" "Riyadh"
site:linkedin.com/jobs "Growth Director" "Riyadh"
site:linkedin.com/jobs "Digital Marketing Director" "Riyadh"
```
Arabic:
```
site:linkedin.com/jobs "مدير التسويق الرقمي" "الرياض"
site:linkedin.com/jobs "مدير نمو" "الرياض"
```

### Priority 3: E-Commerce & D2C Growth Leadership
English:
```
site:linkedin.com/jobs "E-Commerce Director" "Riyadh"
site:linkedin.com/jobs "Head of E-Commerce" "Saudi Arabia"
site:linkedin.com/jobs "D2C Marketing Manager" "Riyadh"
```
Arabic:
```
site:linkedin.com/jobs "مدير التجارة الإلكترونية" "الرياض"
```

### Priority 4: Executive Agency & Commercial Leadership
English:
```
site:linkedin.com/jobs "Managing Director" "Advertising Agency" "Riyadh"
site:linkedin.com/jobs "Media Buying Director" "Riyadh"
site:linkedin.com/jobs "Head of Paid Media" "Riyadh"
```

### Priority 5: All Marketing Roles & Specialists (All Levels across Saudi Arabia)
English:
```
site:linkedin.com/jobs "Marketing Specialist" "Riyadh"
site:linkedin.com/jobs "Digital Marketing Specialist" "Saudi Arabia"
site:linkedin.com/jobs "Performance Marketing Specialist" "Riyadh"
site:linkedin.com/jobs "Media Buyer" "Riyadh"
site:linkedin.com/jobs "Brand Manager" "Riyadh"
site:linkedin.com/jobs "Marketing Lead" "Saudi Arabia"
site:linkedin.com/jobs "Marketing Manager" "Remote" "Saudi Arabia"
```
Arabic:
```
site:linkedin.com/jobs "أخصائي تسويق" "الرياض"
site:linkedin.com/jobs "أخصائي تسويق رقمي" "السعودية"
site:linkedin.com/jobs "مدير حملات إعلانية" "الرياض"
site:linkedin.com/jobs "مسؤول تسويق" "الرياض"
```

## Location Filter
- **Ideal / Accepted for any mode (Onsite/Hybrid/Remote):** Riyadh (الرياض)
- **Outside Riyadh in Saudi Arabia (Jeddah, Dammam, Khobar, etc.):** Remote ONLY
- **International / GCC:** Remote ONLY
- **Excluded:** Any on-site job outside Riyadh

## Language Filter
- English and Arabic. Both are native/fluent working languages. Postings requiring either or both pass cleanly.

## Date Filter
- Include jobs posted within the last 14 days (or active postings with open application deadlines).

## Language Filter

Your working languages and levels are in CLAUDE.md's Languages table. When filtering scraped results, apply `04-job-evaluation.md`'s Language Gate: a posting requiring a language you haven't declared at all is excluded; a posting requiring a higher level than you declared in a language you do work in is not excluded, flag it clearly instead (see `job-scraper/SKILL.md`'s Step 3 "Quick Fit Assessment" for how the flag surfaces in `/scrape` output). Postings simply *written* in a language you don't work in, that don't require it on the job, are fine.

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- "/scrape [focus_area]" -> relevant category queries + custom focus-specific queries
