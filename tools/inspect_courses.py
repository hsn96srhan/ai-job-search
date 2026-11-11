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
    const inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(i => ({
        id: i.id,
        name: i.name,
        type: i.type,
        placeholder: i.placeholder,
        value: i.value
    }));
    const buttons = Array.from(document.querySelectorAll('button, a.btn')).map(b => ({
        tag: b.tagName,
        text: b.innerText.trim(),
        type: b.type
    }));
    return JSON.stringify({inputs, buttons});
})()
"""
print(run_js(8, script))

