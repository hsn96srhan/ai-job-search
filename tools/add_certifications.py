#!/usr/bin/env python3
import subprocess
import base64
import time

def run_js(js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    apple_script = f'''
    tell application "Google Chrome"
        tell tab 2 of window 1
            execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))"
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    return res.stdout.strip()

def add_cert(name, inst, sm, sy, sm_ar, url=""):
    print(f"Adding cert: {name} ({inst})")
    # Click add button
    run_js("(() => { const b = document.getElementById('addNewTraining'); if (b) b.click(); })()")
    time.sleep(1.5)
    
    js = f"""
    (() => {{
        const f = document.getElementById("certificationFormID");
        if (!f) return "certificationFormID not found";
        
        const cn = document.getElementById("trainingForm_certName");
        if (cn) {{
            cn.value = "{name}";
            cn.dispatchEvent(new Event("input", {{bubbles: true}}));
            cn.dispatchEvent(new Event("change", {{bubbles: true}}));
        }}
        
        const ci = document.getElementById("trainingForm_institute");
        if (ci) {{
            ci.value = "{inst}";
            ci.dispatchEvent(new Event("input", {{bubbles: true}}));
            ci.dispatchEvent(new Event("change", {{bubbles: true}}));
        }}
        
        const m = document.getElementById("trainingForm_certStartMonth");
        if (m) {{
            m.value = "{sm}";
            m.dispatchEvent(new Event("change", {{bubbles: true}}));
            const mr = document.getElementById("trainingForm_certStartMonth__r");
            if (mr) mr.value = "{sm_ar}";
        }}
        
        const y = document.getElementById("trainingForm_certStartYear");
        if (y) {{
            y.value = "{sy}";
            y.dispatchEvent(new Event("change", {{bubbles: true}}));
            const yr = document.getElementById("trainingForm_certStartYear__r");
            if (yr) yr.value = "{sy}";
        }}
        
        const noExp = document.getElementById("trainingForm_certHasntExpiry");
        if (noExp) {{
            noExp.checked = true;
            noExp.value = "1";
            noExp.dispatchEvent(new Event("change", {{bubbles: true}}));
        }}
        
        if ("{url}") {{
            const u = document.getElementById("trainingForm_certificateUrl");
            if (u) {{
                u.value = "{url}";
                u.dispatchEvent(new Event("input", {{bubbles: true}}));
            }}
        }}
        
        const btn = document.getElementById("submitCVForm");
        if (btn) {{
            btn.click();
            return "submitted";
        }}
        return "no submit btn";
    }})()
    """
    res = run_js(js)
    print("Result:", res)
    time.sleep(2)

# 1. HRSD Accreditation
add_cert("الاعتماد المهني كمدير تسويق (Professional Marketing Manager Accreditation)", "وزارة الموارد البشرية والتنمية الاجتماعية (HRSD)", "01", "2024", "يناير", "https://hsn96srhan.github.io/hsn/")

# 2. MCIT Udacity Nanodegree
add_cert("Digital Marketing Nanodegree", "MCIT Saudi Arabia & Udacity", "06", "2023", "يونيو", "https://hsn96srhan.github.io/hsn/")

