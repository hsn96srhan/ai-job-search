import path from "path";

export interface CandidateCorporateProfile {
  // Personal
  fullNameArabic: string;
  fullNameEnglish: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  phoneInternational: string;
  nationalityArabic: string;
  nationalityEnglish: string;
  religionArabic: string;
  religionEnglish: string;
  maritalStatusArabic: string;
  maritalStatusEnglish: string;
  genderArabic: string;
  genderEnglish: string;
  cityArabic: string;
  cityEnglish: string;
  countryArabic: string;
  countryEnglish: string;
  currentAddress: string;

  // Work & Legal
  iqamaStatusArabic: string;
  iqamaStatusEnglish: string;
  hasDrivingLicense: boolean;
  drivingLicenseCountry: string;
  hrsdAccredited: boolean;
  hrsdTitle: string;
  currentRoleArabic: string;
  currentRoleEnglish: string;
  yearsOfExperience: number;
  noticePeriod: string;
  noticePeriodDays: number;
  linkedInUrl: string;
  portfolioUrl: string;

  // Compensation Baseline (Current)
  currentBasicSalary: number;
  currentHousingAllowance: number;
  currentTotalBenefitsDescription: string;
  iqamaCoveredByCompany: boolean;
  flightTicketsCoveredByCompany: boolean;
  annualLeaveCoveredByCompany: boolean;
  familyVisitSupport: boolean;

  // Compensation Targets (Expected)
  expectedBasicSalary: number;
  minimumBasicSalaryFloor: number;
  expectedTotalSalaryPackage: number;
  currency: string;

  // Account Creation Credentials (ATS Portals)
  defaultAccountPassword: string;

  // Documents
  masterCvPdfPath: string;
  summaryArabic: string;
  summaryEnglish: string;
}

export const candidateProfile: CandidateCorporateProfile = {
  // Personal Identity
  fullNameArabic: "حسن سرحان",
  fullNameEnglish: "Hassan Sarhan",
  firstName: "Hassan",
  lastName: "Sarhan",
  email: "hsn96srhan@gmail.com",
  phone: "0506267542",
  phoneInternational: "+966506267542",
  nationalityArabic: "مصري",
  nationalityEnglish: "Egyptian",
  religionArabic: "مسلم",
  religionEnglish: "Muslim",
  maritalStatusArabic: "متزوج",
  maritalStatusEnglish: "Married",
  genderArabic: "ذكر",
  genderEnglish: "Male",
  cityArabic: "الرياض",
  cityEnglish: "Riyadh",
  countryArabic: "المملكة العربية السعودية",
  countryEnglish: "Saudi Arabia",
  currentAddress: "Riyadh, Saudi Arabia",

  // Work Authorization & Legal
  iqamaStatusArabic: "إقامة نظامية قابلة للتحويل (نقل كفالة)",
  iqamaStatusEnglish: "Transferable Iqama",
  hasDrivingLicense: true,
  drivingLicenseCountry: "Saudi Arabia",
  hrsdAccredited: true,
  hrsdTitle: "Marketing Manager (Accredited by Ministry of Human Resources and Social Development)",
  currentRoleArabic: "مدير تسويق تنفيذي (معتمد من HRSD)",
  currentRoleEnglish: "Marketing Director (HRSD Accredited)",
  yearsOfExperience: 8,
  noticePeriod: "Immediate / 15 Days",
  noticePeriodDays: 15,
  linkedInUrl: "https://www.linkedin.com/in/srhan-jr/",
  portfolioUrl: "https://hsn96srhan.github.io/hsn/",

  // Current Compensation & Benefits
  currentBasicSalary: 8000,
  currentHousingAllowance: 2000, // 3 months basic per year (25% cash allowance, not company-provided)
  currentTotalBenefitsDescription:
    "راتب أساسي 8000 ريال، بدل سكن نقدي 3 شهور من الأساسي سنوياً (25%)، نقل كفالة عبر قوى، كرت عمل، تأمين طبي تعاوني شامل CCHI، وتذاكر طيران سنوية وإجازة مدفوعة.",
  iqamaCoveredByCompany: true,
  flightTicketsCoveredByCompany: true,
  annualLeaveCoveredByCompany: true,
  familyVisitSupport: true,

  // Target Compensation
  expectedBasicSalary: 9000,
  minimumBasicSalaryFloor: 8000,
  expectedTotalSalaryPackage: 10000, // 10,000 - 12,000+ SAR total package + Qiwa transfer, work permit & medical insurance
  currency: "SAR",

  // Corporate Portal Account Credentials
  defaultAccountPassword: "Hassan@Career2026!",

  // Master Document Paths & Executive Pitches
  masterCvPdfPath: path.resolve(process.cwd(), "cv/marketing-director-hsn.pdf"),
  summaryArabic:
    "مدير تسويق تنفيذي معتمد من وزارة الموارد البشرية والتنمية الاجتماعية (HRSD) بخبرة تزيد عن 8 سنوات في قيادة التسويق الرقمي وتجارة التجزئة والتجارة الإلكترونية في السعودية والخليج، مع إدارة ميزانيات إعلانية بملايين الريالات وتحقيق عائد ROAS يصل إلى 25x.",
  summaryEnglish:
    "HRSD-accredited Marketing Director with 8+ years of leadership experience driving omnichannel retail, e-commerce, and high-performance paid marketing across Saudi Arabia and the GCC, managing multi-million SAR advertising budgets with audited ROAS up to 25x.",
};
