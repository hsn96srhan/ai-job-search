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
    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, .section-title, .card-title')).map(h => h.innerText.trim()).filter(Boolean);
    const btns = Array.from(document.querySelectorAll('button, a.btn')).map(b => b.innerText.trim()).filter(Boolean);
    return JSON.stringify({headings, btns: btns.slice(0, 30)});
})()
"""
print(run_js(8, script))

