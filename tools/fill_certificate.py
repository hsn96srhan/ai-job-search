import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Inspect inputs
inspect_script = """
(() => {
    const inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(i => ({
        id: i.id,
        name: i.name,
        type: i.type,
        placeholder: i.placeholder
    }));
    return JSON.stringify(inputs);
})()
"""
print("Cert inputs:", run_js(8, inspect_script))

fill_script = """
(() => {
    const name = document.querySelector('input[name*="name"], input[placeholder*="الشهادة"], #UserCertificateName');
    if (name) {
        name.value = "Digital Marketing Nanodegree";
        name.dispatchEvent(new Event("input", {bubbles: true}));
    }
    const provider = document.querySelector('input[name*="provider"], input[placeholder*="المانحة"], #UserCertificateProvider');
    if (provider) {
        provider.value = "MCIT Saudi Arabia & Udacity";
        provider.dispatchEvent(new Event("input", {bubbles: true}));
    }
    const m = document.querySelector('select[name*="month"]');
    if (m) {
        m.value = "06";
        m.dispatchEvent(new Event("change", {bubbles: true}));
    }
    const y = document.querySelector('select[name*="year"]');
    if (y) {
        y.value = "2021";
        y.dispatchEvent(new Event("change", {bubbles: true}));
    }
    const desc = document.querySelector('textarea[name*="description"]');
    if (desc) {
        desc.value = "Advanced Nanodegree in Digital Performance Marketing, omnichannel growth campaigns, analytics, and conversion rate optimization.";
        desc.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Submit تقدم
    const submitBtn = Array.from(document.querySelectorAll('button[type=submit]')).find(b => b.innerText.trim() === 'تقدم');
    if (submitBtn) {
        submitBtn.click();
        return "Clicked submit";
    }
    return "Submit not found";
})()
"""

res = run_js(8, fill_script)
print("Fill & Submit result:", res)
time.sleep(2)

# Check page info
info_script = """
(() => {
    return JSON.stringify({
        url: window.location.href,
        score: document.body.innerText.match(/\\d+%/)?.[0],
        title: document.title,
        text: document.body.innerText.slice(0, 500).replace(/\\s+/g, ' ')
    });
})()
"""
print("After submit:", run_js(8, info_script))

