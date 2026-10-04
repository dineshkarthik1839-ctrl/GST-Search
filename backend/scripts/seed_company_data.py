import sys
import os
import uuid
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine
from app.db.metadata import Base
from app.models.company_models import (
    Company, Identifier, GSTRegistration, Director, FinancialYear,
    Filing, CompanyEvent, DataSource, DataRecord, RawMCARecord
)
from app.core.security import hash_identifier

def seed_database():
    print("Initializing CompanyLens PostgreSQL database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("Clearing existing dataset for fresh ingestion...")
        db.query(DataRecord).delete()
        db.query(CompanyEvent).delete()
        db.query(Filing).delete()
        db.query(FinancialYear).delete()
        db.query(Director).delete()
        db.query(GSTRegistration).delete()
        db.query(Identifier).delete()
        db.query(RawMCARecord).delete()
        db.query(Company).delete()
        db.query(DataSource).delete()
        db.commit()

        print("Seeding Data Sources Registry...")
        mca_source = DataSource(
            id=str(uuid.uuid4()),
            name="Ministry of Corporate Affairs",
            type="GOVERNMENT OPEN DATA",
            provider="MCA / data.gov.in",
            base_url="https://data.gov.in/catalog/company-master-data",
            is_active=True,
            priority=10
        )
        gst_source = DataSource(
            id=str(uuid.uuid4()),
            name="Authorized GST Provider",
            type="AUTHORIZED API",
            provider="Licensed GSP Gateway",
            base_url="https://api.gstprovider.authorized.in/v1",
            is_active=True,
            requires_auth=True,
            priority=20
        )
        pan_source = DataSource(
            id=str(uuid.uuid4()),
            name="Income Tax PAN Verification",
            type="AUTHORIZED API",
            provider="Authorized Agency Verification",
            base_url="https://api.panverify.authorized.in/v1",
            is_active=True,
            requires_auth=True,
            priority=30
        )
        fin_source = DataSource(
            id=str(uuid.uuid4()),
            name="Licensed Financial Data Provider",
            type="LICENSED PROVIDER",
            provider="Statutory Filings Analytics Ltd",
            base_url="https://api.financialdata.licensed.in/v1",
            is_active=True,
            requires_auth=True,
            priority=40
        )
        db.add_all([mca_source, gst_source, pan_source, fin_source])
        db.commit()

        companies_data = [
            # 1. TATA MOTORS LIMITED
            {
                "legal_name": "TATA MOTORS LIMITED",
                "trade_name": "Tata Motors",
                "cin": "L28920MH1945PLC004520",
                "pan": "AAACT1234F",
                "company_status": "ACTIVE",
                "company_type": "Public Limited Company",
                "company_class": "Public",
                "company_category": "Company limited by shares",
                "incorporation_date": date(1945, 9, 1),
                "registered_state": "Maharashtra",
                "roc": "ROC Mumbai",
                "registered_address": "Bombay House, 24 Homi Mody Street, Fort, Mumbai - 400001, Maharashtra, India",
                "authorized_capital": 4000000000.0,
                "paid_up_capital": 765900000.0,
                "gstins": [
                    {"gstin": "27AAACT1234F1Z5", "state": "Maharashtra", "jurisdiction": "Commissionerate-Mumbai Central"},
                    {"gstin": "07AAACT1234F1Z3", "state": "Delhi", "jurisdiction": "Commissionerate-Delhi North"},
                    {"gstin": "24AAACT1234F1Z1", "state": "Gujarat", "jurisdiction": "Commissionerate-Sanand Ahmedabad"}
                ],
                "directors": ["Natarajan Chandrasekaran", "Girish Wagh", "Thierry Bollore"],
                "events": [
                    (date(1945, 9, 1), "INCORPORATION", "Incorporated as Tata Locomotive and Engineering Company Limited"),
                    (date(2003, 7, 29), "NAME_CHANGE", "Renamed to Tata Motors Limited")
                ]
            },
            # 2. INFOSYS LIMITED
            {
                "legal_name": "INFOSYS LIMITED",
                "trade_name": "Infosys",
                "cin": "L85110KA1981PLC013115",
                "pan": "AAACI1111F",
                "company_status": "ACTIVE",
                "company_type": "Public Limited Company",
                "company_class": "Public",
                "company_category": "Company limited by shares",
                "incorporation_date": date(1981, 7, 2),
                "registered_state": "Karnataka",
                "roc": "ROC Bangalore",
                "registered_address": "Electronics City, Hosur Road, Bengaluru - 560100, Karnataka, India",
                "authorized_capital": 2400000000.0,
                "paid_up_capital": 2070000000.0,
                "gstins": [
                    {"gstin": "29AAACI1111F1Z8", "state": "Karnataka", "jurisdiction": "Commissionerate-Bengaluru South"},
                    {"gstin": "36AAACI1111F1Z6", "state": "Telangana", "jurisdiction": "Commissionerate-Hyderabad Hitech City"}
                ],
                "directors": ["Salil Parekh", "Nandan Nilekani", "Kiran Mazumdar Shaw"],
                "events": [
                    (date(1981, 7, 2), "INCORPORATION", "Incorporated in Pune as Infosys Consultants Private Limited"),
                    (date(2011, 6, 16), "NAME_CHANGE", "Rebranded as Infosys Limited")
                ]
            },
            # 3. RELIANCE INDUSTRIES LIMITED
            {
                "legal_name": "RELIANCE INDUSTRIES LIMITED",
                "trade_name": "Reliance",
                "cin": "L17110MH1973PLC019786",
                "pan": "AAACR2222F",
                "company_status": "ACTIVE",
                "company_type": "Public Limited Company",
                "company_class": "Public",
                "company_category": "Company limited by shares",
                "incorporation_date": date(1973, 5, 8),
                "registered_state": "Maharashtra",
                "roc": "ROC Mumbai",
                "registered_address": "Maker Chambers IV, 3rd Floor, 222 Nariman Point, Mumbai - 400021, Maharashtra, India",
                "authorized_capital": 15000000000.0,
                "paid_up_capital": 6765000000.0,
                "gstins": [
                    {"gstin": "27AAACR2222F1Z9", "state": "Maharashtra", "jurisdiction": "Commissionerate-Mumbai East"},
                    {"gstin": "24AAACR2222F1Z7", "state": "Gujarat", "jurisdiction": "Commissionerate-Jamnagar"}
                ],
                "directors": ["Mukesh Dhirubhai Ambani", "Nita Mukesh Ambani", "Isha Ambani"],
                "events": [
                    (date(1973, 5, 8), "INCORPORATION", "Incorporated in Maharashtra as Mynylon Limited")
                ]
            },
            # 4. HDFC BANK LIMITED
            {
                "legal_name": "HDFC BANK LIMITED",
                "trade_name": "HDFC Bank",
                "cin": "L65920MH1994PLC080618",
                "pan": "AAACH3333F",
                "company_status": "ACTIVE",
                "company_type": "Public Limited Company",
                "company_class": "Public Banking",
                "company_category": "Company limited by shares",
                "incorporation_date": date(1994, 8, 30),
                "registered_state": "Maharashtra",
                "roc": "ROC Mumbai",
                "registered_address": "HDFC Bank House, Senapati Bapat Marg, Lower Parel, Mumbai - 400013, Maharashtra, India",
                "authorized_capital": 10000000000.0,
                "paid_up_capital": 7580000000.0,
                "gstins": [
                    {"gstin": "27AAACH3333F1Z1", "state": "Maharashtra", "jurisdiction": "Commissionerate-Mumbai Financial Center"},
                    {"gstin": "33AAACH3333F1Z9", "state": "Tamil Nadu", "jurisdiction": "Commissionerate-Chennai Central"}
                ],
                "directors": ["Sashidhar Jagdishan", "Atanu Chakraborty"],
                "events": [
                    (date(1994, 8, 30), "INCORPORATION", "Incorporated as Housing Development Finance Corporation Bank")
                ]
            },
            # 5. ABC TECHNOLOGIES & SOLUTIONS PRIVATE LIMITED
            {
                "legal_name": "ABC TECHNOLOGIES & SOLUTIONS PRIVATE LIMITED",
                "trade_name": "ABC Tech Solutions",
                "cin": "U72200TG2018PTC123456",
                "pan": "ABCDE1234F",
                "company_status": "ACTIVE",
                "company_type": "Private Limited Company",
                "company_class": "Private",
                "company_category": "Company limited by shares",
                "incorporation_date": date(2018, 6, 15),
                "registered_state": "Telangana",
                "roc": "ROC Hyderabad",
                "registered_address": "Plot 42, Silicon Towers, Hitech City, Hyderabad, Telangana - 500081",
                "authorized_capital": 1000000.0,
                "paid_up_capital": 800000.0,
                "gstins": [
                    {"gstin": "36ABCDE1234F1Z5", "state": "Telangana", "jurisdiction": "Commissionerate-Hyderabad"},
                    {"gstin": "27ABCDE1234F1Z5", "state": "Maharashtra", "jurisdiction": "Commissionerate-Pune"},
                    {"gstin": "29ABCDE1234F1Z5", "state": "Karnataka", "jurisdiction": "Commissionerate-Bengaluru"}
                ],
                "directors": ["Rajesh Sharma", "Priya Sharma"],
                "events": [
                    (date(2018, 6, 15), "INCORPORATION", "Incorporated at ROC Hyderabad")
                ]
            },
            # 6. BHARAT LOGISTICS & INFRATECH PRIVATE LIMITED
            {
                "legal_name": "BHARAT LOGISTICS & INFRATECH PRIVATE LIMITED",
                "trade_name": "Bharat Express Logistics",
                "cin": "U60200TN2020PTC098765",
                "pan": "BPARL9876K",
                "company_status": "ACTIVE",
                "company_type": "Private Limited Company",
                "company_class": "Private",
                "company_category": "Company limited by shares",
                "incorporation_date": date(2020, 2, 14),
                "registered_state": "Tamil Nadu",
                "roc": "ROC Chennai",
                "registered_address": "No. 18, Industrial Estate Road, Guindy, Chennai - 600032, Tamil Nadu, India",
                "authorized_capital": 5000000.0,
                "paid_up_capital": 4500000.0,
                "gstins": [
                    {"gstin": "33BPARL9876K1Z9", "state": "Tamil Nadu", "jurisdiction": "Commissionerate-Chennai South"}
                ],
                "directors": ["Karthik Parthiban", "Sundaram Parthiban"],
                "events": [
                    (date(2020, 2, 14), "INCORPORATION", "Incorporated at ROC Chennai")
                ]
            },
            # 7. HIMALAYA BIO-PHARMA RESEARCH FOUNDATION
            {
                "legal_name": "HIMALAYA BIO-PHARMA RESEARCH FOUNDATION",
                "trade_name": "Himalaya Bio-Pharma Foundation",
                "cin": "U85100DL2022NPL543210",
                "pan": "AAACH5432R",
                "company_status": "ACTIVE",
                "company_type": "Non-Profit Organization",
                "company_class": "Section 8 Company",
                "company_category": "Company limited by guarantee",
                "incorporation_date": date(2022, 11, 12),
                "registered_state": "Delhi",
                "roc": "ROC Delhi",
                "registered_address": "4B Institutional Area, Vasant Kunj, New Delhi - 110070, India",
                "authorized_capital": 100000.0,
                "paid_up_capital": 100000.0,
                "gstins": [],
                "directors": ["Dr. Arvind Swaminathan", "Dr. Sunita Mehra"],
                "events": [
                    (date(2022, 11, 12), "INCORPORATION", "Incorporated as Section 8 Company at ROC Delhi")
                ]
            },
            # 7. PRITI SEWING MACHINE CO. (PROPRIETORSHIP)
            {
                "legal_name": "PRITI SEWING MACHINE CO.",
                "trade_name": "Priti Sewing Machine Co.",
                "cin": None,
                "pan": "AFRPG4233M",
                "company_status": "ACTIVE",
                "company_type": "Proprietorship",
                "company_class": "Proprietorship",
                "company_category": "Sole Proprietorship Enterprise",
                "incorporation_date": date(2017, 7, 1),
                "registered_state": "Telangana",
                "roc": "Not Applicable",
                "registered_address": "Shop No. 8-1-411/412, Rashtrapati Road, Opposite Krishna Coffee Works, Shivaji Nagar, Secunderabad, Hyderabad - 500003, Telangana, India",
                "authorized_capital": 0.0,
                "paid_up_capital": 0.0,
                "gstins": [
                    {"gstin": "36AFRPG4233M1Z3", "state": "Telangana", "jurisdiction": "Commissionerate-Hyderabad Secunderabad"}
                ],
                "directors": ["Proprietor (Individual)"],
                "events": [
                    (date(2017, 7, 1), "GST_REGISTRATION", "Registered under GST in Telangana")
                ]
            },
            # 8. ZOMATO LIMITED
            {
                "legal_name": "ZOMATO LIMITED",
                "trade_name": "Zomato",
                "cin": "L93030DL2010PLC198141",
                "pan": "AAACZ9999F",
                "company_status": "ACTIVE",
                "company_type": "Public Limited Company",
                "company_class": "Public",
                "company_category": "Company limited by shares",
                "incorporation_date": date(2010, 1, 18),
                "registered_state": "Delhi",
                "roc": "ROC Delhi",
                "registered_address": "Ground Floor, 12A, 94 Meghdoot, Nehru Place, New Delhi - 110019, India",
                "authorized_capital": 14480000000.0,
                "paid_up_capital": 8820000000.0,
                "gstins": [
                    {"gstin": "07AAACZ9999F1Z4", "state": "Delhi", "jurisdiction": "Commissionerate-Delhi South"}
                ],
                "directors": ["Deepinder Goyal", "Sanjeev Bikhchandani"],
                "events": [
                    (date(2010, 1, 18), "INCORPORATION", "Incorporated as DC Foodiebay Online Services Private Limited"),
                    (date(2021, 4, 9), "IPO", "Converted to Public Limited Company for IPO")
                ]
            }
        ]

        for item in companies_data:
            print(f"Ingesting: {item['legal_name']}...")
            c = Company(
                id=str(uuid.uuid4()),
                cin=item["cin"],
                legal_name=item["legal_name"],
                trade_name=item["trade_name"],
                company_status=item["company_status"],
                company_type=item["company_type"],
                company_class=item["company_class"],
                company_category=item["company_category"],
                incorporation_date=item["incorporation_date"],
                registered_state=item["registered_state"],
                roc=item["roc"],
                registered_address=item["registered_address"],
                authorized_capital=item["authorized_capital"],
                paid_up_capital=item["paid_up_capital"]
            )
            db.add(c)
            db.commit()

            # Store Raw MCA Record if CIN present
            if item["cin"]:
                raw_payload = dict(item)
                if raw_payload.get("incorporation_date"):
                    raw_payload["incorporation_date"] = raw_payload["incorporation_date"].isoformat()
                raw_payload["events"] = [
                    (ed.isoformat(), et, edesc) for ed, et, edesc in item.get("events", [])
                ]
                raw_r = RawMCARecord(
                    id=str(uuid.uuid4()),
                    cin=item["cin"],
                    company_name=item["legal_name"],
                    company_status=item["company_status"],
                    company_class=item["company_class"],
                    company_category=item["company_category"],
                    authorized_capital=item["authorized_capital"],
                    paid_up_capital=item["paid_up_capital"],
                    incorporation_date=item["incorporation_date"],
                    registered_state=item["registered_state"],
                    roc=item["roc"],
                    raw_payload=raw_payload
                )
                db.add(raw_r)

            # Store Identifiers
            if item["cin"]:
                db.add(Identifier(
                    id=str(uuid.uuid4()), company_id=c.id, type="CIN",
                    normalized_value=item["cin"], value_hash=hash_identifier(item["cin"]),
                    is_primary=True, source_id=mca_source.id
                ))
            if item["pan"]:
                db.add(Identifier(
                    id=str(uuid.uuid4()), company_id=c.id, type="PAN",
                    normalized_value=item["pan"], value_hash=hash_identifier(item["pan"]),
                    is_primary=True, source_id=pan_source.id
                ))

            # Store GST Registrations
            for g_item in item.get("gstins", []):
                db.add(GSTRegistration(
                    id=str(uuid.uuid4()),
                    company_id=c.id,
                    gstin=g_item["gstin"],
                    state=g_item["state"],
                    registration_date=item["incorporation_date"],
                    status="ACTIVE",
                    taxpayer_type="Regular",
                    business_constitution=item["company_type"],
                    centre_jurisdiction=g_item["jurisdiction"],
                    state_jurisdiction=f"Circle-{g_item['state']}",
                    principal_place_of_business=item["registered_address"],
                    nature_of_business=["Corporate Business", "Commercial Operations"],
                    source_id=gst_source.id
                ))
                db.add(Identifier(
                    id=str(uuid.uuid4()), company_id=c.id, type="GSTIN",
                    normalized_value=g_item["gstin"], value_hash=hash_identifier(g_item["gstin"]),
                    is_primary=True, source_id=gst_source.id
                ))

            # Store Directors
            for d_name in item.get("directors", []):
                db.add(Director(
                    id=str(uuid.uuid4()),
                    company_id=c.id,
                    name=d_name,
                    designation="Director",
                    appointment_date=item["incorporation_date"],
                    source_id=mca_source.id
                ))

            # Store Filings
            db.add_all([
                Filing(id=str(uuid.uuid4()), company_id=c.id, filing_type="AOC-4", financial_year="FY 2025-26", filing_date=date(2025, 10, 30), status="Approved", source_id=mca_source.id),
                Filing(id=str(uuid.uuid4()), company_id=c.id, filing_type="MGT-7", financial_year="FY 2025-26", filing_date=date(2025, 11, 28), status="Approved", source_id=mca_source.id),
                Filing(id=str(uuid.uuid4()), company_id=c.id, filing_type="DIR-12", financial_year="FY 2024-25", filing_date=date(2024, 8, 15), status="Approved", source_id=mca_source.id)
            ])

            # Store Events
            db.add_all([
                CompanyEvent(id=str(uuid.uuid4()), company_id=c.id, event_type="INCORPORATION", event_date=item["incorporation_date"], description="Incorporation record filed with Registrar of Companies", source_id=mca_source.id),
                CompanyEvent(id=str(uuid.uuid4()), company_id=c.id, event_type="CAPITAL_INCREASE", event_date=date(2020, 1, 1), description="Authorized Capital increased", source_id=mca_source.id),
                CompanyEvent(id=str(uuid.uuid4()), company_id=c.id, event_type="DIRECTOR_APPOINTMENT", event_date=date(2021, 5, 10), description="Director appointment approved", source_id=mca_source.id),
                CompanyEvent(id=str(uuid.uuid4()), company_id=c.id, event_type="ANNUAL_FILING", event_date=date(2025, 10, 30), description="Annual return filing completed", source_id=mca_source.id)
            ])

            db.commit()

        print("Dataset ingestion completed successfully! All companies indexed with full provenance graph.")
    except Exception as e:
        db.rollback()
        print(f"Error during database ingestion: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
