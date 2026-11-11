import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# 1. Click edit for 2838677
click_script = """
(() => {
    const btn = document.querySelector('button[data-edit-url*="2838677"]');
    if (btn) {
        btn.click();
        return "Clicked";
    }
    return "Not found";
})()
"""
print("Click result:", run_js(8, click_script))
time.sleep(1)

# 2. Inspect modal inputs
inspect_script = """
(() => {
    const form = document.querySelector('.modal.show form, #editModalContent form');
    if (!form) return JSON.stringify({error: "No form found"});
    const inputs = Array.from(form.querySelectorAll('input, select, textarea')).map(i => ({
        id: i.id,
        name: i.name,
        type: i.type,
        value: i.value,
        options: i.tagName === 'SELECT' ? Array.from(i.options).slice(0, 15).map(o => ({val: o.value, text: o.text})) : undefined
    }));
    return JSON.stringify({action: form.action, inputs: inputs});
})()
"""
print("Modal form:", run_js(8, inspect_script))

