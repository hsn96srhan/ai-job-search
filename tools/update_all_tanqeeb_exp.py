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
    print(f"Updating experience {btn_id} ({data['company']})...")
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
    run_js(8, click_js)
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
        
        const fd = new FormData(form);
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
    print(f"Result for {btn_id}:", res)
    time.sleep(2.5)

experiences = [
    {
        "id": "2838679",
        "data": {
            "title": "Marketing Director",
            "company": "Arabeva Group",
            "location": "الرياض، المملكة العربية السعودية",
            "from_month": "03",
            "from_year": "2025",
            "to_month": "08",
            "to_year": "2025",
            "to_present": False,
            "desc": "Led marketing and digital performance for 3 global perfume and beauty brands across the GCC, Europe, and the United States."
        }
    },
    {
        "id": "2838680",
        "data": {
            "title": "Digital Commerce Manager",
            "company": "Fantazzia Bed",
            "location": "الرياض، المملكة العربية السعودية",
            "from_month": "02",
            "from_year": "2022",
            "to_month": "03",
            "to_year": "2025",
            "to_present": False,
            "desc": "Built the company’s direct-to-consumer (D2C) e-commerce infrastructure, digital marketing, and inside sales operations from the ground up."
        }
    },
    {
        "id": "2838681",
        "data": {
            "title": "Co-Founder & Marketing Director",
            "company": "VLEX Logistics",
            "location": "القاهرة، مصر",
            "from_month": "01",
            "from_year": "2021",
            "to_month": "12",
            "to_year": "2021",
            "to_present": False,
            "desc": "Co-founded and steered the marketing division for a B2B logistics company dedicated to e-commerce fulfillment and last-mile delivery."
        }
    },
    {
        "id": "2838682",
        "data": {
            "title": "Social Media & Content Specialist",
            "company": "Medica Healthy",
            "location": "القاهرة، مصر",
            "from_month": "07",
            "from_year": "2018",
            "to_month": "12",
            "to_year": "2020",
            "to_present": False,
            "desc": "Executed the go-to-market launch strategy for an integrated healthcare mobile application."
        }
    }
]

for exp in experiences:
    update_exp(exp["id"], exp["data"])

print("All experiences updated successfully.")

