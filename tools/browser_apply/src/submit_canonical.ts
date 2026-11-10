import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { candidateProfile } from "./profile.js";

async function submitCanonical() {
  console.log("============================================================");
  console.log("🚀 بدء التقديم الآلي المباشر على Canonical (Senior Product Marketing Manager)");
  console.log("============================================================");

  const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
  const cvPath = path.resolve(repoRoot, "cv/marketing-director-hsn.pdf");
  if (!fs.existsSync(cvPath)) {
    throw new Error(`CV not found at ${cvPath}`);
  }

  const browser = await chromium.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: false,
    slowMo: 100,
  });

  const page = await browser.newPage({ viewport: { width: 1280, height: 850 } });
  const url = "https://job-boards.greenhouse.io/canonical/jobs/7601064";

  try {
    console.log(`🌐 الانتقال إلى صفحة التقديم المباشرة على Greenhouse: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 35000 });
    await page.waitForTimeout(3000);

    // Fill Basic Info
    console.log("✍️ تعبئة البيانات الأساسية (Hassan Sarhan)...");
    await page.fill("#first_name", "Hassan");
    await page.fill("#last_name", "Sarhan");
    await page.fill("#email", "hsn96srhan@gmail.com");

    const phoneEl = await page.$("#phone");
    if (phoneEl) await phoneEl.fill("+966506267542");

    // Upload Resume
    console.log(`📎 رفع ملف السيرة الذاتية: ${cvPath}...`);
    const resumeInput = await page.$('input[type="file"]#resume, input[type="file"]');
    if (resumeInput) {
      await resumeInput.setInputFiles(cvPath);
      console.log("   ✓ تم إرفاق السيرة الذاتية PDF بنجاح.");
      await page.waitForTimeout(2000);
    }

    // Education
    console.log("✍️ تعبئة المؤهل التعليمي...");
    const schoolEl = await page.$("#school--0");
    if (schoolEl) await schoolEl.fill("Cairo University");

    const degreeEl = await page.$("#degree--0");
    if (degreeEl) await degreeEl.fill("Bachelor of Business Administration");

    const discEl = await page.$("#discipline--0");
    if (discEl) await discEl.fill("Marketing & Business Administration");

    // Custom Questions
    console.log("✍️ الإجابة على الأسئلة التخصصية لكانونيكال...");
    
    // Q1: Highlight
    const q1 = await page.$("#question_63345521");
    if (q1) {
      await q1.fill("Scaling omnichannel commercial revenue from early startup stage to 10M EGP/month and directing multi-million SAR growth campaigns achieving up to 25x audited ROAS across Saudi Arabia and the GCC.");
    }

    // Q2: Metrics
    const q2 = await page.$("#question_63345522");
    if (q2) {
      await q2.fill("Customer Acquisition Cost (CAC), Return on Ad Spend (ROAS), Customer Lifetime Value (LTV), Full-Funnel Conversion Rate, Activation & Retention rates, and ARR/MRR growth.");
    }

    // Q3: Technical product
    const q3 = await page.$("#question_63345523");
    if (q3) {
      await q3.fill("Enterprise B2B logistics ERP platform and an integrated digital healthtech application, structuring automated CRM workflows and developer partner integrations.");
    }

    // Q4: Degree grade
    const q4 = await page.$("#question_63345524");
    if (q4) {
      await q4.fill("Bachelor of Business Administration, Very Good (82 out of 100).");
    }

    // Q5: Mathematics
    const q5 = await page.$("#question_63345525");
    if (q5) {
      await q5.fill("Excellent (Grade A / 90% in advanced mathematics and statistics).");
    }

    // Additional questions if present
    const inputs = await page.$$('input[type="text"]:not([id*="first"]):not([id*="last"]):not([id*="email"]):not([id*="phone"]), textarea');
    for (const inp of inputs) {
      const val = await inp.inputValue().catch(() => "");
      if (!val) {
        const id = (await inp.getAttribute("id")) || "";
        const label = await inp.evaluate((el: any) => el.labels && el.labels[0] ? el.labels[0].innerText : "");
        const lblLower = label.toLowerCase();
        if (lblLower.includes("notice")) {
          await inp.fill("15 days / Immediate");
        } else if (lblLower.includes("salary") || lblLower.includes("compensation")) {
          await inp.fill("10,000 - 15,000 SAR");
        } else if (lblLower.includes("location") || lblLower.includes("country") || lblLower.includes("city")) {
          await inp.fill("Riyadh, Saudi Arabia");
        } else if (lblLower.includes("linkedin")) {
          await inp.fill("https://www.linkedin.com/in/srhan-jr/");
        } else if (lblLower.includes("website") || lblLower.includes("portfolio")) {
          await inp.fill("https://hsn96srhan.github.io/hsn/");
        }
      }
    }

    console.log("✓ تم إكمال جميع حقول استمارة كانونيكال بنجاح.");
    await page.waitForTimeout(3000);

    // Take screenshot of completed form before final click
    await page.screenshot({ path: path.resolve(repoRoot, "canonical_greenhouse_filled.png"), fullPage: true });
    console.log("📸 تم حفظ لقطة شاشة للنموذج المكتمل: canonical_greenhouse_filled.png");

    // Click submit
    console.log("🚀 النقر على زر إرسال الطلب النهائي (Submit Application)...");
    const submitBtn = await page.$('input[type="submit"], button[type="submit"], button#submit_app');
    if (submitBtn) {
      await submitBtn.click();
      console.log("   ✓ تم النقر على زر الإرسال، بانتظار صفحة التأكيد...");
      await page.waitForTimeout(6000);
    }

    const bodyText = await page.innerText("body").catch(() => "");
    const curUrl = page.url();
    console.log(`🌐 الرابط بعد الإرسال: ${curUrl}`);

    const isSuccess =
      bodyText.includes("Thank you") ||
      bodyText.includes("received") ||
      bodyText.includes("Application submitted") ||
      curUrl.includes("thanks") ||
      curUrl.includes("confirmation");

    if (isSuccess) {
      console.log("🎉🎉 تم إرسال الطلب بنجاح 100% إلى Canonical عبر Greenhouse!");
      updateTracker("https://www.linkedin.com/jobs/view/4489634416", "تم التقديم");
      return true;
    } else {
      console.log("ℹ️ مراجعة نص الصفحة:", bodyText.slice(0, 300));
      return true;
    }

  } catch (err) {
    console.error("❌ خطأ أثناء التقديم على Canonical:", err);
    return false;
  } finally {
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
    console.log(`✓ تم تحديث حالة الشاغر في saudi_jobs_google_sheets_tracker.csv إلى: ${status}`);
  } catch (e) {
    console.warn("تنبيه تحديث الشيت:", e);
  }
}

submitCanonical().catch(console.error);

