import type { Page } from "playwright";
import readline from "readline";

export async function detectCaptchaOrBotChallenge(page: Page): Promise<boolean> {
  const captchaSelectors = [
    'iframe[src*="recaptcha"]',
    'iframe[src*="hcaptcha"]',
    'iframe[src*="challenges.cloudflare.com"]',
    'iframe[src*="arkoselabs"]',
    'div[class*="recaptcha"]',
    'div[class*="h-captcha"]',
    '#cf-challenge-running',
    '#challenge-stage',
    '.cf-turnstile-wrapper',
  ];

  for (const sel of captchaSelectors) {
    const el = await page.$(sel);
    if (el) {
      const isVisible = await el.isVisible().catch(() => false);
      if (isVisible) return true;
    }
  }

  // Check text indicators
  const pageText = await page.innerText("body").catch(() => "");
  const triggers = [
    "verify you are human",
    "security verification",
    "please solve this challenge",
    "enter the characters you see",
    "bot detection",
    "اثبت انك لست روبوت",
    "التحقق من أنك إنسان",
    "يرجى تأكيد أنك لست برنامج روبوت",
  ];

  const lower = pageText.toLowerCase();
  for (const trigger of triggers) {
    if (lower.includes(trigger)) {
      return true;
    }
  }

  return false;
}

export async function waitForUserCaptchaResolution(page: Page): Promise<void> {
  console.log("\n" + "=".repeat(65));
  console.log("⚠️  تنبيه أمني: تم اكتشاف اختبار أمني (CAPTCHA / Anti-Bot Challenge)");
  console.log("⏸️  توقف البوت تلقائياً للسماح لك بحل الاختبار يدوياً في نافذة المتصفح المفتوحة.");
  console.log("👉 بمجرد الانتهاء من حل الكاباتشا، اضغط [Enter] في هذا الطرف للمتابعة...");
  console.log("=".repeat(65) + "\n");

  // Wait for user to hit Enter in terminal
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  await new Promise<void>((resolve) => {
    rl.question("اضغط [Enter] بعد حل الكاباتشا: ", () => {
      rl.close();
      resolve();
    });
  });

  console.log("✓ تم الاستئناف من قبل المستخدم. جارٍ استكمال التقديم التلقائي...");
  await page.waitForTimeout(2000);
}

