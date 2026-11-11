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
    const list = Array.from(document.querySelectorAll('[data-edit-url]')).map(b => {
        const item = b.closest('.dropdown')?.parentElement || b.parentElement;
        return {
            editUrl: b.getAttribute('data-edit-url'),
            text: (item ? item.innerText : '').replace(/\\s+/g, ' ')
        };
    });
    return JSON.stringify(list);
})()
"""

out = run_js(8, script)
print(out)

