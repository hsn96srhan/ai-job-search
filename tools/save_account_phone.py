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
    const f = document.getElementById("contactMobileFormID");
    if (!f) return "form not found";
    
    const inp = document.getElementById("contactMobileForm_cellPhone");
    if (!inp) return "inp not found";
    
    inp.focus();
    inp.value = "506267542";
    inp.dispatchEvent(new Event("focus", {bubbles: true}));
    inp.dispatchEvent(new Event("input", {bubbles: true}));
    inp.dispatchEvent(new Event("change", {bubbles: true}));
    inp.dispatchEvent(new Event("blur", {bubbles: true}));
    
    // Find 'حفظ' button
    let p = f.parentElement;
    let saveBtn = null;
    while (p && p !== document.body) {
        saveBtn = Array.from(p.querySelectorAll("button, a.btn")).find(b => b.innerText.trim() === "حفظ");
        if (saveBtn) break;
        p = p.parentElement;
    }
    
    if (saveBtn) {
        saveBtn.click();
        return "Clicked save button";
    }
    return "Save button not found";
})()
"""

print(run_js(script))
time.sleep(2)

check_js = """
(() => {
    const f = document.getElementById("contactMobileFormID");
    if (!f) return "Form closed!";
    const err = f.querySelector(".form-hint, .error, [id*='em_']");
    return "Form still open. Err: " + (err ? err.innerText : "none");
})()
"""
print(run_js(check_js))

