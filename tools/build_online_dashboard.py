#!/usr/bin/env python3
"""Build and bundle the executive online dashboard for GitHub Pages."""

import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"


def load_jobs():
    items = []
    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for r in reader:
            if len(r) >= 14:
                items.append({
                    "id": r[0].strip(),
                    "date": r[1].strip(),
                    "company": r[2].strip(),
                    "title": r[3].strip(),
                    "platform": r[4].strip(),
                    "city": r[5].strip(),
                    "url": r[6].strip(),
                    "fit": r[7].strip(),
                    "status": r[8].strip(),
                    "contact": r[9].strip(),
                    "salary": r[10].strip(),
                    "cv": r[11].strip(),
                    "followup": r[12].strip(),
                    "notes": r[13].strip()
                })
    return items


def build_html(jobs):
    jobs_json = json.dumps(jobs, ensure_ascii=False)

    applied_count = sum(1 for j in jobs if "تم التقديم" in j["status"])
    ready_count = sum(1 for j in jobs if "جاهز للتقديم" in j["status"])
    skipped_count = sum(1 for j in jobs if "تم التخطي" in j["status"])
    closed_count = sum(1 for j in jobs if "مغلقة" in j["status"])
    total_count = len(jobs)

    html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
      max-width: 1400px;
      margin: 0 auto;
    }}

    /* Top Header */
    .header {{
      background: linear-gradient(135deg, #111827 0%, #1e1b4b 100%);
      border: 1px solid #312e81;
      border-radius: 16px;
      padding: 24px 28px;
      margin-bottom: 24px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }}

    .profile-info h1 {{
      font-size: 24px;
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
      font-size: 14px;
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
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 20px;
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
      margin-bottom: 6px;
    }}

    .kpi-number {{
      font-size: 32px;
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

    /* Controls Bar */
    .controls-bar {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 16px 20px;
      margin-bottom: 20px;
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
    }}

    .pill:hover {{
      background: #1e293b;
    }}

    .pill.active {{
      background: #2563eb;
      color: #ffffff;
      border-color: #2563eb;
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
      font-size: 14px;
    }}

    th {{
      background: #0f172a;
      color: #94a3b8;
      font-size: 12px;
      font-weight: 700;
      padding: 14px 18px;
      border-bottom: 1px solid #1e293b;
      white-space: nowrap;
    }}

    td {{
      padding: 14px 18px;
      border-bottom: 1px solid #1f2937;
      vertical-align: middle;
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    tr:hover td {{
      background-color: rgba(30, 41, 59, 0.5);
    }}

    .company-cell strong {{
      color: #ffffff;
      font-size: 15px;
      display: block;
    }}

    .company-cell span {{
      color: #64748b;
      font-size: 12px;
    }}

    .role-cell {{
      font-weight: 600;
      color: #e2e8f0;
      max-width: 320px;
    }}

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
      gap: 10px;
      font-weight: 700;
    }}

    .fit-bar {{
      width: 70px;
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
      padding: 6px 14px;
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
      margin-right: 6px;
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
      background: rgba(0, 0, 0, 0.7);
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
      max-width: 600px;
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
          <span class="badge-live">نظام متصل لحظياً</span>
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

    <!-- Controls & Filters -->
    <div class="controls-bar">
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" id="searchInput" placeholder="ابحث باسم الشركة، المسمى الوظيفي، أو المدينة..." oninput="filterJobs()">
      </div>
      <div class="filter-pills">
        <button class="pill active" onclick="setFilter('all', this)">الكل ({total_count})</button>
        <button class="pill" onclick="setFilter('applied', this)">تم التقديم ({applied_count})</button>
        <button class="pill" onclick="setFilter('ready', this)">جاهز للتقديم ({ready_count})</button>
        <button class="pill" onclick="setFilter('skipped', this)">مستبعد ({skipped_count})</button>
        <button class="pill" onclick="setFilter('closed', this)">مغلق ({closed_count})</button>
      </div>
    </div>

    <!-- Table -->
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>الشركة</th>
            <th>المسمى الوظيفي</th>
            <th>المدينة</th>
            <th>نسبة التوافق</th>
            <th>حالة التقديم</th>
            <th>الإجراء المباشر</th>
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
    <span>✓ تم نسخ بيانات الشيت إلى الحافظة بنجاح! يمكنك الآن لصقها (Cmd+V).</span>
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
    let currentFilter = 'all';

    function renderTable(jobs) {{
      const tbody = document.getElementById('jobsTableBody');
      tbody.innerHTML = '';

      if (jobs.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:30px; color:#94a3b8;">لا توجد شواغر مطابقة لمعايير البحث الحالية</td></tr>';
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

        tr.innerHTML = `
          <td class="company-cell">
            <strong>${{escapeHtml(j.company)}}</strong>
            <span>${{escapeHtml(j.platform)}}</span>
          </td>
          <td class="role-cell">${{escapeHtml(j.title)}}</td>
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
        let matchFilter = true;
        if (currentFilter === 'applied') matchFilter = j.status.includes('تم التقديم');
        else if (currentFilter === 'ready') matchFilter = j.status.includes('جاهز');
        else if (currentFilter === 'skipped') matchFilter = j.status.includes('تم التخطي');
        else if (currentFilter === 'closed') matchFilter = j.status.includes('مغلقة');

        // Match search text
        const matchSearch =
          !query ||
          j.company.toLowerCase().includes(query) ||
          j.title.toLowerCase().includes(query) ||
          j.city.toLowerCase().includes(query);

        return matchFilter && matchSearch;
      }});

      renderTable(filtered);
    }}

    function setFilter(type, btn) {{
      currentFilter = type;
      document.querySelectorAll('.filter-pills .pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      filterJobs();
    }}

    function openDetails(jobId) {{
      const j = allJobs.find(x => x.id === jobId);
      if (!j) return;

      document.getElementById('mCompanyRole').innerText = `${{j.company}} - ${{j.title}}`;
      document.getElementById('modalBody').innerHTML = `
        <div class="modal-row">
          <div class="modal-label">الشركة والمسمى الوظيفي</div>
          <div class="modal-value">${{escapeHtml(j.company)}} | ${{escapeHtml(j.title)}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">المدينة ونمط العمل</div>
          <div class="modal-value">${{escapeHtml(j.city)}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">حالة التقديم الحالية</div>
          <div class="modal-value"><strong>${{escapeHtml(j.status)}}</strong></div>
        </div>
        <div class="modal-row">
          <div class="modal-label">الراتب المستهدف</div>
          <div class="modal-value">${{escapeHtml(j.salary)}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">ملاحظات وإثبات التقديم</div>
          <div class="modal-value">${{escapeHtml(j.notes || 'شاغر مفحوص ومطابق لمعاييرك.')}}</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">رابط التقديم المباشر</div>
          <div class="modal-value"><a href="${{j.url}}" target="_blank" style="color:#60a5fa;">${{j.url}}</a></div>
        </div>
      `;

      document.getElementById('modalOverlay').style.display = 'flex';
    }}

    function closeModal(e) {{
      document.getElementById('modalOverlay').style.display = 'none';
    }}

    function copyToClipboard() {{
      const headers = ['ID', 'التاريخ', 'اسم الشركة', 'المسمى الوظيفي', 'المنصة', 'المدينة', 'الرابط', 'التوافق', 'الحالة', 'جهة الاتصال', 'الراتب', 'السيرة الذاتية', 'المتابعة', 'الملاحظات'];
      const tsvRows = [headers.join('\\t')];

      allJobs.forEach(j => {{
        tsvRows.push([
          j.id, j.date, j.company, j.title, j.platform, j.city, j.url, j.fit, j.status, j.contact, j.salary, j.cv, j.followup, j.notes
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

