import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# The CV page loads sections via AJAX. Find data-* attributes that trigger edit modals
inspect = """
(() => {
    const els = Array.from(document.querySelectorAll('[data-url], [data-href], [onclick], [data-action]')).map(el => ({
        tag: el.tagName,
        id: el.id,
        cls: el.className.slice(0, 50),
        dataUrl: el.getAttribute('data-url'),
        dataHref: el.getAttribute('data-href'),
        dataAction: el.getAttribute('data-action'),
        onclick: el.getAttribute('onclick'),
        text: el.innerText.trim().slice(0, 80)
    })).filter(el => el.dataUrl || el.dataHref || el.dataAction || (el.onclick && !el.onclick.includes('cookie')));
    return JSON.stringify(els.slice(0, 30));
})()
"""
print(run_js(2, inspect))
