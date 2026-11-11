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

# 1. Click edit for Arabiva
print("Open:", run_js("document.getElementById('exp-128584673').click(); 'opened'"))
time.sleep(1)

# 2. Update Arabiva fields
update_js = """
(() => {
    const f = document.getElementById("exp_form");
    if (!f) return "exp_form not found";
    
    // Title
    const title = document.getElementById("experienceForm_jobTitle");
    if (title) {
        title.value = "Marketing Director";
        title.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Company
    const comp = document.getElementById("experienceForm_company");
    if (comp) {
        comp.value = "Arabeva Group";
        comp.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Uncheck currentlyWorkHere
    const curr = document.getElementById("experienceForm_currentlyWorkHere");
    if (curr) curr.checked = false;
    
    // Start Date: 03 / 2025
    const sm = document.getElementById("experienceForm_startMonth");
    if (sm) {
        sm.value = "03";
        sm.dispatchEvent(new Event("change", {bubbles: true}));
        const smr = document.getElementById("experienceForm_startMonth__r");
        if (smr) smr.value = "مارس";
    }
    const sy = document.getElementById("experienceForm_startYear");
    if (sy) {
        sy.value = "2025";
        sy.dispatchEvent(new Event("change", {bubbles: true}));
        const syr = document.getElementById("experienceForm_startYear__r");
        if (syr) syr.value = "2025";
    }
    
    // End Date: 08 / 2025
    const em = document.getElementById("experienceForm_endMonth");
    if (em) {
        em.value = "08";
        em.dispatchEvent(new Event("change", {bubbles: true}));
        const emr = document.getElementById("experienceForm_endMonth__r");
        if (emr) emr.value = "أغسطس";
    }
    const ey = document.getElementById("experienceForm_endYear");
    if (ey) {
        ey.value = "2025";
        ey.dispatchEvent(new Event("change", {bubbles: true}));
        const eyr = document.getElementById("experienceForm_endYear__r");
        if (eyr) eyr.value = "2025";
    }
    
    // WorkMode
    const wm = document.getElementById("experienceForm_workMode_0");
    if (wm) { wm.click(); wm.checked = true; }
    
    // Company size
    const cs = document.getElementById("experienceForm_companySize");
    if (cs && !cs.value) {
        cs.value = "2";
        cs.dispatchEvent(new Event("change", {bubbles: true}));
    }
    
    return "fields set";
})()
"""
print("Set fields:", run_js(update_js))
time.sleep(1)

# 3. Save
save_js = """
(() => {
    const btn = document.getElementById("submitCVForm");
    if (btn) { btn.click(); return "clicked save"; }
    return "no save btn";
})()
"""
print("Save:", run_js(save_js))

