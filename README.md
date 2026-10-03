# GST Search & Corporate Intelligence Platform (CompanyLens)

A production-ready Indian company intelligence, verification, and GST search platform built with FastAPI and React + TypeScript + Vite.

## Overview

GST Search / CompanyLens provides authoritative, multi-source company verification by cross-referencing and synthesizing data from:
- **GSTN System** (GSTIN validation, status, jurisdiction, filing track records)
- **Ministry of Corporate Affairs (MCA)** (CIN validation, company status, directors, authorized & paid-up capital)
- **Income Tax Department** (PAN corporate/individual resolution with cryptographic hashing and masking)
- **Financial Registry** (Credit ratings, revenue, EBITDA, profit margins, balance sheets)

---

## Key Features

1. **Intelligent Identifier Resolution**
   - Instant query auto-detection for **GSTIN** (15-char), **PAN** (10-char), **CIN** (21-char), and fuzzy **Company Name**.
   - Cross-links GSTINs, corporate PANs, and CINs into a unified corporate profile.

2. **Source Badge & Data Lineage**
   - Every single field displays an interactive source badge (`GSTN_DIRECT`, `MCA_DIRECT`, `CBDT_PAN`, `RESOLVED`, `DERIVED`).
   - Audit trail showing verification timestamps, refresh status, and authoritative confidence scores.

3. **Multi-Source Company Comparison**
   - Side-by-side comparison of company metrics, directors, GST compliance, and capitalization.

4. **Watchlist & Due-Diligence Reports**
   - Save companies to a localized watchlist.
   - Generate printable due-diligence reports with compliance summaries.

5. **Security & Compliance**
   - PAN masking (`ABCDE****F`) and cryptographic SHA-256 internal identifier hashing.
   - Rate limiting (in-memory sliding window).
   - SQL injection & XSS sanitization.
   - Secret redaction in logs.

---

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind/Vanilla CSS, Lucide Icons, Framer Motion
- **Backend:** FastAPI, Python 3.12+, SQLAlchemy, SQLite / PostgreSQL, Alembic
- **Testing:** Pytest (Unit, Integration, Security), Vite TypeScript compiler

---

## Getting Started

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt

# Run SQLite / Database migration & seeds
python scripts/seed_company_data.py

# Run FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be accessible at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The web application will be accessible at: `http://localhost:5173`

---

## Running Tests

### Backend Test Suite
```bash
cd backend
pytest tests/test_unit.py tests/test_integration.py tests/test_security.py
```

### Frontend Build Validation
```bash
cd frontend
npm run build
```
