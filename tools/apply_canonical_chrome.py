#!/usr/bin/env python3
"""Submit Canonical application on Greenhouse directly inside Google Chrome."""

import subprocess
import time
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CV_TEXT_FILE = REPO_ROOT / "cv/master_cv_text.txt"

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
    return res.stdout.strip(), res.stderr.strip()

def main():
    with open(CV_TEXT_FILE, "r", encoding="utf-8") as f:
        cv_text = f.read()

    js_cv_text = json.dumps(cv_text)

    fill_script = f'''
    (function() {{
        function setVal(selector, val) {{
            var el = typeof selector === 'string' ? document.querySelector(selector) : selector;
            if (!el) return false;
            var proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
            var setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }}

        // 1. Enter resume manually if not already open
        var ta = document.getElementById('resume_text');
        if (!ta) {{
            var btns = Array.from(document.querySelectorAll('button'));
            var em = btns.find(b => b.innerText.trim() === 'Enter manually');
            if (em) em.click();
        }}
        ta = document.getElementById('resume_text');
        if (ta) {{
            setVal(ta, {js_cv_text});
        }}

        // 2. Personal info
        setVal('#first_name', 'Hassan');
        setVal('#last_name', 'Sarhan');
        setVal('#email', 'hsn96srhan@gmail.com');
        setVal('#phone', '+966506267542');

        // 3. Education text inputs
        setVal('#school--0', 'Akhbar El Yom Academy');
        setVal('#degree--0', 'Bachelor of Journalism');
        setVal('#discipline--0', 'Journalism & Media Communications');

        // 4. Custom essay questions
        setVal('#question_63345521', 'Directed omnichannel commercial growth roadmaps for enterprise clients and D2C brands, managing over 7M SAR in paid media across Snapchat, Meta, TikTok, and Google Ads achieving up to 25x ROAS and scaling revenue to 10M/month.');
        setVal('#question_63345522', 'Customer Acquisition Cost (CAC), Return on Ad Spend (ROAS), Customer Lifetime Value (LTV), Full-Funnel Conversion Rates, Activation & Retention Cohorts, and Pipeline Velocity.');
        setVal('#question_63345523', 'An enterprise B2B logistics ERP platform and digital healthcare SaaS, mapping technical API integrations, developer documentation marketing, and automated onboarding funnels.');
        setVal('#question_63345524', 'Bachelor of Journalism (Akhbar El Yom Academy, Cairo), Very Good (equivalent to GPA 3.2 out of 4.0).');
        setVal('#question_63345533', 'Graduated from the standardized Egyptian National General Secondary Certificate (Thanaweya Amma) with top-tier scores in mathematics, analytical logic, and Arabic language, placing in the top percentiles nationwide.');

        // 5. URLs & Text questions
        setVal('#question_63345529', 'https://hsn96srhan.github.io/hsn/');
        setVal('#question_63345530', 'https://www.linkedin.com/in/srhan-jr/');
        setVal('#question_63345535', '4');

        // 6. React Select Dropdowns
        // Select React Select by clicking and typing or choosing option
        function setReactSelect(containerSelector, optionText) {{
            var container = document.querySelector(containerSelector);
            if (!container) return;
            var input = container.querySelector('input');
            if (input) {{
                input.focus();
                input.value = optionText;
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                // Find matching option in menu
                setTimeout(() => {{
                    var menu = document.querySelector('[class*=\"-menu\"], [role=\"listbox\"]');
                    if (menu) {{
                        var opt = Array.from(menu.querySelectorAll('[class*=\"-option\"], [role=\"option\"]')).find(o => o.innerText.toLowerCase().includes(optionText.toLowerCase()));
                        if (opt) opt.click();
                    }}
                }}, 300);
            }}
        }}

        return {{
            hasResumeText: !!ta,
            firstName: document.getElementById('first_name')?.value,
            lastName: document.getElementById('last_name')?.value,
            email: document.getElementById('email')?.value
        }};
    }})()
    '''
    out, err = run_js(fill_script)
    print("Fill result:", out)
    if err: print("Error:", err)

if __name__ == "__main__":
    main()
