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
    const cvSection = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.includes('السيرة الذاتية المحدّثة') && el.children.length < 5);
    const cvModal = document.querySelector('#uploadCvModal, [id*="cv"], [id*="Cv"]');
    const fileInputs = Array.from(document.querySelectorAll('input[type=file]')).map(f => ({
        id: f.id,
        name: f.name,
        form: f.form ? f.form.action : null
    }));
    return JSON.stringify({fileInputs, modal: cvModal ? cvModal.id : null});
})()
"""
print(run_js(8, script))

