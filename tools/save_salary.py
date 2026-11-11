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
    const f = document.getElementById("exp_salary_form");
    if (!f) return "form not found";
    
    const sal = document.getElementById("experienceForm_monthlySalary");
    if (sal) {
        sal.value = "10000";
        sal.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const curr = document.getElementById("experienceForm_monthlySalaryCurrency");
    if (curr) {
        curr.value = "92";
        curr.dispatchEvent(new Event("change", {bubbles: true}));
        const currR = document.getElementById("experienceForm_monthlySalaryCurrency__r");
        if (currR) currR.value = "SAR";
    }
    
    const btn = document.getElementById("submitCVForm");
    if (btn) {
        btn.click();
        return "Clicked submitCVForm for salary";
    }
    return "Submit button not found";
})()
"""

print(run_js(script))

