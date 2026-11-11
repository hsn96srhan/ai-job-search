#!/usr/bin/env python3
import subprocess
import base64
import json

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
    const items = [];
    document.querySelectorAll("a, button, [class*='edit'], [class*='pencil'], [data-js]").forEach(el => {
        const t = (el.innerText || "").trim();
        const p = el.parentElement ? el.parentElement.innerText.substring(0, 50).replace(/\\n/g, ' ') : '';
        items.push({
            tag: el.tagName,
            cls: el.className,
            text: t,
            parentText: p,
            href: el.href || '',
            id: el.id || '',
            dataset: el.dataset
        });
    });
    return JSON.stringify(items);
})()
"""

res = run_js(script)
try:
    data = json.loads(res)
    for it in data:
        if any(k in it['parentText'] or k in it['text'] for k in ['هاتف', 'اتصال', 'تعديل', '541']):
            print(f"[{it['tag']}] text={it['text']} parent={it['parentText']} id={it['id']} cls={it['cls']}")
except Exception as e:
    print("Error:", e, res[:500])

