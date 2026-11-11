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
    const f = document.getElementById("targetJobID");
    if (!f) return "Form not found";
    
    const selects = {};
    f.querySelectorAll("select").forEach(s => {
        selects[s.id || s.name] = Array.from(s.options).map(o => ({val: o.value, text: o.text}));
    });
    return JSON.stringify(selects);
})()
"""

res = run_js(script)
try:
    data = json.loads(res)
    for k, v in data.items():
        print(f"=== Select: {k} ===")
        for opt in v:
            print(f"   [{opt['val']}] {opt['text']}")
except Exception as e:
    print("Error:", e, res[:500])

