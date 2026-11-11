#!/usr/bin/env python3
import subprocess
import base64
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = REPO_ROOT / "cv/marketing-director-hsn.pdf"
b64_pdf = base64.b64encode(PDF_PATH.read_bytes()).decode('ascii')

js_body = f"""
(function() {{
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
        var dt = new DataTransfer();
        dt.items.add(file);
        var inp = document.getElementById('resume-upload-input');
        if (!inp) return 'NO_FILE_INPUT';
        inp.files = dt.files;
        inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
        inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
        return 'ATTACHED_' + inp.files[0].name + '_' + inp.files[0].size;
    }} catch(e) {{
        return 'ERR: ' + e.message;
    }}
}})()
"""

Path('/tmp/upload_resume.js').write_text(js_body, encoding='utf-8')

as_file = Path('/tmp/run_upload.applescript')
as_file.write_text("""
set jsCode to read POSIX file "/tmp/upload_resume.js" as «class utf8»
tell application "Google Chrome"
    tell active tab of front window
        execute javascript jsCode
    end tell
end tell
""", encoding='utf-8')

res = subprocess.run(["osascript", str(as_file)], capture_output=True, text=True)
print("STDOUT:", res.stdout.strip())
print("STDERR:", res.stderr.strip())

