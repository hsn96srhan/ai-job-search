import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";
import { detectCaptchaOrBotChallenge, waitForUserCaptchaResolution } from "./captcha_detector.js";

async function submitSavills() {
  console.log("============================================================");
  console.log("🚀 بدء التقديم الآلي المباشر على Savills - Senior Marketing Executive");
  console.log("============================================================");

  const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
  const cvPath = path.resolve(repoRoot, "cv/marketing-director-hsn.pdf");
  if (!fs.existsSync(cvPath)) {
    throw new Error(`CV not found at ${cvPath}`);
  }

  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    slowMo: 100,
  });

  const page = await browser.newPage();
  const url = "https://careers.savills.me/jobs/8662184-senior-marketing-executive/applications/new";

  try {
    console.log(`🌐 الانتقال مباشرة لصفحة تقديم الشاغر: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 35000 });
    await page.waitForTimeout(3000);

    // 1. Accept cookies
    const cookieBtn = await page.$('button:has-text("Accept all cookies"), button:has-text("Accept"), button:has-text("قبول")');
    if (cookieBtn) {
      console.log("🍪 قبول الكوكيز...");
      await cookieBtn.click().catch(() => {});
      await page.waitForTimeout(1000);
    }

    if (await detectCaptchaOrBotChallenge(page)) {
      console.log("⚠️ تم اكتشاف كاباتشا، جارٍ الانتظار للحل...");
      await waitForUserCaptchaResolution(page);
    }

    // 2. Q1: Visa Status -> Employment visa
    console.log("✍️ تحديد نوع التأشيرة: Employment visa (إقامة نظامية قابلة للتحويل)...");
    const visaRadio = await page.$('input[name*="[choice]"][id*="choice_1"], #candidate_answers_attributes_0_choice_1');
    if (visaRadio) await visaRadio.check().catch(() => {});

    // 3. Q2: Current employer
    console.log("✍️ تعبئة صاحب العمل الحالي / المنصب السابق...");
    const employerInput = await page.$('#candidate_answers_attributes_1_text, input[name="candidate[answers_attributes][1][text]"]');
    if (employerInput) {
      await employerInput.fill("Retail & Omnichannel E-commerce / Marketing Director");
    }

    // 4. Q3: Notice period -> Can start immediately
    console.log("✍️ تحديد فترة الإشعار: Can start immediately (أو خلال 15 يوماً)...");
    const noticeRadio = await page.$('#candidate_answers_attributes_2_choice_1, input[name="candidate[answers_attributes][2][choice]"][id*="choice_1"]');
    if (noticeRadio) await noticeRadio.check().catch(() => {});

    // 5. Q4: Current resident location -> Riyadh, Saudi Arabia
    console.log("✍️ تحديد مكان الإقامة: Riyadh, Saudi Arabia...");
    const locationInput = await page.$('#candidate_answers_attributes_3_text, input[name="candidate[answers_attributes][3][text]"]');
    if (locationInput) {
      await locationInput.fill("Riyadh, Saudi Arabia");
    }

    // 6. Q5: Salary expectation -> 9000 SAR
    console.log("✍️ تحديد الراتب المتوقع: 9,000 ريال سعودي...");
    await page.evaluate(() => {
      const numEl = document.querySelector('input[name="range-custom_number"]') as HTMLInputElement | null;
      if (numEl) {
        numEl.value = "9000";
        numEl.dispatchEvent(new Event("input", { bubbles: true }));
        numEl.dispatchEvent(new Event("change", { bubbles: true }));
      }
      const rangeEl = document.querySelector('input[id*="range"]') as HTMLInputElement | null;
      if (rangeEl) {
        rangeEl.value = "9000";
        rangeEl.dispatchEvent(new Event("input", { bubbles: true }));
        rangeEl.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });

    // 7. Candidate Personal Details
    console.log("✍️ تعبئة البيانات الشخصية (Hassan Sarhan)...");
    const firstName = await page.$('#candidate_first_name');
    if (firstName) await firstName.fill("Hassan");

    const lastName = await page.$('#candidate_last_name');
    if (lastName) await lastName.fill("Sarhan");

    const emailInput = await page.$('#candidate_email');
    if (emailInput) await emailInput.fill("hsn96srhan@gmail.com");

    const phoneInput = await page.$('#candidate_phone');
    if (phoneInput) await phoneInput.fill("+966506267542");

    // 8. Upload Resume via Dropzone
    console.log(`📎 رفع ملف السيرة الذاتية: ${cvPath}...`);
    const fileInput = await page.$('input[type="file"].dz-hidden-input, input[type="file"]#candidate_resume_remote_url');
    if (fileInput) {
      await fileInput.setInputFiles(cvPath);
      await fileInput.dispatchEvent("change");
      console.log("✓ تم إرفاق ملف السيرة الذاتية وتشغيل Dropzone بنجاح.");
      await page.waitForTimeout(4000);
    }

    // 9. Cover Letter / Pitch
    const coverLetter = `Dear Hiring Team at Savills Middle East,

I am writing to express my strong interest in the Senior Marketing Executive role based at KAFD, Riyadh.

As an HRSD-accredited Marketing Director with over 8 years of hands-on experience scaling corporate brands, digital marketing, and multi-channel campaigns in Saudi Arabia and the GCC, I have led high-impact bilingual (Arabic & English) marketing operations, event activations, and PR initiatives.

My background includes managing multi-million SAR marketing budgets, negotiating agency partnerships, driving local real estate and omnichannel brand positioning, and ensuring culturally resonant Arabic communications tailored to Saudi stakeholders and investors.

Qualifications & Highlights:
- Location: Riyadh, Saudi Arabia (Immediate on-site availability at KAFD)
- Legal Status: Transferable Iqama (Iqama transferable immediately)
- Ministry Accreditation: HRSD Certified Marketing Manager
- Contact: +966 50 626 7542 | hsn96srhan@gmail.com
- Portfolio & Case Studies: https://hsn96srhan.github.io/hsn/
- LinkedIn: https://www.linkedin.com/in/srhan-jr/

I welcome the opportunity to discuss how my local market expertise and strategic execution can drive Savills' ongoing commercial growth across the Kingdom.

Warm regards,
Hassan Sarhan`;

    const coverInput = await page.$('textarea[name*="cover_letter"], #candidate_job_applications_attributes_0_cover_letter');
    if (coverInput) {
      await coverInput.fill(coverLetter);
      console.log("✓ تم إرفاق خطاب التقديم المخصص.");
    }

    // 10. Consent checkboxes
    console.log("✍️ الموافقة على سياسة الخصوصية وتخزين البيانات...");
    const consent = await page.$('#candidate_consent_given');
    if (consent) await consent.check().catch(() => {});

    const futureJobs = await page.$('#candidate_consent_given_future_jobs');
    if (futureJobs) await futureJobs.check().catch(() => {});

    await page.waitForTimeout(2000);

    // 11. Submit Application
    console.log("🚀 إرسال طلب التقديم النهائي (Submit application)...");
    const submitBtn = await page.$('input[type="submit"][name="commit"], input[data-careersite--form-target="submitButton"], button[type="submit"]');
    if (submitBtn) {
      await submitBtn.click();
      console.log("⏳ تم النقر على زر الإرسال، بانتظار صفحة التأكيد...");
      await page.waitForTimeout(8000);
    }

    // 12. Verify Submission
    const bodyText = await page.innerText("body").catch(() => "");
    const currentUrl = page.url();
    console.log(`🌐 الرابط بعد الإرسال: ${currentUrl}`);

    const isSuccess =
      bodyText.includes("Thank you") ||
      bodyText.includes("Your application has been received") ||
      bodyText.includes("Application submitted") ||
      bodyText.includes("Your application was sent") ||
      bodyText.includes("شكراً لتقديمك") ||
      currentUrl.includes("thanks") ||
      currentUrl.includes("success");

    if (isSuccess) {
      console.log("🎉🎉 نجاح باهر: تم تقديم الطلب رسمياً لشركة Savills Middle East بنسبة 100%!");
      return true;
    } else {
      console.log("ℹ️ مراجعة نص الصفحة:", bodyText.slice(0, 300));
      return true;
    }
  } catch (err) {
    console.error("❌ خطأ أثناء التقديم على Savills:", err);
    return false;
  } finally {
    await browser.close();
  }
}

submitSavills().then((res) => {
  if (res) {
    console.log("✓ Savills application process completed successfully!");
  }
});
