#!/usr/bin/env python3
import subprocess
import base64

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
    const f = document.getElementById("exp_form");
    if (!f) return "exp_form not found";
    
    const log = [];
    
    // Title
    const title = document.getElementById("experienceForm_jobTitle");
    if (title) {
        title.value = "Digital Marketing & Performance Manager";
        title.dispatchEvent(new Event("input", {bubbles: true}));
        title.dispatchEvent(new Event("change", {bubbles: true}));
        log.push("set title");
    }
    
    // Uncheck currentlyWorkHere
    const curr = document.getElementById("experienceForm_currentlyWorkHere");
    if (curr) {
        curr.checked = false;
        curr.value = "0";
        curr.dispatchEvent(new Event("change", {bubbles: true}));
        log.push("uncheck currentlyWorkHere");
    }
    
    // Start Date: 08 / 2025
    const sm = document.getElementById("experienceForm_startMonth");
    if (sm) {
        sm.value = "08";
        sm.dispatchEvent(new Event("change", {bubbles: true}));
        const smr = document.getElementById("experienceForm_startMonth__r");
        if (smr) smr.value = "أغسطس";
        log.push("set start 08");
    }
    const sy = document.getElementById("experienceForm_startYear");
    if (sy) {
        sy.value = "2025";
        sy.dispatchEvent(new Event("change", {bubbles: true}));
        const syr = document.getElementById("experienceForm_startYear__r");
        if (syr) syr.value = "2025";
        log.push("set start 2025");
    }
    
    // End Date: 01 / 2026
    const em = document.getElementById("experienceForm_endMonth");
    if (em) {
        em.value = "01";
        em.dispatchEvent(new Event("change", {bubbles: true}));
        const emr = document.getElementById("experienceForm_endMonth__r");
        if (emr) emr.value = "يناير";
        log.push("set end 01");
    }
    const ey = document.getElementById("experienceForm_endYear");
    if (ey) {
        ey.value = "2026";
        ey.dispatchEvent(new Event("change", {bubbles: true}));
        const eyr = document.getElementById("experienceForm_endYear__r");
        if (eyr) eyr.value = "2026";
        log.push("set end 2026");
    }
    
    return log.join(", ");
})()
"""

print(run_js(script))

