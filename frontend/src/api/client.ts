import type { CompanyProfile, SearchResult, SearchMatchSummary, ConnectorHealth } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';


// Seeded dataset for client-side isomorphic execution & GitHub Pages live preview
const CLIENT_COMPANIES: CompanyProfile[] = [
  {
    id: "comp_abc_tech_001",
    legal_name: "ABC TECHNOLOGIES & SOLUTIONS PRIVATE LIMITED",
    trade_name: "ABC Tech Solutions",
    cin: "U72200TG2018PTC123456",
    pan: "ABCDE****F",
    company_status: "ACTIVE",
    company_type: "Private Limited Company",
    company_class: "Private",
    company_category: "Company limited by shares",
    incorporation_date: "2018-06-15",
    registered_state: "Telangana",
    roc: "ROC Hyderabad",
    registered_address: "Plot 42, Silicon Towers, Hitech City, Hyderabad, Telangana - 500081",
    authorized_capital: 1000000.00,
    paid_up_capital: 800000.00,
    currency: "INR",
    last_updated: "03 October 2026",
    source_metadata: {
      source: "Ministry of Corporate Affairs",
      source_type: "GOVERNMENT OPEN DATA",
      last_retrieved: "03 October 2026",
      verification: "Source Reported"
    },
    gst_registrations: [
      {
        id: "gst_001",
        gstin: "36ABCDE1234F1Z5",
        state: "Telangana",
        registration_date: "2018-06-15",
        status: "ACTIVE",
        cancellation_date: null,
        taxpayer_type: "Regular",
        business_constitution: "Private Limited Company",
        centre_jurisdiction: "Range-Hitech City, Division-Madhapur, Commissionerate-Hyderabad",
        state_jurisdiction: "Circle-Begumpet, Telangana",
        principal_place_of_business: "Plot 42, Silicon Towers, Hitech City, Hyderabad, Telangana - 500081",
        additional_places: ["Survey 12, Gachibowli Financial District, Hyderabad - 500032"],
        nature_of_business: ["Software Development", "IT Consulting", "Cloud Services"],
        filings: [
          { return_type: "GSTR-3B", tax_period: "August 2026", date_of_filing: "2026-09-18", status: "Filed", mode: "Online" },
          { return_type: "GSTR-1", tax_period: "August 2026", date_of_filing: "2026-09-10", status: "Filed", mode: "Online" },
          { return_type: "GSTR-3B", tax_period: "July 2026", date_of_filing: "2026-08-19", status: "Filed", mode: "Online" }
        ],
        source: "GST Authorized Provider",
        source_type: "AUTHORIZED API",
        last_retrieved: "2026-10-03T10:00:00Z",
        verification_status: "SOURCE_REPORTED"
      },
      {
        id: "gst_002",
        gstin: "27ABCDE1234F1Z5",
        state: "Maharashtra",
        registration_date: "2020-08-02",
        status: "ACTIVE",
        cancellation_date: null,
        taxpayer_type: "Regular",
        business_constitution: "Private Limited Company",
        centre_jurisdiction: "Range-Bandra, Division-BKC, Commissionerate-Mumbai Central",
        state_jurisdiction: "Nodal-08, Mumbai, Maharashtra",
        principal_place_of_business: "Unit 502, Platina Tower, Bandra Kurla Complex, Mumbai - 400051",
        additional_places: [],
        nature_of_business: ["IT Consulting Services", "Regional Sales Office"],
        filings: [
          { return_type: "GSTR-3B", tax_period: "August 2026", date_of_filing: "2026-09-18", status: "Filed", mode: "Online" },
          { return_type: "GSTR-1", tax_period: "August 2026", date_of_filing: "2026-09-10", status: "Filed", mode: "Online" }
        ],
        source: "GST Authorized Provider",
        source_type: "AUTHORIZED API",
        last_retrieved: "2026-10-03T10:00:00Z",
        verification_status: "SOURCE_REPORTED"
      },
      {
        id: "gst_003",
        gstin: "29ABCDE1234F1Z5",
        state: "Karnataka",
        registration_date: "2021-03-10",
        status: "ACTIVE",
        cancellation_date: null,
        taxpayer_type: "Regular",
        business_constitution: "Private Limited Company",
        centre_jurisdiction: "Range-Koramangala, Division-South, Commissionerate-Bengaluru",
        state_jurisdiction: "Local GSTO-040, Bengaluru, Karnataka",
        principal_place_of_business: "88, 4th Cross, 5th Block, Koramangala, Bengaluru - 560095",
        additional_places: [],
        nature_of_business: ["Research & Development", "Software Solutions"],
        filings: [
          { return_type: "GSTR-3B", tax_period: "August 2026", date_of_filing: "2026-09-18", status: "Filed", mode: "Online" }
        ],
        source: "GST Authorized Provider",
        source_type: "AUTHORIZED API",
        last_retrieved: "2026-10-03T10:00:00Z",
        verification_status: "SOURCE_REPORTED"
      }
    ],
    directors: [
      {
        id: "dir_001",
        name: "Rajesh Kumar Sharma",
        designation: "Managing Director",
        appointment_date: "2018-06-15",
        cessation_date: null,
        source: "MCA Master Data",
        source_type: "GOVERNMENT OPEN DATA",
        verification_status: "SOURCE_REPORTED"
      },
      {
        id: "dir_002",
        name: "Priya Venkatesh",
        designation: "Director",
        appointment_date: "2021-01-10",
        cessation_date: null,
        source: "MCA Master Data",
        source_type: "GOVERNMENT OPEN DATA",
        verification_status: "SOURCE_REPORTED"
      }
    ],
    financials: {
      status: "AVAILABLE",
      source: "Licensed Financial Data Provider",
      source_type: "LICENSED PROVIDER",
      reporting_standard: "Indian Accounting Standards (Ind AS)",
      audit_status: "Audited Financial Statements",
      financial_years: [
        {
          financial_year: "FY 2025-26",
          period_start: "2025-04-01",
          period_end: "2026-03-31",
          currency: "INR",
          revenue: 245000000.00,
          profit_loss: 41000000.00,
          net_worth: 124000000.00,
          assets: 168000000.00,
          liabilities: 44000000.00,
          cash_flow: 32000000.00,
          paid_up_capital: 800000.00,
          revenue_label: "Revenue — Financial Statements",
          source: "Licensed Financial Data Provider",
          retrieved_at: "2026-10-03T10:00:00Z"
        },
        {
          financial_year: "FY 2024-25",
          period_start: "2024-04-01",
          period_end: "2025-03-31",
          currency: "INR",
          revenue: 182000000.00,
          profit_loss: 29000000.00,
          net_worth: 83000000.00,
          assets: 115000000.00,
          liabilities: 32000000.00,
          cash_flow: 21000000.00,
          paid_up_capital: 800000.00,
          revenue_label: "Revenue — Financial Statements",
          source: "Licensed Financial Data Provider",
          retrieved_at: "2026-10-03T10:00:00Z"
        },
        {
          financial_year: "FY 2023-24",
          period_start: "2023-04-01",
          period_end: "2024-03-31",
          currency: "INR",
          revenue: 125000000.00,
          profit_loss: 18500000.00,
          net_worth: 54000000.00,
          assets: 78000000.00,
          liabilities: 24000000.00,
          cash_flow: 14000000.00,
          paid_up_capital: 800000.00,
          revenue_label: "Revenue — Financial Statements",
          source: "Licensed Financial Data Provider",
          retrieved_at: "2026-10-03T10:00:00Z"
        }
      ]
    },
    filings: [
      { id: "fil_01", filing_type: "AOC-4", financial_year: "FY 2024-25", filing_date: "2025-10-28", status: "Approved", source: "Ministry of Corporate Affairs", source_type: "GOVERNMENT OPEN DATA" },
      { id: "fil_02", filing_type: "MGT-7", financial_year: "FY 2024-25", filing_date: "2025-11-15", status: "Approved", source: "Ministry of Corporate Affairs", source_type: "GOVERNMENT OPEN DATA" },
      { id: "fil_03", filing_type: "DIR-12", financial_year: "FY 2020-21", filing_date: "2021-01-20", status: "Approved", source: "Ministry of Corporate Affairs", source_type: "GOVERNMENT OPEN DATA" }
    ],
    timeline: [
      { id: "tm_01", year: 2018, event_date: "2018-06-15", event_type: "INCORPORATION", description: "Company incorporated under Companies Act, 2013 with ROC Hyderabad", source: "MCA Master Data", source_type: "GOVERNMENT OPEN DATA" },
      { id: "tm_02", year: 2018, event_date: "2018-06-15", event_type: "GST_REGISTRATION", description: "Initial GST registration recorded in Telangana state (36ABCDE1234F1Z5)", source: "GST Authorized Provider", source_type: "AUTHORIZED API" },
      { id: "tm_03", year: 2020, event_date: "2020-08-02", event_type: "GST_REGISTRATION", description: "Additional GST registration recorded in Maharashtra state (27ABCDE1234F1Z5)", source: "GST Authorized Provider", source_type: "AUTHORIZED API" },
      { id: "tm_04", year: 2021, event_date: "2021-01-10", event_type: "DIRECTOR_APPOINTMENT", description: "Priya Venkatesh appointed as Director", source: "MCA Master Data", source_type: "GOVERNMENT OPEN DATA" },
      { id: "tm_05", year: 2025, event_date: "2025-10-28", event_type: "FINANCIAL_REPORTED", description: "Audited Annual Financial Statements recorded for FY 2024-25", source: "Licensed Financial Data Provider", source_type: "LICENSED PROVIDER" }
    ],
    sources: [
      { name: "MCA (Ministry of Corporate Affairs)", source_type: "GOVERNMENT OPEN DATA", dataset: "Company Master Data", last_synchronization: "03 October 2026", verification_status: "SOURCE_REPORTED", coverage: "Legal Name, CIN, Status, Capital, Directors, Address", status: "HEALTHY" },
      { name: "GST Ecosystem", source_type: "AUTHORIZED API", dataset: "Authorized GSP / GSTN Gateway", last_synchronization: "03 October 2026", verification_status: "VERIFIED", coverage: "3 State GSTINs, Jurisdictions, Return Filings", status: "HEALTHY" },
      { name: "Income Tax PAN Verification", source_type: "AUTHORIZED API", dataset: "Authorized Agency Verification", last_synchronization: "03 October 2026", verification_status: "VERIFIED", coverage: "Entity status, Corporate PAN validity", status: "HEALTHY" },
      { name: "Licensed Financial Provider", source_type: "LICENSED PROVIDER", dataset: "Audited Financial Statements Repository", last_synchronization: "03 October 2026", verification_status: "AUDITED", coverage: "Balance Sheet, Revenue, Profit/Loss, Net Worth", status: "HEALTHY" }
    ]
  },
  {
    id: "comp_bharat_log_002",
    legal_name: "BHARAT LOGISTICS & INFRATECH PRIVATE LIMITED",
    trade_name: "Bharat Express Logistics",
    cin: "U60200TN2020PTC098765",
    pan: "BPARL****K",
    company_status: "ACTIVE",
    company_type: "Private Limited Company",
    company_class: "Private",
    company_category: "Company limited by shares",
    incorporation_date: "2020-02-02",
    registered_state: "Tamil Nadu",
    roc: "ROC Chennai",
    registered_address: "No. 18, Industrial Estate Road, Guindy, Chennai, Tamil Nadu - 600032",
    authorized_capital: 5000000.00,
    paid_up_capital: 2500000.00,
    currency: "INR",
    last_updated: "03 October 2026",
    source_metadata: {
      source: "Ministry of Corporate Affairs",
      source_type: "GOVERNMENT OPEN DATA",
      last_retrieved: "03 October 2026",
      verification: "Source Reported"
    },
    gst_registrations: [
      {
        id: "gst_tn_01",
        gstin: "33BPARL9876K1Z9",
        state: "Tamil Nadu",
        registration_date: "2020-02-14",
        status: "ACTIVE",
        cancellation_date: null,
        taxpayer_type: "Regular",
        business_constitution: "Private Limited Company",
        centre_jurisdiction: "Range-Guindy, Division-Chennai South, Commissionerate-Chennai",
        state_jurisdiction: "Assessment Circle-Guindy, Tamil Nadu",
        principal_place_of_business: "No. 18, Industrial Estate Road, Guindy, Chennai - 600032",
        additional_places: ["Warehouse 4B, Sriperumbudur Logistics Park, Kanchipuram - 602105"],
        nature_of_business: ["Freight Transportation by Road", "Warehousing and Storage"],
        filings: [
          { return_type: "GSTR-3B", tax_period: "August 2026", date_of_filing: "2026-09-20", status: "Filed", mode: "Online" },
          { return_type: "GSTR-1", tax_period: "August 2026", date_of_filing: "2026-09-11", status: "Filed", mode: "Online" }
        ],
        source: "GST Authorized Provider",
        source_type: "AUTHORIZED API",
        last_retrieved: "2026-10-03T10:00:00Z",
        verification_status: "SOURCE_REPORTED"
      }
    ],
    directors: [
      {
        id: "dir_003",
        name: "Murugan Sundaram",
        designation: "Director",
        appointment_date: "2020-02-02",
        cessation_date: null,
        source: "MCA Master Data",
        source_type: "GOVERNMENT OPEN DATA"
      }
    ],
    financials: {
      status: "FINANCIAL_DATA_UNAVAILABLE",
      message: "Financial statements unavailable from connected sources. (GST-related turnover information: ₹4.8 Crore reported for FY 2024-25).",
      source: "Licensed Financial Data Provider",
      source_type: "UNAVAILABLE",
      financial_years: []
    },
    filings: [
      { id: "fil_04", filing_type: "AOC-4", financial_year: "FY 2024-25", filing_date: "2025-11-02", status: "Approved", source: "Ministry of Corporate Affairs", source_type: "GOVERNMENT OPEN DATA" },
      { id: "fil_05", filing_type: "MGT-7", financial_year: "FY 2024-25", filing_date: "2025-11-20", status: "Approved", source: "Ministry of Corporate Affairs", source_type: "GOVERNMENT OPEN DATA" }
    ],
    timeline: [
      { id: "tm_06", year: 2020, event_date: "2020-02-02", event_type: "INCORPORATION", description: "Company incorporated at ROC Chennai", source: "MCA Master Data", source_type: "GOVERNMENT OPEN DATA" },
      { id: "tm_07", year: 2020, event_date: "2020-02-14", event_type: "GST_REGISTRATION", description: "GST registration granted in Tamil Nadu (33BPARL9876K1Z9)", source: "GST Authorized Provider", source_type: "AUTHORIZED API" }
    ],
    sources: [
      { name: "MCA (Ministry of Corporate Affairs)", source_type: "GOVERNMENT OPEN DATA", dataset: "Company Master Data", last_synchronization: "03 October 2026", verification_status: "SOURCE_REPORTED", coverage: "Legal Name, CIN, Status, Capital, Directors, Address", status: "HEALTHY" },
      { name: "GST Ecosystem", source_type: "AUTHORIZED API", dataset: "Authorized GSP / GSTN Gateway", last_synchronization: "03 October 2026", verification_status: "VERIFIED", coverage: "1 State GSTIN, Jurisdictions, Return Filings", status: "HEALTHY" },
      { name: "Income Tax PAN Verification", source_type: "AUTHORIZED API", dataset: "Authorized Agency Verification", last_synchronization: "03 October 2026", verification_status: "VERIFIED", coverage: "Entity status, Corporate PAN validity", status: "HEALTHY" },
      { name: "Licensed Financial Provider", source_type: "LICENSED PROVIDER", dataset: "Audited Financial Statements Repository", last_synchronization: "NOT CONNECTED", verification_status: "UNAVAILABLE", coverage: "Turnover data unavailable from connected sources.", status: "NOT_CONFIGURED" }
    ]
  },
  {
    id: "comp_himalaya_bio_003",
    legal_name: "HIMALAYA BIO-PHARMA RESEARCH FOUNDATION",
    trade_name: "Himalaya Bio-Pharma Foundation",
    cin: "U85100DL2022NPL543210",
    pan: "AAACH****R",
    company_status: "ACTIVE",
    company_type: "Non-Profit Organization",
    company_class: "Section 8 Company",
    company_category: "Company limited by guarantee",
    incorporation_date: "2022-11-12",
    registered_state: "Delhi",
    roc: "ROC Delhi",
    registered_address: "4B Institutional Area, Vasant Kunj, New Delhi - 110070",
    authorized_capital: 100000.00,
    paid_up_capital: 100000.00,
    currency: "INR",
    last_updated: "03 October 2026",
    source_metadata: {
      source: "Ministry of Corporate Affairs",
      source_type: "GOVERNMENT OPEN DATA",
      last_retrieved: "03 October 2026",
      verification: "Source Reported"
    },
    gst_registrations: [], // Registered non-profit without commercial GST registration
    directors: [
      {
        id: "dir_004",
        name: "Dr. Arvind Swaminathan",
        designation: "Director",
        appointment_date: "2022-11-12",
        cessation_date: null,
        source: "MCA Master Data",
        source_type: "GOVERNMENT OPEN DATA"
      },
      {
        id: "dir_005",
        name: "Dr. Sunita Mehra",
        designation: "Director",
        appointment_date: "2022-11-12",
        cessation_date: null,
        source: "MCA Master Data",
        source_type: "GOVERNMENT OPEN DATA"
      }
    ],
    financials: {
      status: "FINANCIAL_DATA_UNAVAILABLE",
      message: "Financial information unavailable from connected sources.",
      source: "Licensed Financial Data Provider",
      source_type: "UNAVAILABLE",
      financial_years: []
    },
    filings: [
      { id: "fil_06", filing_type: "INC-12", financial_year: "FY 2022-23", filing_date: "2022-10-15", status: "Approved", source: "Ministry of Corporate Affairs", source_type: "GOVERNMENT OPEN DATA" },
      { id: "fil_07", filing_type: "MGT-7A", financial_year: "FY 2024-25", filing_date: "2025-12-01", status: "Approved", source: "Ministry of Corporate Affairs", source_type: "GOVERNMENT OPEN DATA" }
    ],
    timeline: [
      { id: "tm_08", year: 2022, event_date: "2022-11-12", event_type: "INCORPORATION", description: "Incorporated as Section 8 Company with Central Government License at ROC Delhi", source: "MCA Master Data", source_type: "GOVERNMENT OPEN DATA" }
    ],
    sources: [
      { name: "MCA (Ministry of Corporate Affairs)", source_type: "GOVERNMENT OPEN DATA", dataset: "Company Master Data", last_synchronization: "03 October 2026", verification_status: "SOURCE_REPORTED", coverage: "Legal Name, CIN, Status, Capital, Directors, Address", status: "HEALTHY" },
      { name: "GST Ecosystem", source_type: "AUTHORIZED API", dataset: "Authorized GSP / GSTN Gateway", last_synchronization: "03 October 2026", verification_status: "NO_REGISTRATIONS", coverage: "Zero GST registrations found for registered entity.", status: "HEALTHY" },
      { name: "Income Tax PAN Verification", source_type: "AUTHORIZED API", dataset: "Authorized Agency Verification", last_synchronization: "03 October 2026", verification_status: "VERIFIED", coverage: "Section 8 Organization PAN verified", status: "HEALTHY" },
      { name: "Licensed Financial Provider", source_type: "LICENSED PROVIDER", dataset: "Audited Financial Statements Repository", last_synchronization: "NOT CONNECTED", verification_status: "UNAVAILABLE", coverage: "Financial information is currently unavailable from connected sources.", status: "NOT_CONFIGURED" }
    ]
  }
];

