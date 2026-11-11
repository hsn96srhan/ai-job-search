import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# 1. Click careerLevelModal() to open the career level edit modal
open_modal = """
(() => {
    if (typeof careerLevelModal === 'function') {
        careerLevelModal();
        return 'careerLevelModal called';
    }
    return 'function not found';
})()
"""
print("Open career modal:", run_js(2, open_modal))
time.sleep(1.5)

# 2. Find the modal and inspect its inputs
inspect_modal = """
(() => {
    const modal = document.querySelector('.modal-open .modal, [class*="modal"][style*="display: block"], .is-active.modal, [id*="career"]');
    const visibleInputs = Array.from(document.querySelectorAll('input, select, textarea')).filter(el => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && el.offsetParent !== null;
    });
    return JSON.stringify({
        hasModal: Boolean(modal),
        modalId: modal ? modal.id : null,
        inputs: visibleInputs.map(i => ({
            id: i.id,
            name: i.name,
            value: i.value,
            type: i.type,
            selectedText: i.tagName === 'SELECT' ? (i.options[i.selectedIndex] ? i.options[i.selectedIndex].text : null) : undefined
        })).filter(i => i.id || i.name)
    });
})()
"""
print("Modal inputs:", run_js(2, inspect_modal))
