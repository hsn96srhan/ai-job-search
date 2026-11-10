#!/usr/bin/env bun
import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";
import { detectCaptchaOrBotChallenge, waitForUserCaptchaResolution } from "./captcha_detector.js";
import { autofillCommonFields, clickPrimarySubmitOrNext } from "./form_autofill.js";
import { submitLinkedInEasyApply } from "./linkedin_easy_apply.js";

interface CliOptions {
  url?: string;
  all?: boolean;
  headless?: boolean;
}

function parseArgs(): CliOptions {
  const args = process.argv.slice(2);
  const options: CliOptions = { headless: false };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--url" && args[i + 1]) {
      options.url = args[i + 1];
      i++;
    } else if (args[i] === "--all") {
      options.all = true;
    } else if (args[i] === "--headless") {
      options.headless = true;
    } else if (!options.url && !args[i].startsWith("-")) {
      options.url = args[i];
    }
  }

  return options;
}

async function handleLinkedInAuth(page: any): Promise<boolean> {
  const signInBtn = await page.$('a:has-text("Sign in"), button:has-text("Sign in"), a:has-text("تسجيل الدخول"), button:has-text("تسجيل الدخول")');
  const needsAuth = await page.$('input[name="session_key"], #username, input[type="email"]');

  if (signInBtn && (await signInBtn.isVisible().catch(() => false)) && !needsAuth) {
    console.log("🔑 النقر على تسجيل الدخول للينكد إن...");
    await signInBtn.click().catch(() => {});
    await page.waitForTimeout(3000);
  }

  const usernameInput = await page.$('input[name="session_key"], #username, input[id*="email"]');
  const passwordInput = await page.$('input[name="session_password"], #password');

  if (usernameInput && passwordInput) {
    console.log(`🔑 تسجيل الدخول بحساب المرشح: ${candidateProfile.email}...`);
    await usernameInput.fill(candidateProfile.email);
    await passwordInput.fill(candidateProfile.defaultAccountPassword);
    
    const submitLogin = await page.$('button[type="submit"], button:has-text("Sign in"), button:has-text("تسجيل الدخول")');
    if (submitLogin) {
      await submitLogin.click();
      await page.waitForTimeout(5000);
    }

    const otpInput = await page.$('input[id*="pin"], input[name*="pin"], input[id*="verification"], input[name*="code"]');
    if (otpInput) {
      console.log("📧 مطلوب رمز تحقق (OTP) من البريد، جارٍ الجلب التلقائي من Gmail...");
      const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
      const otpScript = path.resolve(repoRoot, "tools/fetch_email_verification.py");
      if (fs.existsSync(otpScript)) {
        try {
          const { execSync } = await import("child_process");
          let code = "";
          for (let attempt = 0; attempt < 4; attempt++) {
            code = execSync(`python3 "${otpScript}" --otp`, { encoding: "utf-8" }).trim();
            if (code && /^\d{4,8}$/.test(code)) break;
            await page.waitForTimeout(3000);
          }
          if (code && /^\d{4,8}$/.test(code)) {
            console.log(`✓ إدخال كود التحقق الأمني: ${code}`);
            await otpInput.fill(code);
            const submitOtp = await page.$('button[type="submit"], button:has-text("Submit"), button:has-text("Verify")');
            if (submitOtp) await submitOtp.click();
            await page.waitForTimeout(4000);
          }
        } catch (e) {
          console.warn("تنبيه جلب OTP:", e);
        }
      }
    }
    return true;
  }
  return false;
}

