import subprocess
import base64
import json

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

check = """
(() => {
    const full = document.body.innerText;
    const idx = full.indexOf('الوظيفة المرغوبة');
    if (idx === -1) return 'Section not found';
    return full.slice(idx, idx + 400).replace(/\\s+/g, ' ');
})()
"""
print(run_js(2, check))
