import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

fill_script = """
(() => {
    const title = document.getElementById("UserCourseTitle");
    if (title) {
        title.value = "الاعتماد المهني كمدير تسويق - Professional Marketing Manager";
        title.dispatchEvent(new Event("input", {bubbles: true}));
    }
    const provider = document.getElementById("UserCourseProvider");
    if (provider) {
        provider.value = "وزارة الموارد البشرية والتنمية الاجتماعية (HRSD)";
        provider.dispatchEvent(new Event("input", {bubbles: true}));
    }
    const m = document.getElementById("UserCourseAccomplishedDateMonth");
    if (m) {
        m.value = "01";
        m.dispatchEvent(new Event("change", {bubbles: true}));
    }
    const y = document.getElementById("UserCourseAccomplishedDateYear");
    if (y) {
        y.value = "2024";
        y.dispatchEvent(new Event("change", {bubbles: true}));
    }
    const desc = document.getElementById("UserCourseDescription");
    if (desc) {
        desc.value = "الاعتماد المهني الرسمي كمدير تسويق صادر عن وزارة الموارد البشرية والتنمية الاجتماعية في المملكة العربية السعودية.";
        desc.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // Find the 'تقدم' submit button
    const submitBtn = Array.from(document.querySelectorAll('button[type=submit]')).find(b => b.innerText.trim() === 'تقدم');
    if (submitBtn) {
        submitBtn.click();
        return "Clicked submit تقدم";
    }
    return "Submit not found";
})()
"""

print(run_js(8, fill_script))
time.sleep(2)

verify_script = """
(() => {
    return {
        url: window.location.href,
        score: document.body.innerText.match(/\\d+%/)?.[0],
        title: document.title,
        text: document.body.innerText.slice(0, 500).replace(/\\s+/g, ' ')
    };
})()
"""
print(run_js(8, verify_script))

