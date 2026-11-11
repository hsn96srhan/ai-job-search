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
    function setSelectValue(selectId, value, text) {
        const sel = document.getElementById(selectId);
        if (!sel) return "select not found: " + selectId;
        sel.value = value;
        sel.dispatchEvent(new Event('change', {bubbles: true}));
        sel.dispatchEvent(new Event('input', {bubbles: true}));
        
        // Also check if there is an input like selectId + '__r'
        const fakeInput = document.getElementById(selectId + '__r') || document.querySelector(`input[name="${sel.name}__v"]`);
        if (fakeInput && text) {
            fakeInput.value = text;
            fakeInput.dispatchEvent(new Event('change', {bubbles: true}));
        }
        
        // Trigger select2 or custom droope if attached
        if (window.jQuery && jQuery(sel).data('select2')) {
            jQuery(sel).val(value).trigger('change');
        }
        return "set " + selectId;
    }

    const log = [];
    // Career Level: 3 (إدارة)
    log.push(setSelectValue('targetJobForm_careerLevel', '3', 'إدارة'));
    
    // Target Job Role: 11 (التسويق والعلاقات العامة)
    log.push(setSelectValue('targetJobForm_targetJobRole', '11', 'التسويق والعلاقات العامة'));
    
    // Visa Status: 2 (تأشيرة إقامة (قابلة للتحويل))
    log.push(setSelectValue('targetJobForm_visaStatus', '2', 'تأشيرة إقامة (قابلة للتحويل)'));
    
    // Notice Period: 1 (فوراً)
    log.push(setSelectValue('targetJobForm_noticePeriod', '1', 'فوراً'));
    
    // Salary Currency: 92 (SAR)
    log.push(setSelectValue('targetJobForm_trgtJobSalaryCurrency', '92', 'SAR'));
    
    // Target Salary: 10000
    const sal = document.getElementById('targetJobForm_trgtJobSalaryValue');
    if (sal) {
        sal.value = '10000';
        sal.dispatchEvent(new Event('input', {bubbles: true}));
        sal.dispatchEvent(new Event('change', {bubbles: true}));
        log.push('set salary');
    }
    
    // Objectives
    const obj = document.getElementById('targetJobForm_objectives');
    if (obj) {
        obj.value = 'مدير تسويق معتمد من وزارة الموارد البشرية والتنمية الاجتماعية بخبرة تفوق 8 سنوات في قيادة استراتيجيات النمو والتسويق الرقمي والأداء (Performance Marketing) والتجارة الإلكترونية في السوق السعودي ودول الخليج. أسعى لقيادة وتطوير المنظومات التسويقية وتحقيق أعلى عائد استثماري للعلامات التجارية الرائدة بالمملكة.';
        obj.dispatchEvent(new Event('input', {bubbles: true}));
        obj.dispatchEvent(new Event('change', {bubbles: true}));
        log.push('set objectives');
    }
    
    // Employment types (e.g. check full-time)
    document.querySelectorAll("input[id^='targetJobForm_employmentType_']").forEach(cb => {
        if (cb.value === "1") cb.checked = true; // full time
    });
    
    // Work mode: onsite, remote, hybrid
    document.querySelectorAll("input[id^='targetJobForm_workMode_']").forEach(cb => {
        cb.checked = true;
    });

    return log.join(', ');
})()
"""

print(run_js(script))

