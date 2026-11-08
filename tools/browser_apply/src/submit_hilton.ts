import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";
import { detectCaptchaOrBotChallenge, waitForUserCaptchaResolution } from "./captcha_detector.js";
import { execSync } from "child_process";

function fetchLatestHiltonCode(): string | null {
  try {
    const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
    const scriptPath = path.resolve(repoRoot, "tools/fetch_hilton_otp.py");
    const out = execSync(`python3 "${scriptPath}"`, { encoding: "utf-8" }).trim();
    return out || null;
  } catch (e) {
    return null;
  }
}

async function submitHilton() {
  console.log("============================================================");
  console.log("🚀 بدء التقديم على Hilton - Assistant Marketing Manager (Oracle HCM)");
  console.log("============================================================");

  const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
  const cvPath = path.resolve(repoRoot, "cv/marketing-director-hsn.pdf");

  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    slowMo: 100,
  });

  const page = await browser.newPage();
  const url = "https://efet.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1009/job/220799/apply/email";

  try {
    console.log(`🌐 الانتقال إلى صفحة التحقق من البريد: ${url}`);
    await page.goto(url, { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForTimeout(2000);

    // Accept cookies if present
    const cookie = await page.$('button:has-text("ACCEPT ALL")');
    if (cookie) await cookie.click().catch(() => {});
    await page.waitForTimeout(1000);

    // Fill email
    console.log("✍️ إدخال البريد الإلكتروني (hsn96srhan@gmail.com)...");
    await page.fill('input[name="primary-email"]', candidateProfile.email);

    // Legal disclaimer
    console.log("✍️ الموافقة على الشروط القانونية...");
    const label = await page.$('label[for="legal-disclaimer-checkbox"]');
    if (label) await label.click().catch(() => {});

    await page.waitForTimeout(1000);

    // Click NEXT
    console.log("👉 النقر على NEXT لطلب رمز التحقق...");
    const nextBtn = await page.$('button.apply-flow-pagination__button:has-text("NEXT")');
    if (nextBtn) {
      await nextBtn.click();
      await page.waitForTimeout(6000);
    }

    // Wait and fetch OTP code from Gmail
    console.log("⏳ جارٍ انتظار وصول رمز التحقق (OTP) من هيلتون إلى البريد...");
    let code: string | null = null;
    for (let i = 0; i < 6; i++) {
      await page.waitForTimeout(4000);
      code = fetchLatestHiltonCode();
      if (code) {
        console.log(`🔑 تم استلام رمز التحقق بنجاح من البريد: ${code}`);
        break;
      }
    }

    if (code) {
      console.log(`✍️ إدخال رمز التحقق ${code} في النموذج...`);
      // Find verification input
      const codeInput = await page.$('input[aria-label*="Verification"], input[id*="verification"], input[name*="code"], input.oj-inputtext-input:visible');
      if (codeInput) {
        await codeInput.fill(code);
        await page.waitForTimeout(1000);
      } else {
        await page.evaluate((c) => {
          const inps = Array.from(document.querySelectorAll('input:not([type=hidden])')) as HTMLInputElement[];
          const target = inps.find(i => i.offsetParent !== null && !i.value);
          if (target) {
            target.value = c;
            target.dispatchEvent(new Event('input', { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
          }
        }, code);
      }

      // Click VERIFY
      console.log("👉 النقر على زر VERIFY للتأكيد...");
      const verifyBtn = await page.$('button:has-text("VERIFY"), button:has-text("Verify")');
      if (verifyBtn) {
        await verifyBtn.click();
        await page.waitForTimeout(6000);
      }
    }

    console.log(`🌐 الصفحة الحالية بعد التحقق: ${page.url()}`);
    let bodyText = await page.innerText("body").catch(() => "");
    console.log("Snippet:", bodyText.slice(0, 400));

    // Handle subsequent application steps in Oracle HCM
    let step = 1;
    while (step <= 6) {
      console.log(`\n[الخطوة ${step} في بوابة هيلتون]: فحص الحقول...`);
      if (await detectCaptchaOrBotChallenge(page)) {
        await waitForUserCaptchaResolution(page);
      }

      // Check file upload
      const fileInput = await page.$('input[type="file"]');
      if (fileInput) {
        console.log("📄 رفع السيرة الذاتية في بوابة هيلتون...");
        await fileInput.setInputFiles(cvPath).catch(() => {});
        await page.waitForTimeout(2000);
      }

      // Fill common text inputs
      await page.evaluate((p) => {
        const inputs = Array.from(document.querySelectorAll('input:not([type=hidden]):not([type=file]), select, textarea')) as (HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement)[];
        inputs.forEach(el => {
          if (el.value) return; // already filled
          const name = (el.name || el.id || el.getAttribute('aria-label') || '').toLowerCase();
          if (name.includes('first')) el.value = p.firstName;
          else if (name.includes('last')) el.value = p.lastName;
          else if (name.includes('phone') || name.includes('mobile')) el.value = p.phoneInternational;
          else if (name.includes('address') || name.includes('city')) el.value = p.cityEnglish;
          else if (name.includes('postal') || name.includes('zip')) el.value = "11564";
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        });
      }, candidateProfile);

      // Check if finished
      bodyText = await page.innerText("body").catch(() => "");
      if (
        bodyText.includes("Thank you for applying") ||
        bodyText.includes("Application Submitted") ||
        bodyText.includes("Your application has been received") ||
        bodyText.includes("Congratulations")
      ) {
        console.log("🎉🎉 تم اكتمال التقديم بنجاح لدى Hilton!");
        updateTracker("https://www.linkedin.com/jobs/view/assistant-marketing-manager-at-hilton-4485328665/", "تم التقديم");
        break;
      }

      // Click Next / Submit in Oracle HCM flow
      const nextOrSubmit = await page.$('button.apply-flow-pagination__button.theme-color-1, button:has-text("SUBMIT"), button:has-text("Submit"), button:has-text("NEXT")');
      if (nextOrSubmit) {
        const btnText = await nextOrSubmit.innerText().catch(() => "");
        console.log(`👉 النقر على زر التقدم: "${btnText}"...`);
        await nextOrSubmit.click();
        await page.waitForTimeout(4000);
      } else {
        console.log("ℹ️ تم الوصول لآخر شاشة.");
        break;
      }

      step++;
    }

    updateTracker("https://www.linkedin.com/jobs/view/assistant-marketing-manager-at-hilton-4485328665/", "تم التقديم");

  } catch (err) {
    console.error("❌ خطأ أثناء معالجة هيلتون:", err);
  } finally {
    await page.waitForTimeout(3000);
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

submitHilton().catch(console.error);
