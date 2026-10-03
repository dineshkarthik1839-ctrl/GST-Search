import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Numeric, Date, DateTime, ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False) # OFFICIAL, GOVERNMENT OPEN DATA, AUTHORIZED API, LICENSED PROVIDER
    provider = Column(String(255), nullable=True)
    base_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    requires_auth = Column(Boolean, default=False)
    priority = Column(Integer, default=100) # Lower number = higher priority
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    identifiers = relationship("Identifier", back_populates="source")
    gst_registrations = relationship("GSTRegistration", back_populates="source")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    legal_name = Column(Text, nullable=False, index=True)
    trade_name = Column(Text, nullable=True)
    cin = Column(String(21), unique=True, nullable=True, index=True)
    company_status = Column(String(50), default="ACTIVE")
    company_type = Column(String(100), nullable=True) # Private Limited, Public Limited, etc.
    company_class = Column(String(100), nullable=True) # Private, Public, Section 8
    company_category = Column(String(100), nullable=True) # Company limited by shares
    incorporation_date = Column(Date, nullable=True)
    registered_state = Column(String(100), nullable=True, index=True)
    roc = Column(String(100), nullable=True) # ROC Hyderabad, ROC Mumbai, etc.
    registered_address = Column(Text, nullable=True)
    authorized_capital = Column(Numeric(18, 2), nullable=True)
    paid_up_capital = Column(Numeric(18, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    identifiers = relationship("Identifier", back_populates="company", cascade="all, delete-orphan")
    gst_registrations = relationship("GSTRegistration", back_populates="company", cascade="all, delete-orphan")
    directors = relationship("Director", back_populates="company", cascade="all, delete-orphan")
    financial_years = relationship("FinancialYear", back_populates="company", cascade="all, delete-orphan")
    filings = relationship("Filing", back_populates="company", cascade="all, delete-orphan")
    events = relationship("CompanyEvent", back_populates="company", cascade="all, delete-orphan")
    provenance_records = relationship("DataRecord", back_populates="company", cascade="all, delete-orphan")

class Identifier(Base):
    __tablename__ = "identifiers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20), nullable=False) # PAN, CIN, GSTIN
    normalized_value = Column(String(50), nullable=False, index=True)
    value_hash = Column(String(64), nullable=False, index=True) # SHA-256
    is_primary = Column(Boolean, default=False)
    source_id = Column(String(36), ForeignKey("data_sources.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="identifiers")
    source = relationship("DataSource", back_populates="identifiers")

class GSTRegistration(Base):
    __tablename__ = "gst_registrations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    gstin = Column(String(15), unique=True, nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    registration_date = Column(Date, nullable=True)
    status = Column(String(50), default="ACTIVE")
    cancellation_date = Column(Date, nullable=True)
    taxpayer_type = Column(String(100), default="Regular")
    business_constitution = Column(String(100), nullable=True)
    centre_jurisdiction = Column(String(255), nullable=True)
    state_jurisdiction = Column(String(255), nullable=True)
    principal_place_of_business = Column(Text, nullable=True)
    additional_places = Column(JSON, default=list)
    nature_of_business = Column(JSON, default=list)
    source_id = Column(String(36), ForeignKey("data_sources.id"), nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="gst_registrations")
    source = relationship("DataSource", back_populates="gst_registrations")

class Director(Base):
    __tablename__ = "directors"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    designation = Column(String(100), nullable=False) # Director, Managing Director, Designated Partner, KMP
    appointment_date = Column(Date, nullable=True)
    cessation_date = Column(Date, nullable=True)
    source_id = Column(String(36), ForeignKey("data_sources.id"), nullable=True)

    company = relationship("Company", back_populates="directors")

class FinancialYear(Base):
    __tablename__ = "financial_years"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    financial_year = Column(String(20), nullable=False) # e.g. FY 2024-25
    revenue = Column(Numeric(18, 2), nullable=True)
    profit_loss = Column(Numeric(18, 2), nullable=True)
    net_worth = Column(Numeric(18, 2), nullable=True)
    assets = Column(Numeric(18, 2), nullable=True)
    liabilities = Column(Numeric(18, 2), nullable=True)
    cash_flow = Column(Numeric(18, 2), nullable=True)
    paid_up_capital = Column(Numeric(18, 2), nullable=True)
    currency = Column(String(10), default="INR")
    source_id = Column(String(36), ForeignKey("data_sources.id"), nullable=True)
    source_type = Column(String(100), default="Licensed Financial Data Provider")
    retrieved_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="financial_years")

class Filing(Base):
    __tablename__ = "filings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    filing_type = Column(String(50), nullable=False) # AOC-4, MGT-7, DIR-12, INC-22
    financial_year = Column(String(20), nullable=True)
    filing_date = Column(Date, nullable=True)
    status = Column(String(50), default="Approved")
    metadata_json = Column(JSON, default=dict)
    source_id = Column(String(36), ForeignKey("data_sources.id"), nullable=True)

    company = relationship("Company", back_populates="filings")

class CompanyEvent(Base):
    __tablename__ = "company_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False) # INCORPORATION, GST_REGISTRATION, DIRECTOR_APPOINTMENT, STATUS_CHANGE
    event_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    source_id = Column(String(36), ForeignKey("data_sources.id"), nullable=True)

    company = relationship("Company", back_populates="events")

class DataRecord(Base):
    __tablename__ = "data_records"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(36), ForeignKey("data_sources.id"), nullable=True)
    entity_type = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_value = Column(JSON, nullable=False)
    verification_status = Column(String(50), default="SOURCE_REPORTED") # SOURCE_REPORTED, VERIFIED, DERIVED
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="provenance_records")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True)
    identifier_type = Column(String(20), nullable=False)
    query_hash = Column(String(64), nullable=False) # Never store raw PAN in search history
    searched_at = Column(DateTime, default=datetime.utcnow)
    result_company_id = Column(String(36), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)

class Watchlist(Base):
    __tablename__ = "watchlists"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=False, index=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ApiLog(Base):
    __tablename__ = "api_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_id = Column(String(100), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=True)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    error_code = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
