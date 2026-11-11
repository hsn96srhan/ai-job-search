import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

fix_script = """
(() => {
    const log = [];
    
    // 1. Fix career level to "إدارة" (val=3)
    const careerSel = document.getElementById('targetJobForm_careerLevel');
    if (careerSel) {
        careerSel.value = '3';
        careerSel.dispatchEvent(new Event('change', {bubbles: true}));
        log.push('career level set to 3 (إدارة)');
    }
    // Update display text
    const careerDisp = document.getElementById('targetJobForm_careerLevel__r');
    if (careerDisp) {
        careerDisp.value = 'إدارة';
        careerDisp.dispatchEvent(new Event('change', {bubbles: true}));
        log.push('career level display set');
    }
    // The __v input
    const careerV = document.querySelector('[name="targetJobForm[careerLevel]__v"]');
    if (careerV) {
        careerV.value = 'إدارة';
        careerV.dispatchEvent(new Event('change', {bubbles: true}));
        log.push('career level __v set');
    }
    
    // 2. Set positionSought field (the target job title)
    const pos = document.getElementById('targetJobForm_positionSought__r');
    if (pos) {
        pos.value = 'مدير تسويق (Marketing Director)';
        pos.dispatchEvent(new Event('input', {bubbles: true}));
        pos.dispatchEvent(new Event('change', {bubbles: true}));
        log.push('positionSought set');
    }
    // Find hidden input for positionSought
    const posByName = document.querySelector('[name="targetJobForm[positionSought]"]');
    if (posByName) {
        posByName.value = 'مدير تسويق (Marketing Director)';
        log.push('positionSought hidden set');
    }
    
    // 3. Make sure employment type "دوام كامل" is checked
    const empFull = document.getElementById('targetJobForm_employmentType_0');
    if (empFull) {
        empFull.checked = true;
        log.push('full time checked');
    }
    
    // 4. Make sure workMode "في مقر العمل" is checked
    const workOnsite = document.getElementById('targetJobForm_workMode_0');
    if (workOnsite) {
        workOnsite.checked = true;
        log.push('onsite checked');
    }
    
    return log.join(', ');
})()
"""

print("Fix result:", run_js(2, fix_script))
time.sleep(0.5)

# Now find and click submit
submit_script = """
(() => {
    // Find the form submit button within the visible modal/form
    const form = document.querySelector('[id*="targetJob"]')?.closest('form') || document.querySelector('form[name*="targetJob"]');
    
    // Try finding submit button near the target job form
    const allSubmits = Array.from(document.querySelectorAll('button[type=submit], input[type=submit]'));
    const visibleSubmits = allSubmits.filter(el => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
    });
    
    if (visibleSubmits.length > 0) {
        // Click the last visible submit (the main form submit)
        const btn = visibleSubmits[visibleSubmits.length - 1];
        btn.click();
        return 'Clicked submit: ' + btn.id + ' ' + btn.className;
    }
    
    // Try finding the save button
    const saveBtn = Array.from(document.querySelectorAll('button, a')).find(b => 
        b.innerText.trim() === 'حفظ' || b.innerText.trim() === 'Save' || b.innerText.trim() === 'تحديث'
    );
    if (saveBtn) {
        saveBtn.click();
        return 'Clicked save button';
    }
    
    return 'No submit found. Forms: ' + document.querySelectorAll('form').length;
})()
"""

print("Submit result:", run_js(2, submit_script))
time.sleep(2.5)

# Verify
verify = """
(() => {
    return document.body.innerText.match(/مبتدئ|إدارة عليا|إدارة\s/)?.[0] || 'Not found';
})()
"""
print("Career level in page:", run_js(2, verify))
