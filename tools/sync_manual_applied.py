#!/usr/bin/env python3
"""Sync manually applied jobs from the dashboard back into the tracker CSV and online dashboard.

Usage:
  python3 tools/sync_manual_applied.py SA-001 SA-004
  python3 tools/sync_manual_applied.py --list
  python3 tools/sync_manual_applied.py --server (starts local HTTP sync bridge on port 5050)
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"
BUILD_DASHBOARD_SCRIPT = REPO_ROOT / "tools" / "build_online_dashboard.py"


def mark_jobs_applied(job_ids, notes_suffix="تم التقديم يدوياً من قِبل المرشح"):
    """Update status of specified job IDs to 'تم التقديم (يدوي)' in the CSV."""
    if not TRACKER_CSV.exists():
        print(f"❌ لم يتم العثور على ملف التتبع: {TRACKER_CSV}")
        return False

    riyadh_tz = timezone(timedelta(hours=3))
    now_str = datetime.now(riyadh_tz).strftime("%Y-%m-%d %I:%M %p").replace("AM", "ص").replace("PM", "م")

    updated_count = 0
    updated_rows = []

    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        updated_rows.append(header)

        for row in reader:
            if not row:
                continue
            jid = row[0].strip()
            if jid in job_ids:
                # Column 9 is status (حالة التقديم)
                row[9] = "تم التقديم (يدوي)"
                # Column 14 is notes (ملاحظات)
                existing_notes = row[14] if len(row) > 14 else ""
                row[14] = f"{notes_suffix} بتاريخ {now_str} | {existing_notes}".strip(" | ")
                updated_count += 1
                print(f"✓ تم تحديث الشاغر {jid} ({row[2]} - {row[3]}) إلى: تم التقديم (يدوي)")
            updated_rows.append(row)

    if updated_count > 0:
        with open(TRACKER_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(updated_rows)

        print(f"\n🎉 تم بنجاح تحديث {updated_count} وظائف في ملف {TRACKER_CSV.name}!")

        # Rebuild online dashboard
        if BUILD_DASHBOARD_SCRIPT.exists():
            subprocess.run([sys.executable, str(BUILD_DASHBOARD_SCRIPT)], check=False)

        # Sync to personal portfolio repo
        hsn_repo = Path("/tmp/hsn_repo")
        if hsn_repo.exists() and (hsn_repo / ".git").exists():
            docs_html = REPO_ROOT / "docs" / "index.html"
            target_dash = hsn_repo / "dashboard.html"
            if docs_html.exists():
                import shutil
                shutil.copy(docs_html, target_dash)
                subprocess.run(["git", "add", "dashboard.html"], cwd=hsn_repo, check=False)
                subprocess.run(["git", "commit", "-m", f"Sync manual application {', '.join(job_ids)}"], cwd=hsn_repo, check=False)
                subprocess.run(["git", "push", "origin", "main"], cwd=hsn_repo, capture_output=True, check=False)

        # Commit and push main repo
        try:
            subprocess.run(["git", "add", "saudi_jobs_google_sheets_tracker.csv", "docs/index.html"], cwd=REPO_ROOT, check=False)
            subprocess.run(["git", "commit", "-m", f"Record manual job application for {', '.join(job_ids)}"], cwd=REPO_ROOT, check=False)
            subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT, capture_output=True, check=False)
            print("✓ تم رفع التحديثات الحية إلى لوحة التحكم على GitHub Pages!")
        except Exception as e:
            print(f"تنبيه مزامنة Git: {e}")

        return True
    else:
        print("ℹ️ لم يتم العثور على معرفات وظائف مطابقة للتحديث.")
        return False


class SyncHandler(BaseHTTPRequestHandler):
    """Lightweight HTTP API handler for real-time dashboard sync."""

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json; charset=utf-8")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/status":
            self.send_response(200)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "running", "time": datetime.now().isoformat()}).encode("utf-8"))
            return

        if parsed.path in ["/api/mark_applied", "/api/toggle_applied"]:
            job_id = params.get("id", [""])[0].strip()
            if not job_id:
                self.send_response(400)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing 'id' parameter"}).encode("utf-8"))
                return

            success = mark_jobs_applied([job_id])
            self.send_response(200 if success else 404)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": success,
                "job_id": job_id,
                "message": f"تم تسجيل التقديم اليدوي على الشاغر {job_id} بنجاح ومزامنة الداشبورد!" if success else "لم يتم العثور على الشاغر"
            }).encode("utf-8"))
            return

        self.send_response(404)
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        # Concise logging
        sys.stderr.write(f"[Sync Server] {args[0]} {args[1]} - {args[2]}\n")


def run_server(port=5050):
    server = HTTPServer(("127.0.0.1", port), SyncHandler)
    print(f"🚀 خادم المزامنة اللحظية المحلي يعمل الآن على: http://127.0.0.1:{port}")
    print("أي نقرة على '✅ قدمت يدوياً' في الداشبورد سيتم مزامنتها تلقائياً وفورياً مع ملف CSV وقوقل شيت!")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nتم إيقاف خادم المزامنة.")


def main():
    parser = argparse.ArgumentParser(description="Sync manual applications to tracker CSV")
    parser.add_argument("jobs", nargs="*", help="Job IDs to mark as applied (e.g. SA-001 SA-004)")
    parser.add_argument("--server", action="store_true", help="Run local HTTP sync bridge on port 5050")
    parser.add_argument("--port", type=int, default=5050, help="Port for sync server (default: 5050)")
    parser.add_argument("--notes", default="تم التقديم يدوياً من قِبل المرشح", help="Custom notes to add")
    args = parser.parse_args()

    if args.server:
        run_server(args.port)
    elif args.jobs:
        mark_jobs_applied(args.jobs, args.notes)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

