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
    const ids = ['skills', 'languagesProfile', 'training', 'socialProfiles', 'references'];
    const res = {};
    ids.forEach(id => {
        const el = document.getElementById(id);
        res[id] = el ? el.innerText.trim().replace(/\\n/g, ' -- ') : 'NOT_FOUND';
    });
    return JSON.stringify(res);
})()
"""

import json
res = json.loads(run_js(script))
for k, v in res.items():
    print(f"=== {k} ===")
    print(v[:200])

