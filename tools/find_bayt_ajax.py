import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

# Navigate back to mycvs 
nav_cmd = """tell application "Google Chrome" to set URL of tab 2 of window 1 to "https://www.bayt.com/ar/mycvs/?cv_id=98683664" """
subprocess.run(["osascript", "-e", nav_cmd])
time.sleep(4)

# Use AJAX to fetch the target job form from Bayt, then post the correction
# First get cookies
get_cookies = """
(() => {
    return document.cookie;
})()
"""
cookies = run_js(2, get_cookies)
print("Cookies length:", len(cookies))

# Find the AJAX endpoint for target job update
# Looking at how Bayt handles this - check network traffic or look for form patterns
# on the mycvs page
find_ajax_patterns = """
(() => {
    // Look for XHR/fetch interceptors or global AJAX URLs
    const scripts = Array.from(document.querySelectorAll('script')).map(s => s.textContent).join('');
    const matches = scripts.match(/targetJob[^"\\s]{0,50}/g);
    return JSON.stringify({
        matches: matches ? matches.slice(0, 20) : [],
        apiUrls: Array.from(scripts.matchAll(/["'](\\/ar\\/cv\\/[^"'\\s]+)["']/g)).map(m => m[1]).filter(Boolean).slice(0, 20)
    });
})()
"""
print("API patterns:", run_js(2, find_ajax_patterns))
