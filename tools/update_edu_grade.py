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

print("Open edu:", run_js("document.getElementById('edu-edit-96432204').click(); 'opened'"))
time.sleep(1.5)

js = """
(() => {
    const f = document.getElementById("educationID");
    if (!f) return "educationID not found";
    
    // Check grade / rating
    const rating = document.getElementById("EducationForm_rating");
    if (rating) {
        // Find 'جيد جداً' or 'جيد'
        const opt = Array.from(rating.options).find(o => o.text.includes("جيد جدا") || o.text.includes("جيد"));
        if (opt) {
            rating.value = opt.value;
            rating.dispatchEvent(new Event("change", {bubbles: true}));
            const rR = document.getElementById("EducationForm_rating__r");
            if (rR) rR.value = opt.text;
        }
    }
    
    const btn = document.getElementById("submitCVForm");
    if (btn) {
        btn.click();
        return "Clicked submitCVForm for edu grade";
    }
    return "Submit button not found";
})()
"""
print("Set grade:", run_js(js))

