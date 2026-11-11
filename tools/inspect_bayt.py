#!/usr/bin/env python3
import subprocess
import json

def run_js(js_code):
    escaped_js = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$')
    apple_script = f'''
    tell application "Google Chrome"
        tell tab 2 of window 1
            execute javascript "{escaped_js}"
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    return res.stdout.strip()

# Let's inspect sections and their edit buttons or links
script = """
(() => {
    const sections = [];
    document.querySelectorAll("section, .card, [class*='section']").forEach(sec => {
        const h = sec.querySelector("h1, h2, h3, h4, h5");
        if (h && h.innerText) {
            const btns = Array.from(sec.querySelectorAll("a, button")).map(b => ({
                text: b.innerText.trim(),
                href: b.href || '',
                id: b.id || '',
                cls: b.className || '',
                onclick: b.getAttribute('onclick') || ''
            })).filter(b => b.text || b.cls.includes('edit') || b.cls.includes('add') || b.cls.includes('icon'));
            sections.push({
                heading: h.innerText.trim(),
                id: sec.id,
                buttons: btns
            });
        }
    });
    return JSON.stringify(sections);
})()
"""

res = run_js(script)
try:
    data = json.loads(res)
    for s in data:
        print(f"=== {s['heading']} (id: {s['id']}) ===")
        for b in s['buttons']:
            print(f"   [{b['text']}] id={b['id']} class={b['cls']} href={b['href']}")
except Exception as e:
    print("Error:", e, "Raw output:", res[:500])
