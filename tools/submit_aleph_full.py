#!/usr/bin/env python3
"""Complete automated application submission for Aleph on Lever."""

import subprocess
import time
import base64
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = REPO_ROOT / "cv/marketing-director-hsn.pdf"
b64_pdf = base64.b64encode(PDF_PATH.read_bytes()).decode('ascii')

js_body = f"""
(function() {{
    try {{
        function setVal(name, val) {{
            var el = document.querySelector('input[name="' + name + '"], textarea[name="' + name + '"]');
            if (!el) return false;
            el.value = val;
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }}

        function setSelect(name, matchText) {{
            var sel = document.querySelector('select[name="' + name + '"]');
            if (!sel) return false;
            var opt = Array.from(sel.options).find(o => o.text.toLowerCase().includes(matchText.toLowerCase()));
            if (opt) {{
                sel.value = opt.value;
                sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }}

        // 1. Basic Fields
        setVal('name', 'Hassan Sarhan');
        setVal('email', 'hsn96srhan@gmail.com');
        setVal('phone', '+966506267542');
        setVal('location', 'Riyadh, Saudi Arabia');
        setVal('selectedLocation', '{{"name":"Riyadh, SAU","id":"9756d36b82c0c6c1faf4a8b97d3be6e409f16da2"}}');
        setVal('org', 'FLUX Ads Agency');
        setVal('urls[LinkedIn]', 'https://www.linkedin.com/in/srhan-jr/');
        setVal('urls[Portfolio]', 'https://hsn96srhan.github.io/hsn/');

        // 2. Privacy Policy Checkbox
        var privacyCb = document.querySelector('input[type="checkbox"][name*="faa1fcd7"]');
        if (privacyCb && !privacyCb.checked) privacyCb.click();

        // 3. Expected Gross Salary
        setVal('cards[09f9307b-f0d7-4c87-a318-dc79310f9689][field0]', '10,000');

        // Currency Select
        var currSel = document.querySelector('select[name="cards[09f9307b-f0d7-4c87-a318-dc79310f9689][field1]"]');
        if (currSel) {{
            var opt = Array.from(currSel.options).find(o => o.text.includes('SAR') || o.text.includes('Saudi') || o.text.includes('USD'));
            if (opt) currSel.value = opt.value;
            currSel.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}

        // Monthly vs Annual
        setSelect('cards[09f9307b-f0d7-4c87-a318-dc79310f9689][field2]', 'Monthly');

        // Notice Period
        setVal('cards[1f3d0b3f-b74b-431b-903b-e68407fb49a3][field0]', '15 days / Immediate');

        // English Proficiency
        var engSel = document.querySelector('select[name="cards[384de934-280e-42a8-973d-540927397c6f][field0]"]');
        if (engSel) {{
            var opt = Array.from(engSel.options).find(o => o.text.toLowerCase().includes('proficient') || o.text.toLowerCase().includes('fluent') || o.text.toLowerCase().includes('advanced') || o.text.includes('C1') || o.text.includes('C2') || o.text.includes('B2'));
            if (opt) engSel.value = opt.value;
            else if (engSel.options.length > 2) engSel.selectedIndex = engSel.options.length - 1;
            engSel.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}

        // Radios (Relatives, Ownership, Consulting -> All "No")
        var radios = Array.from(document.querySelectorAll('input[type="radio"]'));
        radios.forEach(r => {{
            if (r.value === 'No' && !r.checked) r.click();
        }});

        // Nationality: Other
        setSelect('cards[4a195304-5d5b-4786-8b23-12b43b3e6c15][field0]', 'Other');

        // Currently Live in Saudi Arabia: Yes
        setSelect('cards[4a195304-5d5b-4786-8b23-12b43b3e6c15][field1]', 'Yes');

        // Decision checkboxes
        var decCbs = Array.from(document.querySelectorAll('input[name="cards[0cafb958-2e8f-4cdc-9636-db361c5e4e66][field0]"]'));
        decCbs.forEach(cb => {{
            if (cb.value.includes('Reputation') || cb.value.includes('Specific platform') || cb.value.includes('Company culture')) {{
                if (!cb.checked) cb.click();
            }}
        }});

        // Where did you find: LinkedIn
        setSelect('cards[0cafb958-2e8f-4cdc-9636-db361c5e4e66][field2]', 'LinkedIn');

        // File upload via DataTransfer
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

        var fileInp = document.getElementById('resume-upload-input') || document.querySelector('input[name="resume"]');
        if (fileInp) {{
            fileInp.files = dt.files;
            fileInp.dispatchEvent(new Event('input', {{ bubbles: true }}));
            fileInp.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}

        return {{
            firstName: document.querySelector('input[name="name"]')?.value,
            hasFile: fileInp && fileInp.files.length > 0 ? fileInp.files[0].name : 'no file',
            tcChecked: privacyCb ? privacyCb.checked : false
        }};
    }} catch(e) {{
        return {{ error: e.message }};
    }}
}})()
"""

Path('/tmp/aleph_fill.js').write_text(js_body, encoding='utf-8')

# 1. Navigate to Aleph Lever
nav_as = '''
tell application "Google Chrome"
    set URL of active tab of front window to "https://jobs.lever.co/aleph/3ec5aa0c-b3b2-4a40-b7f3-27ed0624b0f8/apply"
end tell
'''
subprocess.run(['osascript', '-e', nav_as], check=True)
print("Navigating to Aleph on Lever...")
time.sleep(4)

# 2. Execute fill
as_content = """set jsCode to read POSIX file "/tmp/aleph_fill.js" as «class utf8»
tell application "Google Chrome"
    tell active tab of front window
        execute javascript jsCode
    end tell
end tell"""

Path('/tmp/run_aleph.applescript').write_text(as_content, encoding='utf-8')
res = subprocess.run(["osascript", "/tmp/run_aleph.applescript"], capture_output=True, text=True)
print("Fill output:", res.stdout.strip())
if res.stderr.strip(): print("Fill error:", res.stderr.strip())

# 3. Submit
time.sleep(2)
sub_as = '''
tell application "Google Chrome"
    tell active tab of front window
        execute javascript "
        var btn = document.getElementById('hcaptchaSubmitBtn');
        if (btn) {
            btn.scrollIntoView({ block: 'center' });
            btn.click();
            'CLICKED_SUBMIT';
        } else {
            'NO_BTN';
        }
        "
    end tell
end tell
'''
sub_res = subprocess.run(["osascript", "-e", sub_as], capture_output=True, text=True)
print("Submit output:", sub_res.stdout.strip())

time.sleep(5)
# Check result
check_as = '''
tell application "Google Chrome"
    tell active tab of front window
        execute javascript "
        JSON.stringify({
            url: window.location.href,
            title: document.title,
            hasThank: document.body.innerText.includes('Thank') || document.body.innerText.includes('received') || document.body.innerText.includes('applied')
        });
        "
    end tell
end tell
'''
check_res = subprocess.run(["osascript", "-e", check_as], capture_output=True, text=True)
print("Result:", check_res.stdout.strip())

