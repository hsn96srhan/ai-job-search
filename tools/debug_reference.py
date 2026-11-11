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

fill_js = """
(() => {
    const f = document.getElementById("referencesID");
    if (!f) return "not found";
    
    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) {
            el.value = val;
            el.dispatchEvent(new Event("input", {bubbles: true}));
            el.dispatchEvent(new Event("change", {bubbles: true}));
            el.dispatchEvent(new Event("blur", {bubbles: true}));
        }
    };
    
    setVal("referencesForm_refName", "Ahmed Al-Mutairi");
    setVal("referencesForm_refTitle", "Chief Executive Officer");
    setVal("referencesForm_refRelation", "FLUX Ads Agency");
    setVal("referencesForm_refEmailAddress", "management@flux-ads.com");
    setVal("referencesForm_refPhone", "506267540");
    
    const btn = document.getElementById("submitCVForm");
    if (btn) {
        btn.click();
        return "Clicked submitCVForm";
    }
    return "No btn";
})()
"""

print(run_js(fill_js))
time.sleep(2)

check_js = """
(() => {
    const f = document.getElementById("referencesID");
    if (!f) return "Form closed successfully!";
    const hints = Array.from(f.querySelectorAll(".form-hint, .error, [id*='em_']")).map(h => ({
        id: h.id, text: h.innerText.trim(), visible: h.offsetParent !== null
    })).filter(h => h.text.length > 0);
    return JSON.stringify(hints);
})()
"""
print("Check:", run_js(check_js))