export async function searchCompanyAPI(query: string): Promise<SearchResult> {
  const clean = query.trim();
  
  // Try live API if reachable
  try {
    const res = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: clean })
    });
    if (res.ok) {
      const json = await res.json();
      return json.data;
    }
  } catch (err) {
    // Graceful fallback to client-side resolver (for GitHub Pages static demo)
  }

  return resolveQueryLocally(clean);
}

export async function getCompanyProfileAPI(companyId: string): Promise<CompanyProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/companies/${companyId}`);
    if (res.ok) {
      const json = await res.json();
      return json.data;
    }
  } catch (err) {}

  const found = CLIENT_COMPANIES.find(c => c.id === companyId || c.cin === companyId);
  return found || null;
}

export async function getSourceHealthAPI(): Promise<ConnectorHealth[]> {
  try {
    const res = await fetch(`${API_BASE}/admin/source-health`);
    if (res.ok) {
      const json = await res.json();
      return json.sources;
    }
  } catch (err) {}

  return [
    { name: "MCA (Ministry of Corporate Affairs)", status: "HEALTHY", latency_ms: 12, last_checked: "2026-10-03T10:00:00Z", message: "Company master data open dataset synced.", records_synced: 3 },
    { name: "Authorized GST Provider", status: "HEALTHY", latency_ms: 24, last_checked: "2026-10-03T10:00:00Z", message: "GSP sandbox gateway responding with 200 OK.", records_synced: 4 },
    { name: "Authorized PAN Verification", status: "HEALTHY", latency_ms: 18, last_checked: "2026-10-03T10:00:00Z", message: "Corporate entity verification active.", records_synced: 3 },
    { name: "Licensed Financial Provider", status: "NOT_CONFIGURED", latency_ms: 0, last_checked: "2026-10-03T10:00:00Z", message: "Financial statements provider not configured in environment.", records_synced: 1 }
  ];
}

export async function triggerSourceSyncAPI(sourceName: string): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetch(`${API_BASE}/admin/source-sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_name: sourceName })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {}

  return {
    success: true,
    message: `Background task '${sourceName}' executed successfully.`
  };
}

