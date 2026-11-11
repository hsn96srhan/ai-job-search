import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# 1. Click the edit button for the target job section
click_edit = """
(() => {
    const btn = document.getElementById('editTargetJob');
    if (!btn) return 'Not found';
    btn.click();
    return 'Clicked';
})()
"""
print("Click edit:", run_js(2, click_edit))
time.sleep(2)

# 2. Inspect the modal/form that appeared
inspect_modal = """
(() => {
    // The modal should now be visible
    const inputs = Array.from(document.querySelectorAll('input, select, textarea')).filter(el => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
    });
    return JSON.stringify({
        url: window.location.href,
        inputs: inputs.map(i => ({
            id: i.id,
            name: i.name,
            value: i.value,
            type: i.type,
            selectedText: i.tagName === 'SELECT' ? (i.options[i.selectedIndex] ? i.options[i.selectedIndex].text : null) : undefined
        })).filter(i => i.id && (i.id.includes('targetJob') || i.id.includes('TargetJob')))
    });
})()
"""
print("Modal inputs:", run_js(2, inspect_modal))
