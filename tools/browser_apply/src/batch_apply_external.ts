import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";
import { detectCaptchaOrBotChallenge, waitForUserCaptchaResolution } from "./captcha_detector.js";
import { autofillCommonFields, clickPrimarySubmitOrNext } from "./form_autofill.js";

const externalJobs = [
  {
    id: "SA-005",
    company: "Savills Middle East",
    title: "Senior Marketing Executive (KAFD)",
    url: "https://careers.savills.me/jobs/8662184-senior-marketing-executive/applications/new",
    fallbackUrl: "https://www.linkedin.com/jobs/view/4487263154"
  },
  {
    id: "SA-008",
    company: "Red Sea Global (شركة البحر الأحمر الدولية)",
    title: "Associate Director - Residential Marketing",
    url: "https://www.linkedin.com/jobs/view/4482280905",
    fallbackUrl: "https://www.redseaglobal.com/en/careers"
  },
  {
    id: "SA-013",
    company: "IHG Hotels & Resorts",
    title: "Marketing Executive",
    url: "https://sa.linkedin.com/jobs/view/marketing-executive-at-ihg-hotels-resorts-4438013067",
    fallbackUrl: "https://careers.ihg.com"
  },
  {
    id: "SA-024",
    company: "Calo Inc.",
    title: "Commercial Director (KSA)",
    url: "https://sa.linkedin.com/jobs/view/commercial-director-ksa-at-calo-inc-4448269583",
    fallbackUrl: "https://apply.workable.com/calo/"
  },
  {
    id: "SA-027",
    company: "IHG Hotels & Resorts",
    title: "Director of Sales & Marketing",
    url: "https://sa.linkedin.com/jobs/view/director-of-sales-marketing-at-ihg-hotels-resorts-4272153246",
    fallbackUrl: "https://careers.ihg.com"
  },
  {
    id: "SA-029",
    company: "IHG Hotels & Resorts",
    title: "Commercial Director",
    url: "https://sa.linkedin.com/jobs/view/commercial-director-at-ihg-hotels-resorts-4476040193",
    fallbackUrl: "https://careers.ihg.com"
  },
  {
    id: "SA-034",
    company: "dentsu",
    title: "Performance Manager",
    url: "https://sa.linkedin.com/jobs/view/performance-manager-at-dentsu-4322076341",
    fallbackUrl: "https://dentsu.wd3.myworkdayjobs.com/Careers"
  },
  {
    id: "SA-038",
    company: "dentsu",
    title: "Senior Performance Executive",
    url: "https://sa.linkedin.com/jobs/view/senior-performance-executive-at-dentsu-4322166193",
    fallbackUrl: "https://dentsu.wd3.myworkdayjobs.com/Careers"
  },
  {
    id: "SA-041",
    company: "dentsu",
    title: "Performance Manager",
    url: "https://sa.linkedin.com/jobs/view/performance-manager-at-dentsu-4379681411",
    fallbackUrl: "https://dentsu.wd3.myworkdayjobs.com/Careers"
  },
  {
    id: "SA-042",
    company: "Fragomen",
    title: "Regional Marketing Manager (ME)",
    url: "https://sa.linkedin.com/jobs/view/regional-marketing-manager-me-at-fragomen-4487270049",
    fallbackUrl: "https://fragomen.wd1.myworkdayjobs.com"
  },
  {
    id: "SA-045",
    company: "PepsiCo",
    title: "Digital Analyst",
    url: "https://sa.linkedin.com/jobs/view/digital-analyst-at-pepsico-4481449399",
    fallbackUrl: "https://www.pepsicojobs.com"
  }
];

function updateTrackerStatus(jobId: string, status: string, notes: string) {
  const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
  const csvPath = path.resolve(repoRoot, "saudi_jobs_google_sheets_tracker.csv");
  if (!fs.existsSync(csvPath)) return;

  try {
    const content = fs.readFileSync(csvPath, "utf-8");
    const lines = content.split("\n");
    const updated = lines.map(line => {
      if (line.startsWith(`${jobId},`)) {
        const parts = line.split(",");
        // Column 9 (index 9) is status, Column 14 (index 14) is notes
        // Safer replacement:
        return line.replace("جاهز للتقديم", status);
      }
      return line;
    });
    fs.writeFileSync(csvPath, updated.join("\n"), "utf-8");
    console.log(`   ✓ تم تحديث حالة ${jobId} في جدول التتبع إلى: '${status}'`);
  } catch (e) {
    console.warn("خطأ في تحديث الجدول:", e);
  }
}

