import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

script = """
(() => {
    const li = document.getElementById("UserLinkedinUrl");
    if (li) {
        li.value = "https://www.linkedin.com/in/srhan-jr/";
        li.dispatchEvent(new Event("input", {bubbles: true}));
    }
    const gh = document.getElementById("UserGithubUrl");
    if (gh) {
        gh.value = "https://github.com/hsn96srhan";
        gh.dispatchEvent(new Event("input", {bubbles: true}));
    }
    const web = document.getElementById("UserWebsite");
    if (web) {
        web.value = "https://hsn96srhan.github.io/hsn/";
        web.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Find the form wrapping these inputs
    const form = (li || web).closest('form');
    if (!form) return "No form found";
    
    // Find submit button in this form or modal
    const btn = form.querySelector('button[type=submit], input[type=submit]') || document.querySelector('.modal.show button[type=submit]');
    if (btn) {
        btn.click();
        return "Clicked submit in form: " + form.action;
    }
    
    // Or send via fetch
    const fd = new FormData(form);
    fetch(form.action, {method: "POST", body: fd}).then(() => window.location.reload());
    return "Submitted via fetch to " + form.action;
})()
"""

print(run_js(8, script))
time.sleep(2)

