#!/usr/bin/env python3
"""Complete dropdown selection and submission for HAMS.AI Asana form."""

import subprocess
import time

def run_js(js_code):
    escaped_js = js_code.replace('\\', '\\\\').replace('"', '\\"')
    apple_script = f'''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "{escaped_js}"
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip()

# Helper to select option in Asana dropdown by label
select_script = '''
(async function() {
    var drops = Array.from(document.querySelectorAll('.WorkRequestsField-dropdown'));
    
    for (var i = 0; i < drops.length; i++) {
        var d = drops[i];
        var card = d.parentElement;
        while (card && !card.innerText.includes('*')) card = card.parentElement;
        var label = (card ? card.innerText.split('\\n')[0] : '').toLowerCase();

        d.scrollIntoView({ block: 'center' });
        d.click();
        await new Promise(r => setTimeout(r, 400));

        var items = Array.from(document.querySelectorAll('[role="option"], [class*="MenuItem"], [class*="menuItem"]'));
        var targetText = '';
        if (label.includes('saudi arabia')) targetText = 'yes';
        else if (label.includes('arabic')) targetText = 'yes';
        else if (label.includes('english')) targetText = 'fluent'; // or professional
        else if (label.includes('highest qualification')) targetText = 'bachelor';
        else if (label.includes('currently employed')) targetText = 'yes';
        else if (label.includes('professional certificates')) targetText = 'yes';

        var match = items.find(it => it.innerText.toLowerCase().includes(targetText));
        if (!match && items.length > 0) match = items[0]; // fallback
        if (match) {
            match.click();
            await new Promise(r => setTimeout(r, 400));
        }
    }
    return 'ALL_DROPDOWNS_SELECTED';
})()
'''

print("Selecting dropdown options...")
out, err = run_js(select_script)
print("Dropdowns result:", out)

time.sleep(2)

# Click submit button
submit_script = '''
(function() {
    var btn = document.querySelector('.WorkRequestsSubmissionForm-submitButton');
    if (!btn) {
        var all = Array.from(document.querySelectorAll('div, button'));
        btn = all.find(b => b.innerText.trim() === 'Submit');
    }
    if (btn) {
        btn.scrollIntoView({ block: 'center' });
        btn.click();
        return 'SUBMIT_CLICKED';
    }
    return 'NO_SUBMIT_BTN';
})()
'''
out, err = run_js(submit_script)
print("Submit click result:", out)

time.sleep(5)

check_script = '''
(function() {
    var txt = document.body.innerText;
    var success = txt.includes('Thank') || txt.includes('received') || txt.includes('submitted') || txt.includes('شكراً');
    return JSON.stringify({
        success: success,
        snippet: txt.substring(0, 300).split('\\n').slice(0, 5).join(' | ')
    });
})()
'''
out, err = run_js(check_script)
print("Final confirmation:", out)
