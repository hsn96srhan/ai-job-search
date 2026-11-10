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

        var fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
        fileInputs.forEach(fi => {{
            var dt = new DataTransfer();
            dt.items.add(file);
            fi.files = dt.files;
            fi.dispatchEvent(new Event('input', {{ bubbles: true }}));
            fi.dispatchEvent(new Event('change', {{ bubbles: true }}));

            var dropTarget = fi.parentElement;
            if (dropTarget) {{
                dropTarget.dispatchEvent(new DragEvent('dragenter', {{ dataTransfer: dt, bubbles: true }}));
                dropTarget.dispatchEvent(new DragEvent('dragover', {{ dataTransfer: dt, bubbles: true }}));
                dropTarget.dispatchEvent(new DragEvent('drop', {{ dataTransfer: dt, bubbles: true }}));
            }}
        }});

        return 'DISPATCHED_ON_' + fileInputs.length + '_TARGETS';
    }} catch(e) {{
        return 'ERR: ' + e.message;
    }}
}})()
"""

Path('/tmp/drop_file.js').write_text(js_body, encoding='utf-8')

res = subprocess.run(["osascript", "/tmp/run_drop.applescript"], capture_output=True, text=True)
print("STDOUT:", res.stdout.strip())
