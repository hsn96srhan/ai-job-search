import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Navigate to mycvs
nav_cmd = """tell application "Google Chrome" to set URL of tab 2 of window 1 to "https://www.bayt.com/ar/mycvs/?cv_id=98683664" """
subprocess.run(["osascript", "-e", nav_cmd])
time.sleep(3)

# Find the target job section edit link
find_edit = """
(() => {
    // Look for edit links near sections 
    const allAnchors = Array.from(document.querySelectorAll('a')).map(a => ({
        href: a.href,
        text: a.innerText.trim(),
        cls: a.className
    })).filter(a => a.href && (a.href.includes('target') || a.href.includes('targetJob') || a.text.includes('تعديل') || a.text.includes('edit')));
    return JSON.stringify(allAnchors.slice(0, 20));
})()
"""
print("Edit links:", run_js(2, find_edit))
