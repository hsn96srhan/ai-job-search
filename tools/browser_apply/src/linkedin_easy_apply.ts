import type { Page } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";

/**
 * Automates the LinkedIn Easy Apply multi-step modal submission.
 */
export async function submitLinkedInEasyApply(page: Page, jobUrl: string): Promise<boolean> {
  console.log(`\n⚡ بدء محاولة التقديم الآلي (LinkedIn Easy Apply) على: ${jobUrl}`);

  const cvPath = path.resolve(process.cwd(), "cv/marketing-director-hsn.pdf");
  if (!fs.existsSync(cvPath)) {
    console.error(`❌ لم يتم العثور على ملف السيرة الذاتية في ${cvPath}`);
    return false;
  }

  try {
    // 1. Find and click Easy Apply button
    const easyApplySelectors = [
      'button.jobs-apply-button',
      'button:has-text("Easy Apply")',
      'button:has-text("التقديم السريع")',
      'button:has-text("التقديم بسهولة")',
      'button[aria-label*="Easy Apply"]',
      'button[aria-label*="التقديم السريع"]',
    ];

    let clickedEasyApply = false;
    for (const sel of easyApplySelectors) {
      const btn = await page.$(sel);
      if (btn && (await btn.isVisible().catch(() => false))) {
        console.log(`👉 تم النقر على زر التقديم السريع (Easy Apply)...`);
        await btn.click().catch(() => {});
        clickedEasyApply = true;
        await page.waitForTimeout(2500);
        break;
      }
    }

    if (!clickedEasyApply) {
      console.log(`ℹ️ لم يتم العثور على زر Easy Apply مباشر، قد يتطلب تسجيل الدخول أولاً.`);
      return false;
    }

    // Check if the modal opened
    const modalSelector = 'div[role="dialog"], .jobs-easy-apply-modal';
    const modal = await page.$(modalSelector);
    if (!modal) {
      console.log(`⚠️ لم يفتح نموذج Easy Apply.`);
      return false;
    }

    let step = 1;
    const maxSteps = 10;
    let submitted = false;

    while (step <= maxSteps) {
      console.log(`   [خطوة التقديم ${step}]: تعبئة بيانات النموذج...`);
      await page.waitForTimeout(1500);

      // 1. Fill Phone if empty
      const phoneInput = await page.$('input[id*="phoneNumber"], input[id*="phone-number"], input[name*="phone"]');
      if (phoneInput) {
        const val = await phoneInput.inputValue().catch(() => "");
        if (!val || val.length < 5) {
          await phoneInput.fill(candidateProfile.phone);
          console.log(`   ✓ تم إدخال رقم الجوال: ${candidateProfile.phone}`);
        }
      }

      // 2. Upload CV if required
      const fileInputs = await page.$$('input[type="file"]');
      for (const fi of fileInputs) {
        if (await fi.isVisible().catch(() => false) || true) {
          try {
            await fi.setInputFiles(cvPath);
            console.log(`   ✓ تم إرفاق السيرة الذاتية: marketing-director-hsn.pdf`);
          } catch {}
        }
      }

      // 3. Answer Common Questions (Radios, Selects, Inputs)
      await answerLinkedInQuestions(page);

      // Strict User Rule: Uncheck any "Follow Company" checkbox before submitting
      const checkboxes = await page.$$('input[type="checkbox"]');
      for (const cb of checkboxes) {
        try {
          const isChecked = await cb.isChecked();
          if (isChecked) {
            const parentText = (await cb.evaluate((el: any) => el.parentElement?.innerText || '')).toLowerCase();
            const labelText = (await cb.evaluate((el: any) => el.labels?.[0]?.innerText || '')).toLowerCase();
            const id = ((await cb.getAttribute('id')) || '').toLowerCase();
            const name = ((await cb.getAttribute('name')) || '').toLowerCase();
            const fullDesc = `${parentText} ${labelText} ${id} ${name}`;
            if (fullDesc.includes('follow') || fullDesc.includes('متابعة') || fullDesc.includes('stay up to date')) {
              console.log('🛡️ تم إلغاء تفعيل خيار متابعة الشركة التلقائي (Unchecked Follow Company) وفقاً لتعليماتك الصارمة.');
              await cb.uncheck();
            }
          }
        } catch {}
      }

      // 4. Check for Submit button
      const submitBtn = await page.$(
        'button:has-text("Submit application"), button:has-text("إرسال الطلب"), button[aria-label="Submit application"], button[aria-label="إرسال الطلب"]'
      );
      if (submitBtn && (await submitBtn.isVisible().catch(() => false))) {
        console.log(`🚀 النقر على زر إرسال الطلب النهائي (Submit Application)...`);
        await submitBtn.click();
        await page.waitForTimeout(4000);
        submitted = true;
        break;
      }

      // 5. Check for Review button
      const reviewBtn = await page.$(
        'button:has-text("Review"), button:has-text("مراجعة"), button[aria-label="Review your application"]'
      );
      if (reviewBtn && (await reviewBtn.isVisible().catch(() => false))) {
        console.log(`   👉 النقر على زر المراجعة (Review)...`);
        await reviewBtn.click();
        await page.waitForTimeout(2000);
        step++;
        continue;
      }

      // 6. Check for Next button
      const nextBtn = await page.$(
        'button:has-text("Next"), button:has-text("التالي"), button[aria-label="Continue to next step"]'
      );
      if (nextBtn && (await nextBtn.isVisible().catch(() => false))) {
        console.log(`   👉 الانتقال للخطوة التالية (Next)...`);
        await nextBtn.click();
        await page.waitForTimeout(2000);
        step++;
        continue;
      }

      // If no Next, Review, or Submit button found, check if Done
      const doneBtn = await page.$('button:has-text("Done"), button:has-text("تم")');
      if (doneBtn && (await doneBtn.isVisible().catch(() => false))) {
        console.log(`🎉 اكتمل التقديم بنجاح!`);
        await doneBtn.click().catch(() => {});
        submitted = true;
        break;
      }

      break;
    }

    // Dismiss post-apply confirmation dialog if present
    const closeBtn = await page.$('button[aria-label="Dismiss"], button:has-text("Done"), button:has-text("تم")');
    if (closeBtn && (await closeBtn.isVisible().catch(() => false))) {
      await closeBtn.click().catch(() => {});
    }

    if (submitted) {
      console.log(`🎉🎉 تم تقديم الطلب بنجاح 100% عبر LinkedIn Easy Apply على الشاغر!`);
      return true;
    }

    return false;
  } catch (err) {
    console.error(`❌ خطأ أثناء Easy Apply:`, err);
    return false;
  }
}