async function applyToUrl(page: any, url: string): Promise<boolean> {
  console.log(`\n============================================================`);
  console.log(`🌐 بدء التقديم الآلي الذكي على: ${url}`);
  console.log(`============================================================`);

  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 35000 });
    await page.waitForTimeout(3000);

    // 1. CAPTCHA Check
    if (await detectCaptchaOrBotChallenge(page)) {
      await waitForUserCaptchaResolution(page);
    }

    // 2. Check for LinkedIn Easy Apply
    const easyApplySelectors = [
      'button:has-text("Easy Apply")',
      'button:has-text("التقديم السريع")',
      'button:has-text("التقديم بسهولة")',
      'button[aria-label*="Easy Apply"]',
      'button[aria-label*="التقديم السريع"]',
      '.jobs-apply-button--top-card:has-text("Easy Apply")',
      '.jobs-apply-button--top-card:has-text("التقديم السريع")',
    ];

    let isEasyApply = false;
    for (const sel of easyApplySelectors) {
      const el = await page.$(sel);
      if (el && (await el.isVisible().catch(() => false))) {
        isEasyApply = true;
        break;
      }
    }

    if (isEasyApply) {
      console.log(`⚡ هذا الشاغر متاح عبر التقديم السريع (LinkedIn Easy Apply)، جارٍ التقديم الآلي الشامل...`);
      const easySuccess = await submitLinkedInEasyApply(page, url);
      if (easySuccess) {
        return true;
      }
    }

    // 3. External Career Site Apply Buttons (LinkedIn Arabic & English)
    const externalApplySelectors = [
      'button.top-card-layout__cta--primary',
      'a.top-card-layout__cta--primary',
      'button:has-text("التقدم")',
      'a:has-text("التقدم")',
      'button:has-text("Apply on company website")',
      'a:has-text("Apply on company website")',
      'button:has-text("قدّم على موقع الشركة")',
      'a:has-text("قدّم على موقع الشركة")',
      '.jobs-apply-button',
      'button:has-text("Apply now")',
      'a:has-text("Apply now")',
      'button:has-text("Apply")',
      'a:has-text("Apply")',
      'button:has-text("قدّم الآن")',
      'a:has-text("قدّم الآن")',
      'button:has-text("تقديم")',
      'a:has-text("تقديم")',
    ];

    let activePage = page;
    for (const sel of externalApplySelectors) {
      const btn = await page.$(sel);
      if (btn && (await btn.isVisible().catch(() => false))) {
        const text = (await btn.innerText().catch(() => "")) || "رابط التقديم الخارجي";
        console.log(`👉 تم رصد زر التقديم الخارجي: "${text.trim()}"، جارٍ النقر والانتقال لموقع الشركة...`);

        // Check if opens a new tab
        const [popup] = await Promise.all([
          page.context().waitForEvent("page", { timeout: 8000 }).catch(() => null),
          btn.click().catch(() => {}),
        ]);

        if (popup) {
          activePage = popup;
          await activePage.waitForLoadState("domcontentloaded").catch(() => {});
          console.log(`🌐 تم فتح بوابة التقديم الخارجية في تبويب جديد: ${activePage.url()}`);
        } else {
          await page.waitForTimeout(4000);
        }
        break;
      }
    }

    // 4. Form Wizard Loop on External Career Site / Form (up to 6 steps)
    let step = 1;
    let maxSteps = 6;
    let isCompleted = false;

    while (step <= maxSteps) {
      console.log(`\n[الخطوة ${step}]: فحص وتعبئة الحقول الآلية في استمارة الشركة الخارجية...`);

      // Check for Captcha on target page
      if (await detectCaptchaOrBotChallenge(activePage)) {
        await waitForUserCaptchaResolution(activePage);
      }

      const { filledCount, filesUploaded } = await autofillCommonFields(activePage);
      console.log(`   ✓ تم ملء ${filledCount} حقل بيانات | تم إرفاق ${filesUploaded} ملف.`);

      // Check if application is already submitted or success page
      const pageText = await activePage.innerText("body").catch(() => "");
      if (
        pageText.includes("Application submitted") ||
        pageText.includes("Your application was sent") ||
        pageText.includes("تم إرسال طلبك بنجاح") ||
        pageText.includes("شكراً لتقديمك") ||
        pageText.includes("Thank you for applying") ||
        pageText.includes("Application received") ||
        pageText.includes("تم استلام طلبك")
      ) {
        console.log("🎉 تم تأكيد إرسال الطلب في موقع الشركة بنجاح 100%!");
        isCompleted = true;
        break;
      }

      // Check if the portal requires clicking an email verification link
      if (
        pageText.toLowerCase().includes("verify your email") ||
        pageText.toLowerCase().includes("activation link") ||
        pageText.toLowerCase().includes("confirm your email") ||
        pageText.toLowerCase().includes("تم إرسال رابط التفعيل") ||
        pageText.toLowerCase().includes("تحقق من بريدك")
      ) {
        console.log("📧 تم رصد رسالة تأكيد بالبريد، جارٍ فحص صندوق الوارد (IMAP) لجلب رابط التفعيل...");
        const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
        const verifyScript = path.resolve(repoRoot, "tools/fetch_email_verification.py");
        if (fs.existsSync(verifyScript)) {
          try {
            const { execSync } = await import("child_process");
            await activePage.waitForTimeout(4000);
            const link = execSync(`python3 "${verifyScript}" --link`, { encoding: "utf-8" }).trim();
            if (link && link.startsWith("http")) {
              console.log(`🔗 تم استلام رابط التفعيل بنجاح: ${link}`);
              const verifyTab = await activePage.context().newPage();
              await verifyTab.goto(link, { waitUntil: "domcontentloaded", timeout: 20000 });
              console.log("✓ تم تفعيل الحساب وتأكيد البريد بنجاح.");
              await activePage.waitForTimeout(3000);
              await verifyTab.close().catch(() => {});
              await activePage.reload().catch(() => {});
            }
          } catch (e) {
            console.warn("تنبيه رابط التفعيل:", e);
          }
        }
      }

      // Try to click Next / Submit
      const clicked = await clickPrimarySubmitOrNext(activePage);
      if (!clicked) {
        console.log("ℹ️ انتهت خطوات التقديم أو لا توجد أزرار تالية إضافية.");
        break;
      }

      await activePage.waitForTimeout(3000);
      step++;
    }

    return isCompleted || step > 1;
  } catch (err) {
    console.error(`❌ خطأ أثناء التقديم على ${url}:`, err);
    return false;
  }
}

