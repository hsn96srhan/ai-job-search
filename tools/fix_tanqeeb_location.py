import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

update_script = """
(() => {
    // 1. Full name
    const fn = document.getElementById("UserFullName");
    if (fn) {
        fn.value = "حسن سرحان";
        fn.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // 2. Job title
    const jt = document.getElementById("UserJobTitle");
    if (jt) {
        jt.value = "مدير تسويق (Marketing Director)";
        jt.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // 3. Summary
    const sum = document.getElementById("UserSummary");
    if (sum) {
        sum.value = "مدير تسويق معتمد من وزارة الموارد البشرية والتنمية الاجتماعية (HRSD) بخبرة تزيد عن 8 سنوات في قيادة استراتيجيات النمو والتسويق الرقمي والأداء للشركات الكبرى والعلامات التجارية في الرياض والمملكة العربية السعودية، وإدارة ميزانيات إعلانية مليونية وتحقيق عوائد استثمار قياسية (ROAS يصل إلى 25x). إقامة عمل نظامية سارية قابلة للتحويل الفوري في الرياض ورخصة قيادة سعودية سارية.";
        sum.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // 4. Country -> 54 (السعودية)
    const cid = document.getElementById("UserCountryId");
    if (cid) {
        cid.value = "54";
        cid.dispatchEvent(new Event("change", {bubbles: true}));
        if (window.$) $(cid).trigger("change");
    }
    
    // 5. State -> 6 (الرياض)
    const sid = document.getElementById("UserStateId");
    if (sid) {
        sid.value = "6";
        sid.dispatchEvent(new Event("change", {bubbles: true}));
        if (window.$) $(sid).trigger("change");
    }
    
    // 6. District -> 249 (الرياض)
    const did = document.getElementById("UserDistrictId");
    if (did) {
        did.value = "249";
        did.dispatchEvent(new Event("change", {bubbles: true}));
        if (window.$) $(did).trigger("change");
    }
    
    // 7. City
    const city = document.getElementById("UserCity");
    if (city) {
        city.value = "الرياض";
        city.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    // 8. Nationality -> 213 (مصر)
    const nat = document.getElementById("UserNationalityId");
    if (nat) {
        nat.value = "213";
        nat.dispatchEvent(new Event("change", {bubbles: true}));
        if (window.$) $(nat).trigger("change");
    }
    
    // 9. Gender male
    const gm = document.getElementById("gender_only_male");
    if (gm) gm.checked = true;
    
    // 10. Min Salary & Currency
    const sal = document.getElementById("UserMinSalary");
    if (sal) sal.value = "10000";
    const cur = document.getElementById("UserCurrencyCode");
    if (cur) cur.value = "SAR";
    
    // 11. Experience years
    const exp = document.getElementById("UserExperienceYears");
    if (exp) exp.value = "8";
    
    return "All fields populated";
})()
"""

print(run_js(8, update_script))
time.sleep(1)

# Now click حفظ
submit_script = """
(() => {
    const btn = Array.from(document.querySelectorAll('button[type=submit]')).find(b => b.innerText.trim() === 'حفظ');
    if (btn) {
        btn.click();
        return "Clicked save";
    }
    return "Save button not found";
})()
"""

print(run_js(8, submit_script))
time.sleep(3)

# Verify
verify_script = """
(() => {
    const cid = document.getElementById("UserCountryId");
    const sid = document.getElementById("UserStateId");
    const city = document.getElementById("UserCity");
    return JSON.stringify({
        url: window.location.href,
        country: cid ? cid.options[cid.selectedIndex]?.text : null,
        state: sid ? sid.options[sid.selectedIndex]?.text : null,
        city: city ? city.value : null
    });
})()
"""
print("Verification:", run_js(8, verify_script))

