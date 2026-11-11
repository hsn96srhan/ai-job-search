import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Get all section headings and their context
inspect = """
(() => {
    const sections = Array.from(document.querySelectorAll('section, [class*="section"], h2, h3')).map(s => ({
        tag: s.tagName,
        id: s.id,
        cls: s.className,
        text: s.innerText.slice(0, 150).replace(/\\s+/g, ' ')
    })).filter(s => s.text.length > 2);
    return JSON.stringify(sections.slice(0, 30));
})()
"""
print(run_js(2, inspect))
