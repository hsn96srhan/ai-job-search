#!/usr/bin/env python3
import subprocess
import base64

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

script = """
(() => {
    const ids = ['personalInformation', 'targetJob', 'contact_info', 'references', 'memberships', 'hobbies', 'disabilities'];
    let out = '';
    
    // Also check for contact info block
    const contactBlock = document.querySelector('[data-js-contact-info]') || document.querySelector('.card.has-pointer') || document.querySelector('[class*=\"contact\"]');
    if (contactBlock) {
        out += '=== contact block ===\\n' + contactBlock.innerText + '\\n\\n';
    }

    ids.forEach(id => {
        const el = document.getElementById(id) || document.querySelector(`[id*="${id}"]`);
        if (el) {
            out += '=== ' + id + ' ===\\n' + el.innerText + '\\n\\n';
        }
    });
    return out;
})()
"""

print(run_js(script))
