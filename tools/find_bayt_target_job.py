import subprocess
import base64
import json

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Find target job edit button
script = """
(() => {
    const editBtn = document.querySelector('a[href*="target-job"], button[data-action*="target-job"], [data-section="target-job"] a, #targetJobSection a');
    const allLinks = Array.from(document.querySelectorAll('a')).filter(a => a.href && a.href.includes('target-job') || a.innerText.includes('الوظيفة المرغوبة'));
    return JSON.stringify({
        editBtn: editBtn ? editBtn.outerHTML : null,
        links: allLinks.map(l => ({text: l.innerText, href: l.href}))
    });
})()
"""

print(run_js(2, script))

