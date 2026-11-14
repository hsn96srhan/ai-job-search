#!/usr/bin/env python3
import base64
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = REPO_ROOT / "cv/marketing-director-hsn.pdf"
b64_pdf = base64.b64encode(PDF_PATH.read_bytes()).decode('ascii')

js_body = f"""
(function() {{
    try {{
        function setVal(name, val) {{
            var el = document.querySelector('input[name="' + name + '"]');
            if (!el) return false;
            var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }}

        // 1. Text Inputs
        setVal('First_Name', 'Hassan');
        setVal('Last_Name', 'Sarhan');
        setVal('Email', 'hsn96srhan@gmail.com');
        setVal('LinkedIn__s', 'https://www.linkedin.com/in/srhan-jr/');

        // 2. Checkboxes
        var cb1 = document.querySelector('input[name="Terms_of_Application_3"]');
        if (cb1 && !cb1.checked) cb1.click();

        var cb2 = document.querySelector('input[name="I_Understand"]');
        if (cb2 && !cb2.checked) cb2.click();

        // 3. File Upload via DataTransfer
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
        var dt = new DataTransfer();
        dt.items.add(file);
        
        var fileInp = document.querySelector('input[name="Resume"], input[type="file"]');
        if (fileInp) {{
            fileInp.files = dt.files;
            fileInp.dispatchEvent(new Event('input', {{ bubbles: true }}));
            fileInp.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}

        return {{
            firstName: document.querySelector('input[name="First_Name"]')?.value,
            lastName: document.querySelector('input[name="Last_Name"]')?.value,
            email: document.querySelector('input[name="Email"]')?.value,
            linkedin: document.querySelector('input[name="LinkedIn__s"]')?.value,
            hasFile: fileInp && fileInp.files && fileInp.files.length > 0 ? fileInp.files[0].name : 'NO_FILE',
            cb1: cb1 ? cb1.checked : false,
            cb2: cb2 ? cb2.checked : false
        }};
    }} catch(e) {{
        return 'ERR: ' + e.message;
    }}
}})()
"""

Path('/tmp/fill_puffy.js').write_text(js_body, encoding='utf-8')

apple_script = """
set jsCode to read POSIX file "/tmp/fill_puffy.js" as «class utf8»
tell application "Google Chrome"
    repeat with wi from 1 to count of windows
        set w to window wi
        repeat with ti from 1 to count of tabs of w
            set t to tab ti of w
            if (URL of t) contains "join.careers.puffy.com" then
                tell t
                    return execute javascript jsCode
                end tell
            end if
        end repeat
    end repeat
    return "TAB_NOT_FOUND"
end tell
"""

res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
print("Fill Output:", res.stdout.strip())
