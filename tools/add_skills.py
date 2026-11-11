#!/usr/bin/env python3
import subprocess
import base64
import time

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

skills_to_add = [
    "Performance Marketing",
    "E-Commerce",
    "Marketing Strategy",
    "Brand Management",
    "Content Strategy"
]

for sk in skills_to_add:
    type_js = f"""
    (() => {{
        const inp = document.getElementById("skillsForm_skillName__r");
        if (!inp) return "no inp";
        inp.value = "{sk}";
        inp.dispatchEvent(new Event("input", {{bubbles: true}}));
        return "typed";
    }})()
    """
    run_js(type_js)
    time.sleep(0.5)
    
    click_js = f"""
    (() => {{
        const lis = Array.from(document.querySelectorAll("li")).filter(l => l.innerText.trim().toLowerCase() === "{sk.lower()}");
        if (lis.length > 0) {{
            lis[0].click();
            return "clicked: {sk}";
        }}
        // fallback: add option directly to select
        const sel = document.getElementById("skillsForm_skillName");
        if (sel) {{
            const opt = new Option("{sk}", "{sk}", true, true);
            sel.add(opt);
            return "appended: {sk}";
        }}
        return "failed";
    }})()
    """
    res = run_js(click_js)
    print(sk, "->", res)
    time.sleep(0.5)

# Now save
save_res = run_js("""
(() => {
    const btn = document.getElementById("submitCVForm");
    if (btn) {
        btn.click();
        return "clicked submit";
    }
    return "no btn";
})()
""")
print("Save result:", save_res)

