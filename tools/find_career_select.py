import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Fix career level from "مبتدئ الخبرة" to "إدارة"
# The careerLevel uses a custom autocomplete/select2 widget with __r (display) and hidden select
# Need to find the hidden select for careerLevel and options

find_career_select = """
(() => {
    // The careerLevel__r is the visible text, there's a hidden select with careerLevel
    const hiddenSel = document.getElementById('targetJobForm_careerLevel');
    const displayEl = document.getElementById('targetJobForm_careerLevel__r');
    
    // Also check for name-based select
    const byName = document.querySelector('[name*="careerLevel"]');
    
    return JSON.stringify({
        hiddenSel: hiddenSel ? {tag: hiddenSel.tagName, type: hiddenSel.type, value: hiddenSel.value, options: Array.from(hiddenSel.options || []).map(o => ({val: o.value, text: o.text}))} : null,
        displayEl: displayEl ? {value: displayEl.value} : null,
        byName: byName ? {tag: byName.tagName, name: byName.name, value: byName.value, type: byName.type, options: Array.from(byName.options || []).map(o => ({val: o.value, text: o.text}))} : null
    });
})()
"""
print(run_js(2, find_career_select))
