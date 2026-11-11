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
    function setVal(id, val) {
        const el = document.getElementById(id);
        if (!el) return "not found: " + id;
        el.value = val;
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        return "set " + id;
    }

    const log = [];
    
    // First / Last Name in Arabic and English
    log.push(setVal('personalInformationForm_firstNameAr', 'حسن'));
    log.push(setVal('personalInformationForm_lastNameAr', 'سرحان'));
    log.push(setVal('personalInformationForm_firstNameLa', 'Hassan'));
    log.push(setVal('personalInformationForm_lastNameLa', 'Sarhan'));
    
    // City: Riyadh (sa,5,0)
    const city = document.getElementById('personalInformationForm_resCity');
    if (city) {
        city.value = 'sa,5,0';
        city.dispatchEvent(new Event('change', {bubbles: true}));
        const cityR = document.getElementById('personalInformationForm_resCity__r');
        if (cityR) cityR.value = 'الرياض';
        log.push('set city Riyadh');
    }
    
    // Visa status: 2 (تأشيرة إقامة (قابلة للتحويل))
    const visa = document.getElementById('personalInformationForm_visaStatus');
    if (visa) {
        visa.value = '2';
        visa.dispatchEvent(new Event('change', {bubbles: true}));
        const visaR = document.getElementById('personalInformationForm_visaStatus__r');
        if (visaR) visaR.value = 'تأشيرة إقامة (قابلة للتحويل)';
        log.push('set visa status 2');
    }
    
    // Driving License Country: sa
    const dl = document.getElementById('personalInformationForm_drivingLicenseCounties');
    if (dl) {
        // select option 'sa'
        Array.from(dl.options).forEach(opt => {
            if (opt.value === 'sa') opt.selected = true;
        });
        dl.dispatchEvent(new Event('change', {bubbles: true}));
        
        // Also check if there is a hidden or helper input
        const dlR = document.getElementById('personalInformationForm_drivingLicenseCounties__r');
        if (dlR) dlR.value = 'المملكة العربية السعودية';
        
        // Find matching checkbox in the searchable list
        const cbs = Array.from(document.querySelectorAll("input[id^='personalInformationForm_drivingLicenseCounties_scb_']"));
        cbs.forEach(cb => {
            const label = cb.closest('li, label, div');
            if (label && label.innerText.includes('السعودية')) {
                cb.checked = true;
                cb.dispatchEvent(new Event('change', {bubbles: true}));
            }
        });
        log.push('set driving license sa');
    }

    return log.join(', ');
})()
"""

print(run_js(script))

