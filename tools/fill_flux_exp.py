#!/usr/bin/env python3
import subprocess
import base64

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
    
    // Job Title
    log.push(setVal('experienceForm_jobTitle', 'Marketing Director'));
    
    // Company
    log.push(setVal('experienceForm_company', 'FLUX Ads'));
    
    // Job Role: 11
    const jr = document.getElementById('experienceForm_jobRole');
    if (jr) {
        jr.value = '11';
        jr.dispatchEvent(new Event('change', {bubbles: true}));
        const jrr = document.getElementById('experienceForm_jobRole__r');
        if (jrr) jrr.value = 'التسويق والعلاقات العامة';
        log.push('set jobRole 11');
    }
    
    // Country: sa
    const co = document.getElementById('experienceForm_country');
    if (co) {
        co.value = 'sa';
        co.dispatchEvent(new Event('change', {bubbles: true}));
        const cor = document.getElementById('experienceForm_country__r');
        if (cor) cor.value = 'المملكة العربية السعودية';
        log.push('set country sa');
    }
    
    // City: Riyadh (sa,5,0)
    const ci = document.getElementById('experienceForm_city');
    if (ci) {
        let opt = Array.from(ci.options).find(o => o.value === 'sa,5,0');
        if (!opt) {
            opt = new Option('الرياض', 'sa,5,0', true, true);
            ci.add(opt);
        }
        ci.value = 'sa,5,0';
        ci.dispatchEvent(new Event('change', {bubbles: true}));
        const cir = document.getElementById('experienceForm_city__r');
        if (cir) cir.value = 'الرياض';
        log.push('set city Riyadh');
    }
    
    // Start Date: 12 / 2025
    const sm = document.getElementById('experienceForm_startMonth');
    if (sm) {
        sm.value = '12';
        sm.dispatchEvent(new Event('change', {bubbles: true}));
        const smr = document.getElementById('experienceForm_startMonth__r');
        if (smr) smr.value = 'ديسمبر';
        log.push('set startMonth 12');
    }
    
    const sy = document.getElementById('experienceForm_startYear');
    if (sy) {
        sy.value = '2025';
        sy.dispatchEvent(new Event('change', {bubbles: true}));
        const syr = document.getElementById('experienceForm_startYear__r');
        if (syr) syr.value = '2025';
        log.push('set startYear 2025');
    }
    
    // Currently work here: CHECK
    const curr = document.getElementById('experienceForm_currentlyWorkHere');
    if (curr) {
        curr.checked = true;
        curr.value = '1';
        curr.dispatchEvent(new Event('change', {bubbles: true}));
        log.push('set currentlyWorkHere');
    }
    
    // Company Industry: 55 (التسويق)
    const ind = document.getElementById('experienceForm_companyInd');
    if (ind) {
        ind.value = '55';
        ind.dispatchEvent(new Event('change', {bubbles: true}));
        const indr = document.getElementById('experienceForm_companyInd__r');
        if (indr) indr.value = 'التسويق';
        log.push('set companyInd 55');
    }
    
    // Company Size: 2 (10-49)
    const cs = document.getElementById('experienceForm_companySize');
    if (cs) {
        cs.value = '2';
        cs.dispatchEvent(new Event('change', {bubbles: true}));
        const csr = document.getElementById('experienceForm_companySize__r');
        if (csr) csr.value = '10-49 موظف';
        log.push('set companySize 2');
    }
    
    // Work Mode: 0 (onsite) or 2 (hybrid)
    const wm = document.getElementById('experienceForm_workMode_0');
    if (wm) wm.checked = true;
    
    // Work Desc
    const desc = document.getElementById('experienceForm_workDesc');
    if (desc) {
        desc.value = `قيادة الاستراتيجية التسويقية الشاملة وإدارة ميزانيات الحملات الإعلانية المدفوعة على منصات Meta, Google Ads, TikTok, Snapchat للعملاء التجاريين في المملكة العربية السعودية.
تحقيق عوائد إنفاق إعلاني (ROAS) تراوحت بين 4x و 25x مع التركيز على نمو المبيعات (E-Commerce Growth) وتوليد العملاء المحتملين (Performance Lead Gen).
إدارة فرق العمل الإبداعية، وصناعة المحتوى، وإطلاق حملات الفيديو التسويقية مع تتبع وتحليل الأداء والـ KPIs باستخدام أدوات Google Analytics 4 و Hotjar ومنصات إدارة الإعلانات.`;
        desc.dispatchEvent(new Event('input', {bubbles: true}));
        desc.dispatchEvent(new Event('change', {bubbles: true}));
        log.push('set workDesc');
    }

    return log.join(', ');
})()
"""

print(run_js(script))

