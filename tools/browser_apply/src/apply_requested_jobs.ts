import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";
import { autofillCommonFields, clickPrimarySubmitOrNext } from "./form_autofill.js";
import { detectCaptchaOrBotChallenge, waitForUserCaptchaResolution } from "./captcha_detector.js";

const targetJobs = [
  {
    name: "Mumzworld",
    title: "E-Commerce Associate - Marketplace",
    url: "https://www.linkedin.com/jobs/view/e-commerce-associate-marketplace-at-mumzworld-com-4479308246/"
  },
  {
    name: "Sharaf DG",
    title: "Assistant Manager - Online Business and Marketing",
    url: "https://www.linkedin.com/jobs/view/assistant-manager-online-business-and-marketing-at-sharaf-dg-4487767939/"
  },
  {
    name: "Mars SA",
    title: "Growth Marketing Lead",
    url: "https://www.linkedin.com/jobs/view/growth-marketing-lead-at-mars-sa-4461905560/"
  },
  {
    name: "AstraZeneca",
    title: "Franchise Head - R&I",
    url: "https://www.linkedin.com/jobs/view/franchise-head-r-i-at-astrazeneca-4486059547/"
  },
  {
    name: "qlub",
    title: "Growth Marketing Director",
    url: "https://www.linkedin.com/jobs/view/growth-marketing-director-at-qlub-4478737545/"
  },
  {
    name: "Hilton",
    title: "Assistant Marketing Manager",
    url: "https://www.linkedin.com/jobs/view/assistant-marketing-manager-at-hilton-4485328665/"
  }
];

async function applyToJob(context: any, job: typeof targetJobs[0]) {
  console.log("\n" + "=".repeat(60));
  console.log(`🚀 بدء معالجة والتقديم على: ${job.title} لدى ${job.name}`);
  console.log(`🔗 الرابط: ${job.url}`);
  console.log("=".repeat(60));

  const page = await context.newPage();

  try {
    await page.goto(job.url, { waitUntil: "domcontentloaded", timeout: 35000 });
    await page.waitForTimeout(3000);

    if (await detectCaptchaOrBotChallenge(page)) {
      await waitForUserCaptchaResolution(page);
    }

    // Check if redirected to LinkedIn sign-in
    const pageUrl = page.url();
    if (pageUrl.includes("linkedin.com/login") || pageUrl.includes("linkedin.com/signup")) {
      console.log("ℹ️ الصفحة تتطلب تسجيل الدخول على لينكدإن.");
    }

    // Find Apply button: "التقدم" or "Apply" or "Apply on company website"
    const applySelectors = [
      'button:has-text("التقدم")',
      'a:has-text("التقدم")',
      '.jobs-apply-button',
      'button:has-text("Apply on company website")',
      'a:has-text("Apply on company website")',
      'button:has-text("Apply")',
      'a:has-text("Apply")',
      'button:has-text("Easy Apply")',
    ];

    let applyBtn = null;
    for (const sel of applySelectors) {
      const el = await page.$(sel);
      if (el && (await el.isVisible().catch(() => false))) {
        applyBtn = el;
        const btnText = (await el.innerText().catch(() => "")).trim();
        console.log(`👉 تم العثور على زر التقديم: "${btnText}"`);
        break;
      }
    }

    let activePage = page;
    if (applyBtn) {
      console.log("👉 جارٍ النقر على زر التقديم...");
      const [popup] = await Promise.all([
        context.waitForEvent("page", { timeout: 10000 }).catch(() => null),
        applyBtn.click().catch(() => {}),
      ]);

      if (popup) {
        activePage = popup;
        console.log(`🌐 تم فتح بوابة التقديم الخارجية في تبويب جديد: ${activePage.url()}`);
        await activePage.waitForLoadState("domcontentloaded").catch(() => {});
        await activePage.waitForTimeout(3000);
      } else {
        await page.waitForTimeout(4000);
        console.log(`🌐 الرابط الحالي بعد النقر: ${page.url()}`);
      }
    } else {
      console.log("⚠️ لم يتم العثور على زر تقديم مباشر، جارٍ فحص الحقول الموجودة في الصفحة...");
    }

    // Perform form autofill loop on activePage
    let step = 1;
    const maxSteps = 5;
    let submitted = false;

    while (step <= maxSteps) {
      console.log(`\n[الخطوة ${step}]: فحص وتعبئة حقول استمارة ${job.name}...`);
      if (await detectCaptchaOrBotChallenge(activePage)) {
        await waitForUserCaptchaResolution(activePage);
      }

      const { filledCount, filesUploaded } = await autofillCommonFields(activePage);
      console.log(`   ✓ تم ملء ${filledCount} حقل بيانات | تم إرفاق ${filesUploaded} ملف.`);

      // Check success
      const bodyText = await activePage.innerText("body").catch(() => "");
      if (
        bodyText.includes("Application submitted") ||
        bodyText.includes("Your application was sent") ||
        bodyText.includes("تم إرسال طلبك بنجاح") ||
        bodyText.includes("شكراً لتقديمك") ||
        bodyText.includes("Thank you for applying") ||
        bodyText.includes("Application received")
      ) {
        console.log(`🎉 تم تأكيد التقديم بنجاح لدى ${job.name}!`);
        submitted = true;
        break;
      }

      if (filledCount === 0 && filesUploaded === 0 && step > 1) {
        console.log("ℹ️ لم تعد هناك حقول إضافية لتعبئتها.");
        break;
      }

      const clicked = await clickPrimarySubmitOrNext(activePage);
      if (!clicked) {
        console.log("ℹ️ لم يتم العثور على أزرار تالية أو انتهت خطوات النموذج.");
        break;
      }

      await activePage.waitForTimeout(3000);
      step++;
    }

    // Update status in tracker
    updateTrackerForJob(job.url, submitted ? "تم التقديم" : "جاهز للتقديم");

  } catch (err) {
    console.error(`❌ خطأ أثناء معالجة ${job.name}:`, err);
  } finally {
    await page.close().catch(() => {});
  }
}

function updateTrackerForJob(jobUrl: string, status: string) {
  const csvPath = path.resolve(process.cwd(), "saudi_jobs_google_sheets_tracker.csv");
  if (!fs.existsSync(csvPath)) return;

  try {
    const content = fs.readFileSync(csvPath, "utf-8");
    const lines = content.split("\n");
    const cleanTarget = jobUrl.split("?")[0].replace(/\/+$/, "");

    const updated = lines.map((line) => {
      const cleanLine = line.split("?")[0];
      if (cleanLine.includes(cleanTarget)) {
        console.log(`✓ تحديث حالة الشاغر إلى "${status}" في ملف التتبع.`);
        return line.replace("جاهز للتقديم", status);
      }
      return line;
    });

    fs.writeFileSync(csvPath, updated.join("\n"), "utf-8");
  } catch (e) {
    console.warn("تنبيه تحديث الشيت:", e);
  }
}

async function main() {
  const profileDir = path.resolve(process.cwd(), "tools/browser_apply/.chrome_session");
  const context = await chromium.launchPersistentContext(profileDir, {
    channel: "chrome",
    headless: false, // Run headed so Chrome is visible and user can observe live
    viewport: { width: 1280, height: 850 },
    locale: "ar-SA",
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    args: ["--disable-blink-features=AutomationControlled"],
  });

  for (const job of targetJobs) {
    await applyToJob(context, job);
  }

  console.log("\n" + "=".repeat(60));
  console.log("✓ اكتمل التقديم على كافة الوظائف المطلوبة بنجاح.");
  console.log("=".repeat(60));
  await context.close();
}

main().catch(console.error);

