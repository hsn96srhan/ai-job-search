import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

time.sleep(2)

script = """
(() => {
    const inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(i => ({
        id: i.id,
        name: i.name,
        type: i.type,
        value: i.value,
        selectedText: i.tagName === 'SELECT' ? (i.options[i.selectedIndex]?.text) : undefined,
        optionsCount: i.tagName === 'SELECT' ? i.options.length : undefined
    }));
    return JSON.stringify(inputs);
})()
"""

print(run_js(8, script))

