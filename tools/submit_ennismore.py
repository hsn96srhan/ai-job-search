#!/usr/bin/env python3
"""Submit SO/ Hotels & Resorts (Ennismore / Accor) application in Google Chrome."""

import subprocess
import base64
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = REPO_ROOT / "cv/marketing-director-hsn.pdf"
b64_pdf = base64.b64encode(PDF_PATH.read_bytes()).decode('ascii')

js_body = f"""
(function() {{
    try {{
        // 1. Fill basic fields
        var fn = document.querySelector('input[name="candidateInformation.firstName"]');
        if (fn) fn.value = 'Hassan';
        var ln = document.querySelector('input[name="candidateInformation.lastName"]');
        if (ln) ln.value = 'Sarhan';
        var em = document.querySelector('input[name="candidateInformation.email"]');
        if (em) em.value = 'hsn96srhan@gmail.com';
        var ph = document.querySelector('input[name="candidateInformation.phoneNumber"]');
        if (ph) ph.value = '+966506267542';

        [fn, ln, em, ph].forEach(el => {{
            if (el) {{
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }});

        // 2. Terms
        var tc = document.querySelector('input[name="terms_and_conditions"]');
        if (tc && !tc.checked) tc.click();

        // 3. File upload via DataTransfer
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

        var fileInp = document.querySelector('input[name="candidateInformation.resume.file"]');
        if (fileInp) {{
            fileInp.files = dt.files;
            fileInp.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}

        return {{
            firstName: fn ? fn.value : null,
            email: em ? em.value : null,
            hasFile: fileInp && fileInp.files.length > 0 ? fileInp.files[0].name : 'no file',
            tcChecked: tc ? tc.checked : false
        }};
    }} catch(e) {{
        return {{ error: e.message }};
    }}
}})()
"""

Path('/tmp/ennismore_fill.js').write_text(js_body, encoding='utf-8')

as_content = """set jsCode to read POSIX file "/tmp/ennismore_fill.js" as «class utf8»
tell application "Google Chrome"
    tell active tab of front window
        execute javascript jsCode
    end tell
end tell"""

Path('/tmp/run_ennismore.applescript').write_text(as_content, encoding='utf-8')

res = subprocess.run(["osascript", "/tmp/run_ennismore.applescript"], capture_output=True, text=True)
print("STDOUT:", res.stdout.strip())
print("STDERR:", res.stderr.strip())
