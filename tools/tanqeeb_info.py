import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

info_script = """
(() => {
    return JSON.stringify({
        url: window.location.href,
        title: document.title,
        score: document.body.innerText.match(/\\d+%/)?.[0],
        heading: document.querySelector('h1, h2, h3, h4')?.innerText,
        text: document.body.innerText.slice(0, 600).replace(/\\s+/g, ' ')
    });
})()
"""

out = run_js(8, info_script)
print("Page Info:", out)

