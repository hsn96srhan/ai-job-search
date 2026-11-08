#!/usr/bin/env python3
"""Build and bundle the executive online dashboard for GitHub Pages."""

import csv
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"


def load_jobs():
    items = []
    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            raw_method = r.get("طريقة التقديم (Application Method)", "").strip()
            # Normalize method names to match user exact terminology: ايزي ابلاي / ايميل / بوابة خارجية
            if "إيميل" in raw_method or "ايميل" in raw_method or "email" in raw_method.lower():
                norm_method = "✉️ ايميل مباشر (Email - آلي)"
            elif "بوابة خارجية" in raw_method or "ats" in raw_method.lower():
                norm_method = "🌐 بوابة خارجية (ATS - آلي)"
            else:
                norm_method = "⚡ ايزي ابلاي (Easy Apply - يدوي)"

            items.append({
                "id": r.get("ID", "").strip(),
                "added_time": r.get("وقت وتاريخ الإضافة (Added Time)", r.get("التاريخ (Date)", "2026-11-08 03:25 ص")).strip(),
                "company": r.get("اسم الشركة (Company)", "").strip(),
                "title": r.get("المسمى الوظيفي (Job Title)", "").strip(),
                "method": norm_method,
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


def build_html(jobs):
    jobs_json = json.dumps(jobs, ensure_ascii=False)

    applied_count = sum(1 for j in jobs if "تم التقديم" in j["status"])
    ready_count = sum(1 for j in jobs if "جاهز" in j["status"])
    skipped_count = sum(1 for j in jobs if "تم التخطي" in j["status"])
    closed_count = sum(1 for j in jobs if "مغلقة" in j["status"])
    total_count = len(jobs)

    # Method Counts
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
  <title>لوحة التقديم الآلي والتتبع التنفيذي | حسن سرحان</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0b0f19;
      --card-bg: #111827;
      --card-border: #1f2937;
      --text-main: #f9fafb;
      --text-muted: #9ca3af;
      --accent-green: #10b981;
      --accent-blue: #3b82f6;
      --accent-purple: #8b5cf6;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-cyan: #06b6d4;
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
      line-height: 1.6;
      min-height: 100vh;
      padding: 24px 16px;
    }}

    .container {{
      max-width: 1460px;
      margin: 0 auto;
    }}

    /* Top Header */
    .header {{
      background: linear-gradient(135deg, #111827 0%, #1e1b4b 100%);
      border: 1px solid #312e81;
      border-radius: 16px;
      padding: 22px 28px;
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }}

    .profile-info h1 {{
      font-size: 23px;
      font-weight: 800;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .badge-live {{
      font-size: 12px;
      font-weight: 700;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 4px 10px;
      border-radius: 20px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .badge-live::before {{
      content: "";
      width: 8px;
      height: 8px;
      background-color: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 8px #10b981;
    }}

    .profile-meta {{
      font-size: 13.5px;
      color: #cbd5e1;
      margin-top: 6px;
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .profile-meta span {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .header-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}

    .btn {{
      font-family: var(--font);
      font-size: 13px;
      font-weight: 700;
      padding: 10px 18px;
      border-radius: 10px;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      transition: all 0.2s ease;
    }}

    .btn-primary {{
      background: #2563eb;
      color: #ffffff;
    }}
    .btn-primary:hover {{ background: #1d4ed8; transform: translateY(-1px); }}

    .btn-success {{
      background: #059669;
      color: #ffffff;
    }}
    .btn-success:hover {{ background: #047857; transform: translateY(-1px); }}

    .btn-secondary {{
      background: #1f2937;
      color: #e5e7eb;
      border: 1px solid #374151;
    }}
    .btn-secondary:hover {{ background: #374151; }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }}

    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 18px 20px;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease;
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
    }}

    .kpi-card::before {{
      content: "";
      position: absolute;
      top: 0;
      right: 0;
      left: 0;
      height: 4px;
    }}

    .kpi-total::before {{ background: #6366f1; }}
    .kpi-applied::before {{ background: var(--accent-green); }}
    .kpi-ready::before {{ background: var(--accent-blue); }}
    .kpi-skipped::before {{ background: #64748b; }}

    .kpi-label {{
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 4px;
    }}

    .kpi-number {{
      font-size: 30px;
      font-weight: 900;
      line-height: 1.1;
      margin-bottom: 4px;
    }}

    .kpi-total .kpi-number {{ color: #a5b4fc; }}
    .kpi-applied .kpi-number {{ color: #34d399; }}
    .kpi-ready .kpi-number {{ color: #60a5fa; }}
    .kpi-skipped .kpi-number {{ color: #94a3b8; }}

    .kpi-subtext {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    /* Dedicated Application Channels Section */
    .channels-card {{
      background: #101626;
      border: 1px solid #1e293b;
      border-radius: 14px;
      padding: 18px 22px;
      margin-bottom: 20px;
    }}

    .channels-header-row {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      gap: 10px;
    }}

    .channels-title {{
      font-size: 14px;
      font-weight: 800;
      color: #f1f5f9;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .channels-sync-time {{
      font-size: 12px;
      color: #94a3b8;
      background: #0b0f19;
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid #1e293b;
    }}

    .channels-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
    }}

    .channel-box {{
      background: #141d33;
      border-radius: 12px;
      padding: 14px 16px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      border: 1px solid transparent;
      transition: all 0.2s ease;
    }}

    .channel-box:hover {{
      transform: translateY(-2px);
    }}

    .ch-easy {{
      border-color: rgba(245, 158, 11, 0.35);
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, #141d33 100%);
    }}

    .ch-email {{
      border-color: rgba(139, 92, 246, 0.35);
      background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, #141d33 100%);
    }}

    .ch-ats {{
      border-color: rgba(6, 182, 212, 0.35);
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, #141d33 100%);
    }}

    .ch-icon {{
      font-size: 24px;
      line-height: 1;
      padding-top: 2px;
    }}

    .ch-info {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .ch-name {{
      font-size: 14px;
      font-weight: 800;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .ch-easy .ch-name {{ color: #fcd34d; }}
    .ch-email .ch-name {{ color: #c4b5fd; }}
    .ch-ats .ch-name {{ color: #67e8f9; }}

    .ch-count {{
      font-size: 13px;
      font-weight: 900;
      background: rgba(0, 0, 0, 0.3);
      padding: 2px 8px;
      border-radius: 6px;
    }}

    .ch-desc {{
      font-size: 12px;
      color: #94a3b8;
      line-height: 1.5;
    }}

    /* Controls Bar */
    .controls-bar {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 16px 20px;
      margin-bottom: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .controls-top {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}

    .search-box {{
      flex: 1;
      min-width: 280px;
      position: relative;
    }}

    .search-box input {{
      width: 100%;
      font-family: var(--font);
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 10px 16px 10px 40px;
      color: #ffffff;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s ease;
    }}

    .search-box input:focus {{
      border-color: #3b82f6;
    }}

    .search-box svg {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: #64748b;
      width: 18px;
      height: 18px;
    }}

    .filter-section {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
    }}

    .filter-label {{
      font-size: 12.5px;
      font-weight: 800;
      color: #cbd5e1;
      min-width: 120px;
    }}

    .filter-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .pill {{
      font-family: var(--font);
      font-size: 12px;
      font-weight: 700;
      padding: 6px 14px;
      border-radius: 8px;
      border: 1px solid #334155;
      background: #0f172a;
      color: #cbd5e1;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .pill:hover {{
      background: #1e293b;
    }}

    .pill.active {{
      background: #2563eb;
      color: #ffffff;
      border-color: #2563eb;
    }}

    .pill-method.active-email {{
      background: #7c3aed !important;
      border-color: #7c3aed !important;
      color: #ffffff !important;
    }}

    .pill-method.active-ats {{
      background: #0891b2 !important;
      border-color: #0891b2 !important;
      color: #ffffff !important;
    }}

    .pill-method.active-easy {{
      background: #d97706 !important;
      border-color: #d97706 !important;
      color: #ffffff !important;
    }}

    /* Table Container */
    .table-container {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      overflow-x: auto;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: right;
      font-size: 13.5px;
    }}

    th {{
      background: #0f172a;
      color: #94a3b8;
      font-size: 12px;
      font-weight: 800;
      padding: 14px 16px;
      border-bottom: 1px solid #1e293b;
      white-space: nowrap;
    }}

    th.th-highlight {{
      color: #38bdf8;
      background: #131d33;
    }}

    td {{
      padding: 14px 16px;
      border-bottom: 1px solid #1f2937;
      vertical-align: middle;
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    tr:hover td {{
      background-color: rgba(30, 41, 59, 0.45);
    }}

    .company-cell strong {{
      color: #ffffff;
      font-size: 14.5px;
      display: block;
    }}

    .company-cell span {{
      color: #64748b;
      font-size: 12px;
    }}

    .role-cell {{
      font-weight: 600;
      color: #e2e8f0;
      max-width: 280px;
    }}

    /* Method Badges (ايزي ابلاي / ايميل / بوابة خارجية) */
    .badge-method {{
      font-size: 12px;
      font-weight: 800;
      padding: 6px 12px;
      border-radius: 8px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}

    .method-email {{
      background: rgba(139, 92, 246, 0.22);
      color: #c4b5fd;
      border: 1px solid rgba(139, 92, 246, 0.45);
    }}

    .method-ats {{
      background: rgba(6, 182, 212, 0.22);
      color: #67e8f9;
      border: 1px solid rgba(6, 182, 212, 0.45);
    }}

    .method-easy {{
      background: rgba(245, 158, 11, 0.22);
      color: #fcd34d;
      border: 1px solid rgba(245, 158, 11, 0.45);
    }}

    /* Time Badge: وقت إضافة الوظيفة على الداشبورد */
    .time-cell {{
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}

    .time-main {{
      font-size: 12.5px;
      font-weight: 700;
      color: #38bdf8;
      background: #0f172a;
      border: 1px solid #1e293b;
      padding: 4px 8px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }}

    .time-sub {{
      font-size: 10.5px;
      color: #64748b;
      font-weight: 600;
    }}

    /* Status Tags */
    .tag-status {{
      font-size: 11px;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 6px;
      display: inline-block;
      white-space: nowrap;
    }}

    .status-applied {{
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    .status-ready {{
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }}

    .status-skipped {{
      background: rgba(148, 163, 184, 0.15);
      color: #94a3b8;
      border: 1px solid rgba(148, 163, 184, 0.3);
    }}

    .status-closed {{
      background: rgba(244, 63, 94, 0.15);
      color: #fb7185;
      border: 1px solid rgba(244, 63, 94, 0.3);
    }}

    .fit-meter {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 700;
    }}

    .fit-bar {{
      width: 60px;
      height: 6px;
      background: #1e293b;
      border-radius: 3px;
      overflow: hidden;
    }}

    .fit-fill {{
      height: 100%;
      border-radius: 3px;
    }}

    .action-cell {{
      white-space: nowrap;
    }}

    .btn-apply {{
      font-family: var(--font);
      font-size: 12px;
      font-weight: 700;
      padding: 6px 12px;
      border-radius: 8px;
      background: #2563eb;
      color: #ffffff;
      text-decoration: none;
      display: inline-block;
      transition: background 0.15s ease;
    }}

    .btn-apply:hover {{
      background: #1d4ed8;
    }}

    .btn-done {{
      font-size: 12px;
      font-weight: 700;
      color: #34d399;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .btn-view {{
      font-family: var(--font);
      font-size: 12px;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 8px;
      background: #1e293b;
      color: #cbd5e1;
      border: 1px solid #334155;
      cursor: pointer;
      margin-left: 6px;
    }}

    .btn-view:hover {{
      background: #334155;
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: #059669;
      color: #ffffff;
      padding: 12px 24px;
      border-radius: 12px;
      font-weight: 700;
      font-size: 14px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .toast.show {{
      transform: translateX(-50%) translateY(0);
    }}

    /* Modal */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(4px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 999;
      padding: 16px;
    }}

    .modal-card {{
      background: #111827;
      border: 1px solid #374151;
      border-radius: 16px;
      width: 100%;
      max-width: 680px;
      padding: 24px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
      max-height: 90vh;
      overflow-y: auto;
    }}

    .modal-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 16px;
      border-bottom: 1px solid #1f2937;
      padding-bottom: 14px;
    }}

    .modal-title {{
      font-size: 18px;
      font-weight: 800;
      color: #ffffff;
    }}

    .modal-close {{
      background: none;
      border: none;
      color: #94a3b8;
      font-size: 24px;
      cursor: pointer;
    }}

    .modal-highlight-box {{
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .m-highlight-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }}

    .m-hl-label {{
      font-size: 13px;
      font-weight: 700;
      color: #94a3b8;
    }}

    .m-hl-val {{
      font-size: 13.5px;
      font-weight: 800;
      color: #f1f5f9;
    }}

    .modal-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 12px;
    }}

    .modal-row {{
      margin-bottom: 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .modal-label {{
      font-size: 12px;
      color: #94a3b8;
      font-weight: 600;
    }}

    .modal-value {{
      font-size: 14px;
      color: #f1f5f9;
      background: #0f172a;
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid #1e293b;
    }}
  </style>
</head>
<body>

  <div class="container">

    <!-- Top Executive Header -->
    <header class="header">
      <div class="profile-info">
        <h1>
          حسن سرحان | لوحة التقديم الآلي والتتبع
          <span class="badge-live">نظام متصل ومحدّث لحظياً</span>
        </h1>
        <div class="profile-meta">
          <span>💼 مدير تسويق تنفيذي (معتمد من HRSD)</span>
          <span>📍 الرياض، السعودية</span>
          <span>💰 الراتب: أساسي 8,000 ريال / باكدج 10,000 ريال</span>
          <span>⚡ فترة الإشعار: فوري (15 يوم)</span>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-success" onclick="copyToClipboard()">
          📋 نسخ للشيت (Cmd+V)
        </button>
        <a href="https://docs.google.com/spreadsheets/d/1pmyTxkwRc8NjddIfraoZzgV5CMulabVA59hdvKVzsYs" target="_blank" class="btn btn-primary">
          📊 فتح قوقل شيت
        </a>
        <a href="https://hsn96srhan.github.io/hsn/" target="_blank" class="btn btn-secondary">
          🌐 البورتفوليو
        </a>
      </div>
    </header>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card kpi-total">
        <div class="kpi-label">إجمالي الفرص المفحوصة</div>
        <div class="kpi-number" id="kpi-total">{total_count}</div>
        <div class="kpi-subtext">شواغر تسويق مستهدفة بالرياض وعن بعد</div>
      </div>
      <div class="kpi-card kpi-applied">
        <div class="kpi-label">تم التقديم رسمياً</div>
        <div class="kpi-number" id="kpi-applied">{applied_count}</div>
        <div class="kpi-subtext">تقديم مؤكد عبر البريد وبوابات ATS مع إرفاق السيرة الذاتية</div>
      </div>
      <div class="kpi-card kpi-ready">
        <div class="kpi-label">جاهز للتقديم الفوري</div>
        <div class="kpi-number" id="kpi-ready">{ready_count}</div>
        <div class="kpi-subtext">فرص مؤهلة ومطابقة لكافة معاييرك التنفيذية</div>
      </div>
      <div class="kpi-card kpi-skipped">
        <div class="kpi-label">مستبعد / مغلق من جهة العمل</div>
        <div class="kpi-number" id="kpi-skipped">{skipped_count + closed_count}</div>
        <div class="kpi-subtext">شروط غير مطابقة أو شواغر أغلقت التقديم</div>
      </div>
    </div>

    <!-- Prominent Dedicated Channels Box (ايزي ابلاي / ايميل / بوابة خارجية) -->
    <div class="channels-card">
      <div class="channels-header-row">
        <div class="channels-title">
          <span>🎯 تصنيف طرق التقديم المستخدمة في لوحة التحكم (Channels):</span>
        </div>
        <div class="channels-sync-time">
          🕒 آخر فحص ومزامنة: {now_str} (بتوقيت الرياض)
        </div>
      </div>
      <div class="channels-grid">
        <div class="channel-box ch-easy">
          <div class="ch-icon">⚡</div>
          <div class="ch-info">
            <div class="ch-name">
              <span>ايزي ابلاي (Easy Apply - يدوي)</span>
              <span class="ch-count">{easy_count} وظيفة</span>
            </div>
            <div class="ch-desc">
              شواغر التقديم السريع عبر لينكد إن — مخصصة لتقديمك اليدوي بضغطة زر واحدة دون تدخل البوت.
            </div>
          </div>
        </div>
        <div class="channel-box ch-email">
          <div class="ch-icon">✉️</div>
          <div class="ch-info">
            <div class="ch-name">
              <span>ايميل مباشر (Direct Email - آلي)</span>
              <span class="ch-count">{email_count} وظائف</span>
            </div>
            <div class="ch-desc">
              تم التقديم عليها وإرسال السيرة الذاتية PDF التنفيذية آلياً عبر SMTP مع متابعة الردود.
            </div>
          </div>
        </div>
        <div class="channel-box ch-ats">
          <div class="ch-icon">🌐</div>
          <div class="ch-info">
            <div class="ch-name">
              <span>بوابة خارجية (External ATS - آلي)</span>
              <span class="ch-count">{ats_count} وظيفة</span>
            </div>
            <div class="ch-desc">
              بوابات توظيف عالمية (Teamtailor, Ashby, Oracle HCM, Workday) تم التقديم عليها بروبوت المتصفح.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Controls & Multi-Filters -->
    <div class="controls-bar">
      <div class="controls-top">
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input type="text" id="searchInput" placeholder="ابحث باسم الشركة، المسمى، طريقة التقديم (ايزي ابلاي/ايميل/بوابة)، أو وقت الإضافة..." oninput="filterJobs()">
        </div>
      </div>

      <!-- Filter Row 1: Method -->
      <div class="filter-section">
        <span class="filter-label">طريقة التقديم:</span>
        <div class="filter-pills">
          <button class="pill pill-method active" onclick="setMethodFilter('all', this)">جميع الطرق ({total_count})</button>
          <button class="pill pill-method" onclick="setMethodFilter('easy', this)">⚡ ايزي ابلاي ({easy_count})</button>
          <button class="pill pill-method" onclick="setMethodFilter('email', this)">✉️ ايميل مباشر ({email_count})</button>
          <button class="pill pill-method" onclick="setMethodFilter('ats', this)">🌐 بوابة خارجية ({ats_count})</button>
        </div>
      </div>

      <!-- Filter Row 2: Status -->
      <div class="filter-section">
        <span class="filter-label">حالة التقديم:</span>
        <div class="filter-pills">
          <button class="pill active" onclick="setStatusFilter('all', this)">الكل ({total_count})</button>
          <button class="pill" onclick="setStatusFilter('applied', this)">تم التقديم ({applied_count})</button>
          <button class="pill" onclick="setStatusFilter('ready', this)">جاهز للتقديم ({ready_count})</button>
          <button class="pill" onclick="setStatusFilter('skipped', this)">مستبعد ({skipped_count})</button>
          <button class="pill" onclick="setStatusFilter('closed', this)">مغلق ({closed_count})</button>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>الشركة والمصدر</th>
            <th>المسمى الوظيفي</th>
            <th class="th-highlight">طريقة التقديم المستخدمة</th>
            <th class="th-highlight">وقت إضافة الوظيفة على الداشبورد</th>
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

  <!-- Toast -->
  <div id="toast" class="toast">
    <span>✓ تم نسخ كافة بيانات الشيت الـ 15 عموداً إلى الحافظة بنجاح! يمكنك لصقها الآن (Cmd+V).</span>
  </div>

  <!-- Details Modal -->
  <div id="modalOverlay" class="modal-overlay" onclick="closeModal(event)">
    <div class="modal-card" onclick="event.stopPropagation()">
      <div class="modal-header">
        <div class="modal-title" id="mCompanyRole">تفاصيل الشاغر</div>
        <button class="modal-close" onclick="closeModal()">&times;</button>
      </div>
      <div id="modalBody"></div>
    </div>
  </div>

  <script>
    const allJobs = {jobs_json};
    let currentStatusFilter = 'all';
    let currentMethodFilter = 'all';

    function renderTable(jobs) {{
      const tbody = document.getElementById('jobsTableBody');
      tbody.innerHTML = '';

      if (jobs.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:35px; color:#94a3b8;">لا توجد شواغر مطابقة لمعايير البحث والتصفية المختارة</td></tr>';
        return;
      }}

      jobs.forEach(j => {{
        const tr = document.createElement('tr');

        // Status tag
        let statusTag = '';
        if (j.status.includes('تم التقديم')) {{
          statusTag = '<span class="tag-status status-applied">✓ تم التقديم</span>';
        }} else if (j.status.includes('جاهز')) {{
          statusTag = '<span class="tag-status status-ready">🚀 جاهز للتقديم</span>';
        }} else if (j.status.includes('مغلقة')) {{
          statusTag = '<span class="tag-status status-closed">🔒 مغلقة</span>';
        }} else {{
          statusTag = '<span class="tag-status status-skipped">⚠️ تم التخطي</span>';
        }}

        // Method tag (ايزي ابلاي / ايميل مباشر / بوابة خارجية)
        let methodTag = '';
        if (j.method.includes('ايميل')) {{
          methodTag = '<span class="badge-method method-email">✉️ ايميل مباشر (آلي)</span>';
        }} else if (j.method.includes('بوابة خارجية')) {{
          methodTag = '<span class="badge-method method-ats">🌐 بوابة خارجية (آلي)</span>';
        }} else {{
          methodTag = '<span class="badge-method method-easy">⚡ ايزي ابلاي (يدوي)</span>';
        }}

        // Fit meter
        const fitNum = parseInt(j.fit.replace(/[^0-9]/g, '')) || 85;
        const fitColor = fitNum >= 88 ? '#10b981' : (fitNum >= 80 ? '#3b82f6' : '#94a3b8');

        // Action button
        let actionBtn = '';
        if (j.status.includes('تم التقديم')) {{
          actionBtn = '<span class="btn-done">✓ تم إرسال الطلب</span>';
        }} else if (j.status.includes('مغلقة')) {{
          actionBtn = '<span style="color:#fb7185; font-size:12px; font-weight:700;">مغلقة من الشركة</span>';
        }} else if (j.status.includes('تم التخطي')) {{
          actionBtn = '<span style="color:#64748b; font-size:12px;">مستبعد من التقديم</span>';
        }} else {{
          actionBtn = `<a href="${{j.url}}" target="_blank" class="btn-apply">قدّم الآن ↗</a>`;
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
              <span class="time-sub">📅 ${{escapeHtml(datePart)}} (أضيفت للداشبورد)</span>
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
        if (currentStatusFilter === 'applied') matchStatus = j.status.includes('تم التقديم');
        else if (currentStatusFilter === 'ready') matchStatus = j.status.includes('جاهز');
        else if (currentStatusFilter === 'skipped') matchStatus = j.status.includes('تم التخطي');
        else if (currentStatusFilter === 'closed') matchStatus = j.status.includes('مغلقة');

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
      btn.parentElement.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
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

      document.getElementById('mCompanyRole').innerText = `${{j.company}} - ${{j.title}}`;
      document.getElementById('modalBody').innerHTML = `
        <div class="modal-highlight-box">
          <div class="m-highlight-item">
            <span class="m-hl-label">⏰ وقت إضافة الوظيفة على الداشبورد:</span>
            <span class="m-hl-val" style="color:#38bdf8;">🕒 ${{escapeHtml(j.added_time)}} (بتوقيت الرياض)</span>
          </div>
          <div class="m-highlight-item">
            <span class="m-hl-label">🎯 طريقة التقديم المعتمدة:</span>
            <span class="m-hl-val">${{escapeHtml(j.method)}}</span>
          </div>
        </div>
        <div class="modal-row">
          <div class="modal-label">الشركة والمسمى الوظيفي</div>
          <div class="modal-value">${{escapeHtml(j.company)}} | ${{escapeHtml(j.title)}}</div>
        </div>
        <div class="modal-grid">
          <div class="modal-row">
            <div class="modal-label">المدينة ونمط العمل</div>
            <div class="modal-value">${{escapeHtml(j.city)}}</div>
          </div>
          <div class="modal-row">
            <div class="modal-label">حالة التقديم الحالية</div>
            <div class="modal-value"><strong>${{escapeHtml(j.status)}}</strong></div>
          </div>
        </div>
        <div class="modal-row">
          <div class="modal-label">مسؤول التوظيف / جهة الاتصال</div>
          <div class="modal-value">${{escapeHtml(j.contact)}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">الراتب المستهدف</div>
          <div class="modal-value">${{escapeHtml(j.salary)}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">ملاحظات وتأكيد التقديم الفعلي</div>
          <div class="modal-value" style="line-height:1.7;">${{escapeHtml(j.notes || 'شاغر مفحوص ومطابق لمعايير حسن سرحان.')}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">رابط التقديم المباشر</div>
          <div class="modal-value"><a href="${{j.url}}" target="_blank" style="color:#60a5fa; word-break:break-all;">${{j.url}}</a></div>
        </div>
      `;

      document.getElementById('modalOverlay').style.display = 'flex';
    }}

    function closeModal(e) {{
      document.getElementById('modalOverlay').style.display = 'none';
    }}

    function copyToClipboard() {{
      const headers = [
        'ID',
        'وقت وتاريخ الإضافة على الداشبورد',
        'اسم الشركة',
        'المسمى الوظيفي',
        'طريقة التقديم (ايزي ابلاي / ايميل / بوابة)',
        'المنصة / المصدر',
        'المدينة',
        'رابط الوظيفة',
        'نسبة التوافق',
        'حالة التقديم',
        'جهة الاتصال',
        'الراتب المستهدف',
        'نسخة السيرة الذاتية',
        'تاريخ المتابعة',
        'ملاحظات وتأكيد التقديم'
      ];
      const tsvRows = [headers.join('\\t')];

      allJobs.forEach(j => {{
        tsvRows.push([
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
        ].map(val => (val || '').replace(/\\t/g, ' ').replace(/\\n/g, ' ')).join('\\t'));
      }});

      navigator.clipboard.writeText(tsvRows.join('\\n')).then(() => {{
        const toast = document.getElementById('toast');
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3500);
      }});
    }}

    function escapeHtml(text) {{
      if (!text) return '';
      return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }}

    // Initial render
    renderTable(allJobs);
  </script>
</body>
</html>
"""
    return html_content


def main():
    jobs = load_jobs()
    html_content = build_html(jobs)

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

    print(f"✓ Generated executive dashboard ({len(jobs)} jobs) in reports/ and docs/")


if __name__ == "__main__":
    main()
