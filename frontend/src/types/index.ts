export interface SourceMetadata {
  source: string;
  source_type: 'OFFICIAL' | 'GOVERNMENT OPEN DATA' | 'AUTHORIZED API' | 'LICENSED PROVIDER' | 'USER PROVIDED' | 'DERIVED' | 'UNAVAILABLE';
  last_retrieved: string;
  verification?: string;
  verification_status?: string;
}

export interface GSTFilingInfo {
  return_type: string;
  tax_period: string;
  date_of_filing: string;
  status: string;
  mode: string;
}

export interface GSTRegistration {
  id: string;
  gstin: string;
  state: string;
  registration_date: string | null;
  status: string;
  cancellation_date: string | null;
  taxpayer_type: string;
  business_constitution: string | null;
  centre_jurisdiction: string | null;
  state_jurisdiction: string | null;
  principal_place_of_business: string | null;
  additional_places: string[];
  nature_of_business: string[];
  filings: GSTFilingInfo[];
  source: string;
  source_type: string;
  last_retrieved: string;
  verification_status: string;
}

export interface Director {
  id: string;
  name: string;
  designation: string;
  appointment_date: string | null;
  cessation_date: string | null;
  source: string;
  source_type: string;
  verification_status?: string;
}

export interface FinancialYearData {
  financial_year: string;
  period_start?: string;
  period_end?: string;
  currency: string;
  revenue: number | null;
  profit_loss: number | null;
  net_worth: number | null;
  assets: number | null;
  liabilities: number | null;
  cash_flow: number | null;
  paid_up_capital: number | null;
  revenue_label: string;
  source: string;
  retrieved_at: string;
}

export interface FinancialRecord {
  status: 'AVAILABLE' | 'FINANCIAL_DATA_UNAVAILABLE';
  message?: string;
  source: string;
  source_type: string;
  reporting_standard?: string;
  audit_status?: string;
  financial_years: FinancialYearData[];
}

export interface Filing {
  id: string;
  filing_type: string;
  financial_year: string | null;
  filing_date: string | null;
  status: string;
  metadata?: Record<string, any>;
  source: string;
  source_type: string;
}

export interface CompanyEvent {
  id: string;
  year: number;
  event_date: string;
  event_type: string;
  description: string;
  old_value?: any;
  new_value?: any;
  source: string;
  source_type: string;
}

export interface DataSourceProvenance {
  name: string;
  source_type: string;
  dataset: string;
  last_synchronization: string;
  verification_status: string;
  coverage: string;
  status: 'HEALTHY' | 'DEGRADED' | 'NOT_CONFIGURED' | 'DOWN';
}

export interface CompanyProfile {
  id: string;
  legal_name: string;
  trade_name: string | null;
  cin: string;
  pan: string | null;
  company_status: string;
  company_type: string | null;
  company_class: string | null;
  company_category: string | null;
  incorporation_date: string | null;
  registered_state: string | null;
  roc: string | null;
  registered_address: string | null;
  authorized_capital: number;
  paid_up_capital: number;
  currency: string;
  last_updated: string;
  source_metadata: SourceMetadata;
  gst_registrations: GSTRegistration[];
  directors: Director[];
  financials: FinancialRecord;
  filings: Filing[];
  timeline: CompanyEvent[];
  sources: DataSourceProvenance[];
}

export interface SearchMatchSummary {
  id: string;
  legal_name: string;
  trade_name?: string | null;
  cin: string;
  company_status: string;
  registered_state: string;
  incorporation_year?: number;
  gst_count: number;
  sources: string[];
  similarity_score: number;
}

export interface SearchResult {
  identifierType: 'GSTIN' | 'PAN' | 'CIN' | 'COMPANY_NAME' | 'UNKNOWN';
  resolution: 'EXACT_MATCH' | 'HIGH_CONFIDENCE' | 'POSSIBLE_MATCH' | 'UNRESOLVED';
  searchedIdentifier?: string;
  confidenceScore: number;
  companies: CompanyProfile[] | SearchMatchSummary[];
  message?: string;
}

export interface ConnectorHealth {
  name: string;
  status: 'HEALTHY' | 'DEGRADED' | 'NOT_CONFIGURED' | 'DOWN';
  latency_ms: number;
  last_checked: string;
  message?: string;
  records_synced?: number;
}
