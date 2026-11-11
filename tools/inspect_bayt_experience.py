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
    const sec = document.getElementById("experience");
    if (!sec) return "Not found";
    
    // Find all experience cards/items inside section
    const items = [];
    sec.querySelectorAll("li, .card-item, [id^='exp-']").forEach(el => {
        items.push({
            id: el.id,
            cls: el.className,
            tag: el.tagName,
            text: el.innerText.trim().replace(/\\n/g, ' -- '),
            html: el.outerHTML.substring(0, 200)
        });
    });
    
    // Find add button
    const addBtn = sec.querySelector("[id*='add'], [class*='add'], a.btn, a[href*='experience']");
    
    return JSON.stringify({
        addBtn: addBtn ? {id: addBtn.id, text: addBtn.innerText, cls: addBtn.className, dataset: addBtn.dataset} : null,
        itemsCount: items.length,
        items: items
    });
})()
"""

res = run_js(script)
try:
    data = json.loads(res)
    print("Add button:", data["addBtn"])
    print("Items count:", data["itemsCount"])
    for it in data["items"]:
        print(f"[{it['tag']}] id={it['id']} text={it['text'][:150]}")
except Exception as e:
    print("Error:", e, res[:500])

