#!/usr/bin/env python3
"""Execute job applications directly inside the user's running Google Chrome browser."""

import subprocess
import time
import sys
import re
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_CSV = REPO_ROOT / "saudi_jobs_google_sheets_tracker.csv"

def run_js(js_code):
    escaped_js = js_code.replace('\\', '\\\\').replace('"', '\\"')
    apple_script = f'''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "{escaped_js}"
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    if res.returncode != 0:
        return {"error": res.stderr.strip()}
    return {"result": res.stdout.strip()}

def set_chrome_url(url):
    apple_script = f'''
    tell application "Google Chrome"
        set URL of active tab of front window to "{url}"
    end tell
    '''
    subprocess.run(["osascript", "-e", apple_script], check=True)

def check_permission():
    res = run_js("document.title")
    if "error" in res:
        return False, res["error"]
    return True, res["result"]

def update_tracker(job_url, new_status="تم التقديم"):
    if not TRACKER_CSV.exists():
        return
    with open(TRACKER_CSV, "r", encoding="utf-8") as f:
        content = f.read()
    clean_u = re.sub(r'\?.*$', '', job_url).rstrip('/')
    lines = content.split("\n")
    updated = []
    for line in lines:
        if clean_u in line and "جاهز للتقديم" in line:
            line = line.replace("جاهز للتقديم", new_status)
            print(f"✓ تم تحديث حالة الشاغر في الشيت إلى: {new_status}")
        updated.append(line)
    with open(TRACKER_CSV, "w", encoding="utf-8") as f:
        f.write("\n".join(updated))

def apply_current_tab():
    """Automate the Easy Apply process on the currently opened tab."""
    print("⚡ محاولة النقر على زر التقديم السريع (Easy Apply)...")

    click_easy_apply_js = """
    (function() {
        const btns = Array.from(document.querySelectorAll('button'));
        const target = btns.find(b => {
            const txt = b.innerText.trim().toLowerCase();
            return txt.includes('easy apply') || txt.includes('التقديم السريع') || txt.includes('التقديم بسهولة');
        });
        if (target) {
            target.click();
            return 'CLICKED_EASY_APPLY';
        }
        return 'BUTTON_NOT_FOUND';
    })()
    """
    res = run_js(click_easy_apply_js)
    if res.get("result") != "CLICKED_EASY_APPLY":
        print(f"لم يتم العثور على زر Easy Apply أو قد يكون تم التقديم مسبقاً ({res})")
        return False

    time.sleep(2)

    # Step through modal up to 8 steps
    for step in range(1, 9):
        print(f"-> معالجة الخطوة {step} من استمارة التقديم...")

        fill_step_js = """
        (function() {
            // 1. Fill Phone if empty
            const phone = document.querySelector('input[id*="phoneNumber"], input[id*="phone-number"], input[name*="phone"]');
            if (phone && (!phone.value || phone.value.length < 5)) {
                phone.value = "0506267542";
                phone.dispatchEvent(new Event('input', { bubbles: true }));
                phone.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // 2. Fill numeric & text questions
            const inputs = Array.from(document.querySelectorAll('input[type="text"], input[type="number"], textarea'));
            inputs.forEach(inp => {
                if (!inp.value) {
                    const label = (inp.labels && inp.labels[0] ? inp.labels[0].innerText : inp.placeholder || '').toLowerCase();
                    if (label.includes('year') || label.includes('خبرة') || label.includes('experience')) {
                        inp.value = '8';
                    } else if (label.includes('salary') || label.includes('راتب') || label.includes('compensation')) {
                        inp.value = '10000';
                    } else if (label.includes('notice') || label.includes('إشعار')) {
                        inp.value = '15';
                    } else if (label.includes('city') || label.includes('مدينة')) {
                        inp.value = 'Riyadh, Saudi Arabia';
                    }
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });

            // 3. Radio buttons (Yes/No)
            const fieldsets = Array.from(document.querySelectorAll('fieldset, .jobs-easy-apply-form-section__grouping'));
            fieldsets.forEach(fs => {
                const txt = fs.innerText.toLowerCase();
                if (txt.includes('sponsorship now or in the future') || txt.includes('require sponsorship')) {
                    const noBtn = fs.querySelector('label:has-text("No"), input[value="No"], label:has-text("لا")') || fs.querySelectorAll('input[type="radio"]')[1];
                    if (noBtn) noBtn.click();
                } else if (txt.includes('authorized') || txt.includes('license') || txt.includes('iqama') || txt.includes('reside') || txt.includes('موافق')) {
                    const yesBtn = fs.querySelector('label:has-text("Yes"), input[value="Yes"], label:has-text("نعم")') || fs.querySelectorAll('input[type="radio"]')[0];
                    if (yesBtn) yesBtn.click();
                }
            });

            // Strict User Rule: Uncheck any "Follow Company" checkbox before review or submission
            const allCheckboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
            allCheckboxes.forEach(cb => {
                const label = (cb.labels && cb.labels[0] ? cb.labels[0].innerText : '').toLowerCase();
                const parent = (cb.parentElement ? cb.parentElement.innerText : '').toLowerCase();
                const desc = `${label} ${parent} ${cb.id} ${cb.name}`.toLowerCase();
                if (desc.includes('follow') || desc.includes('متابعة') || desc.includes('stay up to date')) {
                    if (cb.checked) {
                        cb.click();
                    }
                }
            });

            // 4. Check for Submit button
            const btns = Array.from(document.querySelectorAll('button'));
            const submitBtn = btns.find(b => {
                const t = b.innerText.trim().toLowerCase();
                return t.includes('submit application') || t.includes('إرسال الطلب');
            });
            if (submitBtn) {
                submitBtn.click();
                return 'SUBMITTED';
            }

            // 5. Check for Review button
            const reviewBtn = btns.find(b => {
                const t = b.innerText.trim().toLowerCase();
                return t.includes('review') || t.includes('مراجعة');
            });
            if (reviewBtn) {
                reviewBtn.click();
                return 'REVIEW_CLICKED';
            }

            // 6. Check for Next button
            const nextBtn = btns.find(b => {
                const t = b.innerText.trim().toLowerCase();
                return t.includes('next') || t.includes('التالي');
            });
            if (nextBtn) {
                nextBtn.click();
                return 'NEXT_CLICKED';
            }

            // 7. Check for Done button
            const doneBtn = btns.find(b => {
                const t = b.innerText.trim().toLowerCase();
                return t === 'done' || t === 'تم';
            });
            if (doneBtn) {
                doneBtn.click();
                return 'DONE_CLICKED';
            }

            return 'NO_ACTION_FOUND';
        })()
        """
        step_res = run_js(fill_step_js)
        status = step_res.get("result", "")
        print(f"   النتيجة: {status}")

        if status in ["SUBMITTED", "DONE_CLICKED"]:
            print("🎉🎉 تم إرسال الطلب بنجاح بنسبة 100%!")
            time.sleep(3)
            # Dismiss done dialog
            run_js("document.querySelector('button[aria-label=\"Dismiss\"], button:has-text(\"Done\"), button:has-text(\"تم\")')?.click()")
            return True

        time.sleep(2)

    return False

def main():
    ok, msg = check_permission()
    if not ok:
        print("❌ تنبيه: خيار AppleScript غير مفعل بعد في متصفح كروم.")
        print(msg)
        sys.exit(1)

    print("🚀 بدء التقديم الآلي عبر متصفح كروم المفتوح...")
    apply_current_tab()

if __name__ == "__main__":
    main()
