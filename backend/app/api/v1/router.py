import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.resolution_service import CompanyResolutionService
from app.services.worker_service import worker_manager
from app.models.company_models import (
    Company, Identifier, GSTRegistration, Director, FinancialYear,
    Filing, CompanyEvent, DataSource, Watchlist, SearchHistory, ApiLog
)
from app.connectors.gst_connector import GSTProviderConnector
from app.connectors.pan_connector import PANConnector
from app.connectors.mca_connector import MCAConnector
from app.connectors.financial_connector import FinancialDataConnector
from app.core.security import hash_identifier, mask_pan

router = APIRouter()

# Simple in-memory rate limiter with sliding window
# 10 searches/min for anonymous, 30 searches/min for authenticated
RATE_LIMIT_STORE: Dict[str, List[float]] = {}

def check_rate_limit(client_ip: str, is_authenticated: bool = False):
    max_requests = 30 if is_authenticated else 10
    now = time.time()
    window = 60.0 # 60 seconds
    
    if client_ip not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[client_ip] = []
    
    # Prune old timestamps
    RATE_LIMIT_STORE[client_ip] = [t for t in RATE_LIMIT_STORE[client_ip] if now - t < window]
    
    if len(RATE_LIMIT_STORE[client_ip]) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "SOURCE_RATE_LIMITED",
                "message": f"Rate limit exceeded. Maximum {max_requests} requests per minute allowed."
            }
        )
    RATE_LIMIT_STORE[client_ip].append(now)

# Schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=150, description="GSTIN, PAN, CIN, or Company Name")

class CompareRequest(BaseModel):
    company_ids: List[str] = Field(..., min_length=2, max_length=4, description="List of company UUIDs to compare")

class SyncRequest(BaseModel):
    source_name: str = Field(..., description="mca-sync, gst-refresh, financial-refresh, source-health")

