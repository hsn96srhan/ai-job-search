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
    // Find the pencil buttons or edit triggers near the top
    const buttons = [];
    document.querySelectorAll('.card, [class*="header"]').forEach(c => {
        c.querySelectorAll('a, button, [class*="pencil"], [class*="edit"]').forEach(el => {
            buttons.push({
                tag: el.tagName,
                cls: el.className,
                id: el.id,
                text: el.innerText.trim(),
                href: el.href || '',
                onclick: el.getAttribute('onclick') || '',
                dataset: JSON.stringify(el.dataset)
            });
        });
    });
    return JSON.stringify(buttons.slice(0, 30));
})()
"""

print(run_js(script))

