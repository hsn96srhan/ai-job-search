#!/usr/bin/env python3
"""Autonomous LinkedIn Easy Apply engine executing directly inside authenticated Google Chrome."""

import subprocess
import time
import sys
import os
import json
import csv
import re
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

def nav_tab(url):
    apple_script = f'''
    tell application "Google Chrome"
        set URL of active tab of front window to "{url}"
    end tell
    '''
    subprocess.run(["osascript", "-e", apple_script], check=True)

def update_tracker_status(job_id, new_status="تم التقديم", note=None):
    if not TRACKER_CSV.exists():
        return
    with open(TRACKER_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    found = False
    for r in rows:
        if r['ID'] == job_id:
            r['حالة التقديم (Status)'] = new_status
            if note:
                r['ملاحظات وتأكيد التقديم (Notes)'] = note
            found = True
            break

    if found:
        with open(TRACKER_CSV, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✓ تم تحديث حالة الشاغر {job_id} في الشيت إلى: {new_status}")

def unfollow_network_companies():
    """Navigate to LinkedIn followed companies and unfollow to maintain zero-follow rule."""
    print("🔒 تنفيذ فحص عدم متابعة الشركات (LinkedIn Zero-Follow Rule)...")
    nav_tab("https://www.linkedin.com/mynetwork/network-manager/company/")
    time.sleep(3.5)
    
    unfollow_js = """
    (function() {
        var btns = Array.from(document.querySelectorAll('button'));
        var followingBtns = btns.filter(b => {
            var t = b.innerText.trim().toLowerCase();
            return t === 'following' || t === 'متابع';
        });
        if (followingBtns.length > 0) {
            followingBtns[0].click();
            return 'CLICKED_UNFOLLOW';
        }
        return 'NO_FOLLOWING';
    })()
    """
    res = run_js(unfollow_js).get("result", "")
    if res == "CLICKED_UNFOLLOW":
        time.sleep(1.5)
        confirm_js = """
        (function() {
            var modalBtns = Array.from(document.querySelectorAll('.artdeco-modal button, [role="dialog"] button'));
            var unfollowBtn = modalBtns.find(b => b.innerText.trim().toLowerCase() === 'unfollow' || b.innerText.trim() === 'إلغاء المتابعة');
            if (unfollowBtn) {
                unfollowBtn.click();
                return 'CONFIRMED_UNFOLLOW';
            }
            return 'NO_CONFIRM_MODAL';
        })()
        """
        run_js(confirm_js)
        print("✓ تم إلغاء متابعة الشركة بنجاح للحفاظ على خصوصية الحساب.")
    else:
        print("✓ تم التحقق: لا توجد شركات تمت متابعتها.")

def apply_job(job_id, job_url):
    print(f"\n==========================================")
    print(f"🚀 بدء معالجة الوظيفة {job_id}: {job_url}")
    print(f"==========================================")

    nav_tab(job_url)
    time.sleep(4)

    # 1. Check if already applied
    check_applied_js = """
    (function() {
        var text = document.body.innerText;
        var applied = text.includes('Application submitted') || text.includes('Applied') || text.includes('تم إرسال الطلب') || text.includes('تم التقديم');
        return applied ? 'ALREADY_APPLIED' : 'NOT_APPLIED';
    })()
    """
    applied_res = run_js(check_applied_js).get("result", "")
    if applied_res == "ALREADY_APPLIED":
        print(f"✓ الشاغر {job_id} تم التقديم عليه مسبقاً في لينكد إن.")
        update_tracker_status(job_id, "تم التقديم", "تم تأكيد التقديم مسبقاً عبر لينكد إن")
        return True

    # 2. Click Easy Apply
    click_easy_apply_js = """
    (function() {
        var btns = Array.from(document.querySelectorAll('button, a'));
        var target = btns.find(b => {
            var txt = b.innerText.trim().toLowerCase();
            return txt.includes('easy apply') || txt.includes('التقديم السريع') || txt.includes('التقديم بسهولة');
        });
        if (target) {
            target.click();
            return 'CLICKED_EASY_APPLY';
        }
        return 'EASY_APPLY_NOT_FOUND';
    })()
    """
    click_res = run_js(click_easy_apply_js).get("result", "")
    if click_res != "CLICKED_EASY_APPLY":
        print(f"⚠️ لم يتم العثور على زر Easy Apply للوظيفة {job_id} ({click_res})")
        return False

    print("✓ تم النقر على زر التقديم السريع (Easy Apply).")
    time.sleep(2.5)

    # 3. Form filler script for each step
    fill_step_js = """
    (function() {
        var d = document.querySelector('dialog') || document.querySelector('.jobs-easy-apply-modal') || document.querySelector('[role=\"dialog\"]');
        if (!d) return 'NO_MODAL';

        // Helper to set React controlled input
        function setReactVal(elem, val) {
            var proto = elem.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
            var setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
            setter.call(elem, val);
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // Phone input
        var phone = d.querySelector('input[id*=\"phoneNumber\"], input[id*=\"phone-number\"], input[name*=\"phone\"]');
        if (phone && (!phone.value || phone.value.trim().length < 5)) {
            setReactVal(phone, '0506267542');
        }

        // Text / Number inputs and textareas
        var inputs = Array.from(d.querySelectorAll('input[type=\"text\"], input[type=\"number\"], textarea'));
        inputs.forEach(inp => {
            var val = (inp.value || '').trim();
            if (val.length === 0) {
                var labelElem = inp.labels && inp.labels[0] ? inp.labels[0] : null;
                var label = (labelElem ? labelElem.innerText : inp.placeholder || inp.getAttribute('aria-label') || '').toLowerCase();
                var parentText = (inp.parentElement && inp.parentElement.parentElement ? inp.parentElement.parentElement.innerText : '').toLowerCase();
                var combined = label + ' ' + parentText;

                // Current Salary
                if (combined.includes('current') && (combined.includes('salary') || combined.includes('compensation') || combined.includes('package') || combined.includes('راتب') || combined.includes('حالي'))) {
                    if (combined.includes('usd') || combined.includes('dollar')) {
                        setReactVal(inp, (inp.type === 'number' || combined.includes('number') || combined.includes('numeric')) ? '2400' : '2,400 USD');
                    } else if (inp.type === 'number' || combined.includes('number') || combined.includes('أرقام') || combined.includes('digits') || combined.includes('numeric')) {
                        setReactVal(inp, combined.includes('basic') || combined.includes('أساسي') ? '8000' : '10000');
                    } else {
                        setReactVal(inp, combined.includes('basic') || combined.includes('أساسي') ? '8,000 SAR' : '10,000 SAR (8,000 Basic + 2,000 Housing)');
                    }
                }
                // Expected Salary
                else if (combined.includes('expect') || combined.includes('متوقع') || combined.includes('desired salary') || combined.includes('target salary') || combined.includes('salary')) {
                    if (combined.includes('usd') || combined.includes('dollar')) {
                        setReactVal(inp, (inp.type === 'number' || combined.includes('number') || combined.includes('numeric')) ? '3000' : '2,800 - 3,200 USD');
                    } else if (inp.type === 'number' || combined.includes('number') || combined.includes('أرقام') || combined.includes('digits') || combined.includes('numeric')) {
                        setReactVal(inp, combined.includes('basic') || combined.includes('أساسي') ? '9000' : '11000');
                    } else {
                        setReactVal(inp, combined.includes('basic') || combined.includes('أساسي') ? '9,000 - 10,000 SAR' : '10,000 - 12,000 SAR');
                    }
                }
                // References
                else if (combined.includes('reference') || combined.includes('تزكية') || combined.includes('معرفين')) {
                    setReactVal(inp, 'Available upon formal request / interview stage (Senior Executive References in Riyadh).');
                }
                // Benefits / Compensation details
                else if (combined.includes('benefit') || combined.includes('مزايا') || combined.includes('allowance')) {
                    setReactVal(inp, 'Cash housing allowance (3 months basic salary annually / 25%), in-kingdom sponsorship transfer via Qiwa (نقل كفالة), statutory work permit (كرت عمل), comprehensive medical insurance (CCHI), and annual flight tickets.');
                }
                // Sponsorship / Work Authorization Details
                else if (combined.includes('sponsor') || combined.includes('كفالة') || combined.includes('تأشيرة') || combined.includes('visa')) {
                    setReactVal(inp, 'Transferable Iqama in Riyadh (إقامة قابلة للتحويل). Requires standard in-kingdom sponsorship transfer via Qiwa, work permit, cash housing allowance (3 months basic), and medical insurance.');
                }
                // Experience / Years
                else if (combined.includes('year') || combined.includes('خبرة') || combined.includes('experience')) {
                    setReactVal(inp, '8');
                }
                // Notice Period
                else if (combined.includes('notice') || combined.includes('إشعار') || combined.includes('start date') || combined.includes('join') || combined.includes('availability')) {
                    setReactVal(inp, '15');
                }
                // City / Location
                else if (combined.includes('city') || combined.includes('مدينة') || combined.includes('location') || combined.includes('reside') || combined.includes('address')) {
                    setReactVal(inp, 'Riyadh, Saudi Arabia');
                }
                // Essay: Why join / Interest
                else if (combined.includes('why') || combined.includes('interest') || combined.includes('excite') || combined.includes('لماذا') || combined.includes('اهتمام')) {
                    setReactVal(inp, 'Passionate about scaling commercial growth and high-performance marketing in Saudi Arabia. As an HRSD-accredited Marketing Director with 8+ years of experience managing 7M+ SAR in ad budgets, delivering up to 25x ROAS, and scaling monthly revenue engines to 10M, I bring proven leadership in customer acquisition, CAC reduction, and omnichannel brand building.');
                }
                // Essay: Accomplishments / Success / Metrics
                else if (combined.includes('achieve') || combined.includes('initiative') || combined.includes('success') || combined.includes('metric') || combined.includes('إنجاز') || combined.includes('مبادرة') || combined.includes('نجاح')) {
                    setReactVal(inp, 'Built and scaled an omnichannel commercial growth engine from early-stage to 10M/month in revenue. Directed 7M+ SAR in paid media across Snapchat, Meta, TikTok, and Google Ads achieving up to 25x audited ROAS, while reducing CAC by 28% and boosting customer retention through automated CRM workflows.');
                }
                // Essay: Additional Info / About you
                else if (combined.includes('additional') || combined.includes('strengthen') || combined.includes('about you') || combined.includes('إضافي') || combined.includes('معلومات')) {
                    setReactVal(inp, 'HRSD-accredited Marketing Director based in Riyadh with Transferable Iqama, valid Saudi Driving License, and immediate availability. Proven track record leading 20+ member cross-functional teams, managing multi-million SAR media budgets, and scaling GCC consumer brands aligned with Vision 2030.');
                }
                // Generic numeric fallback if required
                else if (inp.type === 'number') {
                    setReactVal(inp, '8');
                }
            }
        });

        // Dropdowns (<select>)
        var selects = Array.from(d.querySelectorAll('select'));
        selects.forEach(sel => {
            if (!sel.value || sel.value === '' || sel.selectedIndex <= 0) {
                var txt = (sel.parentElement ? sel.parentElement.innerText : '').toLowerCase();
                var opts = Array.from(sel.options);
                var match = null;
                if (txt.includes('notice') || txt.includes('إشعار')) {
                    match = opts.find(o => o.text.includes('15') || o.text.toLowerCase().includes('immediate') || o.text.includes('1 month') || o.text.includes('30'));
                } else if (txt.includes('experience') || txt.includes('خبرة')) {
                    match = opts.find(o => o.text.includes('8') || o.text.includes('5+') || o.text.toLowerCase().includes('expert') || o.text.toLowerCase().includes('senior'));
                } else if (txt.includes('english') || txt.includes('arabic') || txt.includes('language')) {
                    match = opts.find(o => o.text.toLowerCase().includes('fluent') || o.text.toLowerCase().includes('native') || o.text.toLowerCase().includes('professional'));
                } else if (txt.includes('sponsor') || txt.includes('كفالة') || txt.includes('تأشيرة')) {
                    // Candidate requires local sponsorship transfer via Qiwa -> Answer Yes
                    match = opts.find(o => o.text.toLowerCase() === 'yes' || o.text === 'نعم');
                } else {
                    match = opts.find(o => o.text.toLowerCase() === 'yes' || o.text === 'نعم');
                }
                if (match) {
                    sel.value = match.value;
                    sel.dispatchEvent(new Event('change', { bubbles: true }));
                } else if (opts.length > 1) {
                    sel.selectedIndex = 1;
                    sel.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        });

        // Radio buttons
        var fieldsets = Array.from(d.querySelectorAll('fieldset, .jobs-easy-apply-form-section__grouping'));
        fieldsets.forEach(fs => {
            var txt = fs.innerText.toLowerCase();
            var radios = Array.from(fs.querySelectorAll('input[type=\"radio\"]'));
            var checked = radios.some(r => r.checked);
            if (!checked && radios.length >= 2) {
                // If asked about Saudi nationality specifically, answer No (candidate is Egyptian resident)
                if (txt.includes('saudi national') || txt.includes('سعودي الجنسية') || txt.includes('مواطن')) {
                    var noR = radios.find(r => (r.value || '').toLowerCase() === 'no' || (r.labels && r.labels[0] && r.labels[0].innerText.includes('No'))) || radios[1];
                    noR.click();
                } else {
                    // For sponsorship transfer, authorized to work, driving license, experience -> Yes
                    var yesR = radios.find(r => (r.value || '').toLowerCase() === 'yes' || (r.labels && r.labels[0] && r.labels[0].innerText.includes('Yes'))) || radios[0];
                    yesR.click();
                }
            }
        });

        // Check for Submit application button
        var btns = Array.from(d.querySelectorAll('button'));
        var submitBtn = btns.find(b => {
            var t = b.innerText.trim().toLowerCase();
            return t.includes('submit application') || t.includes('إرسال الطلب');
        });
        if (submitBtn) {
            // STRICT MANDATE: Uncheck ANY "Follow Company" checkbox exactly ONCE right before submit
            var liveCheckboxes = Array.from(d.querySelectorAll('input[type="checkbox"]'));
            liveCheckboxes.forEach(cb => {
                var label = (cb.labels && cb.labels[0] ? cb.labels[0].innerText : '');
                var pText = (cb.parentElement ? cb.parentElement.innerText : '');
                var desc = (label + ' ' + pText + ' ' + cb.id + ' ' + cb.name).toLowerCase();
                if (desc.includes('follow') || desc.includes('متابعة') || desc.includes('stay up to date')) {
                    if (cb.checked) {
                        // Click label or wrapper to trigger React synthetic event
                        if (cb.labels && cb.labels[0]) {
                            cb.labels[0].click();
                        } else if (cb.parentElement) {
                            cb.parentElement.click();
                        } else {
                            cb.click();
                        }
                    }
                }
            });
            submitBtn.click();
            return 'SUBMITTED';
        }

        // Check for Review button
        var reviewBtn = btns.find(b => {
            var t = b.innerText.trim().toLowerCase();
            return t.includes('review') || t.includes('مراجعة');
        });
        if (reviewBtn) {
            reviewBtn.click();
            return 'REVIEW_CLICKED';
        }

        // Check for Next button
        var nextBtn = btns.find(b => {
            var t = b.innerText.trim().toLowerCase();
            return t.includes('next') || t.includes('التالي');
        });
        if (nextBtn) {
            nextBtn.click();
            return 'NEXT_CLICKED';
        }

        return 'NO_ACTION_MATCH';
    })()
    """

    # Loop up to 10 steps to fill and submit
    submitted = False
    for step in range(1, 11):
        print(f"   -> معالجة المرحلة {step} من استمارة التقديم...")
        res = run_js(fill_step_js).get("result", "")
        print(f"      الإجراء: {res}")

        if res == "SUBMITTED":
            submitted = True
            print(f"🎉 تم إرسال استمارة الوظيفة {job_id} بنجاح!")
            time.sleep(3)
            # Dismiss done modal
            dismiss_js = """
            (function() {
                var d = document.querySelector('dialog') || document.querySelector('.jobs-easy-apply-modal') || document.body;
                var btns = Array.from(d.querySelectorAll('button'));
                var doneBtn = btns.find(b => {
                    var t = b.innerText.trim().toLowerCase();
                    return t === 'done' || t === 'تم' || b.getAttribute('aria-label') === 'Dismiss';
                });
                if (doneBtn) doneBtn.click();
            })()
            """
            run_js(dismiss_js)
            time.sleep(2)
            update_tracker_status(job_id, "تم التقديم", "تم التقديم آلياً بنجاح عبر لينكد إن Easy Apply (مع إلغاء متابعة الشركة)")
            unfollow_network_companies()
            break
        elif res in ["NEXT_CLICKED", "REVIEW_CLICKED"]:
            time.sleep(2)
        elif res == "NO_ACTION_MATCH":
            time.sleep(1.5)
        else:
            time.sleep(1.5)

    return submitted

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_id = sys.argv[1]
        target_url = sys.argv[2] if len(sys.argv) > 2 else ""
        apply_job(target_id, target_url)
    else:
        print("Usage: python3 tools/autonomous_easy_apply.py <JOB_ID> <JOB_URL>")
