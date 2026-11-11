import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Navigate to profile with open_social
cmd = """tell application "Google Chrome" to set URL of tab 8 of window 1 to "https://saudi.tanqeeb.com/ar/profile/70204357?open_social=linkedin_url" """
subprocess.run(["osascript", "-e", cmd])
time.sleep(2)

inspect_script = """
(() => {
    const inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(i => ({
        id: i.id,
        name: i.name,
        placeholder: i.placeholder,
        value: i.value,
        type: i.type
    }));
    return JSON.stringify(inputs);
})()
"""
print("Inputs on profile:", run_js(8, inspect_script))

