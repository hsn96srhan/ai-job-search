import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Navigate to target job edit URL
nav_cmd = """tell application "Google Chrome" to set URL of tab 2 of window 1 to "https://www.bayt.com/ar/cv/98683664/?section=targetJob" """
subprocess.run(["osascript", "-e", nav_cmd])
time.sleep(3)

check = """
(() => {
    return JSON.stringify({
        url: window.location.href,
        title: document.title,
        bodySlice: document.body.innerText.slice(0, 500).replace(/\\s+/g, ' ')
    });
})()
"""
print(run_js(2, check))