async function answerLinkedInQuestions(page: Page) {
  // 1. Text / Number Inputs
  const questions = await page.$$('.jobs-easy-apply-form-section__grouping, .fb-dash-form-element');

  for (const q of questions) {
    try {
      const qText = (await q.innerText().catch(() => "")).toLowerCase();
      const input = await q.$('input[type="text"], input[type="number"], textarea');
      if (!input) continue;

      const currentVal = await input.inputValue().catch(() => "");
      if (currentVal && currentVal.length > 0) continue;

      // A. Current Salary
      if (qText.includes("current") && (qText.includes("salary") || qText.includes("compensation") || qText.includes("راتب") || qText.includes("حالي"))) {
        if (qText.includes("basic") || qText.includes("أساسي")) {
          await input.fill("8000");
          console.log(`     -> الراتب الأساسي الحالي: 8,000 ريال`);
        } else {
          await input.fill("10000");
          console.log(`     -> الراتب الإجمالي الحالي: 10,000 ريال`);
        }
      }
      // B. Expected Salary
      else if (qText.includes("expect") || qText.includes("متوقع") || qText.includes("salary") || qText.includes("راتب") || qText.includes("compensation") || qText.includes("package")) {
        const type = await input.getAttribute("type");
        if (type === "number") {
          if (qText.includes("basic") || qText.includes("أساسي")) {
            await input.fill("9000");
            console.log(`     -> الراتب الأساسي المتوقع: 9,000 ريال`);
          } else {
            await input.fill("10000");
            console.log(`     -> الراتب الإجمالي المتوقع: 10,000 ريال`);
          }
        } else {
          if (qText.includes("basic") || qText.includes("أساسي")) {
            await input.fill("9,000 - 10,000 SAR");
          } else {
            await input.fill("10,000 - 12,000 SAR");
          }
          console.log(`     -> مدى الراتب المتوقع: 10,000 - 12,000 ريال`);
        }
      }
      // C. Years of Experience
      else if (qText.includes("year") || qText.includes("خبرة") || qText.includes("experience")) {
        await input.fill("8");
        console.log(`     -> إجابة سنوات الخبرة: 8 سنوات`);
      }
      // D. Notice Period
      else if (qText.includes("notice") || qText.includes("إشعار") || qText.includes("start")) {
        await input.fill("15");
        console.log(`     -> إجابة فترة الإشعار: 15 يوماً`);
      }
      // E. Location / City
      else if (qText.includes("city") || qText.includes("مدينة") || qText.includes("location")) {
        await input.fill("Riyadh, Saudi Arabia");
        console.log(`     -> إجابة المدينة: Riyadh, Saudi Arabia`);
      }
      // F. Essay: Why join / Interest
      else if (qText.includes("why") || qText.includes("interest") || qText.includes("excite") || qText.includes("لماذا") || qText.includes("اهتمام")) {
        await input.fill("Passionate about scaling commercial growth and high-performance marketing in Saudi Arabia. As an HRSD-accredited Marketing Director with 8+ years of experience managing 7M+ SAR in ad budgets, delivering up to 25x ROAS, and scaling monthly revenue engines to 10M, I bring proven leadership in customer acquisition, CAC reduction, and omnichannel brand building.");
      }
      // G. Essay: Accomplishment / Initiative / Metric
      else if (qText.includes("achieve") || qText.includes("initiative") || qText.includes("success") || qText.includes("metric") || qText.includes("إنجاز") || qText.includes("مبادرة") || qText.includes("نجاح")) {
        await input.fill("Built and scaled an omnichannel commercial growth engine from early-stage to 10M/month in revenue. Directed 7M+ SAR in paid media across Snapchat, Meta, TikTok, and Google Ads achieving up to 25x audited ROAS, while reducing CAC by 28% and boosting customer retention through automated CRM workflows.");
      }
      // H. Essay: Additional Information / Summary
      else if (qText.includes("additional") || qText.includes("strengthen") || qText.includes("know you") || qText.includes("إضافي") || qText.includes("معلومات") || qText.includes("about you")) {
        await input.fill("HRSD-accredited Marketing Director based in Riyadh with Transferable Iqama, valid Saudi Driving License, and immediate availability. Proven track record leading 20+ member cross-functional teams, managing multi-million SAR media budgets, and scaling GCC consumer brands aligned with Vision 2030.");
      }
    } catch {}
  }

  // 2. Radio buttons (Yes/No questions)
  const radioGroups = await page.$$('fieldset, .jobs-easy-apply-form-section__grouping');
  for (const group of radioGroups) {
    try {
      const gText = (await group.innerText().catch(() => "")).toLowerCase();
      // Usually "Yes" for authorization, driving license, residency
      if (
        gText.includes("authorized") ||
        gText.includes("sponsorship") ||
        gText.includes("license") ||
        gText.includes("reside") ||
        gText.includes("iqama") ||
        gText.includes("موافق") ||
        gText.includes("رخصة")
      ) {
        if (gText.includes("require sponsorship") || gText.includes("sponsorship now or in the future")) {
          // No sponsorship required because of transferable iqama
          const noBtn = await group.$('label:has-text("No"), input[value="No"], label:has-text("لا")');
          if (noBtn) await noBtn.click().catch(() => {});
        } else {
          // Yes for authorization, license, iqama
          const yesBtn = await group.$('label:has-text("Yes"), input[value="Yes"], label:has-text("نعم")');
          if (yesBtn) await yesBtn.click().catch(() => {});
        }
      }
    } catch {}
  }

  // 3. Dropdowns / Selects
  const selects = await page.$$('select');
  for (const sel of selects) {
    try {
      const label = (await sel.getAttribute("aria-label")) || "";
      const options = await sel.$$eval('option', opts => opts.map(o => ({ val: o.value, text: o.text })));
      // Prefer Yes or first positive answer
      const yesOpt = options.find(o => o.text.toLowerCase().includes("yes") || o.text.includes("نعم"));
      if (yesOpt) {
        await sel.selectOption(yesOpt.val);
      }
    } catch {}
  }
}

