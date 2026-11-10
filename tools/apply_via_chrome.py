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

            // 2. Intelligent Handling for Salary & Essay Questions
            const inputs = Array.from(document.querySelectorAll('input[type="text"], input[type="number"], textarea'));
            inputs.forEach(inp => {
                if (!inp.value || inp.value.trim().length === 0) {
                    const label = (inp.labels && inp.labels[0] ? inp.labels[0].innerText : inp.placeholder || inp.getAttribute('aria-label') || '').toLowerCase();
                    const proto = inp.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
                    const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;

                    function setVal(val) {
                        setter.call(inp, val);
                        inp.dispatchEvent(new Event('input', { bubbles: true }));
                        inp.dispatchEvent(new Event('change', { bubbles: true }));
                    }

                    // A. Current Salary (الراتب الحالي)
                    if (label.includes('current') && (label.includes('salary') || label.includes('compensation') || label.includes('راتب') || label.includes('حالي'))) {
                        if (label.includes('basic') || label.includes('أساسي')) {
                            setVal('8000');
                        } else {
                            setVal('10000');
                        }
                    }
                    // B. Expected Salary (الراتب المتوقع)
                    else if (label.includes('expect') || label.includes('متوقع') || label.includes('salary') || label.includes('راتب') || label.includes('compensation') || label.includes('package')) {
                        if (inp.type === 'number') {
                            if (label.includes('basic') || label.includes('أساسي')) {
                                setVal('9000');
                            } else {
                                setVal('10000');
                            }
                        } else {
                            if (label.includes('basic') || label.includes('أساسي')) {
                                setVal('9,000 - 10,000 SAR');
                            } else {
                                setVal('10,000 - 12,000 SAR');
                            }
                        }
                    }
                    // Benefits / Allowances
                    else if (label.includes('benefit') || label.includes('مزايا') || label.includes('allowance')) {
                        setVal('Cash housing allowance (3 months basic salary annually / 25%), in-kingdom sponsorship transfer via Qiwa (نقل كفالة), statutory work permit (كرت عمل), comprehensive medical insurance (CCHI), and annual flight tickets.');
                    }
                    // Sponsorship / Legal
                    else if (label.includes('sponsor') || label.includes('كفالة') || label.includes('تأشيرة') || label.includes('visa')) {
                        setVal('Transferable Iqama in Riyadh (إقامة قابلة للتحويل). Requires standard in-kingdom sponsorship transfer via Qiwa, work permit, cash housing allowance (3 months basic), and medical insurance.');
                    }
                    else if (label.includes('year') || label.includes('خبرة') || label.includes('experience')) {
                        setVal('8');
                    }
                    // D. Notice Period
                    else if (label.includes('notice') || label.includes('إشعار') || label.includes('start date') || label.includes('join')) {
                        setVal('15');
                    }
                    // E. Location / City
                    else if (label.includes('city') || label.includes('مدينة') || label.includes('location') || label.includes('reside') || label.includes('address')) {
                        setVal('Riyadh, Saudi Arabia');
                    }
                    // F. Essay: Why join / Interest
                    else if (label.includes('why') || label.includes('interest') || label.includes('excite') || label.includes('لماذا') || label.includes('اهتمام')) {
                        setVal("Passionate about scaling commercial growth and high-performance marketing in Saudi Arabia. As an HRSD-accredited Marketing Director with 8+ years of experience managing 7M+ SAR in ad budgets, delivering up to 25x ROAS, and scaling monthly revenue engines to 10M, I bring proven leadership in customer acquisition, CAC reduction, and omnichannel brand building.");
                    }
                    // G. Essay: Accomplishment / Initiative / Metric
                    else if (label.includes('achieve') || label.includes('initiative') || label.includes('success') || label.includes('metric') || label.includes('إنجاز') || label.includes('مبادرة') || label.includes('نجاح')) {
                        setVal("Built and scaled an omnichannel commercial growth engine from early-stage to 10M/month in revenue. Directed 7M+ SAR in paid media across Snapchat, Meta, TikTok, and Google Ads achieving up to 25x audited ROAS, while reducing CAC by 28% and boosting customer retention through automated CRM workflows.");
                    }
                    // H. Essay: Additional Information / Summary
                    else if (label.includes('additional') || label.includes('strengthen') || label.includes('know you') || label.includes('إضافي') || label.includes('معلومات') || label.includes('about you')) {
                        setVal("HRSD-accredited Marketing Director based in Riyadh with Transferable Iqama, valid Saudi Driving License, and immediate availability. Proven track record leading 20+ member cross-functional teams, managing multi-million SAR media budgets, and scaling GCC consumer brands aligned with Vision 2030.");
                    }
                }
            });

            // 3. Radio buttons (Yes/No)
            const fieldsets = Array.from(document.querySelectorAll('fieldset, .jobs-easy-apply-form-section__grouping'));
            fieldsets.forEach(fs => {
                const txt = fs.innerText.toLowerCase();
                const radios = Array.from(fs.querySelectorAll('input[type="radio"]'));
                const checked = radios.some(r => r.checked);
                if (!checked && radios.length >= 2) {
                    if (txt.includes('saudi national') || txt.includes('سعودي الجنسية') || txt.includes('مواطن')) {
                        const noBtn = fs.querySelector('label:has-text("No"), input[value="No"], label:has-text("لا")') || radios[1];
                        if (noBtn) noBtn.click();
                    } else {
                        // Sponsorship transfer, authorized to work, driving license, experience -> Yes
                        const yesBtn = fs.querySelector('label:has-text("Yes"), input[value="Yes"], label:has-text("نعم")') || radios[0];
                        if (yesBtn) yesBtn.click();
                    }
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