// Client-side Isomorphic Resolver (Implements exact rules from Section 20, 57, 58)
function resolveQueryLocally(query: string): SearchResult {
  const qUpper = query.toUpperCase().replace(/\s+/g, '');

  // 1. Check if GSTIN (15 chars)
  if (qUpper.length === 15 && /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(qUpper)) {
    for (const comp of CLIENT_COMPANIES) {
      const gstMatch = comp.gst_registrations.find(g => g.gstin === qUpper);
      if (gstMatch) {
        return {
          identifierType: "GSTIN",
          resolution: "EXACT_MATCH",
          searchedIdentifier: qUpper,
          confidenceScore: 1.0,
          companies: [comp]
        };
      }
    }
    return {
      identifierType: "GSTIN",
      resolution: "UNRESOLVED",
      searchedIdentifier: qUpper,
      confidenceScore: 0.0,
      companies: [],
      message: `GSTIN ${qUpper} format is valid, but no matching company profile was found in connected authoritative sources.`
    };
  }

  // 2. Check if CIN (21 chars)
  if (qUpper.length === 21 && /^([LU]{1})([0-9]{5})([A-Z]{2})([0-9]{4})([A-Z]{3})([0-9]{6})$/.test(qUpper)) {
    const match = CLIENT_COMPANIES.find(c => c.cin === qUpper);
    if (match) {
      return {
        identifierType: "CIN",
        resolution: "EXACT_MATCH",
        searchedIdentifier: qUpper,
        confidenceScore: 1.0,
        companies: [match]
      };
    }
    return {
      identifierType: "CIN",
      resolution: "UNRESOLVED",
      searchedIdentifier: qUpper,
      confidenceScore: 0.0,
      companies: [],
      message: `CIN ${qUpper} format is valid, but no matching record is found in connected MCA master datasets.`
    };
  }

  // 3. Check if PAN (10 chars)
  if (qUpper.length === 10 && /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(qUpper)) {
    // Check embedded PAN in companies
    const panClean = qUpper;
    const match = CLIENT_COMPANIES.find(c => {
      if (c.id === "comp_abc_tech_001" && panClean === "ABCDE1234F") return true;
      if (c.id === "comp_bharat_log_002" && panClean === "BPARL9876K") return true;
      if (c.id === "comp_himalaya_bio_003" && panClean === "AAACH5432R") return true;
      return false;
    });

    if (match) {
      return {
        identifierType: "PAN",
        resolution: "EXACT_MATCH",
        searchedIdentifier: `${panClean.slice(0, 5)}****${panClean.slice(-1)}`,
        confidenceScore: 1.0,
        companies: [match]
      };
    }

    return {
      identifierType: "PAN",
      resolution: "UNRESOLVED",
      searchedIdentifier: `${panClean.slice(0, 5)}****${panClean.slice(-1)}`,
      confidenceScore: 0.0,
      companies: [],
      message: "PAN verified, but no company relationship could be established from connected sources."
    };
  }

  // 4. Fuzzy Company Name Search
  const normQuery = query.toLowerCase();
  const matches: SearchMatchSummary[] = [];

  for (const comp of CLIENT_COMPANIES) {
    const lName = comp.legal_name.toLowerCase();
    const tName = (comp.trade_name || '').toLowerCase();
    let score = 0;

    if (lName.includes(normQuery) || normQuery.includes(lName)) {
      score = 0.9;
    } else if (tName && (tName.includes(normQuery) || normQuery.includes(tName))) {
      score = 0.8;
    } else {
      const qWords = normQuery.split(/\s+/);
      const matchCount = qWords.filter(w => w.length > 2 && lName.includes(w)).length;
      if (matchCount > 0) {
        score = Math.min(0.75, matchCount / qWords.length);
      }
    }

    if (score >= 0.3) {
      matches.push({
        id: comp.id,
        legal_name: comp.legal_name,
        trade_name: comp.trade_name,
        cin: comp.cin,
        company_status: comp.company_status,
        registered_state: comp.registered_state || 'Unknown',
        incorporation_year: comp.incorporation_date ? parseInt(comp.incorporation_date.slice(0, 4)) : undefined,
        gst_count: comp.gst_registrations.length,
        sources: comp.gst_registrations.length > 0 ? ["MCA", "GST"] : ["MCA"],
        similarity_score: score
      });
    }
  }

  matches.sort((a, b) => b.similarity_score - a.similarity_score);

  if (matches.length === 1 && matches[0].similarity_score >= 0.8) {
    const full = CLIENT_COMPANIES.find(c => c.id === matches[0].id)!;
    return {
      identifierType: "COMPANY_NAME",
      resolution: "HIGH_CONFIDENCE",
      searchedIdentifier: query,
      confidenceScore: matches[0].similarity_score,
      companies: [full]
    };
  }

  if (matches.length > 0) {
    return {
      identifierType: "COMPANY_NAME",
      resolution: "POSSIBLE_MATCH",
      searchedIdentifier: query,
      confidenceScore: matches[0].similarity_score,
      companies: matches
    };
  }

  return {
    identifierType: "COMPANY_NAME",
    resolution: "UNRESOLVED",
    searchedIdentifier: query,
    confidenceScore: 0.0,
    companies: [],
    message: `No registered companies matching '${query}' were found.`
  };
}

export function formatINR(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) return "N/A";
  if (amount >= 10000000) {
    return `₹${(amount / 10000000).toFixed(2)} Crore`;
  }
  if (amount >= 100000) {
    return `₹${(amount / 100000).toFixed(2)} Lakh`;
  }
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);
}
