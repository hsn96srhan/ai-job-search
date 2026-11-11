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
    const chk = document.getElementById("UserExperienceToPresent");
    if (chk && !chk.checked) {
        chk.checked = true;
    }
    const form = document.querySelector("#editModalContent form");
    const fd = new FormData(form);
    
    // Use jQuery ajax since Tanqeeb uses it
    let result = "pending";
    if (window.$) {
        $.ajax({
            url: form.action,
            type: "POST",
            data: fd,
            processData: false,
            contentType: false,
            success: function(resp) {
                window._last_ajax_resp = resp;
                window.location.reload();
            },
            error: function(err) {
                window._last_ajax_err = err;
            }
        });
        return "ajax sent";
    }
    return "no jQuery";
})()
"""

out = run_js(8, script)
print("AJAX trigger:", out)
time.sleep(2)

verify = """
(() => {
    return document.body.innerText.slice(0, 700).replace(/\\s+/g, ' ');
})()
"""
print("After reload:", run_js(8, verify))

