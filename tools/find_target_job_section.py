import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# The target job section shows "مبتدئ". From the initial data, the form IDs are:
# targetJobForm_careerLevel etc. The form probably loads via a toggle
# Let's check if there's a "تعديل" toggle associated with the target job section

# First scroll to and find the target job section
find_section = """
(() => {
    // All elements containing "الوظيفة المرغوبة"
    const els = Array.from(document.querySelectorAll('*')).filter(el => 
        el.childNodes.length === 1 && 
        el.textContent.trim() === 'الوظيفة المرغوبة'
    );
    return JSON.stringify(els.map(el => ({
        tag: el.tagName,
        id: el.id,
        cls: el.className,
        parentId: el.parentElement?.id,
        parentCls: el.parentElement?.className,
        siblings: Array.from(el.parentElement?.children || []).map(c => ({
            tag: c.tagName,
            id: c.id,
            cls: c.className,
            text: c.innerText?.trim().slice(0, 100),
            onclick: c.getAttribute('onclick')
        }))
    })));
})()
"""
print(run_js(2, find_section))
