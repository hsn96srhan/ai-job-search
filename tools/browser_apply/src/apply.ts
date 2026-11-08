#!/usr/bin/env bun
import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";
import { detectCaptchaOrBotChallenge, waitForUserCaptchaResolution } from "./captcha_detector.js";
import { autofillCommonFields, clickPrimarySubmitOrNext } from "./form_autofill.js";

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

async function applyToUrl(page: any, url: string): Promise<boolean> {
  console.log(`\n============================================================`);
  console.log(`🌐 بدء التقديم الآلي الذكي على: ${url}`);
  console.log(`============================================================`);

  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(3000);

    // 1. CAPTCHA Check
    if (await detectCaptchaOrBotChallenge(page)) {
      await waitForUserCaptchaResolution(page);
    }

    // 2. Check for LinkedIn Easy Apply (Strict User Rule: Never auto-submit Easy Apply, leave for candidate manual submit)
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
      console.log(`ℹ️ [استبعاد آلي للتقديم السريع] الشاغر (${url}) يعتمد Easy Apply (التقديم السريع عبر لينكدإن).`);
      console.log(`📌 توجيه المرشح الصارم: يتم إبقاؤه بحالة 'جاهز للتقديم' للتقديم اليدوي السريع من قِبل المرشح.`);
      return false; // strictly skip auto-apply, keep as ready
    }

    // 3. External Career Site Apply Buttons (LinkedIn Arabic & English)
    const externalApplySelectors = [
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
        pageText.includes("Thank you for applying")
      ) {
        console.log("🎉 تم تأكيد إرسال الطلب في موقع الشركة بنجاح 100%!");
        isCompleted = true;
        break;
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
    const updatedLines = lines.map((line) => {
      if (line.includes(targetUrl) && line.includes("جاهز للتقديم")) {
        return line.replace("جاهز للتقديم", "تم التقديم");
      }
      return line;
    });
    fs.writeFileSync(csvPath, updatedLines.join("\n"), "utf-8");
    console.log(`✓ تم تحديث حالة الشاغر إلى 'تم التقديم' في ملف التتبع والشيت!`);
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

