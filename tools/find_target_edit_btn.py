import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Find div.u-right inside card-head adjacent to الوظيفة المرغوبة
find_edit_btn = """
(() => {
    const h4 = Array.from(document.querySelectorAll('h4')).find(h => h.innerText.trim() === 'الوظيفة المرغوبة');
    if (!h4) return "H4 not found";
    const cardHead = h4.closest('.card-head, .card-title, [class*="card"]');
    if (!cardHead) return "cardHead not found";
    // Look for edit button in card head
    const btn = cardHead.querySelector('a, button');
    return JSON.stringify({
        cardHeadHtml: cardHead.outerHTML.slice(0, 500),
        btn: btn ? {tag: btn.tagName, href: btn.href, onclick: btn.getAttribute('onclick'), text: btn.innerText.trim(), cls: btn.className} : null
    });
})()
"""
print(run_js(2, find_edit_btn))
