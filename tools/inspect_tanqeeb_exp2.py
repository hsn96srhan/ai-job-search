import subprocess
import base64
import json

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

script = """
(() => {
    // Find all cards or container elements that hold experience items
    const editBtns = Array.from(document.querySelectorAll('button[data-edit-url]'));
    const items = [];
    const seen = new Set();
    
    for (const btn of editBtns) {
        const url = btn.getAttribute('data-edit-url');
        if (seen.has(url)) continue;
        seen.add(url);
        
        let container = btn;
        // traverse up to find container with text
        for (let i = 0; i < 6; i++) {
            if (container.parentElement) {
                container = container.parentElement;
                if (container.classList.contains('card') || container.classList.contains('border') || container.innerText.includes('Marketing') || container.innerText.includes('يناير') || container.innerText.includes('مدير')) {
                    break;
                }
            }
        }
        items.push({
            url: url,
            text: container ? container.innerText.replace(/\\s+/g, ' ') : ''
        });
    }
    return JSON.stringify(items);
})()
"""

out = run_js(8, script)
print(out)

