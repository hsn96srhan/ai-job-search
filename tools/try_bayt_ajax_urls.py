import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Navigate back to mycvs page, then use AJAX to load edit section
nav_cmd = """tell application "Google Chrome" to set URL of tab 2 of window 1 to "https://www.bayt.com/ar/mycvs/?cv_id=98683664" """
subprocess.run(["osascript", "-e", nav_cmd])
time.sleep(4)

# Try fetching the target job section edit form via AJAX
ajax_load = """
(async () => {
    // Try to fetch the target job edit form
    const urls = [
        '/ar/cv/targetJob/edit/?cv_id=98683664',
        '/ar/cv/98683664/targetJob/',
        '/ar/jobseeker/targetJob/?cv_id=98683664',
    ];
    for (const url of urls) {
        const r = await fetch(url);
        if (r.ok) {
            return JSON.stringify({url: url, status: r.status, text: (await r.text()).slice(0, 200)});
        }
    }
    return "none worked";
})()
"""
result = run_js(2, ajax_load)
print("AJAX result:", result[:500] if result else "empty")
