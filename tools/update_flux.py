import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Currently the modal for 2838677 is already open in Tab 8!
# Let's set the values for FLUX Ads:
# From Month: 12 (December)
# From Year: 2025
# Company Location: الرياض
# To Present: checked
script = """
(() => {
    const loc = document.getElementById("UserExperienceCompanyLocation");
    if (loc) {
        loc.value = "الرياض، المملكة العربية السعودية";
        loc.dispatchEvent(new Event("input", {bubbles: true}));
    }
    const fm = document.getElementById("UserExperienceFromDateMonth");
    if (fm) {
        fm.value = "12";
        fm.dispatchEvent(new Event("change", {bubbles: true}));
        if (window.$ && $(fm).select2) $(fm).trigger("change");
    }
    const fy = document.getElementById("UserExperienceFromDateYear");
    if (fy) {
        fy.value = "2025";
        fy.dispatchEvent(new Event("change", {bubbles: true}));
        if (window.$ && $(fy).select2) $(fy).trigger("change");
    }
    const chk = document.getElementById("UserExperienceToPresent");
    if (chk && !chk.checked) {
        chk.click();
    }
    
    // Submit button
    const btn = document.querySelector("#editModalContent button[type=submit], .modal.show button[type=submit]");
    if (btn) {
        btn.click();
        return "Clicked submit";
    }
    return "Submit button not found";
})()
"""

out = run_js(8, script)
print("Submit result:", out)
time.sleep(2)

# Verify updated text
verify_script = """
(() => {
    return document.body.innerText.slice(0, 700).replace(/\\s+/g, ' ');
})()
"""
print("Body after submit:", run_js(8, verify_script))

