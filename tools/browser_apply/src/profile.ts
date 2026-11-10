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
  iqamaNumber: string;
  currentlyOnCompanySponsorship: boolean;
  hasDrivingLicense: boolean;
  drivingLicenseCountry: string;
  hrsdAccredited: boolean;
  hrsdTitle: string;
  educationDegreeArabic: string;
  educationDegreeEnglish: string;
  educationInstitutionArabic: string;
  educationInstitutionEnglish: string;
  educationGraduationYear: number;
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
  workHistory: Array<{
    company: string;
    roleArabic: string;
    roleEnglish: string;
    location: string;
    startDate: string;
    endDate: string;
    isCurrent: boolean;
    descriptionArabic: string;
  }>;
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
  iqamaStatusArabic: "إقامة عمل نظامية سارية قابلة للتحويل (نقل كفالة عبر قوى)",
  iqamaStatusEnglish: "Work Visa - Transferable Iqama via Qiwa",
  iqamaNumber: "2644162360",
  currentlyOnCompanySponsorship: true,
  hasDrivingLicense: true,
  drivingLicenseCountry: "Saudi Arabia",
  hrsdAccredited: true,
  hrsdTitle: "Marketing Manager (Accredited by Ministry of Human Resources and Social Development)",
  educationDegreeArabic: "بكالوريوس إعلام قسم صحافة",
  educationDegreeEnglish: "Bachelor of Journalism & Media",
  educationInstitutionArabic: "أكاديمية أخبار اليوم",
  educationInstitutionEnglish: "Akhbar El Yom Academy",
  educationGraduationYear: 2018,
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
  workHistory: [
    {
      company: "FLUX Ads Agency",
      roleArabic: "مدير التسويق",
      roleEnglish: "Marketing Director",
      location: "الرياض، المملكة العربية السعودية",
      startDate: "2025-12",
      endDate: "Present",
      isCurrent: true,
      descriptionArabic: "قيادة الاستراتيجيات التسويقية والنمو لأكثر من 30 عميلاً بالسوق السعودي، والإشراف المباشر على 4 قطاعات: السوشيال ميديا، الإنتاج الإبداعي، الحملات الخارجية، والتطوير البرمجي."
    },
    {
      company: "RAKETBE Agency",
      roleArabic: "مدير التسويق الرقمي والأداء",
      roleEnglish: "Digital Marketing & Performance Manager",
      location: "الرياض، المملكة العربية السعودية",
      startDate: "2025-08",
      endDate: "2026-01",
      isCurrent: false,
      descriptionArabic: "إخراج وإدارة الحملات الإعلانية المدفوعة بالسعودية، إدارة الميزانيات وتحقيق عائد ROAS من 5x حتى 25x، ورفع معدلات التحويل 25% وخفض تكلفة الاستحواذ 32%."
    },
    {
      company: "Arabiva Group",
      roleArabic: "مدير التسويق",
      roleEnglish: "Marketing Director",
      location: "الكويت والخليج وأوروبا وأمريكا",
      startDate: "2025-03",
      endDate: "2025-08",
      isCurrent: false,
      descriptionArabic: "قيادة الاستراتيجيات التسويقية لـ 3 علامات تجارية عالمية للعطور، توطين المتاجر الإلكترونية للخليج، وتوسيع الصادرات بنسبة +65%."
    },
    {
      company: "Fantazzia Bed",
      roleArabic: "مدير التجارة الرقمية",
      roleEnglish: "Digital Commerce / E-Commerce Manager",
      location: "مصر والخليج وإفريقيا",
      startDate: "2022-02",
      endDate: "2025-03",
      isCurrent: false,
      descriptionArabic: "تأسيس المتجر الإلكتروني وإدارة المبيعات والتسويق والكول سنتر والوصول بالمبيعات إلى 10 مليون شهرياً (5 مليون متجر إلكتروني + 5 مليون سوشيال وكول سنتر)."
    },
    {
      company: "VLEX Shipping",
      roleArabic: "شريك مؤسس ومدير تسويق",
      roleEnglish: "Co-Founder & Marketing Director",
      location: "القاهرة والجيزة، مصر",
      startDate: "2021-01",
      endDate: "2021-12",
      isCurrent: false,
      descriptionArabic: "تأسيس التسويق لشركة الشحن والتوصيل للمتاجر الإلكترونية، واستقطاب أكثر من 1,000 تاجر تجزئة عبر قنوات رقمية مؤتمتة."
    },
    {
      company: "Medica Healthy App",
      roleArabic: "أخصائي سوشيال ميديا ومحتوى",
      roleEnglish: "Social Media & Content Specialist",
      location: "القاهرة، مصر",
      startDate: "2018-07",
      endDate: "2020-12",
      isCurrent: false,
      descriptionArabic: "إطلاق التطبيق الطبي الشامل لحجز الأطباء والمختبرات والصيدليات، وتجاوز مليون مشاهدة تفاعلية وبناء الثقة لدى المرضى."
    }
  ]
};
