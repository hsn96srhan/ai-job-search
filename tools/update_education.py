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

script = """
(() => {
    const f = document.getElementById("educationID");
    if (!f) return "educationID not found";
    
    // Major
    const m = document.getElementById("EducationForm_major");
    if (m) {
        m.value = "Journalism & Mass Communication (إعلام قسم صحافة)";
        m.dispatchEvent(new Event("input", {bubbles: true}));
        m.dispatchEvent(new Event("change", {bubbles: true}));
    }
    
    // City
    const c = document.getElementById("EducationForm_educationCityText");
    if (c) {
        c.value = "القاهرة";
        c.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Description
    const d = document.getElementById("EducationForm_description");
    if (d) {
        d.value = "بكالوريوس إعلام قسم صحافة - أكاديمية أخبار اليوم (2014 - 2018). دراسة متقدمة في الإعلام والاتصال الجماهيري، صناعة المحتوى الإبداعي، وإدارة الحملات الإعلامية والتسويقية.";
        d.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const saveBtn = document.getElementById("submitCVForm");
    if (saveBtn) {
        saveBtn.click();
        return "Clicked saveBtn for education";
    }
    return "saveBtn not found";
})()
"""

print(run_js(script))

