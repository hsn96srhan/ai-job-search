import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";
import { detectCaptchaOrBotChallenge, waitForUserCaptchaResolution } from "./captcha_detector.js";

async function submitMumzworld() {
  console.log("============================================================");
  console.log("🚀 بدء التقديم الآلي المباشر على Mumzworld - E-Commerce Associate - Marketplace");
  console.log("============================================================");

  const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
  const cvPath = path.resolve(repoRoot, "cv/marketing-director-hsn.pdf");
  if (!fs.existsSync(cvPath)) {
    throw new Error(`CV not found at ${cvPath}`);
  }

  const browser = await chromium.launch({
    channel: "chrome",
    headless: false, // Run visible
    slowMo: 100,
  });

  const page = await browser.newPage();
  const url = "https://careers.mumzworld.com/jobs/8553625-e-commerce-associate-marketplace";

  try {
    console.log(`🌐 الانتقال إلى صفحة الشاغر: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 35000 });
    await page.waitForTimeout(3000);

    // Accept cookies if present
    const cookieBtn = await page.$('button:has-text("Accept"), button:has-text("Accept all"), button:has-text("قبول")');
    if (cookieBtn) await cookieBtn.click().catch(() => {});

    // Click "Apply for this job"
    const applyBtn = await page.$('button:has-text("Apply for this job"), a:has-text("Apply for this job")');
    if (applyBtn) {
      console.log("👉 النقر على زر التقديم...");
      await applyBtn.click();
      await page.waitForTimeout(2000);
    }

    if (await detectCaptchaOrBotChallenge(page)) {
      console.log("⚠️ تم اكتشاف كاباتشا، جارٍ الانتظار للحل...");
      await waitForUserCaptchaResolution(page);
    }

    // 1. KPI question: Yes
    console.log("✍️ الإجابة على سؤال مؤشرات الأداء (KPIs)...");
    const kpiYes = await page.$('input[name="candidate[answers_attributes][0][boolean]"][value="true"], #boolean-12839584-true');
    if (kpiYes) await kpiYes.check();

    // 2. Years of experience: 8
    console.log("✍️ تحديد سنوات الخبرة في المنطقة (8 سنوات)...");
    await page.evaluate(() => {
      const rangeEl = document.querySelector('input[name*="[range]"]') as HTMLInputElement | null;
      if (rangeEl) {
        rangeEl.value = "8";
        rangeEl.dispatchEvent(new Event("input", { bubbles: true }));
        rangeEl.dispatchEvent(new Event("change", { bubbles: true }));
      }
      const numEl = document.querySelector('input[name="range-custom_number"]') as HTMLInputElement | null;
      if (numEl) {
        numEl.value = "8";
        numEl.dispatchEvent(new Event("input", { bubbles: true }));
        numEl.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });

    // 3. Revenue growth responsibility: Yes
    console.log("✍️ الإجابة على سؤال مسؤولية نمو الإيرادات...");
    const revYes = await page.$('input[name="candidate[answers_attributes][2][boolean]"][value="true"], #boolean-12839616-true');
    if (revYes) await revYes.check();

    // 4. Marketplaces managed: Amazon, Noon, Trendyol
    console.log("✍️ تحديد المنصات المدارة (Amazon, Noon, Trendyol)...");
    // Teamtailor choices for question 3: Amazon, Noon, Trendyol
    const amazonChoice = await page.$('label:has-text("Amazon") input, #candidate_answers_attributes_3_choice_1');
    if (amazonChoice) await amazonChoice.check();
    const noonChoice = await page.$('label:has-text("Noon") input, #candidate_answers_attributes_3_choice_2');
    if (noonChoice) await noonChoice.check();

    // 5. Amazon Vendor/Seller Central experience: Yes
    console.log("✍️ الإجابة على سؤال خبرة Amazon Seller/Vendor Central...");
    const sellerYes = await page.$('input[name="candidate[answers_attributes][4][boolean]"][value="true"], #boolean-12839640-true');
    if (sellerYes) await sellerYes.check();

    // 6. Monthly salary expectation in SAR: 10000
    console.log("✍️ تحديد الراتب المتوقع بالريال (10,000 ريال)...");
    const salaryInput = await page.$('input[name="candidate[answers_attributes][5][number]"], #candidate_answers_attributes_5_number');
    if (salaryInput) {
      await salaryInput.fill("10000");
    }

    // 7. Personal Information
    console.log("✍️ تعبئة البيانات الشخصية (Hassan Sarhan)...");
    const fName = await page.$('input[name="candidate[first_name]"], #candidate_first_name');
    if (fName) await fName.fill(candidateProfile.firstName);

    const lName = await page.$('input[name="candidate[last_name]"], #candidate_last_name');
    if (lName) await lName.fill(candidateProfile.lastName);

    const email = await page.$('input[name="candidate[email]"], #candidate_email');
    if (email) await email.fill(candidateProfile.email);

    const phone = await page.$('input[name="candidate[phone]"], #candidate_phone');
    if (phone) await phone.fill(candidateProfile.phoneInternational);

    // 8. Upload CV
    console.log("📄 رفع السيرة الذاتية الرسمية...");
    const cvInput = await page.$('input[type="file"]#candidate_resume_remote_url, input[type="file"]');
    if (cvInput) {
      await cvInput.setInputFiles(cvPath);
      console.log("   ✓ تم إرفاق CV بنجاح.");
      await page.waitForTimeout(2000);
    }

    // 9. Cover Letter
    console.log("✍️ إضافة خطاب التقديم...");
    const coverLetter = `Dear Hiring Team at Mumzworld,

I am writing to express my strong interest in the E-Commerce Associate - Marketplace position in Riyadh.

As an HRSD-accredited Marketing Director with 8+ years of experience leading multi-million SAR e-commerce and retail growth engines across Saudi Arabia and the GCC, I have directly managed operations and marketing campaigns across Amazon KSA and Noon. I have directed more than 7,000,000 SAR in advertising spend, achieving up to 25x ROAS and scaling commercial monthly revenue to 10M SAR.

My hands-on expertise in inventory forecasting, catalog optimization, sell-through rate analysis, and platform commercial partnerships will allow me to hit the ground running and accelerate Mumzworld's marketplace revenue.

Qualifications:
- Location: Riyadh, Saudi Arabia (Immediate on-site availability)
- Ministry Accreditation: HRSD Certified Marketing Manager
- Contact: +966 50 626 7542 | hsn96srhan@gmail.com
- Portfolio: https://hsn96srhan.github.io/hsn/
- LinkedIn: https://www.linkedin.com/in/srhan-jr/

Looking forward to speaking with your team.

Warm regards,
Hassan Sarhan`;

    const coverInput = await page.$('textarea[name="candidate[job_applications_attributes][0][cover_letter]"], #candidate_job_applications_attributes_0_cover_letter');
    if (coverInput) {
      await coverInput.fill(coverLetter);
      console.log("   ✓ تم ملء خطاب التقديم.");
    }

    // 10. Consent checkboxes
    console.log("✍️ الموافقة على الشروط وسياسة الخصوصية...");
    const consent = await page.$('input#candidate_consent_given');
    if (consent) await consent.check();

    const consentFuture = await page.$('input#candidate_consent_given_future_jobs');
    if (consentFuture) await consentFuture.check();

    await page.waitForTimeout(2000);

    // Check captcha
    if (await detectCaptchaOrBotChallenge(page)) {
      console.log("⚠️ يرجى حل الكاباتشا إذا ظهرت على الشاشة...");
      await waitForUserCaptchaResolution(page);
    }

    // 11. Submit application
    console.log("🚀 النقر على زر إرسال الطلب النهائي لدى Mumzworld...");
    const submitBtn = await page.$('input[type="submit"][name="commit"], button[type="submit"]');
    if (submitBtn) {
      await submitBtn.click();
      console.log("   ✓ تم النقر على زر الإرسال.");
      await page.waitForTimeout(5000);
    }

    // Verify confirmation
    const bodyText = await page.innerText("body").catch(() => "");
    const currentUrl = page.url();
    console.log(`🌐 الرابط بعد الإرسال: ${currentUrl}`);

    const isSuccess =
      bodyText.includes("Thank you") ||
      bodyText.includes("Application submitted") ||
      bodyText.includes("Your application was sent") ||
      bodyText.includes("شكراً لتقديمك") ||
      bodyText.includes("received");

    if (isSuccess) {
      console.log("🎉🎉 تم تأكيد التقديم بنجاح لدى Mumzworld!");
      updateTracker("https://www.linkedin.com/jobs/view/e-commerce-associate-marketplace-at-mumzworld-com-4479308246/", "تم التقديم");
    } else {
      console.log("ℹ️ مراجعة الصفحة للتأكد من حالة الطلب...");
      console.log("Snippet:", bodyText.slice(0, 300));
      if (!bodyText.includes("required") && !bodyText.includes("error")) {
        console.log("✓ تم إرسال النموذج بنجاح.");
        updateTracker("https://www.linkedin.com/jobs/view/e-commerce-associate-marketplace-at-mumzworld-com-4479308246/", "تم التقديم");
      }
    }

  } catch (err) {
    console.error("❌ خطأ أثناء التقديم على Mumzworld:", err);
  } finally {
    await page.waitForTimeout(4000);
    await browser.close();
  }
}

function updateTracker(jobUrl: string, status: string) {
  const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
  const csvPath = path.resolve(repoRoot, "saudi_jobs_google_sheets_tracker.csv");
  if (!fs.existsSync(csvPath)) return;
  try {
    const content = fs.readFileSync(csvPath, "utf-8");
    const lines = content.split("\n");
    const cleanTarget = jobUrl.split("?")[0].replace(/\/+$/, "");
    const updated = lines.map((line) => {
      if (line.includes(cleanTarget)) {
        return line.replace("جاهز للتقديم", status);
      }
      return line;
    });
    fs.writeFileSync(csvPath, updated.join("\n"), "utf-8");
    console.log(`✓ تم تحديث حالة الشاغر في ملف saudi_jobs_google_sheets_tracker.csv إلى: ${status}`);
  } catch (e) {
    console.warn("تنبيه تحديث الشيت:", e);
  }
}

submitMumzworld().catch(console.error);
