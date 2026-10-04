import uuid
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.company_models import (
    Company, Identifier, GSTRegistration, Director, FinancialYear,
    Filing, CompanyEvent, DataSource, DataRecord, RawMCARecord
)
from app.core.security import hash_identifier

logger = logging.getLogger("app.mca_pipeline")

class MCADataMapper:
    """
    Normalizes raw MCA Open Government Data schema fields into standardized CompanyLens entities.
    """
    @staticmethod
    def normalize_company_status(status: Optional[str]) -> str:
        if not status:
            return "ACTIVE"
        s = status.strip().upper()
        if "ACT" in s or "OPEN" in s:
            return "ACTIVE"
        elif "STRUCK" in s or "DEFUNCT" in s:
            return "STRUCK_OFF"
        elif "DORMANT" in s:
            return "DORMANT"
        elif "LIQUIDATION" in s or "WINDING" in s:
            return "UNDER_LIQUIDATION"
        elif "AMALGAMATED" in s or "MERGED" in s:
            return "DISSOLVED"
        return s

    @staticmethod
    def parse_date(date_str: Any) -> Optional[date]:
        if not date_str:
            return None
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, datetime):
            return date_str.date()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(str(date_str).strip(), fmt).date()
            except ValueError:
                pass
        return None

    @classmethod
    def map_raw_to_company(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        legal_name = str(raw.get("company_name") or raw.get("legal_name") or "").strip()
        cin = str(raw.get("cin") or "").strip().upper()
        return {
            "cin": cin,
            "legal_name": legal_name,
            "trade_name": raw.get("trade_name") or legal_name,
            "company_status": cls.normalize_company_status(raw.get("company_status")),
            "company_type": raw.get("company_type") or "Private Limited Company",
            "company_class": raw.get("company_class") or "Private",
            "company_category": raw.get("company_category") or "Company limited by shares",
            "incorporation_date": cls.parse_date(raw.get("incorporation_date") or raw.get("registration_date")),
            "registered_state": raw.get("registered_state") or "India",
            "roc": raw.get("roc") or f"ROC {raw.get('registered_state', 'India')}",
            "registered_address": raw.get("registered_address") or raw.get("address"),
            "authorized_capital": float(raw.get("authorized_capital") or 0.0),
            "paid_up_capital": float(raw.get("paid_up_capital") or 0.0)
        }

class MCAChangeDetector:
    """
    Detects modifications between existing MCA database state and newly ingested raw data records.
    """
    @staticmethod
    def has_changed(existing: Company, normalized: Dict[str, Any]) -> Tuple[bool, List[str]]:
        changed_fields = []
        if existing.legal_name != normalized["legal_name"]:
            changed_fields.append("legal_name")
        if existing.company_status != normalized["company_status"]:
            changed_fields.append("company_status")
        if normalized["authorized_capital"] and existing.authorized_capital != normalized["authorized_capital"]:
            changed_fields.append("authorized_capital")
        if normalized["paid_up_capital"] and existing.paid_up_capital != normalized["paid_up_capital"]:
            changed_fields.append("paid_up_capital")
        if normalized["registered_address"] and existing.registered_address != normalized["registered_address"]:
            changed_fields.append("registered_address")
        return len(changed_fields) > 0, changed_fields

class MCARepository:
    """
    Performs transactional CRUD operations for MCA datasets in PostgreSQL/SQLite.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_by_cin(self, cin: str) -> Optional[Company]:
        return self.db.query(Company).filter(Company.cin == cin.strip().upper()).first()

    def get_by_name(self, name: str) -> Optional[Company]:
        return self.db.query(Company).filter(Company.legal_name == name.strip()).first()

    def upsert_company(self, company_data: Dict[str, Any], source_id: Optional[str] = None) -> Tuple[Company, str]:
        cin = company_data.get("cin")
        existing = self.get_by_cin(cin) if cin else None
        if not existing and company_data.get("legal_name"):
            existing = self.get_by_name(company_data["legal_name"])

        if existing:
            changed, fields = MCAChangeDetector.has_changed(existing, company_data)
            if changed:
                for f in fields:
                    setattr(existing, f, company_data[f])
                existing.updated_at = datetime.utcnow()
                self.db.commit()
                return existing, "UPDATED"
            return existing, "UNCHANGED"
        else:
            c = Company(
                id=str(uuid.uuid4()),
                cin=company_data.get("cin"),
                legal_name=company_data["legal_name"],
                trade_name=company_data.get("trade_name"),
                company_status=company_data.get("company_status", "ACTIVE"),
                company_type=company_data.get("company_type"),
                company_class=company_data.get("company_class"),
                company_category=company_data.get("company_category"),
                incorporation_date=company_data.get("incorporation_date"),
                registered_state=company_data.get("registered_state"),
                roc=company_data.get("roc"),
                registered_address=company_data.get("registered_address"),
                authorized_capital=company_data.get("authorized_capital"),
                paid_up_capital=company_data.get("paid_up_capital")
            )
            self.db.add(c)
            self.db.commit()

            # Create primary CIN identifier if CIN present
            if cin:
                ident = Identifier(
                    id=str(uuid.uuid4()),
                    company_id=c.id,
                    type="CIN",
                    normalized_value=cin,
                    value_hash=hash_identifier(cin),
                    is_primary=True,
                    source_id=source_id
                )
                self.db.add(ident)
                self.db.commit()

            return c, "INSERTED"

class MCAImporter:
    """
    Executes the 10-stage MCA Open Data Ingestion Pipeline:
    SOURCE -> FETCH -> RAW DB -> VALIDATE -> NORMALIZE -> DEDUPLICATE -> UPSERT -> IDENTIFIERS -> PROVENANCE -> REPORT
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo = MCARepository(db)

    def run_import_pipeline(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        report = {
            "records_read": len(records),
            "records_inserted": 0,
            "records_updated": 0,
            "records_unchanged": 0,
            "records_rejected": 0,
            "duplicates_detected": 0,
            "errors": [],
            "timestamp": datetime.utcnow().isoformat()
        }

        # Get or create MCA DataSource
        mca_source = self.db.query(DataSource).filter(DataSource.name.like("%Ministry of Corporate Affairs%")).first()
        if not mca_source:
            mca_source = DataSource(
                id=str(uuid.uuid4()),
                name="Ministry of Corporate Affairs",
                type="GOVERNMENT OPEN DATA",
                provider="MCA / data.gov.in",
                base_url="https://data.gov.in/catalog/company-master-data",
                is_active=True,
                priority=10
            )
            self.db.add(mca_source)
            self.db.commit()

        seen_cins = set()

        for idx, item in enumerate(records):
            try:
                cin = str(item.get("cin") or "").strip().upper()
                company_name = str(item.get("company_name") or item.get("legal_name") or "").strip()

                if not company_name:
                    report["records_rejected"] += 1
                    report["errors"].append(f"Row {idx+1}: Missing company name")
                    continue

                if cin:
                    if cin in seen_cins:
                        report["duplicates_detected"] += 1
                        continue
                    seen_cins.add(cin)

                # Store Raw MCA Record
                if cin:
                    raw_rec = self.db.query(RawMCARecord).filter(RawMCARecord.cin == cin).first()
                    if not raw_rec:
                        raw_rec = RawMCARecord(
                            id=str(uuid.uuid4()),
                            cin=cin,
                            company_name=company_name,
                            company_status=item.get("company_status"),
                            company_class=item.get("company_class"),
                            company_category=item.get("company_category"),
                            authorized_capital=float(item.get("authorized_capital") or 0.0),
                            paid_up_capital=float(item.get("paid_up_capital") or 0.0),
                            incorporation_date=MCADataMapper.parse_date(item.get("incorporation_date")),
                            registered_state=item.get("registered_state"),
                            roc=item.get("roc"),
                            raw_payload=item
                        )
                        self.db.add(raw_rec)
                        self.db.commit()

                # Map & Upsert
                normalized = MCADataMapper.map_raw_to_company(item)
                company, status = self.repo.upsert_company(normalized, source_id=mca_source.id)

                if status == "INSERTED":
                    report["records_inserted"] += 1
                elif status == "UPDATED":
                    report["records_updated"] += 1
                elif status == "UNCHANGED":
                    report["records_unchanged"] += 1

                # Ingest directors if present
                if "directors" in item and isinstance(item["directors"], list):
                    for d_name in item["directors"]:
                        if d_name:
                            existing_dir = self.db.query(Director).filter(
                                Director.company_id == company.id,
                                Director.name == str(d_name).strip()
                            ).first()
                            if not existing_dir:
                                self.db.add(Director(
                                    id=str(uuid.uuid4()),
                                    company_id=company.id,
                                    name=str(d_name).strip(),
                                    designation="Director",
                                    appointment_date=company.incorporation_date,
                                    source_id=mca_source.id
                                ))
                    self.db.commit()

            except Exception as e:
                self.db.rollback()
                report["records_rejected"] += 1
                report["errors"].append(f"Row {idx+1}: {str(e)}")

        return report

class MCAConnector:
    """
    Interface connector for Ministry of Corporate Affairs data services.
    """
    def __init__(self, db: Session):
        self.db = db
        self.importer = MCAImporter(db)

    async def search_by_cin(self, cin: str) -> Optional[Dict[str, Any]]:
        c = self.db.query(Company).filter(Company.cin == cin.strip().upper()).first()
        if c:
            return {
                "cin": c.cin,
                "legal_name": c.legal_name,
                "company_status": c.company_status,
                "company_class": c.company_class,
                "registered_state": c.registered_state,
                "incorporation_date": c.incorporation_date.isoformat() if c.incorporation_date else None,
                "authorized_capital": float(c.authorized_capital or 0.0),
                "paid_up_capital": float(c.paid_up_capital or 0.0)
            }
        return None
