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

print("Open reference:", run_js("document.querySelector('#references a, #references button, #hob').click(); 'opened'"))
time.sleep(1.5)

js = """
(() => {
    const f = document.getElementById("referencesID");
    if (!f) return "referencesID not found";
    
    const name = document.getElementById("referencesForm_refName");
    if (name) {
        name.value = "Tamer Abdelhamid (تامر عبدالحميد)";
        name.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const email = document.getElementById("referencesForm_refEmailAddress");
    if (email) {
        email.value = "executive@raketbe.com";
        email.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const title = document.getElementById("referencesForm_refTitle");
    if (title) {
        title.value = "Managing Director";
        title.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const rel = document.getElementById("referencesForm_refRelation");
    if (rel) {
        rel.value = "RAKETBE AGENCY";
        rel.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const phone = document.getElementById("referencesForm_refPhone");
    if (phone) {
        phone.value = "506267541";
        phone.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const btn = document.getElementById("submitCVForm");
    if (btn) {
        btn.click();
        return "Clicked submitCVForm for reference 2";
    }
    return "Submit button not found";
})()
"""
print("Fill & Save:", run_js(js))

