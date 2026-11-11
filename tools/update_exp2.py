import subprocess
import base64
import json
import time

def run_js(tab, js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    cmd = f"""tell application "Google Chrome" to tell tab {tab} of window 1 to execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))" """
    res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
    return res.stdout.strip()

def update_exp(btn_id, data):
    # Click edit button
    click_js = f"""
    (() => {{
        const btn = document.querySelector('button[data-edit-url*="{btn_id}"]');
        if (btn) {{
            btn.click();
            return "Clicked";
        }}
        return "Not found";
    }})()
    """
    print(f"Opening modal for {btn_id}:", run_js(8, click_js))
    time.sleep(1.2)
    
    fill_and_submit_js = f"""
    (() => {{
        const form = document.querySelector('#editModalContent form');
        if (!form) return "No form";
        
        const title = document.getElementById("UserExperienceJobTitle");
        if (title) title.value = "{data['title']}";
        
        const comp = document.getElementById("UserExperienceComapnyName");
        if (comp) comp.value = "{data['company']}";
        
        const loc = document.getElementById("UserExperienceCompanyLocation");
        if (loc) loc.value = "{data['location']}";
        
        const fm = document.getElementById("UserExperienceFromDateMonth");
        if (fm) fm.value = "{data['from_month']}";
        
        const fy = document.getElementById("UserExperienceFromDateYear");
        if (fy) fy.value = "{data['from_year']}";
        
        const tm = document.getElementById("UserExperienceToDateMonth");
        if (tm) tm.value = "{data['to_month']}";
        
        const ty = document.getElementById("UserExperienceToDateYear");
        if (ty) ty.value = "{data['to_year']}";
        
        const chk = document.getElementById("UserExperienceToPresent");
        if (chk) chk.checked = {str(data.get('to_present', False)).lower()};
        
        const desc = document.getElementById("UserExperienceDescription");
        if (desc) desc.value = `{data['desc']}`;
        
        // Use fetch to POST form
        const fd = new FormData(form);
        // ensure to_present is properly passed
        if ({str(data.get('to_present', False)).lower()}) {{
            fd.set("data[UserExperience][to_present]", "1");
        }} else {{
            fd.delete("data[UserExperience][to_present]");
        }}
        
        fetch(form.action, {{
            method: "POST",
            body: fd
        }}).then(() => {{
            window.location.reload();
        }});
        return "Fetch submitted";
    }})()
    """
    res = run_js(8, fill_and_submit_js)
    print(f"Submitted {btn_id}:", res)
    time.sleep(2.5)

# 2. RAKETBE: Aug 2025 to Jan 2026
raketbe = {
    "title": "Digital Marketing & Performance Manager",
    "company": "RAKETBE Agency",
    "location": "الرياض، المملكة العربية السعودية",
    "from_month": "08",
    "from_year": "2025",
    "to_month": "01",
    "to_year": "2026",
    "to_present": False,
    "desc": "Managed high-scale performance marketing budgets across Snapchat, Meta, TikTok, and Google Ads, consistently achieving ROAS from 5x up to 25x."
}

update_exp("2838678", raketbe)

