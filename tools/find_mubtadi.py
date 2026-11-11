import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Full body text to find "مبتدئ" section
inspect = """
(() => {
    const full = document.body.innerText;
    const idx = full.indexOf('مبتدئ');
    if (idx === -1) return "No مبتدئ found";
    return full.slice(Math.max(0, idx-200), idx+300).replace(/\\s+/g, ' ');
})()
"""
print(run_js(2, inspect))
