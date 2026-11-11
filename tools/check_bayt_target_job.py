import subprocess
import base64
import json

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Navigate to the CV edit page to get the target job section
nav_cmd = """tell application "Google Chrome" to set URL of tab 2 of window 1 to "https://www.bayt.com/ar/cv/98683664/edit/?section=targetJob" """
subprocess.run(["osascript", "-e", nav_cmd])

import time
time.sleep(3)

check = """
(() => {
    return JSON.stringify({
        url: window.location.href,
        title: document.title,
        inputs: Array.from(document.querySelectorAll('input, select, textarea')).map(i => ({
            id: i.id,
            name: i.name,
            value: i.value,
            selectedText: i.tagName === 'SELECT' ? (i.options[i.selectedIndex] ? i.options[i.selectedIndex].text : null) : undefined,
            type: i.type
        })).filter(i => i.id && i.id.includes('targetJob'))
    });
})()
"""
print(run_js(2, check))
