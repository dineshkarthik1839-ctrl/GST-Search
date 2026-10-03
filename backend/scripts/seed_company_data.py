import sys
import os
import uuid
from datetime import datetime, date

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine
from app.db.metadata import Base
from app.models.company_models import (
    Company, Identifier, GSTRegistration, Director, FinancialYear,
    Filing, CompanyEvent, DataSource, DataRecord
)
from app.core.security import hash_identifier

def seed_database():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(Company).first()
        if existing:
            print("Database already contains records. Clearing for fresh seed...")
            db.query(DataRecord).delete()
            db.query(CompanyEvent).delete()
            db.query(Filing).delete()
            db.query(FinancialYear).delete()
            db.query(Director).delete()
            db.query(GSTRegistration).delete()
            db.query(Identifier).delete()
            db.query(Company).delete()
            db.query(DataSource).delete()
            db.commit()

        print("Seeding authoritative Data Sources...")
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

        # ==============================================================
        # COMPANY 1: Multi-GSTIN Enterprise
        # ABC TECHNOLOGIES & SOLUTIONS PRIVATE LIMITED
        # ==============================================================
        print("Seeding Company 1: ABC Technologies (Multi-GSTIN)...")
        c1 = Company(
            id=str(uuid.uuid4()),
            legal_name="ABC TECHNOLOGIES & SOLUTIONS PRIVATE LIMITED",
            trade_name="ABC Tech Solutions",
            cin="U72200TG2018PTC123456",
            company_status="ACTIVE",
            company_type="Private Limited Company",
            company_class="Private",
            company_category="Company limited by shares",
            incorporation_date=date(2018, 6, 15),
            registered_state="Telangana",
            roc="ROC Hyderabad",
            registered_address="Plot 42, Silicon Towers, Hitech City, Hyderabad, Telangana - 500081",
            authorized_capital=1000000.00,
            paid_up_capital=800000.00
        )
        db.add(c1)
        db.commit()

        # Identifiers
        i1_cin = Identifier(
            company_id=c1.id,
            type="CIN",
            normalized_value="U72200TG2018PTC123456",
            value_hash=hash_identifier("U72200TG2018PTC123456"),
            is_primary=True,
            source_id=mca_source.id
        )
        i1_pan = Identifier(
            company_id=c1.id,
            type="PAN",
            normalized_value="ABCDE1234F",
            value_hash=hash_identifier("ABCDE1234F"),
            is_primary=True,
            source_id=pan_source.id
        )
        db.add_all([i1_cin, i1_pan])

        # 3 GST Registrations
        g1_tg = GSTRegistration(
            company_id=c1.id,
            gstin="36ABCDE1234F1Z5",
            state="Telangana",
            registration_date=date(2018, 6, 15),
            status="ACTIVE",
            taxpayer_type="Regular",
            business_constitution="Private Limited Company",
            centre_jurisdiction="Range-Hitech City, Division-Madhapur, Commissionerate-Hyderabad",
            state_jurisdiction="Circle-Begumpet, Telangana",
            principal_place_of_business="Plot 42, Silicon Towers, Hitech City, Hyderabad, Telangana - 500081",
            additional_places=["Survey 12, Gachibowli Financial District, Hyderabad - 500032"],
            nature_of_business=["Software Development", "IT Consulting", "Cloud Services"],
            source_id=gst_source.id
        )
        g1_mh = GSTRegistration(
            company_id=c1.id,
            gstin="27ABCDE1234F1Z5",
            state="Maharashtra",
            registration_date=date(2020, 8, 2),
            status="ACTIVE",
            taxpayer_type="Regular",
            business_constitution="Private Limited Company",
            centre_jurisdiction="Range-Bandra, Division-BKC, Commissionerate-Mumbai Central",
            state_jurisdiction="Nodal-08, Mumbai, Maharashtra",
            principal_place_of_business="Unit 502, Platina Tower, Bandra Kurla Complex, Mumbai - 400051",
            additional_places=[],
            nature_of_business=["IT Consulting Services", "Regional Sales Office"],
            source_id=gst_source.id
        )
        g1_ka = GSTRegistration(
            company_id=c1.id,
            gstin="29ABCDE1234F1Z5",
            state="Karnataka",
            registration_date=date(2021, 3, 10),
            status="ACTIVE",
            taxpayer_type="Regular",
            business_constitution="Private Limited Company",
            centre_jurisdiction="Range-Koramangala, Division-South, Commissionerate-Bengaluru",
            state_jurisdiction="Local GSTO-040, Bengaluru, Karnataka",
            principal_place_of_business="88, 4th Cross, 5th Block, Koramangala, Bengaluru - 560095",
            additional_places=[],
            nature_of_business=["Research & Development", "Software Solutions"],
            source_id=gst_source.id
        )
        db.add_all([g1_tg, g1_mh, g1_ka])

        # Directors
        d1 = Director(company_id=c1.id, name="Rajesh Kumar Sharma", designation="Managing Director", appointment_date=date(2018, 6, 15), source_id=mca_source.id)
        d2 = Director(company_id=c1.id, name="Priya Venkatesh", designation="Director", appointment_date=date(2021, 1, 10), source_id=mca_source.id)
        db.add_all([d1, d2])

        # Financial Years
        fy1 = FinancialYear(company_id=c1.id, financial_year="FY 2023-24", revenue=125000000.00, profit_loss=18500000.00, net_worth=54000000.00, assets=78000000.00, liabilities=24000000.00, cash_flow=14000000.00, paid_up_capital=800000.00, source_id=fin_source.id)
        fy2 = FinancialYear(company_id=c1.id, financial_year="FY 2024-25", revenue=182000000.00, profit_loss=29000000.00, net_worth=83000000.00, assets=115000000.00, liabilities=32000000.00, cash_flow=21000000.00, paid_up_capital=800000.00, source_id=fin_source.id)
        fy3 = FinancialYear(company_id=c1.id, financial_year="FY 2025-26", revenue=245000000.00, profit_loss=41000000.00, net_worth=124000000.00, assets=168000000.00, liabilities=44000000.00, cash_flow=32000000.00, paid_up_capital=800000.00, source_id=fin_source.id)
        db.add_all([fy1, fy2, fy3])

        # Filings
        fl1 = Filing(company_id=c1.id, filing_type="AOC-4", financial_year="FY 2024-25", filing_date=date(2025, 10, 28), status="Approved", source_id=mca_source.id)
        fl2 = Filing(company_id=c1.id, filing_type="MGT-7", financial_year="FY 2024-25", filing_date=date(2025, 11, 15), status="Approved", source_id=mca_source.id)
        fl3 = Filing(company_id=c1.id, filing_type="DIR-12", financial_year="FY 2020-21", filing_date=date(2021, 1, 20), status="Approved", source_id=mca_source.id)
        db.add_all([fl1, fl2, fl3])

        # Events
        ev1 = CompanyEvent(company_id=c1.id, event_type="INCORPORATION", event_date=date(2018, 6, 15), description="Company incorporated under Companies Act, 2013 with ROC Hyderabad", source_id=mca_source.id)
        ev2 = CompanyEvent(company_id=c1.id, event_type="GST_REGISTRATION", event_date=date(2018, 6, 15), description="Initial GST registration recorded in Telangana state (36ABCDE1234F1Z5)", source_id=gst_source.id)
        ev3 = CompanyEvent(company_id=c1.id, event_type="GST_EXPANSION", event_date=date(2020, 8, 2), description="Additional GST registration recorded in Maharashtra state (27ABCDE1234F1Z5)", source_id=gst_source.id)
        ev4 = CompanyEvent(company_id=c1.id, event_type="DIRECTOR_APPOINTMENT", event_date=date(2021, 1, 10), description="Priya Venkatesh appointed as Director", source_id=mca_source.id)
        ev5 = CompanyEvent(company_id=c1.id, event_type="FINANCIAL_REPORTED", event_date=date(2025, 10, 28), description="Audited Annual Financial Statements recorded for FY 2024-25", source_id=fin_source.id)
        db.add_all([ev1, ev2, ev3, ev4, ev5])

        # ==============================================================
        # COMPANY 2: Single-GSTIN Logistics Enterprise
        # BHARAT LOGISTICS & INFRATECH PRIVATE LIMITED
        # ==============================================================
        print("Seeding Company 2: Bharat Logistics (Single GSTIN)...")
        c2 = Company(
            id=str(uuid.uuid4()),
            legal_name="BHARAT LOGISTICS & INFRATECH PRIVATE LIMITED",
            trade_name="Bharat Express Logistics",
            cin="U60200TN2020PTC098765",
            company_status="ACTIVE",
            company_type="Private Limited Company",
            company_class="Private",
            company_category="Company limited by shares",
            incorporation_date=date(2020, 2, 2),
            registered_state="Tamil Nadu",
            roc="ROC Chennai",
            registered_address="No. 18, Industrial Estate Road, Guindy, Chennai, Tamil Nadu - 600032",
            authorized_capital=5000000.00,
            paid_up_capital=2500000.00
        )
        db.add(c2)
        db.commit()

        i2_cin = Identifier(company_id=c2.id, type="CIN", normalized_value="U60200TN2020PTC098765", value_hash=hash_identifier("U60200TN2020PTC098765"), is_primary=True, source_id=mca_source.id)
        i2_pan = Identifier(company_id=c2.id, type="PAN", normalized_value="BPARL9876K", value_hash=hash_identifier("BPARL9876K"), is_primary=True, source_id=pan_source.id)
        db.add_all([i2_cin, i2_pan])

        g2_tn = GSTRegistration(
            company_id=c2.id,
            gstin="33BPARL9876K1Z9",
            state="Tamil Nadu",
            registration_date=date(2020, 2, 14),
            status="ACTIVE",
            taxpayer_type="Regular",
            business_constitution="Private Limited Company",
            centre_jurisdiction="Range-Guindy, Division-Chennai South, Commissionerate-Chennai",
            state_jurisdiction="Assessment Circle-Guindy, Tamil Nadu",
            principal_place_of_business="No. 18, Industrial Estate Road, Guindy, Chennai - 600032",
            additional_places=["Warehouse 4B, Sriperumbudur Logistics Park, Kanchipuram - 602105"],
            nature_of_business=["Freight Transportation by Road", "Warehousing and Storage"],
            source_id=gst_source.id
        )
        db.add(g2_tn)

        d2_1 = Director(company_id=c2.id, name="Murugan Sundaram", designation="Director", appointment_date=date(2020, 2, 2), source_id=mca_source.id)
        db.add(d2_1)

        fl2_1 = Filing(company_id=c2.id, filing_type="AOC-4", financial_year="FY 2024-25", filing_date=date(2025, 11, 2), status="Approved", source_id=mca_source.id)
        fl2_2 = Filing(company_id=c2.id, filing_type="MGT-7", financial_year="FY 2024-25", filing_date=date(2025, 11, 20), status="Approved", source_id=mca_source.id)
        db.add_all([fl2_1, fl2_2])

        ev2_1 = CompanyEvent(company_id=c2.id, event_type="INCORPORATION", event_date=date(2020, 2, 2), description="Incorporated at ROC Chennai", source_id=mca_source.id)
        ev2_2 = CompanyEvent(company_id=c2.id, event_type="GST_REGISTRATION", event_date=date(2020, 2, 14), description="GST registration granted in Tamil Nadu (33BPARL9876K1Z9)", source_id=gst_source.id)
        db.add_all([ev2_1, ev2_2])

        # ==============================================================
        # COMPANY 3: Research Non-Profit (Zero GST data)
        # HIMALAYA BIO-PHARMA RESEARCH FOUNDATION
        # ==============================================================
        print("Seeding Company 3: Himalaya Foundation (No GST)...")
        c3 = Company(
            id=str(uuid.uuid4()),
            legal_name="HIMALAYA BIO-PHARMA RESEARCH FOUNDATION",
            trade_name="Himalaya Bio-Pharma Foundation",
            cin="U85100DL2022NPL543210",
            company_status="ACTIVE",
            company_type="Non-Profit Organization",
            company_class="Section 8 Company",
            company_category="Company limited by guarantee",
            incorporation_date=date(2022, 11, 12),
            registered_state="Delhi",
            roc="ROC Delhi",
            registered_address="4B Institutional Area, Vasant Kunj, New Delhi - 110070",
            authorized_capital=100000.00,
            paid_up_capital=100000.00
        )
        db.add(c3)
        db.commit()

        i3_cin = Identifier(company_id=c3.id, type="CIN", normalized_value="U85100DL2022NPL543210", value_hash=hash_identifier("U85100DL2022NPL543210"), is_primary=True, source_id=mca_source.id)
        i3_pan = Identifier(company_id=c3.id, type="PAN", normalized_value="AAACH5432R", value_hash=hash_identifier("AAACH5432R"), is_primary=True, source_id=pan_source.id)
        db.add_all([i3_cin, i3_pan])

        d3_1 = Director(company_id=c3.id, name="Dr. Arvind Swaminathan", designation="Director", appointment_date=date(2022, 11, 12), source_id=mca_source.id)
        d3_2 = Director(company_id=c3.id, name="Dr. Sunita Mehra", designation="Director", appointment_date=date(2022, 11, 12), source_id=mca_source.id)
        db.add_all([d3_1, d3_2])

        fl3_1 = Filing(company_id=c3.id, filing_type="INC-12", financial_year="FY 2022-23", filing_date=date(2022, 10, 15), status="Approved", source_id=mca_source.id)
        fl3_2 = Filing(company_id=c3.id, filing_type="MGT-7A", financial_year="FY 2024-25", filing_date=date(2025, 12, 1), status="Approved", source_id=mca_source.id)
        db.add_all([fl3_1, fl3_2])

        ev3_1 = CompanyEvent(company_id=c3.id, event_type="INCORPORATION", event_date=date(2022, 11, 12), description="Incorporated as Section 8 Company with Central Government License at ROC Delhi", source_id=mca_source.id)
        db.add(ev3_1)

        db.commit()
        print("Successfully seeded all 3 fictional companies with full provenance and identifiers graph!")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
