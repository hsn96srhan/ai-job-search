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

js = """
(() => {
    const f = document.getElementById("educationID");
    if (!f) return "educationID not found";
    
    // Grade system: 1 (التقدير)
    const g = document.getElementById("EducationForm_grade");
    if (g) {
        g.value = "1";
        g.dispatchEvent(new Event("change", {bubbles: true}));
        const gr = document.getElementById("EducationForm_grade__r");
        if (gr) gr.value = "التقدير";
    }
    
    // Rating: 2 (جيد جداً)
    const r = document.getElementById("EducationForm_rating");
    if (r) {
        r.value = "2";
        r.dispatchEvent(new Event("change", {bubbles: true}));
        const rr = document.getElementById("EducationForm_rating__r");
        if (rr) rr.value = "جيد جداً";
    }
    
    // Month: 06 (يونيو)
    const m = document.getElementById("EducationForm_completionMonth");
    if (m) {
        m.value = "06";
        m.dispatchEvent(new Event("change", {bubbles: true}));
        const mr = document.getElementById("EducationForm_completionMonth__r");
        if (mr) mr.value = "يونيو";
    }
    
    // Year: 2018
    const y = document.getElementById("EducationForm_completionYear");
    if (y) {
        y.value = "2018";
        y.dispatchEvent(new Event("change", {bubbles: true}));
        const yr = document.getElementById("EducationForm_completionYear__r");
        if (yr) yr.value = "2018";
    }
    
    const saveBtn = document.getElementById("submitCVForm");
    if (saveBtn) {
        saveBtn.click();
        return "Clicked saveBtn for education grade";
    }
    return "saveBtn not found";
})()
"""

print(run_js(js))

