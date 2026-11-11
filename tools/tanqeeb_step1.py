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
    // Full Name
    const name = document.getElementById("UserFullName");
    if (name) {
        name.value = "حسن سرحان";
        name.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Job Title
    const title = document.getElementById("UserJobTitle");
    if (title) {
        title.value = "مدير تسويق (Marketing Director)";
        title.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Birth date: 1996-04-22
    const bd = document.getElementById("UserBirthDate");
    if (bd) {
        bd.value = "1996-04-22";
        bd.dispatchEvent(new Event("input", {bubbles: true}));
        bd.dispatchEvent(new Event("change", {bubbles: true}));
    }
    
    // Experience years: 8
    const exp = document.getElementById("UserExperienceYears");
    if (exp) {
        exp.value = "8";
        exp.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Male
    const m = document.getElementById("gender_only_male");
    if (m) {
        m.click();
        m.checked = true;
    }
    
    // Nationality: 213 (مصر)
    const nat = document.getElementById("UserNationalityId");
    if (nat) {
        nat.value = "213";
        nat.dispatchEvent(new Event("change", {bubbles: true}));
    }
    
    // City: الرياض
    const city = document.getElementById("UserCity");
    if (city) {
        city.value = "الرياض";
        city.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Min salary: 10000
    const sal = document.getElementById("UserMinSalary");
    if (sal) {
        sal.value = "10000";
        sal.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Currency: SAR
    const cur = document.getElementById("UserCurrencyCode");
    if (cur) {
        cur.value = "SAR";
        cur.dispatchEvent(new Event("change", {bubbles: true}));
    }
    
    // Next step button
    const btns = Array.from(document.querySelectorAll("button, input[type=submit]"));
    const nextBtn = btns.find(b => (b.innerText || b.value || "").includes("الخطوة التالية"));
    if (nextBtn) {
        nextBtn.click();
        return "Clicked nextBtn";
    }
    return "Next button not found";
})()
"""

print(run_js_tab(8, script))