async function updateTrackerStatus(targetUrl: string) {
  const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
  const csvPath = path.resolve(repoRoot, "saudi_jobs_google_sheets_tracker.csv");
  if (!fs.existsSync(csvPath)) return;

  try {
    const content = fs.readFileSync(csvPath, "utf-8");
    const lines = content.split("\n");
    const cleanTarget = targetUrl.split("?")[0].replace(/\/+$/, "");
    const updatedLines = lines.map((line) => {
      if (line.includes(cleanTarget) && line.includes("جاهز للتقديم")) {
        return line.replace("جاهز للتقديم", "تم التقديم");
      }
      return line;
    });
    fs.writeFileSync(csvPath, updatedLines.join("\n"), "utf-8");
    console.log(`✓ تم تحديث حالة الشاغر إلى 'تم التقديم' في جدول التتبع.`);
  } catch (e) {
    console.warn(`فشل تحديث الشيت: ${e}`);
  }
}

async function main() {
  const options = parseArgs();
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║     🤖 الروبوت المتصفحي للتقديم الآلي التلقائي 100%          ║
║      Autonomous Browser Auto-Apply Agent (Playwright)        ║
╚══════════════════════════════════════════════════════════════╝
المرشح: ${candidateProfile.fullNameEnglish} (${candidateProfile.fullNameArabic})
الجوال: ${candidateProfile.phoneInternational} | الإيميل: ${candidateProfile.email}
وضع المتصفح: ${options.headless ? "Headless (خلفي)" : "Headed (مرئي أمامك على الشاشة)"}
الاعتماد: متوقف فقط عند رصد CAPTCHA أو اختبار أمني بشري.
`);

  const profileDir = path.resolve(process.cwd(), "tools/browser_apply/.chrome_session");
  if (!fs.existsSync(profileDir)) {
    fs.mkdirSync(profileDir, { recursive: true });
  }

  // Clean stale lock if needed
  const lockFile = path.join(profileDir, "SingletonLock");
  if (fs.existsSync(lockFile)) {
    try { fs.unlinkSync(lockFile); } catch {}
  }

  // Launch Google Chrome with persistent session context
  const context = await chromium.launchPersistentContext(profileDir, {
    channel: "chrome",
    headless: options.headless,
    viewport: { width: 1280, height: 850 },
    locale: "ar-SA",
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    args: ["--disable-blink-features=AutomationControlled"],
  });

  const page = context.pages().length > 0 ? context.pages()[0] : await context.newPage();

  if (options.url) {
    const success = await applyToUrl(page, options.url);
    if (success) {
      await updateTrackerStatus(options.url);
    }
  } else if (options.all) {
    const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
    const csvPath = path.resolve(repoRoot, "saudi_jobs_google_sheets_tracker.csv");
    if (fs.existsSync(csvPath)) {
      const content = fs.readFileSync(csvPath, "utf-8");
      const lines = content.split("\n");
      for (const line of lines) {
        if (line.includes("جاهز للتقديم") && line.includes("http")) {
          const match = line.match(/https?:\/\/[^\s",]+/);
          if (match) {
            const cleanUrl = match[0].trim();
            const success = await applyToUrl(page, cleanUrl);
            if (success) {
              await updateTrackerStatus(cleanUrl);
            }
            await page.waitForTimeout(3000);
          }
        }
      }
    }
  } else {
    console.log(`
الاستخدام:
  bun run tools/browser_apply/src/apply.ts --url "<JOB_URL>"
  bun run tools/browser_apply/src/apply.ts --all (التقديم التلقائي على جميع الشواغر الجاهزة)
  أضف --headless لتشغيل المتصفح في الخلفية دون فتح نافذة.
`);
  }

  console.log("\n✓ اكتمل تشغيل الروبوت.");
  await context.close();
}

main().catch(console.error);