async function processJob(context: any, job: typeof externalJobs[0]) {
  console.log("\n" + "=".repeat(65));
  console.log(`🚀 [${job.id}] بدء معالجة والتقديم على: ${job.title} لدى ${job.company}`);
  console.log(`🔗 الرابط: ${job.url}`);
  console.log("=".repeat(65));

  const page = await context.newPage();

  try {
    await page.goto(job.url, { waitUntil: "domcontentloaded", timeout: 35000 });
    await page.waitForTimeout(3000);

    // Check CAPTCHA
    if (await detectCaptchaOrBotChallenge(page)) {
      console.log("⚠️ تم رصد اختبار أمني/كابتشا، بانتظار الحل...");
      await waitForUserCaptchaResolution(page);
    }

    // Check if on LinkedIn and has offsite apply button
    let activePage = page;
    const applySelectors = [
      'button.top-card-layout__cta--primary',
      'a.top-card-layout__cta--primary',
      'button:has-text("Apply on company website")',
      'a:has-text("Apply on company website")',
      'button:has-text("التقدم")',
      'a:has-text("التقدم")',
      'button:has-text("Apply now")',
      'a:has-text("Apply now")',
      'button:has-text("Apply")',
      'a:has-text("Apply")',
    ];

    for (const sel of applySelectors) {
      const btn = await page.$(sel);
      if (btn && (await btn.isVisible().catch(() => false))) {
        const btnText = (await btn.innerText().catch(() => "")) || "Apply";
        console.log(`👉 تم العثور على زر التقديم: "${btnText.trim()}"، جارٍ النقر والانتقال...`);
        const [popup] = await Promise.all([
          context.waitForEvent("page", { timeout: 8000 }).catch(() => null),
          btn.click().catch(() => {}),
        ]);

        if (popup) {
          activePage = popup;
          console.log(`🌐 تم فتح بوابة التقديم في تبويب جديد: ${activePage.url()}`);
          await activePage.waitForLoadState("domcontentloaded").catch(() => {});
          await activePage.waitForTimeout(3000);
        } else {
          await page.waitForTimeout(3000);
        }
        break;
      }
    }

    // Step-by-step form autofill
    let step = 1;
    let maxSteps = 5;
    let submitted = false;

    while (step <= maxSteps) {
      console.log(`   [خطوة ${step}]: تعبئة الحقول ورفع السيرة الذاتية...`);

      if (await detectCaptchaOrBotChallenge(activePage)) {
        await waitForUserCaptchaResolution(activePage);
      }

      const { filledCount, filesUploaded } = await autofillCommonFields(activePage);
      console.log(`   ✓ تم ملء ${filledCount} حقول بيانات | تم رفع ${filesUploaded} ملفات.`);

      const pageText = await activePage.innerText("body").catch(() => "");
      if (
        pageText.includes("Thank you for applying") ||
        pageText.includes("Application submitted") ||
        pageText.includes("Your application was sent") ||
        pageText.includes("تم إرسال طلبك بنجاح") ||
        pageText.includes("شكراً لتقديمك")
      ) {
        console.log(`🎉 [نجاح رسمي 100%] تم تأكيد إرسال الطلب لدى ${job.company}!`);
        submitted = true;
        break;
      }

      const nextClicked = await clickPrimarySubmitOrNext(activePage);
      if (!nextClicked) {
        console.log("   ℹ️ لا توجد خطوات إضافية في هذا النموذج.");
        break;
      }

      await activePage.waitForTimeout(3000);
      step++;
    }

    if (submitted) {
      updateTrackerStatus(job.id, "تم التقديم", `تم التقديم بنجاح عبر بوابة ATS المستقلة لـ ${job.company}`);
    } else {
      console.log(`ℹ️ [حالة ${job.id}] تم فحص البوابة وتعبئة البيانات الأولية (تحت المتابعة).`);
    }

  } catch (err) {
    console.error(`❌ خطأ أثناء معالجة ${job.id} (${job.company}):`, err);
  } finally {
    await page.close().catch(() => {});
  }
}

async function runBatch() {
  console.log(`
╔═════════════════════════════════════════════════════════════════════════╗
║  🚀 بدء تشغيل روبوت التقديم الآلي الذكي على الـ 11 بوابة خارجية دفعة واحدة  ║
╚═════════════════════════════════════════════════════════════════════════╝
المرشح: ${candidateProfile.fullNameEnglish} (${candidateProfile.fullNameArabic})
الجوال: ${candidateProfile.phoneInternational} | البريد: ${candidateProfile.email}
عدد الشواغر الخارجية المستهدفة: ${externalJobs.length} شواغر
`);

  const browser = await chromium.launch({
    channel: "chrome",
    headless: false, // User sees browser executing
    slowMo: 80,
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 850 },
    locale: "ar-SA",
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
  });

  for (const job of externalJobs) {
    await processJob(context, job);
    await new Promise(r => setTimeout(r, 2000));
  }

  await browser.close();
  console.log("\n============================================================");
  console.log("✓ اكتمل تشغيل دفعة التقديم الآلي على البوابات الخارجية بالكامل.");
  console.log("============================================================");
}

runBatch().catch(console.error);
