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
    const items = [];
    document.querySelectorAll("#cvBuilderWrapper li, #cvBuilderWrapper .row").forEach(row => {
        const textSpan = row.querySelector("span, a");
        if (textSpan) {
            const isCompleted = row.innerHTML.includes("line-through") || row.classList.contains("is-done");
            const txt = row.innerText.trim().replace(/\\n/g, ' ');
            if (txt && txt.length < 120 && !txt.includes("عزّز") && !txt.includes("زد من") && !txt.includes("ابنِ") && !txt.includes("أكمل")) {
                items.push({text: txt, done: isCompleted});
            }
        }
    });
    return JSON.stringify(items);
})()
"""

res = run_js(script)
try:
    data = json.loads(res)
    for it in data:
        status = "[DONE]" if it['done'] else "[PENDING]"
        print(f"{status} {it['text']}")
except Exception as e:
    print("Error:", e, res)

