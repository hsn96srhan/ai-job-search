#!/usr/bin/env python3
"""Build and render complete HTML dashboard from saudi_jobs_google_sheets_tracker.csv."""

import csv
import html
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"
DASHBOARD_FILE = REPO_ROOT / "reports" / "application-dashboard.html"


def generate_table_rows(data_rows):
    html_rows = []

    for idx, r in enumerate(data_rows, 1):
        if not r or len(r) < 7:
            continue

        # Extract columns
        # In original rows: 0:ID, 1:Date, 2:Company, 3:Title, 4:Platform, 5:City, 6:URL, 7:Fit, 8:Status...
        # In newly added rows: 0:ID, 1:Company, 2:Title, 3:City, 4:Fit, 5:Status, 6:URL...
        if len(r) >= 14 and r[1].startswith("2026"):
            # Original format
            cid = r[0]
            company = r[2]
            title = r[3]
            city = r[5]
            url = r[6]
            fit = r[7]
            status = r[8]
            contact = r[9]
            notes = r[13]
        else:
            # New format
            cid = r[0]
            company = r[1]
            title = r[2]
            city = r[3]
            fit = r[4]
            status = r[5]
            url = r[6]
            contact = r[7] if len(r) > 7 else ""
            notes = r[11] if len(r) > 11 else ""

        fit_num = int(re.sub(r"[^\d]", "", fit)) if re.sub(r"[^\d]", "", fit) else 85
        fit_color = "#16a34a" if fit_num >= 85 else ("#2563eb" if fit_num >= 80 else "#94a3b8")

        pill_class = "pill-ready"
        row_bg = ""
        if "تم التقديم" in status:
            pill_class = "pill-applied"
            row_bg = "background:#f0fdf4;"
        elif "تم التخطي" in status:
            pill_class = "pill-skipped"
            row_bg = "background:#f8fafc;"

        # Action cell
        if "تم التقديم" in status:
            action_html = f"""<span style="font-size:12px; color:#15803d; font-weight:700;">
              ✓ تم إرسال السيرة الذاتية رسمياً ({html.escape(contact)})
            </span>"""
        elif "تم التخطي" in status:
            action_html = f"""<span style="font-size:12px; color:#64748b;">
              ⚠️ {html.escape(notes if notes else 'مستبعد بحسب المعايير')}
            </span>"""
        else:
            action_html = f"""<a href="{html.escape(url)}" target="_blank" class="btn-apply-1click" style="text-decoration:none;">
              🚀 قدّم الآن بالرابط المباشر
            </a>
            <button class="btn-details" onclick="openApplyAndShowPitch('{html.escape(url)}', 'general')">
              📋 تفاصيل
            </button>"""

        clean_company = html.escape(company)
        clean_title = html.escape(title)
        clean_city = html.escape(city)

        row_html = f"""          <tr style="{row_bg}">
            <td>
              <strong>{clean_company}</strong>
            </td>
            <td>{clean_title}</td>
            <td>{clean_city}</td>
            <td>
              <div class="fit-meter">
                <div class="fit-bar-bg"><div class="fit-bar-fill" style="width: {fit_num}%; background:{fit_color};"></div></div>
                <strong>{fit_num}%</strong>
              </div>
            </td>
            <td><span class="pill {pill_class}">{html.escape(status)}</span></td>
            <td>{action_html}</td>
          </tr>"""
        html_rows.append(row_html)

    return "\n".join(html_rows)


def main():
    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    data_rows = rows[1:]
    applied_count = sum(1 for r in data_rows if "تم التقديم" in r)
    ready_count = sum(1 for r in data_rows if "جاهز للتقديم" in r)
    skipped_count = sum(1 for r in data_rows if "تم التخطي" in r)

    table_body = generate_table_rows(data_rows)

    with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Update KPIs
    content = re.sub(
        r'<div class="kpi-card green"[^>]*>.*?<div class="kpi-value"[^>]*>\d+</div>.*?</div>\s*</div>',
        f"""<div class="kpi-card green" style="padding:12px 16px; border-right-color:#16a34a; background:#f0fdf4;">
        <div class="kpi-title" style="color:#166534; font-size:11px;">تم التقديم</div>
        <div class="kpi-value" style="font-size:22px; color:#15803d; margin:2px 0;">{applied_count}</div>
        <div class="kpi-desc" style="font-size:11px;">تقديم آلي بالإيميل (سحاب الجنوب + RAM Systems + Corebridge + Astek)</div>
      </div>""",
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r'<div class="kpi-card"[^>]*border-right-color:#2563eb;[^>]*>.*?<div class="kpi-value"[^>]*>\d+</div>.*?</div>\s*</div>',
        f"""<div class="kpi-card" style="padding:12px 16px; border-right-color:#2563eb; background:#eff6ff;">
        <div class="kpi-title" style="color:#1e40af; font-size:11px;">جاهز للتقديم الفعلي</div>
        <div class="kpi-value" style="font-size:22px; color:#2563eb; margin:2px 0;">{ready_count}</div>
        <div class="kpi-desc" style="font-size:11px;">شواغر حقيقية مفحوصة ومجهزة بالكامل للتقديم</div>
      </div>""",
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r'<div class="kpi-card"[^>]*border-right-color:#94a3b8;[^>]*>.*?<div class="kpi-value"[^>]*>\d+</div>.*?</div>\s*</div>',
        f"""<div class="kpi-card" style="padding:12px 16px; border-right-color:#94a3b8; background:#f8fafc;">
        <div class="kpi-title" style="color:#475569; font-size:11px;">تم التخطي (مستبعد)</div>
        <div class="kpi-value" style="font-size:22px; color:#64748b; margin:2px 0;">{skipped_count}</div>
        <div class="kpi-desc" style="font-size:11px;">شروط غير مطابقة (سعوديين فقط / حضوري خارج الرياض)</div>
      </div>""",
        content,
        flags=re.DOTALL
    )

    # Replace tbody
    content = re.sub(
        r'<tbody>.*?</tbody>',
        f'<tbody>\n{table_body}\n        </tbody>',
        content,
        flags=re.DOTALL
    )

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✓ تم تحديث لوحة التحكم بنجاح: {applied_count} تم التقديم | {ready_count} جاهز للتقديم | {skipped_count} تم التخطي | الإجمالي {len(data_rows)}")


if __name__ == "__main__":
    main()

