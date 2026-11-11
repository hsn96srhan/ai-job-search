#!/usr/bin/env python3
import subprocess
import base64
import time

def run_js_tab(tab_idx, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    apple_script = f'''
    tell application "Google Chrome"
        tell tab {tab_idx} of window 1
            execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))"
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    return res.stdout.strip()

script = """
(() => {
    const name = document.getElementById("UserFullName");
    if (name) {
        name.value = "حسن سرحان";
        name.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const email = document.getElementById("UserEmail");
    if (email) {
        email.value = "hsn96srhan@gmail.com";
        email.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const cc = document.getElementById("countryCodeUserMobile");
    if (cc) {
        cc.value = "sa";
        cc.dispatchEvent(new Event("change", {bubbles: true}));
    }
    
    const mob = document.getElementById("UserMobile");
    if (mob) {
        mob.value = "506267542";
        mob.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const title = document.getElementById("UserJobTitle");
    if (title) {
        title.value = "مدير تسويق";
        title.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const pass = document.getElementById("UserPassword");
    if (pass) {
        pass.value = "Hassan@Career2026!";
        pass.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const btns = Array.from(document.querySelectorAll("button, input[type=submit]"));
    const sub = btns.find(b => (b.innerText || b.value || "").includes("قم بالتسجيل والمتابعة"));
    if (sub) {
        sub.click();
        return "Clicked register with clean name";
    }
    return "Submit btn not found";
})()
"""

print(run_js_tab(8, script))
