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
    const res = {};
    
    // Completeness score
    const scores = [];
    document.querySelectorAll("text, div, span, h4, h3, h2").forEach(el => {
        const t = (el.innerText || "").trim();
        if (t.includes("%") && t.length < 20) scores.push(t);
    });
    res['scores'] = Array.from(new Set(scores));
    
    // Check pending booster suggestions
    const boosters = [];
    document.querySelectorAll("#cvBuilderWrapper a, #cvBuilderWrapper li").forEach(el => {
        const t = el.innerText.trim().replace(/\\n/g, ' ');
        if (t && t.length < 100) boosters.push(t);
    });
    res['boosters'] = Array.from(new Set(boosters)).slice(0, 15);
    
    // Header text
    const h = document.querySelector(".card.has-pointer") || document.querySelector(".card");
    res['header'] = h ? h.innerText.substring(0, 400).replace(/\\n/g, ' -- ') : '';
    
    return JSON.stringify(res);
})()
"""

res = run_js(script)
try:
    data = json.loads(res)
    print("Scores:", data['scores'])
    print("Header:", data['header'])
    print("Boosters:")
    for b in data['boosters']:
        print("  -", b)
except Exception as e:
    print("Error:", e, res)

