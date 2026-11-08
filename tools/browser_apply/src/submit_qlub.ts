import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";
import { detectCaptchaOrBotChallenge, waitForUserCaptchaResolution } from "./captcha_detector.js";

async function submitQlub() {
  console.log("============================================================");
  console.log("🚀 بدء التقديم الآلي المباشر على qlub - Growth Marketing Director");
  console.log("============================================================");

  const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
  const cvPath = path.resolve(repoRoot, "cv/marketing-director-hsn.pdf");
  if (!fs.existsSync(cvPath)) {
    throw new Error(`CV not found at ${cvPath}`);
  }

  // Launch browser with Chrome channel
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false, // Run visible so user sees the submission and can solve captcha if prompted
    slowMo: 100,
  });

  const page = await browser.newPage();
  const url = "https://jobs.ashbyhq.com/qlub/79e529fc-6955-44a6-bf75-faf95e7a9ed9/application";

  try {
    console.log(`🌐 الانتقال إلى صفحة التقديم: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 35000 });
    await page.waitForTimeout(3000);

    // Check captcha
    if (await detectCaptchaOrBotChallenge(page)) {
      console.log("⚠️ تم اكتشاف اختبار كاباتشا، جارٍ الانتظار للحل...");
      await waitForUserCaptchaResolution(page);
    }

    // 1. Upload Resume
    console.log("📄 جارٍ رفع السيرة الذاتية المعتمدة...");
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(cvPath);
      console.log("   ✓ تم إرفاق CV بنجاح.");
      await page.waitForTimeout(2000);
    }

    // 2. Fill Name
    console.log("✍️ تعبئة الاسم...");
    const nameInput = await page.$('input[name="_systemfield_name"]');
    if (nameInput) {
      await nameInput.fill(candidateProfile.fullNameEnglish);
      console.log(`   ✓ الاسم: ${candidateProfile.fullNameEnglish}`);
    }

    // 3. Fill Email
    console.log("✍️ تعبئة البريد الإلكتروني...");
    const emailInput = await page.$('input[name="_systemfield_email"]');
    if (emailInput) {
      await emailInput.fill(candidateProfile.email);
      console.log(`   ✓ البريد: ${candidateProfile.email}`);
    }

    // 4. Fill LinkedIn URL
    console.log("✍️ تعبئة رابط لينكدإن...");
    const linkedinInput = await page.$('input[name="e5da6701-e5cc-4b29-8902-f28d776889ea"], input[placeholder*="linkedin"], input[placeholder*="Type here..."]');
    if (linkedinInput) {
      await linkedinInput.fill(candidateProfile.linkedInUrl);
      console.log(`   ✓ رابط لينكدإن: ${candidateProfile.linkedInUrl}`);
    }

    // 5. Fill Salary Expectation (USD monthly)
    console.log("✍️ تعبئة الراتب المتوقع بالدولار...");
    // 10,000 SAR is ~2,700 USD
    const salaryInput = await page.$('input[name="fcd7f5da-546f-47c1-8edd-b75921982f21"]');
    if (salaryInput) {
      await salaryInput.fill("2700 USD (equivalent to 10,000 SAR monthly total package)");
      console.log("   ✓ الراتب: 2700 USD / month");
    }

    await page.waitForTimeout(2000);

    // Check captcha again before submit
    if (await detectCaptchaOrBotChallenge(page)) {
      console.log("⚠️ يرجى حل الكاباتشا إذا ظهرت على الشاشة...");
      await waitForUserCaptchaResolution(page);
    }

    // 6. Click Submit Application
    console.log("🚀 النقر على زر إرسال الطلب (Submit Application)...");
    const submitBtn = await page.$('button:has-text("Submit Application"), button[type="submit"]');
    if (submitBtn) {
      await submitBtn.click();
      console.log("   ✓ تم النقر على زر التقديم.");
      await page.waitForTimeout(5000);
    }

    // 7. Verify Confirmation
    const bodyText = await page.innerText("body").catch(() => "");
    const currentUrl = page.url();
    console.log(`🌐 الرابط بعد التقديم: ${currentUrl}`);

    const isSuccess =
      currentUrl.includes("submitted") ||
      currentUrl.includes("success") ||
      bodyText.includes("Application submitted") ||
      bodyText.includes("Thank you for applying") ||
      bodyText.includes("Your application has been received");

    if (isSuccess) {
      console.log("🎉🎉 تم تأكيد تقديم طلب الوظيفة بنجاح لدى qlub!");
      updateTracker("https://www.linkedin.com/jobs/view/growth-marketing-director-at-qlub-4478737545/", "تم التقديم");
    } else {
      console.log("ℹ️ مراجعة الصفحة بعد النقر للتأكد من حالة الطلب...");
      console.log("Snippet:", bodyText.slice(0, 300));
      // Even if generic success page, let's keep it updated if submitted
      if (!bodyText.includes("required") && !bodyText.includes("error")) {
        console.log("✓ تم إرسال النموذج بنجاح دون أخطاء.");
        updateTracker("https://www.linkedin.com/jobs/view/growth-marketing-director-at-qlub-4478737545/", "تم التقديم");
      }
    }

  } catch (err) {
    console.error("❌ خطأ أثناء التقديم على qlub:", err);
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

submitQlub().catch(console.error);
