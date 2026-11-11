import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# The career level edit on Bayt is done through a form accessible via AJAX
# Let's look at the actual form URL by scanning scripts for forms
find_script = """
(() => {
    // profileB8 object contains methods for editing sections
    const methods = Object.keys(window.profileB8 || {});
    const targetJobFn = typeof profileB8 !== 'undefined' ? Object.keys(profileB8).filter(k => k.toLowerCase().includes('target') || k.toLowerCase().includes('career') || k.toLowerCase().includes('job')) : [];
    
    // also check for form URLs in scripts
    const allText = Array.from(document.scripts).map(s => s.src || s.textContent).join(' ');
    const formUrls = allText.match(/\\/ar\\/cv\\/[a-zA-Z0-9_/-]+/g);
    return JSON.stringify({
        profileB8Methods: methods,
        targetRelated: targetJobFn,
        formUrls: formUrls ? [...new Set(formUrls)].slice(0, 30) : []
    });
})()
"""
print(run_js(2, find_script))
