import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Navigate back to mycvs 
nav_cmd = """tell application "Google Chrome" to set URL of tab 2 of window 1 to "https://www.bayt.com/ar/mycvs/?cv_id=98683664" """
subprocess.run(["osascript", "-e", nav_cmd])
time.sleep(3)

# Find the actual edit form URL for target job by inspecting the page
find_forms = """
(() => {
    const forms = Array.from(document.querySelectorAll('form')).map(f => ({
        action: f.action,
        id: f.id,
        method: f.method,
        inputIds: Array.from(f.querySelectorAll('input, select')).map(i => i.id).filter(Boolean)
    }));
    return JSON.stringify(forms);
})()
"""
print(run_js(2, find_forms))
