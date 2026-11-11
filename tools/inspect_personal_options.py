#!/usr/bin/env python3
import subprocess
import base64
import json

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
    const f = document.getElementById("personalInformationID");
    if (!f) return "Form not found";
    
    const res = {};
    ['personalInformationForm_resCity', 'personalInformationForm_visaStatus', 'personalInformationForm_hasDrivingLicense', 'personalInformationForm_drivingLicenseCounties'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            res[id] = Array.from(el.options || []).map(o => ({val: o.value, text: o.text})).slice(0, 30);
        }
    });
    
    // Check radio buttons for driving license
    const rads = Array.from(f.querySelectorAll("input[type=radio]")).map(r => ({id: r.id, name: r.name, val: r.value, label: (r.closest('label') || {}).innerText}));
    res['radios'] = rads;
    
    return JSON.stringify(res);
})()
"""

res = run_js(script)
try:
    data = json.loads(res)
    for k, v in data.items():
        print(f"=== {k} ===")
        print(v)
except Exception as e:
    print("Error:", e, res[:500])

