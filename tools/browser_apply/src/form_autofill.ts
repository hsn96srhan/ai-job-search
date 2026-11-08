import type { Page } from "playwright";
import { candidateProfile } from "./profile.js";
import fs from "fs";
import path from "path";

export async function autofillCommonFields(page: Page): Promise<{ filledCount: number; filesUploaded: number }> {
  let filledCount = 0;
  let filesUploaded = 0;

  // 1. Text, Email, Tel inputs and Textareas
  const inputs = await page.$$('input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="checkbox"]):not([type="radio"]), textarea');

  for (const input of inputs) {
    try {
      const isVisible = await input.isVisible();
      if (!isVisible) continue;

      const name = (await input.getAttribute("name"))?.toLowerCase() || "";
      const id = (await input.getAttribute("id"))?.toLowerCase() || "";
      const placeholder = (await input.getAttribute("placeholder"))?.toLowerCase() || "";
      const ariaLabel = (await input.getAttribute("aria-label"))?.toLowerCase() || "";
      const type = (await input.getAttribute("type"))?.toLowerCase() || "text";

      const descriptor = `${name} ${id} ${placeholder} ${ariaLabel}`.toLowerCase();

      // Check current value
      const val = await input.inputValue().catch(() => "");
      if (val && val.length > 0) continue;

      // Password / Confirm Password (for ATS account creation e.g. Workday/Taleo/Greenhouse/Oracle HCM)
      if (type === "password" || descriptor.includes("password") || descriptor.includes("كلمة المرور") || descriptor.includes("السر")) {
        await input.fill(candidateProfile.defaultAccountPassword);
        filledCount++;
        console.log(`   ✓ تم إدخال كلمة مرور الحساب الآمنة تلقائياً.`);
        continue;
      }

      // OTP / Verification Code (e.g. Oracle HCM / Hilton / Corporate Verification)
      if (descriptor.includes("verification") || descriptor.includes("passcode") || descriptor.includes("رمز التحقق") || descriptor.includes("otp") || descriptor.includes("code")) {
        // Try to fetch latest OTP from candidate's Gmail inbox via IMAP
        const repoRoot = path.resolve(process.cwd(), process.cwd().endsWith("browser_apply") ? "../.." : ".");
        const otpScript = path.resolve(repoRoot, "tools/fetch_hilton_otp.py");
        if (fs.existsSync(otpScript)) {
          try {
            const { execSync } = await import("child_process");
            const otpCode = execSync(`python3 "${otpScript}"`, { encoding: "utf-8" }).trim();
            if (otpCode && /^\d{4,8}$/.test(otpCode)) {
              await input.fill(otpCode);
              filledCount++;
              console.log(`   ✓ تم استلام وإدخال رمز التحقق الأمني (OTP) تلقائياً من البريد: ${otpCode}`);
              continue;
            }
          } catch {}
        }
      }

      // Email
      if (type === "email" || descriptor.includes("email") || descriptor.includes("بريد") || descriptor.includes("إيميل")) {
        await input.fill(candidateProfile.email);
        filledCount++;
        continue;
      }

      // Phone
      if (type === "tel" || descriptor.includes("phone") || descriptor.includes("mobile") || descriptor.includes("جوال") || descriptor.includes("هاتف")) {
        await input.fill(candidateProfile.phoneInternational);
        filledCount++;
        continue;
      }

      // Nationality
      if (descriptor.includes("nationality") || descriptor.includes("جنسية") || descriptor.includes("الجنسية")) {
        await input.fill(descriptor.includes("جنسية") ? candidateProfile.nationalityArabic : candidateProfile.nationalityEnglish);
        filledCount++;
        continue;
      }

      // Religion
      if (descriptor.includes("religion") || descriptor.includes("ديانة") || descriptor.includes("الدين")) {
        await input.fill(descriptor.includes("ديانة") || descriptor.includes("الدين") ? candidateProfile.religionArabic : candidateProfile.religionEnglish);
        filledCount++;
        continue;
      }

      // Marital Status
      if (descriptor.includes("marital") || descriptor.includes("الحالة الاجتماعية") || descriptor.includes("اجتماعية")) {
        await input.fill(descriptor.includes("اجتماعية") ? candidateProfile.maritalStatusArabic : candidateProfile.maritalStatusEnglish);
        filledCount++;
        continue;
      }

      // Current Basic Salary
      if (descriptor.includes("current basic") || descriptor.includes("current salary") || descriptor.includes("الراتب الحالي") || descriptor.includes("الأساسي الحالي")) {
        await input.fill(candidateProfile.currentBasicSalary.toString());
        filledCount++;
        continue;
      }

      // Current Housing Allowance
      if (descriptor.includes("housing") || descriptor.includes("بدل سكن") || descriptor.includes("سكن")) {
        await input.fill(candidateProfile.currentHousingAllowance.toString());
        filledCount++;
        continue;
      }

      // Expected Basic Salary
      if (descriptor.includes("expected basic") || descriptor.includes("basic salary") || descriptor.includes("الأساسي المتوقع") || descriptor.includes("الراتب الأساسي")) {
        await input.fill(candidateProfile.expectedBasicSalary.toString());
        filledCount++;
        continue;
      }

      // Total Expected Package / Salary
      if (descriptor.includes("package") || descriptor.includes("total salary") || descriptor.includes("expected salary") || descriptor.includes("شامل") || descriptor.includes("الراتب المتوقع") || descriptor.includes("الراتب")) {
        await input.fill(candidateProfile.expectedTotalSalaryPackage.toString());
        filledCount++;
        continue;
      }

      // Benefits details
      if (descriptor.includes("benefit") || descriptor.includes("مزايا") || descriptor.includes("بدلات")) {
        await input.fill(candidateProfile.currentTotalBenefitsDescription);
        filledCount++;
        continue;
      }

      // First Name
      if (descriptor.includes("first") || descriptor.includes("fname") || descriptor.includes("الاسم الأول")) {
        await input.fill(candidateProfile.firstName);
        filledCount++;
        continue;
      }

      // Last Name
      if (descriptor.includes("last") || descriptor.includes("lname") || descriptor.includes("surname") || descriptor.includes("العائلة") || descriptor.includes("اللقب")) {
        await input.fill(candidateProfile.lastName);
        filledCount++;
        continue;
      }

      // Full Name
      if (descriptor.includes("full") || descriptor.includes("name") || descriptor.includes("الاسم")) {
        await input.fill(candidateProfile.fullNameEnglish);
        filledCount++;
        continue;
      }

      // City / Location / Address
      if (descriptor.includes("city") || descriptor.includes("location") || descriptor.includes("مدينة") || descriptor.includes("عنوان") || descriptor.includes("الرياض")) {
        await input.fill(candidateProfile.currentAddress);
        filledCount++;
        continue;
      }

      // LinkedIn Profile
      if (descriptor.includes("linkedin") || descriptor.includes("لينكد")) {
        await input.fill(candidateProfile.linkedInUrl);
        filledCount++;
        continue;
      }

      // Portfolio / Website
      if (descriptor.includes("website") || descriptor.includes("portfolio") || descriptor.includes("site") || descriptor.includes("موقع") || descriptor.includes("معرض")) {
        await input.fill(candidateProfile.portfolioUrl);
        filledCount++;
        continue;
      }

      // Years of Experience
      if (descriptor.includes("experience") || descriptor.includes("years") || descriptor.includes("خبرة") || descriptor.includes("سنوات")) {
        await input.fill(candidateProfile.yearsOfExperience.toString());
        filledCount++;
        continue;
      }

      // Notice Period / Availability
      if (descriptor.includes("notice") || descriptor.includes("availability") || descriptor.includes("إشعار") || descriptor.includes("جاهزية")) {
        await input.fill(candidateProfile.noticePeriod);
        filledCount++;
        continue;
      }
    } catch {
      // Ignore individual element errors
    }
  }

  // 2. Select Dropdowns (Dropdown matching for Nationality, Gender, Marital Status, Country)
  const selects = await page.$$("select");
  for (const sel of selects) {
    try {
      const isVisible = await sel.isVisible();
      if (!isVisible) continue;

      const name = (await sel.getAttribute("name"))?.toLowerCase() || "";
      const id = (await sel.getAttribute("id"))?.toLowerCase() || "";
      const ariaLabel = (await sel.getAttribute("aria-label"))?.toLowerCase() || "";
      const descriptor = `${name} ${id} ${ariaLabel}`.toLowerCase();

      // Nationality select
      if (descriptor.includes("nationality") || descriptor.includes("جنسية")) {
        await sel.selectOption({ label: "Egyptian" }).catch(() => sel.selectOption({ label: "مصر" }));
        filledCount++;
        continue;
      }

      // Country of Residence
      if (descriptor.includes("country") || descriptor.includes("دولة") || descriptor.includes("بلد")) {
        await sel.selectOption({ label: "Saudi Arabia" }).catch(() => sel.selectOption({ label: "المملكة العربية السعودية" }));
        filledCount++;
        continue;
      }

      // Gender
      if (descriptor.includes("gender") || descriptor.includes("جنس") || descriptor.includes("نوع")) {
        await sel.selectOption({ label: "Male" }).catch(() => sel.selectOption({ label: "ذكر" }));
        filledCount++;
        continue;
      }

      // Marital Status
      if (descriptor.includes("marital") || descriptor.includes("اجتماعية")) {
        await sel.selectOption({ label: "Married" }).catch(() => sel.selectOption({ label: "متزوج" }));
        filledCount++;
        continue;
      }

      // Religion select
      if (descriptor.includes("religion") || descriptor.includes("ديانة") || descriptor.includes("دين")) {
        await sel.selectOption({ label: "Muslim" })
          .catch(() => sel.selectOption({ label: "مسلم" }))
          .catch(() => sel.selectOption({ label: "Islam" }))
          .catch(() => sel.selectOption({ label: "الإسلام" }));
        filledCount++;
        continue;
      }

      // Iqama / Sponsorship Transfer select
      if (descriptor.includes("iqama") || descriptor.includes("sponsorship") || descriptor.includes("إقامة") || descriptor.includes("كفالة")) {
        await sel.selectOption({ label: "Transferable" })
          .catch(() => sel.selectOption({ label: "قابل للتحويل" }))
          .catch(() => sel.selectOption({ label: "نعم" }))
          .catch(() => sel.selectOption({ label: "Yes" }));
        filledCount++;
        continue;
      }

      // Driving License select
      if (descriptor.includes("license") || descriptor.includes("driving") || descriptor.includes("قيادة") || descriptor.includes("رخصة")) {
        await sel.selectOption({ label: "Yes" })
          .catch(() => sel.selectOption({ label: "نعم" }))
          .catch(() => sel.selectOption({ label: "Valid Saudi License" }));
        filledCount++;
        continue;
      }

      // Notice Period dropdown
      if (descriptor.includes("notice") || descriptor.includes("availability") || descriptor.includes("إشعار")) {
        await sel.selectOption({ index: 1 }).catch(() => {});
        filledCount++;
        continue;
      }
    } catch {
      // Ignore select error
    }
  }

  // 3. Upload CV / Resume
  const fileInputs = await page.$$('input[type="file"]');
  if (fileInputs.length > 0 && fs.existsSync(candidateProfile.masterCvPdfPath)) {
    for (const fileInput of fileInputs) {
      try {
        await fileInput.setInputFiles(candidateProfile.masterCvPdfPath);
        filesUploaded++;
        console.log(`✓ تم إرفاق السيرة الذاتية PDF تلقائياً: ${candidateProfile.masterCvPdfPath}`);
      } catch (e) {
        console.warn(`فشل إرفاق الملف: ${e}`);
      }
    }
  }

  // 4. Checkboxes for terms & conditions and agreement
  const checkboxes = await page.$$('input[type="checkbox"]');
  for (const cb of checkboxes) {
    try {
      const isVisible = await cb.isVisible();
      if (!isVisible) continue;
      const isChecked = await cb.isChecked();
      if (!isChecked) {
        await cb.check();
      }
    } catch {
      // Ignore
    }
  }

  // 5. Radio Buttons for common questions (e.g., Transferable Iqama, Driving license, Authorized to work)
  const radioButtons = await page.$$('input[type="radio"]');
  for (const rb of radioButtons) {
    try {
      const isVisible = await rb.isVisible();
      if (!isVisible) continue;
      const val = (await rb.getAttribute("value"))?.toLowerCase() || "";
      const id = (await rb.getAttribute("id"))?.toLowerCase() || "";
      const text = `${val} ${id}`;

      // Select "Yes" for right to work, transferable iqama, driving license
      if (text.includes("yes") || text.includes("true") || text.includes("نعم") || val === "1") {
        await rb.check().catch(() => {});
      }
    } catch {
      // Ignore
    }
  }

  return { filledCount, filesUploaded };
}

