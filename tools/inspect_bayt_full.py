import subprocess
import base64
import json

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

script = """
(() => {
    return {
        url: window.location.href,
        title: document.title,
        bodyText: document.body.innerText.slice(0, 1500).replace(/\\s+/g, ' ')
    };
})()
"""

print(run_js(2, script))

