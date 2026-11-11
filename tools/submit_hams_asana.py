#!/usr/bin/env python3
"""Submit HAMS.AI application on Asana form directly inside Google Chrome."""

import subprocess
import time
import base64
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = REPO_ROOT / "cv/marketing-director-hsn.pdf"
b64_pdf = base64.b64encode(PDF_PATH.read_bytes()).decode('ascii')

js_body = f"""
(function() {{
    try {{
        function setVal(el, val) {{
            if (!el) return false;
            var proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
            var setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }}

        // Helper to find input by question label text
        function fillByLabel(labelText, val) {{
            var allLabels = Array.from(document.querySelectorAll('label, .formStructureView-fieldTitle, [class*="fieldTitle"]'));
            var target = allLabels.find(l => l.innerText.toLowerCase().includes(labelText.toLowerCase()));
            if (target) {{
                var card = target.closest('.formStructureView-field, [class*="field"], .WorkRequestsField') || target.parentElement;
                if (card) {{
                    var inp = card.querySelector('input[type="text"], input:not([type]), textarea');
                    if (inp) {{
                        setVal(inp, val);
                        return true;
                    }}
                }}
            }}
            return false;
        }}

        // 1. Text Inputs
        fillByLabel('Full Name', 'Hassan Sarhan');
        fillByLabel('Nationality', 'Egyptian (Transferable Iqama in Riyadh)');
        fillByLabel('Email address', 'hsn96srhan@gmail.com');
        fillByLabel('LinkedIn URL', 'https://www.linkedin.com/in/srhan-jr/');
        fillByLabel('Contact Number', '+966506267542');
        fillByLabel('University name', 'Akhbar El Yom Academy, Cairo');
        fillByLabel('Major', 'Journalism & Media Communications');
        fillByLabel('GPA', '3.2');
        fillByLabel('How many years of experience', '8');

        // 2. Custom Essay Questions
        fillByLabel('most successful marketing campaign', 'Directed an omnichannel performance campaign with 7M+ SAR budget across Snapchat, Meta, TikTok, and Google Ads. Engineered segmented funnels and optimized conversion tracking, achieving up to 25x audited ROAS and scaling monthly revenue to 10M.');
        fillByLabel('developed a marketing strategy or quarterly', 'Yes, across 30+ enterprise clients at FLUX Ads. I begin by analyzing unit economics and customer cohorts, defining OKRs and target CPA/CAC, allocating budget across top-of-funnel brand building and bottom-of-funnel acquisition, and establishing automated weekly dashboard reviews.');
        fillByLabel('campaign that didn\\'t perform as expected', 'Identified a drop in conversion rate during a perfume e-commerce blitz due to high checkout friction and generic creative fatigue. Analyzed Hotjar and post-click drop-offs, restructured the landing page with 1-click checkout, and switched to localized UGC video angles, reducing CPA by 32%.');
        fillByLabel('experience do you have with SEO', 'Built localized GCC e-commerce stores with technical SEO, schema markup, and speed optimizations. Structured keyword clusters around high-intent commercial queries, increasing organic inbound traffic by 45% and reducing paid dependency.');
        fillByLabel('B2B technology company with multiple products', 'Prioritize the product with the highest gross margin and fastest sales cycle (lowest CAC/LTV ratio). Focus budget on high-intent inbound search (Google Ads) and targeted account-based LinkedIn outbound, while creating case studies to establish domain credibility.');
        fillByLabel('marketing metrics do you monitor most closely', 'ROAS, blended CAC, LTV, and conversion rate. In a campaign where ROAS looked acceptable at 4x but CAC was creeping up due to audience saturation, I reallocated 40% of the budget to retargeting segmented CRM lookalikes, restoring ROAS to 8x+ and saving 150k SAR in ad spend.');
        fillByLabel('Duplicate of Duplicate of', 'Focus on the flagship MVP that solves the clearest enterprise pain point. Deploy 60% of budget on high-intent search and LinkedIn ABM, 20% on product marketing content, and 20% on remarketing.');
        fillByLabel('managed external marketing agencies', 'Led and supervised 4 internal divisions and multiple external creative studios. Implemented strict creative briefs with clear KPIs, brand guidelines, and 48-hour SLA review cycles to guarantee brand consistency and high ROAS.');
        fillByLabel('improvement you made on a process', 'Automated lead capture, qualification, and WhatsApp follow-up workflows via CRM integration, cutting lead response time by 60% and lifting abandoned-cart recovery by 28%.');
        fillByLabel('What do you know about Hams.AI', 'Hams.AI (همس) is a pioneering Saudi AI enterprise providing cutting-edge generative AI, conversational intelligence, and localized enterprise technology tailored for the Saudi and GCC market aligned with Vision 2030.');
        fillByLabel('What motivates you to join Hams.AI', 'As an HRSD-accredited Marketing Director in Riyadh with 8+ years scaling high-performance growth, joining Hams.AI allows me to leverage my proven performance marketing, brand scaling, and GTM expertise to accelerate AI adoption across Saudi enterprise and consumer sectors.');
        fillByLabel('Why should we choose you', 'HRSD-accredited Marketing Director in Riyadh with Transferable Iqama, Saudi Driving License, and immediate availability. Proven track record managing 7M+ SAR in ad spend, delivering up to 25x ROAS, scaling revenue to 10M/month, and leading 20+ cross-functional specialists.');
        fillByLabel('professional certificates', 'Yes, Accredited Marketing Manager by Ministry of Human Resources and Social Development (HRSD, Saudi Arabia).');

        // 3. Checkboxes
        var cbs = Array.from(document.querySelectorAll('input[type="checkbox"]'));
        cbs.forEach(cb => {{
            var p = cb.parentElement;
            while (p && p.innerText.trim().length < 3) p = p.parentElement;
            var txt = (p ? p.innerText : '').toLowerCase();
            if (txt.includes('ai solutions') || txt.includes('saas') || txt.includes('agency') || txt.includes('b2c') || txt.includes('e-commerce')) {{
                if (!cb.checked) cb.click();
            }}
        }});

        // 4. File uploads via DataTransfer
        var b64Data = "{b64_pdf}";
        var byteCharacters = atob(b64Data);
        var byteArrays = [];
        for (var offset = 0; offset < byteCharacters.length; offset += 512) {{
            var slice = byteCharacters.slice(offset, offset + 512);
            var byteNumbers = new Array(slice.length);
            for (var i = 0; i < slice.length; i++) {{
                byteNumbers[i] = slice.charCodeAt(i);
            }}
            byteArrays.push(new Uint8Array(byteNumbers));
        }}
        var blob = new Blob(byteArrays, {{ type: "application/pdf" }});
        var file1 = new File([blob], "marketing-director-hsn.pdf", {{ type: "application/pdf", lastModified: Date.now() }});
        var file2 = new File([blob], "marketing-director-hsn.pdf", {{ type: "application/pdf", lastModified: Date.now() }});

        var fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
        fileInputs.forEach((fi, idx) => {{
            var dt = new DataTransfer();
            dt.items.add(idx === 0 ? file1 : file2);
            fi.files = dt.files;
            fi.dispatchEvent(new Event('input', {{ bubbles: true }}));
            fi.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }});

        return {{
            filesAttached: fileInputs.map(f => f.files[0] ? f.files[0].name : 'none')
        }};
    }} catch(e) {{
        return {{ error: e.message }};
    }}
}})()
"""

Path('/tmp/hams_fill.js').write_text(js_body, encoding='utf-8')

as_content = """set jsCode to read POSIX file "/tmp/hams_fill.js" as «class utf8»
tell application "Google Chrome"
    tell active tab of front window
        execute javascript jsCode
    end tell
end tell"""

Path('/tmp/run_hams.applescript').write_text(as_content, encoding='utf-8')
res = subprocess.run(["osascript", "/tmp/run_hams.applescript"], capture_output=True, text=True)
print("Fill output:", res.stdout.strip())
if res.stderr.strip(): print("Fill error:", res.stderr.strip())

