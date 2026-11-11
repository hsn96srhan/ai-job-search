#!/usr/bin/env python3
import subprocess
import base64
import time

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

def update_role(btn_id, title_val, comp_val, start_m, start_y, end_m, end_y, start_m_ar, end_m_ar):
    print(f"=== Updating {btn_id} ({title_val}) ===")
    run_js(f"document.getElementById('{btn_id}').click()")
    time.sleep(1.5)
    
    js = f"""
    (() => {{
        const title = document.getElementById("experienceForm_jobTitle");
        if (title) {{
            title.value = "{title_val}";
            title.dispatchEvent(new Event("input", {{bubbles: true}}));
        }}
        if ("{comp_val}") {{
            const comp = document.getElementById("experienceForm_company");
            if (comp) {{
                comp.value = "{comp_val}";
                comp.dispatchEvent(new Event("input", {{bubbles: true}}));
            }}
        }}
        const curr = document.getElementById("experienceForm_currentlyWorkHere");
        if (curr) curr.checked = false;
        
        const sm = document.getElementById("experienceForm_startMonth");
        if (sm) {{
            sm.value = "{start_m}";
            sm.dispatchEvent(new Event("change", {{bubbles: true}}));
            const smr = document.getElementById("experienceForm_startMonth__r");
            if (smr) smr.value = "{start_m_ar}";
        }}
        const sy = document.getElementById("experienceForm_startYear");
        if (sy) {{
            sy.value = "{start_y}";
            sy.dispatchEvent(new Event("change", {{bubbles: true}}));
            const syr = document.getElementById("experienceForm_startYear__r");
            if (syr) syr.value = "{start_y}";
        }}
        const em = document.getElementById("experienceForm_endMonth");
        if (em) {{
            em.value = "{end_m}";
            em.dispatchEvent(new Event("change", {{bubbles: true}}));
            const emr = document.getElementById("experienceForm_endMonth__r");
            if (emr) emr.value = "{end_m_ar}";
        }}
        const ey = document.getElementById("experienceForm_endYear");
        if (ey) {{
            ey.value = "{end_y}";
            ey.dispatchEvent(new Event("change", {{bubbles: true}}));
            const eyr = document.getElementById("experienceForm_endYear__r");
            if (eyr) eyr.value = "{end_y}";
        }}
        const wm = document.getElementById("experienceForm_workMode_0");
        if (wm) {{ wm.click(); wm.checked = true; }}
        
        const cs = document.getElementById("experienceForm_companySize");
        if (cs && !cs.value) {{
            cs.value = "2";
            cs.dispatchEvent(new Event("change", {{bubbles: true}}));
        }}
        return "set";
    }})()
    """
    res = run_js(js)
    print("Set fields:", res)
    time.sleep(1)
    
    save_res = run_js("(() => { const b = document.getElementById('submitCVForm'); if(b){b.click(); return 'saved';} return 'no btn'; })()")
    print("Save result:", save_res)
    time.sleep(2)

# Fantazzia: February 2022 to March 2025
update_role('exp-128584674', 'Digital Commerce Manager', 'FANTAZZIA BED', '02', '2022', '03', '2025', 'فبراير', 'مارس')

# VLEX: January 2021 to December 2021
update_role('exp-128584675', 'Co-Founder & Marketing Director', 'VLEX (Flex Shipping)', '01', '2021', '12', '2021', 'يناير', 'ديسمبر')