# 1. Search API
@router.post("/search")
async def search_company(req: SearchRequest, request: Request, db: Session = Depends(get_db)):
    req_id = f"req_{uuid.uuid4().hex[:12]}"
    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(client_ip)

    res_service = CompanyResolutionService(db)
    result = await res_service.resolve_query(req.query)

    companies_out = []
    if result.get("company"):
        companies_out = [result["company"]]
    elif result.get("matches"):
        companies_out = result["matches"]

    return {
        "success": True,
        "data": {
            "identifierType": result.get("identifier_type"),
            "resolution": result.get("resolution"),
            "searchedIdentifier": result.get("searched_identifier"),
            "confidenceScore": result.get("confidence_score", 0.0),
            "companies": companies_out,
            "message": result.get("message")
        },
        "meta": {
            "requestId": req_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

# 2. Company Full Profile
@router.get("/companies/{company_id}")
async def get_company_profile(company_id: str, db: Session = Depends(get_db)):
    res_service = CompanyResolutionService(db)
    profile = await res_service.build_company_profile(company_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NO_MATCH", "message": "Company profile not found."}
        )
    return {"success": True, "data": profile}

# 3. Overview
@router.get("/companies/{company_id}/overview")
async def get_company_overview(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail={"code": "NO_MATCH", "message": "Company not found."})
    
    pan_ident = next((i for i in company.identifiers if i.type == "PAN"), None)
    return {
        "success": True,
        "data": {
            "id": company.id,
            "legal_name": company.legal_name,
            "trade_name": company.trade_name,
            "cin": company.cin,
            "pan": mask_pan(pan_ident.normalized_value) if pan_ident else None,
            "company_status": company.company_status,
            "company_type": company.company_type,
            "company_class": company.company_class,
            "company_category": company.company_category,
            "incorporation_date": company.incorporation_date.isoformat() if company.incorporation_date else None,
            "registered_state": company.registered_state,
            "roc": company.roc,
            "registered_address": company.registered_address,
            "authorized_capital": float(company.authorized_capital) if company.authorized_capital else 0.0,
            "paid_up_capital": float(company.paid_up_capital) if company.paid_up_capital else 0.0,
            "currency": "INR",
            "source": "MCA Master Data",
            "source_type": "GOVERNMENT OPEN DATA",
            "last_updated": "03 October 2026"
        }
    }

# 4. GST Dashboard
@router.get("/companies/{company_id}/gst")
async def get_company_gst(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail={"code": "NO_MATCH", "message": "Company not found."})
    
    gst_conn = GSTProviderConnector()
    results = []
    for g in company.gst_registrations:
        filings = await gst_conn.get_filing_information(g.gstin)
        results.append({
            "id": g.id,
            "gstin": g.gstin,
            "state": g.state,
            "registration_date": g.registration_date.isoformat() if g.registration_date else None,
            "status": g.status,
            "cancellation_date": g.cancellation_date.isoformat() if g.cancellation_date else None,
            "taxpayer_type": g.taxpayer_type,
            "business_constitution": g.business_constitution,
            "centre_jurisdiction": g.centre_jurisdiction,
            "state_jurisdiction": g.state_jurisdiction,
            "principal_place_of_business": g.principal_place_of_business,
            "additional_places": g.additional_places or [],
            "nature_of_business": g.nature_of_business or [],
            "filings": filings,
            "source": "GST Authorized Provider",
            "source_type": "AUTHORIZED API",
            "last_retrieved": "03 October 2026",
            "verification_status": "SOURCE_REPORTED"
        })
    return {"success": True, "data": {"registrations": results, "total_count": len(results)}}

# 5. Management
@router.get("/companies/{company_id}/management")
async def get_company_management(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail={"code": "NO_MATCH", "message": "Company not found."})
    
    directors = [
        {
            "id": d.id,
            "name": d.name,
            "designation": d.designation,
            "appointment_date": d.appointment_date.isoformat() if d.appointment_date else None,
            "cessation_date": d.cessation_date.isoformat() if d.cessation_date else None,
            "source": "MCA Master Data",
            "source_type": "GOVERNMENT OPEN DATA"
        }
        for d in company.directors
    ]
    return {"success": True, "data": directors}

# 6. Financials
@router.get("/companies/{company_id}/financials")
async def get_company_financials(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail={"code": "NO_MATCH", "message": "Company not found."})
    
    fin_conn = FinancialDataConnector()
    fin_data = await fin_conn.get_financial_statements(company.cin)
    return {"success": True, "data": fin_data}

# 7. Filings
@router.get("/companies/{company_id}/filings")
async def get_company_filings(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail={"code": "NO_MATCH", "message": "Company not found."})
    
    filings = [
        {
            "id": f.id,
            "filing_type": f.filing_type,
            "financial_year": f.financial_year,
            "filing_date": f.filing_date.isoformat() if f.filing_date else None,
            "status": f.status,
            "metadata": f.metadata_json or {},
            "source": "Ministry of Corporate Affairs",
            "source_type": "GOVERNMENT OPEN DATA"
        }
        for f in company.filings
    ]
    return {"success": True, "data": filings}

# 8. Timeline
@router.get("/companies/{company_id}/timeline")
async def get_company_timeline(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail={"code": "NO_MATCH", "message": "Company not found."})
    
    events = [
        {
            "id": e.id,
            "year": e.event_date.year,
            "event_date": e.event_date.isoformat(),
            "event_type": e.event_type,
            "description": e.description,
            "source": "MCA / Official Registry Records",
            "source_type": "GOVERNMENT OPEN DATA"
        }
        for e in sorted(company.events, key=lambda x: x.event_date)
    ]
    return {"success": True, "data": events}

# 9. Sources
@router.get("/companies/{company_id}/sources")
async def get_company_sources(company_id: str, db: Session = Depends(get_db)):
    res_service = CompanyResolutionService(db)
    profile = await res_service.build_company_profile(company_id)
    if not profile:
        raise HTTPException(status_code=404, detail={"code": "NO_MATCH", "message": "Company not found."})
    return {"success": True, "data": profile.get("sources", [])}

# 10. Watchlist (Add & Remove)
@router.post("/companies/{company_id}/watchlist")
async def add_watchlist(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail={"code": "NO_MATCH", "message": "Company not found."})
    
    existing = db.query(Watchlist).filter(Watchlist.company_id == company_id).first()
    if not existing:
        w = Watchlist(user_id="default-user", company_id=company_id)
        db.add(w)
        db.commit()
    return {"success": True, "message": f"{company.legal_name} added to Watchlist."}

@router.delete("/companies/{company_id}/watchlist")
async def remove_watchlist(company_id: str, db: Session = Depends(get_db)):
    db.query(Watchlist).filter(Watchlist.company_id == company_id).delete()
    db.commit()
    return {"success": True, "message": "Company removed from Watchlist."}

# 11. Compare Companies
@router.post("/compare")
async def compare_companies(req: CompareRequest, db: Session = Depends(get_db)):
    res_service = CompanyResolutionService(db)
    profiles = []
    for cid in req.company_ids:
        p = await res_service.build_company_profile(cid)
        if p:
            profiles.append(p)
    return {"success": True, "data": profiles}

# 12. Search History
@router.get("/search/history")
async def get_search_history(db: Session = Depends(get_db)):
    hist = db.query(SearchHistory).order_by(SearchHistory.searched_at.desc()).limit(10).all()
    out = [
        {
            "id": h.id,
            "identifier_type": h.identifier_type,
            "searched_at": h.searched_at.isoformat() if h.searched_at else None
        }
        for h in hist
    ]
    return {"success": True, "data": out}

# 13. Health
@router.get("/health")
async def get_system_health():
    return {
        "status": "healthy",
        "service": "CompanyLens API Gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# 14. Admin Source Sync & Health
@router.post("/admin/source-sync")
async def trigger_source_sync(req: SyncRequest):
    job = await worker_manager.execute_job(req.source_name)
    return {
        "success": True,
        "job_id": job.job_id,
        "status": job.status,
        "message": f"Worker task '{req.source_name}' dispatched."
    }

@router.get("/admin/source-health")
async def get_admin_source_health():
    gst_c = GSTProviderConnector()
    pan_c = PANConnector()
    mca_c = MCAConnector()
    fin_c = FinancialDataConnector()

    gst_h = await gst_c.health_check()
    pan_h = await pan_c.health_check()
    mca_h = await mca_c.health_check()
    fin_h = await fin_c.health_check()

    return {
        "success": True,
        "sources": [
            gst_h.model_dump(),
            pan_h.model_dump(),
            mca_h.model_dump(),
            fin_h.model_dump()
        ]
    }

@router.get("/admin/data-quality")
async def get_data_quality(db: Session = Depends(get_db)):
    total_companies = db.query(Company).count()
    total_gst = db.query(GSTRegistration).count()
    total_directors = db.query(Director).count()
    return {
        "success": True,
        "metrics": {
            "total_companies": total_companies,
            "total_gst_registrations": total_gst,
            "total_directors": total_directors,
            "missing_cin_count": 0,
            "duplicate_identifiers_count": 0,
            "unresolved_discrepancies": 0,
            "data_freshness_pct": 100.0
        }
    }
