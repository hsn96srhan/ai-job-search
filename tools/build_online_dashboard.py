#!/usr/bin/env python3
"""Build an executive, clean, high-performance HTML dashboard (White Theme).

Features:
- Premium White/Light Executive Theme (Stripe/Linear aesthetic)
- Direct, crisp professional Arabic copy (no fluff)
- Real-time dynamic filter pills and KPI counters
- Manual application tracking & bi-directional sync
- Perfect RTL alignment, typography, and responsive spacing
"""

import csv
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"
PLATFORMS_JSON = REPO_ROOT / "platforms_registry.json"


def load_platforms():
    """تحميل كتالوج المنصات من platforms_registry.json"""
    if not PLATFORMS_JSON.exists():
        return []
    with open(PLATFORMS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("platforms", [])


def load_jobs():
    items = []
    if not TRACKER_CSV.exists():
        return items

    with open(TRACKER_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            items.append({
                "id": r.get("ID", "").strip(),
                "added_time": r.get("وقت وتاريخ الإضافة (Added Time)", "").strip(),
                "company": r.get("اسم الشركة (Company)", "").strip(),
                "title": r.get("المسمى الوظيفي (Job Title)", "").strip(),
                "method": r.get("طريقة التقديم (Application Method)", "").strip(),
                "platform": r.get("المنصة / المصدر (Platform)", "").strip(),
                "city": r.get("المدينة (City)", "").strip(),
                "url": r.get("رابط الوظيفة (Job URL)", "").strip(),
                "fit": r.get("نسبة التوافق (Fit Score %)", "").strip(),
                "status": r.get("حالة التقديم (Status)", "").strip(),
                "contact": r.get("مسؤول التوظيف / جهة الاتصال (Contact)", "").strip(),
                "salary": r.get("الراتب المستهدف (Salary)", "").strip(),
                "cv": r.get("نسخة السيرة الذاتية (CV File)", "").strip(),
                "followup": r.get("تاريخ المتابعة (Next Follow-up)", "").strip(),
                "notes": r.get("ملاحظات وتأكيد التقديم (Notes)", "").strip()
            })
    return items


def build_platforms_section_html(platforms):
    """يبني قسم HTML لكتالوج المنصات"""
    if not platforms:
        return ""

    rows_html = ""
    for p in platforms:
        status = p.get("profile_status", "—")
        profile_url = p.get("profile_url", "")
        name_ar = p.get("name_ar", "")
        name_en = p.get("name_en", "")
        scope = p.get("scope", "")
        notes = p.get("notes", "")
        category = p.get("category", "")

        # لون الحالة
        if "100%" in status:
            badge_cls = "badge-green"
        elif "87%" in status or "جزئي" in status or "🟡" in status:
            badge_cls = "badge-yellow"
        elif "لم يبدأ" in status or "❌" in status:
            badge_cls = "badge-red"
        elif "يدوي" in status or "⏭️" in status:
            badge_cls = "badge-gray"
        else:
            badge_cls = "badge-blue"

        profile_link = f'<a href="{profile_url}" target="_blank" class="platform-link">🔗 عرض</a>' if profile_url else "—"

        rows_html += f"""
        <tr>
          <td><strong>{name_ar}</strong><br/><small style="color:#666">{name_en}</small></td>
          <td><small>{scope}</small></td>
          <td><span class="platform-badge {badge_cls}">{status}</span></td>
          <td>{profile_link}</td>
          <td><small style="color:#888">{notes}</small></td>
        </tr>"""

    total = len(platforms)
    done = sum(1 for p in platforms if "100%" in p.get("profile_status", ""))
    partial = sum(1 for p in platforms if "87%" in p.get("profile_status", "") or "🟡" in p.get("profile_status", ""))
    pending = sum(1 for p in platforms if "لم يبدأ" in p.get("profile_status", ""))

    return f"""
    <!-- ═══════════ قسم المنصات ═══════════ -->
    <section class="platforms-section" id="platforms">
      <div class="section-header">
        <h2 class="section-title">🌐 كتالوج منصات التوظيف</h2>
        <div class="platform-kpis">
          <span class="pkpi pkpi-total">📋 {total} منصة</span>
          <span class="pkpi pkpi-done">✅ {done} مكتملة</span>
          <span class="pkpi pkpi-partial">🟡 {partial} جزئية</span>
          <span class="pkpi pkpi-pending">❌ {pending} لم تُبدأ</span>
        </div>
      </div>
      <div class="table-wrap">
        <table class="platforms-table">
          <thead>
            <tr>
              <th>المنصة</th>
              <th>النطاق</th>
              <th>حالة الملف</th>
              <th>الرابط</th>
              <th>ملاحظات</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </section>
    <style>
      .platforms-section {{ margin: 2.5rem 0; }}
      .platform-kpis {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.5rem; }}
      .pkpi {{ padding: 0.25rem 0.9rem; border-radius: 999px; font-size: 0.82rem; font-weight: 600; }}
      .pkpi-total {{ background:#f1f5f9; color:#334155; }}
      .pkpi-done {{ background:#dcfce7; color:#166534; }}
      .pkpi-partial {{ background:#fef9c3; color:#854d0e; }}
      .pkpi-pending {{ background:#fee2e2; color:#991b1b; }}
      .platforms-table {{ width:100%; border-collapse:collapse; font-size:0.9rem; }}
      .platforms-table th {{ background:#f8fafc; color:#475569; font-weight:600; padding:0.65rem 1rem; text-align:right; border-bottom:2px solid #e2e8f0; }}
      .platforms-table td {{ padding:0.65rem 1rem; border-bottom:1px solid #f1f5f9; vertical-align:top; }}
      .platforms-table tr:hover td {{ background:#fafafa; }}
      .platform-badge {{ display:inline-block; padding:0.2rem 0.65rem; border-radius:999px; font-size:0.78rem; font-weight:600; white-space:nowrap; }}
      .badge-green {{ background:#dcfce7; color:#15803d; }}
      .badge-yellow {{ background:#fef9c3; color:#a16207; }}
      .badge-red {{ background:#fee2e2; color:#b91c1c; }}
      .badge-gray {{ background:#f1f5f9; color:#64748b; }}
      .badge-blue {{ background:#dbeafe; color:#1d4ed8; }}
      .platform-link {{ color:#2563eb; text-decoration:none; font-weight:500; }}
      .platform-link:hover {{ text-decoration:underline; }}
    </style>
    """


def build_html(jobs):
    jobs_json = json.dumps(jobs, ensure_ascii=False)

    applied_count = sum(1 for j in jobs if "تم التقديم" in j["status"])
    manual_applied_count = sum(1 for j in jobs if "يدوي" in j["status"])
    auto_applied_count = sum(1 for j in jobs if "تم التقديم" in j["status"] and "يدوي" not in j["status"])
    ready_count = sum(1 for j in jobs if "جاهز" in j["status"])
    skipped_count = sum(1 for j in jobs if "تم التخطي" in j["status"])
    closed_count = sum(1 for j in jobs if "مغلقة" in j["status"])
    total_count = len(jobs)

    # Channel Counts
    email_count = sum(1 for j in jobs if "ايميل" in j["method"])
    ats_count = sum(1 for j in jobs if "بوابة خارجية" in j["method"])
    easy_count = sum(1 for j in jobs if "ايزي ابلاي" in j["method"])

    riyadh_tz = timezone(timedelta(hours=3))
    now_str = datetime.now(riyadh_tz).strftime("%Y-%m-%d %I:%M %p").replace("AM", "ص").replace("PM", "م")

    html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>لوحة التقديم والمتابعة | حسن سرحان</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border-color: #e2e8f0;
      --border-subtle: #f1f5f9;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-subtle: #94a3b8;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --emerald: #10b981;
      --emerald-dark: #047857;
      --emerald-bg: #ecfdf5;
      --emerald-border: #a7f3d0;
      --blue: #3b82f6;
      --blue-dark: #1d4ed8;
      --blue-bg: #eff6ff;
      --blue-border: #bfdbfe;
      --purple: #8b5cf6;
      --purple-dark: #6d28d9;
      --purple-bg: #f5f3ff;
      --purple-border: #ddd6fe;
      --amber: #f59e0b;
      --amber-dark: #b45309;
      --amber-bg: #fffbeb;
      --amber-border: #fde68a;
      --rose: #f43f5e;
      --rose-dark: #be123c;
      --rose-bg: #fff1f2;
      --rose-border: #fecdd3;
      --font: 'Cairo', system-ui, -apple-system, sans-serif;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font);
      background-color: var(--bg);
      color: var(--text-main);
      line-height: 1.5;
      padding: 24px 20px;
      -webkit-font-smoothing: antialiased;
    }}

    .container {{
      max-width: 1440px;
      margin: 0 auto;
    }}

    /* Header */
    .header {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 20px 24px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }}

    .profile-info h1 {{
      font-size: 20px;
      font-weight: 800;
      color: var(--text-main);
      margin-bottom: 6px;
      letter-spacing: -0.3px;
    }}

    .profile-meta {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px 12px;
      font-size: 13px;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .profile-meta .sep {{
      color: var(--text-subtle);
    }}

    .badge-live {{
      font-size: 11.5px;
      font-weight: 700;
      background: var(--emerald-bg);
      color: var(--emerald-dark);
      border: 1px solid var(--emerald-border);
      padding: 2px 8px;
      border-radius: 9999px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}

    .badge-live::before {{
      content: '';
      width: 6px;
      height: 6px;
      background: var(--emerald);
      border-radius: 50%;
      display: inline-block;
    }}

    .header-actions {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .btn {{
      font-family: var(--font);
      font-size: 13px;
      font-weight: 700;
      padding: 8px 14px;
      border-radius: 8px;
      text-decoration: none;
      cursor: pointer;
      border: 1px solid transparent;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}

    .btn-primary {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }}
    .btn-primary:hover {{ background: var(--primary-hover); }}

    .btn-secondary {{
      background: #ffffff;
      color: #334155;
      border-color: var(--border-color);
    }}
    .btn-secondary:hover {{ background: #f8fafc; border-color: #cbd5e1; }}

    .btn-sync-manual {{
      background: var(--emerald-bg);
      color: var(--emerald-dark);
      border-color: var(--emerald-border);
    }}
    .btn-sync-manual:hover {{
      background: #dcfce7;
      border-color: #86efac;
    }}

    .pulse-badge {{
      display: inline-block;
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--emerald);
    }}

    /* KPI Summary Cards */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }}

    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
      transition: border-color 0.15s ease;
    }}

    .kpi-label {{
      font-size: 13px;
      color: var(--text-muted);
      font-weight: 600;
    }}

    .kpi-number {{
      font-size: 32px;
      font-weight: 800;
      color: var(--text-main);
      line-height: 1.1;
      font-variant-numeric: tabular-nums;
    }}

    .kpi-subtext {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .kpi-applied {{
      background: #fcfdfd;
      border-color: #bbf7d0;
    }}
    .kpi-applied .kpi-number {{ color: var(--emerald-dark); }}

    .kpi-ready {{
      background: #fcfdfd;
      border-color: #bfdbfe;
    }}
    .kpi-ready .kpi-number {{ color: var(--blue-dark); }}

    .kpi-skipped .kpi-number {{ color: var(--text-muted); }}

    /* Controls Bar */
    .controls-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }}

    .controls-top-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .controls-bottom-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      border-top: 1px solid var(--border-subtle);
      padding-top: 12px;
    }}

    .search-box {{
      flex: 1;
      min-width: 280px;
      position: relative;
    }}

    .search-box input {{
      width: 100%;
      font-family: var(--font);
      background: #f8fafc;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 9px 12px 9px 36px;
      color: var(--text-main);
      font-size: 13.5px;
      outline: none;
      transition: all 0.15s ease;
    }}

    .search-box input:focus {{
      background: #ffffff;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }}

    .search-icon {{
      position: absolute;
      left: 11px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-subtle);
      font-size: 14px;
      pointer-events: none;
    }}

    .filter-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }}

    .filter-label {{
      font-size: 12.5px;
      font-weight: 700;
      color: var(--text-muted);
      margin-left: 4px;
    }}

    .pill {{
      font-family: var(--font);
      font-size: 12px;
      font-weight: 600;
      background: #ffffff;
      color: #475569;
      border: 1px solid var(--border-color);
      padding: 5px 12px;
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .pill:hover {{
      background: #f1f5f9;
      color: var(--text-main);
      border-color: #cbd5e1;
    }}

    .pill.active {{
      background: #0f172a;
      color: #ffffff;
      border-color: #0f172a;
    }}

    .pill.active-applied {{
      background: var(--emerald-dark);
      color: #ffffff;
      border-color: var(--emerald-dark);
    }}

    .pill.active-manual {{
      background: #059669;
      color: #ffffff;
      border-color: #059669;
    }}

    .pill.active-auto {{
      background: #4338ca;
      color: #ffffff;
      border-color: #4338ca;
    }}

    .pill.active-ready {{
      background: #d97706;
      color: #ffffff;
      border-color: #d97706;
    }}

    .pill.active-skipped {{
      background: #475569;
      color: #ffffff;
      border-color: #475569;
    }}

    .pill.active-closed {{
      background: var(--rose-dark);
      color: #ffffff;
      border-color: var(--rose-dark);
    }}

    .pill-method {{
      font-family: var(--font);
      font-size: 12px;
      font-weight: 600;
      background: #ffffff;
      color: #475569;
      border: 1px solid var(--border-color);
      padding: 5px 11px;
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .pill-method:hover {{ background: #f1f5f9; color: var(--text-main); }}
    .pill-method.active {{ background: #0f172a; color: #fff; border-color: #0f172a; }}
    .pill-method.active-email {{ background: var(--blue-dark); color: #fff; border-color: var(--blue-dark); }}
    .pill-method.active-ats {{ background: var(--purple-dark); color: #fff; border-color: var(--purple-dark); }}
    .pill-method.active-easy {{ background: var(--amber-dark); color: #fff; border-color: var(--amber-dark); }}

    /* Table Container */
    .table-container {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow-x: auto;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13.5px;
      text-align: right;
    }}

    thead th {{
      background: #f8fafc;
      color: #475569;
      font-weight: 700;
      padding: 12px 16px;
      border-bottom: 1px solid var(--border-color);
      white-space: nowrap;
      font-size: 12.5px;
    }}

    tbody td {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--border-subtle);
      vertical-align: middle;
      color: var(--text-main);
    }}

    tbody tr:hover {{
      background: #f8fafc;
    }}

    .company-cell strong {{
      color: var(--text-main);
      display: block;
      font-size: 13.5px;
      font-weight: 700;
    }}

    .company-cell span {{
      color: var(--text-muted);
      font-size: 11.5px;
    }}

    .role-cell {{
      font-weight: 600;
      color: #1e293b;
      max-width: 240px;
    }}

    .time-cell {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .time-main {{
      font-weight: 700;
      color: #0369a1;
      font-size: 12px;
    }}

    .time-sub {{
      font-size: 11px;
      color: var(--text-muted);
    }}

    .fit-meter {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 700;
      font-size: 12px;
    }}

    .fit-bar {{
      width: 44px;
      height: 5px;
      background: #e2e8f0;
      border-radius: 9999px;
      overflow: hidden;
    }}

    .fit-fill {{
      height: 100%;
      border-radius: 9999px;
    }}

    /* Badges */
    .badge-method {{
      font-size: 11.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
    }}

    .method-email {{ background: var(--blue-bg); color: var(--blue-dark); border: 1px solid var(--blue-border); }}
    .method-ats {{ background: var(--purple-bg); color: var(--purple-dark); border: 1px solid var(--purple-border); }}
    .method-easy {{ background: var(--amber-bg); color: var(--amber-dark); border: 1px solid var(--amber-border); }}

    .tag-status {{
      font-size: 11.5px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 9999px;
      display: inline-block;
      white-space: nowrap;
    }}

    .status-applied {{ background: var(--emerald-bg); color: var(--emerald-dark); border: 1px solid var(--emerald-border); }}
    .status-ready {{ background: var(--blue-bg); color: var(--blue-dark); border: 1px solid var(--blue-border); }}
    .status-skipped {{ background: #f1f5f9; color: #475569; border: 1px solid var(--border-color); }}
    .status-closed {{ background: var(--rose-bg); color: var(--rose-dark); border: 1px solid var(--rose-border); }}

    .action-cell {{
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .btn-apply {{
      font-family: var(--font);
      font-size: 11.5px;
      font-weight: 700;
      padding: 5px 10px;
      border-radius: 6px;
      background: var(--primary);
      color: #ffffff;
      text-decoration: none;
      display: inline-block;
      transition: background 0.15s ease;
    }}
    .btn-apply:hover {{ background: var(--primary-hover); }}

    .btn-done {{
      font-size: 11.5px;
      font-weight: 700;
      color: var(--emerald-dark);
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }}

    .btn-mark-manual {{
      font-family: var(--font);
      font-size: 11px;
      font-weight: 700;
      padding: 5px 9px;
      border-radius: 6px;
      background: var(--emerald-bg);
      color: var(--emerald-dark);
      border: 1px solid var(--emerald-border);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 3px;
      transition: all 0.15s ease;
      white-space: nowrap;
    }}
    .btn-mark-manual:hover {{
      background: var(--emerald);
      color: #ffffff;
      border-color: var(--emerald);
    }}

    .btn-done-manual {{
      font-family: var(--font);
      font-size: 11px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 6px;
      background: #f0fdf4;
      color: var(--emerald-dark);
      border: 1px solid var(--emerald);
      display: inline-flex;
      align-items: center;
      gap: 3px;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }}
    .btn-done-manual:hover {{
      background: #fee2e2;
      border-color: #ef4444;
      color: #dc2626;
    }}

    .btn-view {{
      font-family: var(--font);
      font-size: 11.5px;
      font-weight: 600;
      padding: 5px 10px;
      border-radius: 6px;
      background: #ffffff;
      color: #334155;
      border: 1px solid var(--border-color);
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .btn-view:hover {{
      background: #f1f5f9;
      border-color: #cbd5e1;
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: #0f172a;
      color: #ffffff;
      padding: 10px 20px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 13px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
      transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .toast.show {{
      transform: translateX(-50%) translateY(0);
    }}

    /* Modals */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.45);
      backdrop-filter: blur(4px);
      display: none;
      justify-content: center;
      align-items: center;
      z-index: 999;
      padding: 16px;
    }}

    .modal-card {{
      background: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      width: 100%;
      max-width: 640px;
      padding: 24px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
      max-height: 90vh;
      overflow-y: auto;
    }}

    .modal-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 16px;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 12px;
    }}

    .modal-header h3 {{
      font-size: 17px;
      color: var(--text-main);
      font-weight: 800;
    }}

    .modal-close {{
      background: none;
      border: none;
      color: var(--text-subtle);
      font-size: 22px;
      cursor: pointer;
      line-height: 1;
      padding: 2px 6px;
    }}
    .modal-close:hover {{ color: var(--text-main); }}

    .modal-highlight-box {{
      background: #f8fafc;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .m-highlight-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }}

    .m-hl-label {{
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-muted);
    }}

    .m-hl-val {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
    }}

    .modal-manual-action-card {{
      background: var(--emerald-bg);
      border: 1px solid var(--emerald-border);
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 14px;
    }}

    .modal-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 10px;
    }}

    .modal-row {{
      margin-bottom: 10px;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}

    .modal-label {{
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 600;
    }}

    .modal-value {{
      font-size: 13.5px;
      color: var(--text-main);
      background: #f8fafc;
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
    }}
  </style>
</head>
<body>

  <div class="container">

    <!-- Header -->
    <header class="header">
      <div class="profile-info">
        <h1>لوحة التقديم والمتابعة</h1>
        <div class="profile-meta">
          <span>💼 حسن سرحان</span>
          <span class="sep">•</span>
          <span>مدير تسويق تنفيذي</span>
          <span class="sep">•</span>
          <span>الرياض</span>
          <span class="sep">•</span>
          <span>💰 8,000 أساسي / 10,000 باكدج</span>
          <span class="sep">•</span>
          <span class="badge-live">نظام متصل ومحدّث</span>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-sync-manual" onclick="openSyncModal()" id="btnSyncManual">
          <span class="pulse-badge"></span>
          🔄 مزامنة تقديمي (<span id="manualAppliedCount">0</span>)
        </button>
        <button class="btn btn-secondary" onclick="copyToClipboard()">
          📋 نسخ للجدول
        </button>
        <a href="https://docs.google.com/spreadsheets/d/1pmyTxkwRc8NjddIfraoZzgV5CMulabVA59hdvKVzsYs" target="_blank" class="btn btn-primary">
          📊 قوقل شيت
        </a>
        <a href="https://hsn96srhan.github.io/hsn/" target="_blank" class="btn btn-secondary">
          🌐 بورتفوليو
        </a>
      </div>
    </header>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card kpi-total">
        <div class="kpi-label">إجمالي الفرص</div>
        <div class="kpi-number" id="kpi-total">{total_count}</div>
        <div class="kpi-subtext">شواغر تسويق مستهدفة بالرياض وعن بعد</div>
      </div>
      <div class="kpi-card kpi-applied">
        <div class="kpi-label">تم التقديم</div>
        <div class="kpi-number" id="kpi-applied">{applied_count}</div>
        <div class="kpi-subtext"><span id="kpiSubApplied">{manual_applied_count} يدوياً • {auto_applied_count} آلياً</span></div>
      </div>
      <div class="kpi-card kpi-ready">
        <div class="kpi-label">جاهز للتقديم</div>
        <div class="kpi-number" id="kpi-ready">{ready_count}</div>
        <div class="kpi-subtext">فرص مؤهلة بانتظار الإرسال</div>
      </div>
      <div class="kpi-card kpi-skipped">
        <div class="kpi-label">مستبعد / مغلق</div>
        <div class="kpi-number" id="kpi-skipped">{skipped_count + closed_count}</div>
        <div class="kpi-subtext">غير مطابقة أو مغلقة من الشركة</div>
      </div>
    </div>

    <!-- Controls Bar -->
    <div class="controls-card">
      <div class="controls-top-row">
        <div class="search-box">
          <input type="text" id="searchInput" placeholder="بحث باسم الشركة، المسمى الوظيفي، أو المدينة..." oninput="filterJobs()">
          <span class="search-icon">🔍</span>
        </div>
        <div class="filter-pills" id="methodFilterPills">
          <span class="filter-label">القناة:</span>
          <button class="pill-method active" onclick="setMethodFilter('all', this)">كل القنوات (<span id="pillCountMethodAll">{total_count}</span>)</button>
          <button class="pill-method" onclick="setMethodFilter('easy', this)">⚡ ايزي ابلاي (<span id="pillCountMethodEasy">{easy_count}</span>)</button>
          <button class="pill-method" onclick="setMethodFilter('email', this)">✉️ إيميل مباشر (<span id="pillCountMethodEmail">{email_count}</span>)</button>
          <button class="pill-method" onclick="setMethodFilter('ats', this)">🌐 بوابة ATS (<span id="pillCountMethodAts">{ats_count}</span>)</button>
        </div>
      </div>

      <div class="controls-bottom-row">
        <div class="filter-pills" id="statusFilterPills">
          <span class="filter-label">الحالة:</span>
          <button class="pill active" onclick="setStatusFilter('all', this)">الكل (<span id="pillCountAll">{total_count}</span>)</button>
          <button class="pill" onclick="setStatusFilter('applied', this)">✓ تم التقديم (<span id="pillCountApplied">{applied_count}</span>)</button>
          <button class="pill" onclick="setStatusFilter('manual', this)">👤 قدّمت يدوياً (<span id="pillCountManual">{manual_applied_count}</span>)</button>
          <button class="pill" onclick="setStatusFilter('auto', this)">🤖 تقديم آلي (<span id="pillCountAuto">{auto_applied_count}</span>)</button>
          <button class="pill" onclick="setStatusFilter('ready', this)">🚀 جاهز (<span id="pillCountReady">{ready_count}</span>)</button>
          <button class="pill" onclick="setStatusFilter('skipped', this)">⚠️ مستبعد (<span id="pillCountSkipped">{skipped_count}</span>)</button>
          <button class="pill" onclick="setStatusFilter('closed', this)">🔒 مغلقة (<span id="pillCountClosed">{closed_count}</span>)</button>
        </div>
      </div>
    </div>

    <!-- Table Container -->
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>الشركة</th>
            <th>المسمى الوظيفي</th>
            <th>طريقة التقديم</th>
            <th>تاريخ الإضافة</th>
            <th>المدينة</th>
            <th>التوافق</th>
            <th>الحالة</th>
            <th>الإجراء</th>
          </tr>
        </thead>
        <tbody id="jobsTableBody">
          <!-- Populated by JavaScript -->
        </tbody>
      </table>
    </div>

  </div>

  <!-- Details Modal -->
  <div class="modal-overlay" id="modalOverlay" onclick="if(event.target===this) closeModal()">
    <div class="modal-card">
      <div class="modal-header">
        <h3 id="mCompanyRole">تفاصيل الشاغر</h3>
        <button class="modal-close" onclick="closeModal()">×</button>
      </div>
      <div id="modalBody"></div>
    </div>
  </div>

  <!-- Manual Application Sync Modal -->
  <div class="modal-overlay" id="syncModalOverlay" onclick="if(event.target===this) closeSyncModal()">
    <div class="modal-card" style="max-width: 600px;">
      <div class="modal-header">
        <div>
          <h3>🔄 مزامنة التقديم اليدوي</h3>
          <p style="font-size: 12.5px; color: var(--text-muted); margin-top: 3px;">الوظائف التي قمت بتقديمها بنفسك يدوياً لحفظها في ملف التتبع وقوقل شيت</p>
        </div>
        <button class="modal-close" onclick="closeSyncModal()">×</button>
      </div>
      <div id="syncModalBody" style="padding: 14px 0;"></div>
      <div style="display: flex; gap: 8px; justify-content: flex-end; border-top: 1px solid var(--border-subtle); padding-top: 14px; flex-wrap: wrap;">
        <button class="btn btn-secondary" onclick="closeSyncModal()">إغلاق</button>
        <button class="btn btn-secondary" onclick="copySyncCommand()">📋 نسخ أمر Terminal</button>
        <button class="btn btn-primary" onclick="syncWithLocalServer()">⚡ مزامنة فورية</button>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div class="toast" id="toast">
    <span>✓ تم نسخ البيانات للجدول (Cmd+V)</span>
  </div>

  <script>
    const allJobs = {jobs_json};
    let currentStatusFilter = 'all';
    let currentMethodFilter = 'all';

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      toast.innerText = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 3500);
    }}

    function updateCountsAndUI() {{
      const total = allJobs.length;
      const appliedJobs = allJobs.filter(j => j.status.includes('تم التقديم'));
      const manualJobs = allJobs.filter(j => j.status.includes('يدوي') || j.manual === true);
      const autoJobs = allJobs.filter(j => j.status.includes('تم التقديم') && !j.status.includes('يدوي') && !j.manual);
      const readyJobs = allJobs.filter(j => j.status.includes('جاهز'));
      const skippedJobs = allJobs.filter(j => j.status.includes('تم التخطي'));
      const closedJobs = allJobs.filter(j => j.status.includes('مغلقة'));

      const easyJobs = allJobs.filter(j => j.method.includes('ايزي ابلاي'));
      const emailJobs = allJobs.filter(j => j.method.includes('ايميل'));
      const atsJobs = allJobs.filter(j => j.method.includes('بوابة خارجية'));

      const manualStore = JSON.parse(localStorage.getItem('manual_applied_jobs') || '{{}}');
      const manualStoreCount = Object.keys(manualStore).length;

      // Update KPI cards
      const kpiTotal = document.getElementById('kpi-total');
      if (kpiTotal) kpiTotal.innerText = total;

      const kpiApplied = document.getElementById('kpi-applied');
      if (kpiApplied) kpiApplied.innerText = appliedJobs.length;

      const kpiSubApplied = document.getElementById('kpiSubApplied');
      if (kpiSubApplied) kpiSubApplied.innerText = `${{manualJobs.length}} يدوياً • ${{autoJobs.length}} آلياً`;

      const kpiReady = document.getElementById('kpi-ready');
      if (kpiReady) kpiReady.innerText = readyJobs.length;

      const kpiSkipped = document.getElementById('kpi-skipped');
      if (kpiSkipped) kpiSkipped.innerText = skippedJobs.length + closedJobs.length;

      // Update Header Sync badge
      const manualBadge = document.getElementById('manualAppliedCount');
      if (manualBadge) manualBadge.innerText = manualStoreCount;

      // Safe DOM updater helper
      const setEl = (id, val) => {{
        const el = document.getElementById(id);
        if (el) el.innerText = val;
      }};

      // Update Status filter pill spans
      setEl('pillCountAll', total);
      setEl('pillCountApplied', appliedJobs.length);
      setEl('pillCountManual', manualJobs.length);
      setEl('pillCountAuto', autoJobs.length);
      setEl('pillCountReady', readyJobs.length);
      setEl('pillCountSkipped', skippedJobs.length);
      setEl('pillCountClosed', closedJobs.length);

      // Update Method filter pill spans
      setEl('pillCountMethodAll', total);
      setEl('pillCountMethodEasy', easyJobs.length);
      setEl('pillCountMethodEmail', emailJobs.length);
      setEl('pillCountMethodAts', atsJobs.length);
    }}

    function initManualApplied() {{
      const manualStore = JSON.parse(localStorage.getItem('manual_applied_jobs') || '{{}}');
      allJobs.forEach(j => {{
        if (!j.originalStatus) j.originalStatus = j.status;
        if (manualStore[j.id]) {{
          j.manual = true;
          j.status = 'تم التقديم (يدوي)';
        }} else if (j.status.includes('يدوي')) {{
          j.manual = true;
        }}
      }});
      updateCountsAndUI();
    }}

    function toggleManualApply(jobId) {{
      const j = allJobs.find(x => x.id === jobId);
      if (!j) return;

      const manualStore = JSON.parse(localStorage.getItem('manual_applied_jobs') || '{{}}');
      const isCurrentlyManual = !!manualStore[jobId];

      if (isCurrentlyManual) {{
        delete manualStore[jobId];
        j.manual = false;
        j.status = j.originalStatus || 'جاهز للتقديم';
        showToast('↩ تم التراجع عن تسجيل التقديم اليدوي لـ ' + j.company);
      }} else {{
        manualStore[jobId] = {{
          id: j.id,
          company: j.company,
          title: j.title,
          time: new Date().toLocaleTimeString('ar-SA', {{ hour: '2-digit', minute: '2-digit' }}),
          date: new Date().toLocaleDateString('ar-SA')
        }};
        j.manual = true;
        if (!j.originalStatus) j.originalStatus = j.status;
        j.status = 'تم التقديم (يدوي)';
        showToast('✓ تم تسجيل تقديمك اليدوي على ' + j.company);

        // Background live sync to local bridge server if active
        fetch(`http://127.0.0.1:5050/api/mark_applied?id=${{jobId}}`, {{ mode: 'cors' }})
          .then(r => r.json())
          .then(data => {{
            if (data.success) console.log('✓ تم التحديث التلقائي في ملف التتبع وقوقل شيت:', data);
          }})
          .catch(() => {{}});
      }}

      localStorage.setItem('manual_applied_jobs', JSON.stringify(manualStore));
      updateCountsAndUI();
      filterJobs();
    }}

    function renderTable(jobs) {{
      const tbody = document.getElementById('jobsTableBody');
      tbody.innerHTML = '';

      if (jobs.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:35px; color:#64748b;">لا توجد شواغر مطابقة لمعايير البحث والتصفية المختارة</td></tr>';
        return;
      }}

      jobs.forEach(j => {{
        const tr = document.createElement('tr');

        // Status tag
        let statusTag = '';
        if (j.status.includes('تم التقديم')) {{
          statusTag = j.manual ? '<span class="tag-status status-applied">✓ تم التقديم (يدوي)</span>' : '<span class="tag-status status-applied">✓ تم التقديم</span>';
        }} else if (j.status.includes('جاهز')) {{
          statusTag = '<span class="tag-status status-ready">جاهز للتقديم</span>';
        }} else if (j.status.includes('مغلقة')) {{
          statusTag = '<span class="tag-status status-closed">مغلقة</span>';
        }} else {{
          statusTag = '<span class="tag-status status-skipped">مستبعد</span>';
        }}

        // Method tag
        let methodTag = '';
        if (j.method.includes('ايميل')) {{
          methodTag = '<span class="badge-method method-email">✉️ إيميل مباشر</span>';
        }} else if (j.method.includes('بوابة خارجية')) {{
          methodTag = '<span class="badge-method method-ats">🌐 بوابة ATS</span>';
        }} else {{
          methodTag = '<span class="badge-method method-easy">⚡ ايزي ابلاي</span>';
        }}

        // Fit meter
        const fitNum = parseInt(j.fit.replace(/[^0-9]/g, '')) || 85;
        const fitColor = fitNum >= 88 ? '#10b981' : (fitNum >= 80 ? '#2563eb' : '#64748b');

        // Action button
        let actionBtn = '';
        if (j.status.includes('تم التقديم')) {{
          if (j.manual) {{
            actionBtn = `<button class="btn-done-manual" onclick="toggleManualApply('${{j.id}}')" title="اضغط للتراجع">✓ قدّمت يدوياً</button>`;
          }} else {{
            actionBtn = '<span class="btn-done">✓ تم الإرسال</span>';
          }}
        }} else if (j.status.includes('مغلقة')) {{
          actionBtn = '<span style="color:#be123c; font-size:12px; font-weight:700;">مغلقة</span>';
        }} else if (j.status.includes('تم التخطي')) {{
          actionBtn = `<button class="btn-mark-manual" onclick="toggleManualApply('${{j.id}}')" title="تسجيل تقديم يدوي">✅ قدّمت</button>`;
        }} else {{
          actionBtn = `<a href="${{j.url}}" target="_blank" class="btn-apply">قدّم الآن ↗</a> <button class="btn-mark-manual" onclick="toggleManualApply('${{j.id}}')" title="تسجيل تقديم يدوي">✅ قدّمت</button>`;
        }}

        // Parse date and time cleanly
        const timeParts = j.added_time.split(' ');
        const datePart = timeParts[0] || '2026-11-08';
        const timePart = timeParts.slice(1).join(' ') || j.added_time;

        tr.innerHTML = `
          <td class="company-cell">
            <strong>${{escapeHtml(j.company)}}</strong>
            <span>${{escapeHtml(j.platform)}}</span>
          </td>
          <td class="role-cell">${{escapeHtml(j.title)}}</td>
          <td>${{methodTag}}</td>
          <td>
            <div class="time-cell">
              <span class="time-main">🕒 ${{escapeHtml(timePart)}}</span>
              <span class="time-sub">📅 ${{escapeHtml(datePart)}}</span>
            </div>
          </td>
          <td>${{escapeHtml(j.city)}}</td>
          <td>
            <div class="fit-meter">
              <div class="fit-bar">
                <div class="fit-fill" style="width: ${{fitNum}}%; background: ${{fitColor}};"></div>
              </div>
              <span>${{fitNum}}%</span>
            </div>
          </td>
          <td>${{statusTag}}</td>
          <td class="action-cell">
            <button class="btn-view" onclick="openDetails('${{j.id}}')">التفاصيل</button>
            ${{actionBtn}}
          </td>
        `;

        tbody.appendChild(tr);
      }});
    }}

    function filterJobs() {{
      const query = document.getElementById('searchInput').value.trim().toLowerCase();

      const filtered = allJobs.filter(j => {{
        // Match status filter
        let matchStatus = true;
        if (currentStatusFilter === 'applied') {{
          matchStatus = j.status.includes('تم التقديم');
        }} else if (currentStatusFilter === 'manual') {{
          matchStatus = j.status.includes('يدوي') || j.manual === true;
        }} else if (currentStatusFilter === 'auto') {{
          matchStatus = j.status.includes('تم التقديم') && !j.status.includes('يدوي') && !j.manual;
        }} else if (currentStatusFilter === 'ready') {{
          matchStatus = j.status.includes('جاهز');
        }} else if (currentStatusFilter === 'skipped') {{
          matchStatus = j.status.includes('تم التخطي');
        }} else if (currentStatusFilter === 'closed') {{
          matchStatus = j.status.includes('مغلقة');
        }}

        // Match method filter
        let matchMethod = true;
        if (currentMethodFilter === 'email') matchMethod = j.method.includes('ايميل');
        else if (currentMethodFilter === 'ats') matchMethod = j.method.includes('بوابة خارجية');
        else if (currentMethodFilter === 'easy') matchMethod = j.method.includes('ايزي ابلاي');

        // Match search text
        const matchSearch =
          !query ||
          j.company.toLowerCase().includes(query) ||
          j.title.toLowerCase().includes(query) ||
          j.city.toLowerCase().includes(query) ||
          j.method.toLowerCase().includes(query) ||
          j.added_time.toLowerCase().includes(query);

        return matchStatus && matchMethod && matchSearch;
      }});

      renderTable(filtered);
    }}

    function setStatusFilter(type, btn) {{
      currentStatusFilter = type;
      btn.parentElement.querySelectorAll('.pill').forEach(p => {{
        p.classList.remove('active', 'active-applied', 'active-manual', 'active-auto', 'active-ready', 'active-skipped', 'active-closed');
      }});
      btn.classList.add('active');
      if (type === 'applied') btn.classList.add('active-applied');
      else if (type === 'manual') btn.classList.add('active-manual');
      else if (type === 'auto') btn.classList.add('active-auto');
      else if (type === 'ready') btn.classList.add('active-ready');
      else if (type === 'skipped') btn.classList.add('active-skipped');
      else if (type === 'closed') btn.classList.add('active-closed');
      filterJobs();
    }}

    function setMethodFilter(type, btn) {{
      currentMethodFilter = type;
      btn.parentElement.querySelectorAll('.pill-method').forEach(p => {{
        p.classList.remove('active', 'active-email', 'active-ats', 'active-easy');
      }});
      btn.classList.add('active');
      if (type === 'email') btn.classList.add('active-email');
      else if (type === 'ats') btn.classList.add('active-ats');
      else if (type === 'easy') btn.classList.add('active-easy');
      filterJobs();
    }}

    function openDetails(jobId) {{
      const j = allJobs.find(x => x.id === jobId);
      if (!j) return;

      const isManual = !!j.manual;
      const isApplied = j.status.includes('تم التقديم');

      document.getElementById('mCompanyRole').innerText = `${{j.company}} - ${{j.title}}`;
      document.getElementById('modalBody').innerHTML = `
        <div class="modal-manual-action-card">
          <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
            <div>
              <h4 style="font-size:13.5px; font-weight:800; color:var(--emerald-dark); margin-bottom:2px;">
                ${{isApplied ? '✓ الوظيفة مسجلة كـ "تم التقديم"' : 'توثيق التقديم اليدوي'}}
              </h4>
              <p style="font-size:12px; color:var(--text-muted);">
                ${{isManual ? 'تم تسجيل تقديمك المباشر في المنظومة وقاعدة البيانات.' : 'إذا قمت بالتقديم بنفسك على موقع الشركة أو لينكدإن، اضغط الزر لتحديث الحالة.'}}
              </p>
            </div>
            <button class="${{isManual ? 'btn-done-manual' : 'btn-mark-manual'}}" style="font-size:12px; padding:6px 14px;" onclick="toggleManualApply('${{j.id}}'); openDetails('${{j.id}}');">
              ${{isManual ? '↩ إلغاء التحديد' : '✅ تأكيد التقديم يدوياً'}}
            </button>
          </div>
        </div>
        <div class="modal-highlight-box">
          <div class="m-highlight-item">
            <span class="m-hl-label">⏰ تاريخ ووقت الإضافة:</span>
            <span class="m-hl-val" style="color:#0369a1;">🕒 ${{escapeHtml(j.added_time)}}</span>
          </div>
          <div class="m-highlight-item">
            <span class="m-hl-label">🎯 طريقة التقديم:</span>
            <span class="m-hl-val">${{escapeHtml(j.method)}}</span>
          </div>
        </div>
        <div class="modal-row">
          <div class="modal-label">الشركة والمسمى</div>
          <div class="modal-value">${{escapeHtml(j.company)}} | ${{escapeHtml(j.title)}}</div>
        </div>
        <div class="modal-grid">
          <div class="modal-row">
            <div class="modal-label">المدينة ونمط العمل</div>
            <div class="modal-value">${{escapeHtml(j.city)}}</div>
          </div>
          <div class="modal-row">
            <div class="modal-label">الحالة الحالية</div>
            <div class="modal-value"><strong>${{escapeHtml(j.status)}}</strong></div>
          </div>
        </div>
        <div class="modal-row">
          <div class="modal-label">جهة الاتصال</div>
          <div class="modal-value">${{escapeHtml(j.contact)}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">الراتب المستهدف</div>
          <div class="modal-value">${{escapeHtml(j.salary)}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">ملاحظات التقديم</div>
          <div class="modal-value" style="line-height:1.6;">${{escapeHtml(j.notes || 'شاغر مفحوص ومطابق لمعايير حسن سرحان.')}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">رابط التقديم المباشر</div>
          <div class="modal-value"><a href="${{j.url}}" target="_blank" style="color:var(--primary); word-break:break-all;">${{j.url}}</a></div>
        </div>
      `;
      document.getElementById('modalOverlay').style.display = 'flex';
    }}

    function closeModal() {{
      document.getElementById('modalOverlay').style.display = 'none';
    }}

    function openSyncModal() {{
      const manualStore = JSON.parse(localStorage.getItem('manual_applied_jobs') || '{{}}');
      const keys = Object.keys(manualStore);
      const container = document.getElementById('syncModalBody');

      if (keys.length === 0) {{
        container.innerHTML = `
          <div style="text-align:center; padding:24px; color:var(--text-muted);">
            <div style="font-size:36px; margin-bottom:8px;">✓</div>
            <h4 style="font-size:15px; color:var(--text-main); margin-bottom:4px;">كافة التقديمات متطابقة مع قوقل شيت</h4>
            <p style="font-size:12.5px;">لم تسجل أي تقديمات يدوية جديدة غير متزامنة على هذا المتصفح.</p>
          </div>
        `;
      }} else {{
        let listHtml = keys.map(k => {{
          const item = manualStore[k];
          return `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:#f8fafc; border:1px solid var(--border-color); border-radius:8px; margin-bottom:6px;">
              <div>
                <strong style="color:var(--text-main); font-size:13px;">${{escapeHtml(item.company)}}</strong>
                <span style="color:var(--text-muted); font-size:12px; margin-right:8px;">${{escapeHtml(item.title)}}</span>
              </div>
              <span style="font-size:11.5px; color:var(--emerald-dark); font-weight:700;">🕒 ${{item.time}}</span>
            </div>
          `;
        }}).join('');

        container.innerHTML = `
          <div style="margin-bottom:12px;">
            <p style="font-size:13px; color:var(--text-main); font-weight:600; margin-bottom:8px;">
              لديك <span style="color:var(--emerald-dark); font-weight:800;">${{keys.length}}</span> وظائف مسجلة يدوياً جاهزة للمزامنة:
            </p>
            <div style="max-height:220px; overflow-y:auto;">${{listHtml}}</div>
          </div>
        `;
      }}

      document.getElementById('syncModalOverlay').style.display = 'flex';
    }}

    function closeSyncModal() {{
      document.getElementById('syncModalOverlay').style.display = 'none';
    }}

    function copySyncCommand() {{
      const manualStore = JSON.parse(localStorage.getItem('manual_applied_jobs') || '{{}}');
      const keys = Object.keys(manualStore);
      if (keys.length === 0) {{
        showToast('ℹ️ لا توجد تقديمات يدوية جديدة للنسخ');
        return;
      }}
      const cmd = `python3 tools/sync_manual_applied.py ${{keys.join(' ')}}`;
      navigator.clipboard.writeText(cmd).then(() => {{
        showToast('📋 تم نسخ أمر المزامنة! الصقه في Terminal');
      }});
    }}

    function syncWithLocalServer() {{
      const manualStore = JSON.parse(localStorage.getItem('manual_applied_jobs') || '{{}}');
      const keys = Object.keys(manualStore);
      if (keys.length === 0) {{
        showToast('ℹ️ لا توجد تقديمات يدوية جديدة للمزامنة');
        return;
      }}

      let completed = 0;
      let failed = 0;

      Promise.all(keys.map(k =>
        fetch(`http://127.0.0.1:5050/api/mark_applied?id=${{k}}`, {{ mode: 'cors' }})
          .then(r => r.json())
          .then(data => {{ if (data.success) completed++; else failed++; }})
          .catch(() => failed++)
      )).then(() => {{
        if (completed > 0) {{
          showToast(`🎉 تمت المزامنة! تم تحديث ${{completed}} وظائف.`);
          closeSyncModal();
        }} else {{
          showToast('⚠️ تعذر الاتصال بالخادم المحلي. استخدم نسخ أمر Terminal.');
        }}
      }});
    }}

    function copyToClipboard() {{
      const headers = [
        'ID',
        'تاريخ الإضافة',
        'اسم الشركة',
        'المسمى الوظيفي',
        'طريقة التقديم',
        'المنصة',
        'المدينة',
        'رابط الوظيفة',
        'نسبة التوافق',
        'حالة التقديم',
        'جهة الاتصال',
        'الراتب المستهدف',
        'ملف السيرة الذاتية',
        'تاريخ المتابعة',
        'ملاحظات'
      ];

      const rows = allJobs.map(j => [
        j.id,
        j.added_time,
        j.company,
        j.title,
        j.method,
        j.platform,
        j.city,
        j.url,
        j.fit,
        j.status,
        j.contact,
        j.salary,
        j.cv,
        j.followup,
        j.notes
      ]);

      const tsvContent = [
        headers.join('\\t'),
        ...rows.map(r => r.map(c => (c || '').replace(/\\t/g, ' ').replace(/\\r?\\n/g, ' ')).join('\\t'))
      ].join('\\n');

      navigator.clipboard.writeText(tsvContent).then(() => {{
        showToast('✓ تم نسخ البيانات للجدول (Cmd+V)');
      }}).catch(() => {{
        showToast('فشل النسخ إلى الحافظة');
      }});
    }}

    function escapeHtml(text) {{
      if (!text) return '';
      return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }}

    // Initial render with localStorage hydration
    initManualApplied();
    filterJobs();
  </script>
</body>
</html>
"""
    return html_content


def main():
    jobs = load_jobs()
    platforms = load_platforms()
    html_content = build_html(jobs)

    # Inject platforms section before </body>
    if platforms:
        platforms_html = build_platforms_section_html(platforms)
        html_content = html_content.replace("</body>", platforms_html + "\n</body>", 1)

    # 1. Save to reports/application-dashboard.html
    reports_file = REPO_ROOT / "reports" / "application-dashboard.html"
    reports_file.parent.mkdir(parents=True, exist_ok=True)
    with open(reports_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 2. Save to docs/index.html (for GitHub Pages root)
    docs_file = REPO_ROOT / "docs" / "index.html"
    docs_file.parent.mkdir(parents=True, exist_ok=True)
    with open(docs_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Generated clean executive white-theme dashboard ({len(jobs)} jobs, {len(platforms)} platforms) in reports/ and docs/")


if __name__ == "__main__":
    main()
