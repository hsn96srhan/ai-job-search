#!/usr/bin/env python3
"""Fill and submit Aleph Lever application directly inside Google Chrome."""

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

fill_script = '''
(function() {
    function setVal(name, val) {
        var el = document.querySelector('input[name="' + name + '"], textarea[name="' + name + '"]');
        if (!el) return false;
        el.value = val;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
    }

    function setSelect(name, matchText) {
        var sel = document.querySelector('select[name="' + name + '"]');
        if (!sel) return false;
        var opt = Array.from(sel.options).find(o => o.text.toLowerCase().includes(matchText.toLowerCase()));
        if (opt) {
            sel.value = opt.value;
            sel.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }
        return false;
    }

    // 1. Basic Fields
    setVal('name', 'Hassan Sarhan');
    setVal('email', 'hsn96srhan@gmail.com');
    setVal('phone', '+966506267542');
    setVal('location', 'Riyadh, Saudi Arabia');
    setVal('org', 'FLUX Ads Agency');
    setVal('urls[LinkedIn]', 'https://www.linkedin.com/in/srhan-jr/');
    setVal('urls[Portfolio]', 'https://hsn96srhan.github.io/hsn/');

    // 2. Privacy Policy Checkbox
    var privacyCb = document.querySelector('input[type="checkbox"][name*="faa1fcd7"]');
    if (privacyCb && !privacyCb.checked) privacyCb.click();

    // 3. Expected Gross Salary
    setVal('cards[09f9307b-f0d7-4c87-a318-dc79310f9689][field0]', '10,000');

    // Currency Select
    var currSel = document.querySelector('select[name="cards[09f9307b-f0d7-4c87-a318-dc79310f9689][field1]"]');
    if (currSel) {
        var opt = Array.from(currSel.options).find(o => o.text.includes('SAR') || o.text.includes('Saudi'));
        if (opt) currSel.value = opt.value;
        else {
            // Find USD or first valid
            var usd = Array.from(currSel.options).find(o => o.text.includes('USD'));
            if (usd) currSel.value = usd.value;
        }
        currSel.dispatchEvent(new Event('change', { bubbles: true }));
    }

    // Monthly vs Annual
    setSelect('cards[09f9307b-f0d7-4c87-a318-dc79310f9689][field2]', 'Monthly');

    // Notice Period
    setVal('cards[1f3d0b3f-b74b-431b-903b-e68407fb49a3][field0]', '15 days / Immediate');

    // English Proficiency
    var engSel = document.querySelector('select[name="cards[384de934-280e-42a8-973d-540927397c6f][field0]"]');
    if (engSel) {
        var opt = Array.from(engSel.options).find(o => o.text.toLowerCase().includes('proficient') || o.text.toLowerCase().includes('fluent') || o.text.toLowerCase().includes('advanced') || o.text.includes('C1') || o.text.includes('C2') || o.text.includes('B2'));
        if (opt) engSel.value = opt.value;
        else if (engSel.options.length > 2) engSel.selectedIndex = engSel.options.length - 1;
        engSel.dispatchEvent(new Event('change', { bubbles: true }));
    }

    // Radios (Relatives, Ownership, Consulting -> All "No")
    var radios = Array.from(document.querySelectorAll('input[type="radio"]'));
    radios.forEach(r => {
        if (r.value === 'No' && !r.checked) r.click();
    });

    // Nationality: Other
    setSelect('cards[4a195304-5d5b-4786-8b23-12b43b3e6c15][field0]', 'Other');

    // Currently Live in Saudi Arabia: Yes
    setSelect('cards[4a195304-5d5b-4786-8b23-12b43b3e6c15][field1]', 'Yes');

    // Decision checkboxes
    var decCbs = Array.from(document.querySelectorAll('input[name="cards[0cafb958-2e8f-4cdc-9636-db361c5e4e66][field0]"]'));
    decCbs.forEach(cb => {
        if (cb.value.includes('Reputation') || cb.value.includes('Specific platform') || cb.value.includes('Company culture')) {
            if (!cb.checked) cb.click();
        }
    });

    // Where did you find: LinkedIn
    setSelect('cards[0cafb958-2e8f-4cdc-9636-db361c5e4e66][field2]', 'LinkedIn');

    return {
        name: document.querySelector('input[name="name"]')?.value,
        email: document.querySelector('input[name="email"]')?.value,
        phone: document.querySelector('input[name="phone"]')?.value,
        salary: document.querySelector('input[name="cards[09f9307b-f0d7-4c87-a318-dc79310f9689][field0]"]')?.value,
        liveInKsa: document.querySelector('select[name="cards[4a195304-5d5b-4786-8b23-12b43b3e6c15][field1]"]')?.value
    };
})()
'''

out, err = run_js(fill_script)
print("Fill result:", out)
if err: print("Error:", err)
