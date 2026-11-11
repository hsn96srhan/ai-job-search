#!/usr/bin/env python3
import subprocess
import base64
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = REPO_ROOT / "cv/marketing-director-hsn.pdf"
b64_pdf = base64.b64encode(PDF_PATH.read_bytes()).decode('ascii')

def run_js(js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    apple_script = f'''
    tell application "Google Chrome"
        tell tab 2 of window 1
            execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))"
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    return res.stdout.strip()

js = f"""
(() => {{
    try {{
        var b64Data = "{b64_pdf}";
        var byteCharacters = atob(b64Data);
        var byteArrays = [];
        for (var offset = 0; offset < byteCharacters.length; offset += 512) {{
            var slice = byteCharacters.slice(offset, offset + 512);
            var byteNumbers = new Array(slice.length);
            for (var i = 0; i < slice.length; i++) {{
                byteNumbers[i] = slice.charCodeAt(i);
            }}
            byteArrays.push(new Uint8Array(byteNumbers));
        }}
        var blob = new Blob(byteArrays, {{ type: "application/pdf" }});
        var file = new File([blob], "marketing-director-hsn.pdf", {{ type: "application/pdf", lastModified: Date.now() }});

        var fi = document.getElementById("uploadCvForm_uploadCv");
        if (!fi) return "uploadCvForm_uploadCv not found";
        
        var dt = new DataTransfer();
        dt.items.add(file);
        fi.files = dt.files;
        fi.dispatchEvent(new Event('input', {{ bubbles: true }}));
        fi.dispatchEvent(new Event('change', {{ bubbles: true }}));

        // Now find and click 'تحميل ومتابعة'
        var f = document.getElementById("replaceCVFormID");
        var btns = Array.from(f.querySelectorAll("button, a.btn, input[type=submit]"));
        var submitBtn = btns.find(b => (b.innerText || b.value || "").includes("تحميل ومتابعة"));
        if (submitBtn) {{
            submitBtn.click();
            return "File attached and clicked submitBtn";
        }}
        return "Submit button not found";
    }} catch(e) {{
        return "Error: " + e.message;
    }}
}})()
"""

print(run_js(js))