export async function clickPrimarySubmitOrNext(page: Page): Promise<boolean> {
  const submitSelectors = [
    'button[type="submit"]',
    'input[type="submit"]',
    'button:has-text("Submit Application")',
    'button:has-text("Submit")',
    'button:has-text("Apply")',
    'button:has-text("Create Account")',
    'button:has-text("Create account")',
    'button:has-text("Sign In")',
    'button:has-text("Continue")',
    'button:has-text("Next")',
    'button:has-text("Review")',
    'button:has-text("تقديم")',
    'button:has-text("إنشاء حساب")',
    'button:has-text("تسجيل الدخول")',
    'button:has-text("إرسال الطلب")',
    'button:has-text("التالي")',
    'button:has-text("متابعة")',
    'button:has-text("حفظ ومتابعة")',
    '.jobs-apply-button',
  ];

  for (const sel of submitSelectors) {
    const btn = await page.$(sel);
    if (btn) {
      const isVisible = await btn.isVisible().catch(() => false);
      const isEnabled = await btn.isEnabled().catch(() => false);
      if (isVisible && isEnabled) {
        const text = (await btn.innerText().catch(() => "")) || "زر الإجراء";
        console.log(`👉 جارٍ الضغط على: "${text.trim()}"`);
        await btn.click({ timeout: 5000 }).catch(() => {});
        await page.waitForTimeout(2000);
        return true;
      }
    }
  }

  return false;
}
