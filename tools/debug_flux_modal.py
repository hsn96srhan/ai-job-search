import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Click edit for 2838677
click_script = """
(() => {
    const btn = document.querySelector('button[data-edit-url*="2838677"]');
    if (btn) btn.click();
    return "Clicked";
})()
"""
run_js(8, click_script)
time.sleep(1)

inspect_script = """
(() => {
    const m = document.getElementById("UserExperienceFromDateMonth");
    const y = document.getElementById("UserExperienceFromDateYear");
    return JSON.stringify({
        m_val: m ? m.value : null,
        m_text: m ? m.options[m.selectedIndex]?.text : null,
        y_val: y ? y.value : null,
        y_text: y ? y.options[y.selectedIndex]?.text : null,
        form_data: Array.from(new FormData(document.querySelector('#editModalContent form'))).map(([k,v]) => `${k}=${v}`)
    });
})()
"""
print("Current modal state:", run_js(8, inspect_script))

