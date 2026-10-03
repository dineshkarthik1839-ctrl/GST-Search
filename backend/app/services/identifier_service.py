import re
from typing import Dict, Any, Optional, Tuple
from enum import Enum

class IdentifierType(str, Enum):
    GSTIN = "GSTIN"
    PAN = "PAN"
    CIN = "CIN"
    COMPANY_NAME = "COMPANY_NAME"
    UNKNOWN = "UNKNOWN"

# GST State codes mapping
GST_STATE_CODES = {
    "01": "Jammu and Kashmir", "02": "Himachal Pradesh", "03": "Punjab", "04": "Chandigarh",
    "05": "Uttarakhand", "06": "Haryana", "07": "Delhi", "08": "Rajasthan",
    "09": "Uttar Pradesh", "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram", "16": "Tripura",
    "17": "Meghalaya", "18": "Assam", "19": "West Bengal", "20": "Jharkhand",
    "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "26": "Dadra and Nagar Haveli and Daman and Diu", "27": "Maharashtra", "29": "Karnataka",
    "30": "Goa", "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu",
    "34": "Puducherry", "35": "Andaman and Nicobar Islands", "36": "Telangana",
    "37": "Andhra Pradesh", "38": "Ladakh", "97": "Other Territory", "99": "Centre Jurisdiction"
}

# PAN 4th Character Entity Types
PAN_ENTITY_TYPES = {
    'C': "Company",
    'P': "Person / Individual",
    'H': "Hindu Undivided Family (HUF)",
    'F': "Firm / Limited Liability Partnership (LLP)",
    'A': "Association of Persons (AOP)",
    'T': "Trust",
    'B': "Body of Individuals (BOI)",
    'L': "Local Authority",
    'J': "Artificial Juridical Person",
    'G': "Government Agency"
}

# CIN Company Class Codes
CIN_CLASS_CODES = {
    'PTC': "Private Limited Company",
    'PLC': "Public Limited Company",
    'SGC': "State Government Company",
    'GOI': "Union Government Company",
    'NPL': "Non-Profit License / Section 8",
    'FTC': "Foreign Company",
    'ULL': "Unlisted Public Limited",
    'GAP': "General Association / Partnership"
}

GSTIN_REGEX = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
PAN_REGEX = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
CIN_REGEX = re.compile(r'^([LU]{1})([0-9]{5})([A-Z]{2})([0-9]{4})([A-Z]{3})([0-9]{6})$')

def calculate_gstin_checksum(gstin_14: str) -> str:
    """
    Computes GSTIN 15th check character using GSTIN Mod 36 algorithm.
    """
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    factor = 1
    total = 0
    mod = 36

    for char in gstin_14:
        code_point = chars.index(char)
        digit = factor * code_point
        factor = 2 if factor == 1 else 1
        digit = (digit // mod) + (digit % mod)
        total += digit

    remainder = total % mod
    check_code_point = (mod - remainder) % mod
    return chars[check_code_point]

def validate_gstin(gstin: str) -> Dict[str, Any]:
    """
    Validates GSTIN format, structure, and extracts state and PAN.
    """
    clean = gstin.strip().upper()
    if not GSTIN_REGEX.match(clean):
        return {
            "is_valid": False,
            "error": "Invalid GSTIN format. Expected 15-character alphanumeric format (e.g. 27ABCDE1234F1Z5)."
        }
    
    state_code = clean[:2]
    embedded_pan = clean[2:12]
    entity_code = clean[12]
    checksum_char = clean[14]
    
    expected_checksum = calculate_gstin_checksum(clean[:14])
    checksum_valid = (expected_checksum == checksum_char)

    return {
        "is_valid": True,
        "normalized_value": clean,
        "state_code": state_code,
        "state_name": GST_STATE_CODES.get(state_code, "Unknown Jurisdiction"),
        "embedded_pan": embedded_pan,
        "entity_code": entity_code,
        "checksum_valid": checksum_valid,
        "checksum_char": checksum_char
    }

def validate_pan(pan: str) -> Dict[str, Any]:
    """
    Validates PAN format and identifies entity type according to 4th character.
    """
    clean = pan.strip().upper()
    if not PAN_REGEX.match(clean):
        return {
            "is_valid": False,
            "error": "Invalid PAN format. Expected 10 alphanumeric characters (e.g. ABCDE1234F)."
        }
    
    entity_char = clean[3]
    entity_type = PAN_ENTITY_TYPES.get(entity_char, "Other")
    is_corporate = entity_char in ['C', 'F', 'A', 'T', 'B', 'L', 'J', 'G']

    return {
        "is_valid": True,
        "normalized_value": clean,
        "entity_code": entity_char,
        "entity_type": entity_type,
        "is_corporate": is_corporate,
        "masked_pan": f"{clean[:5]}****{clean[-1]}"
    }

def validate_cin(cin: str) -> Dict[str, Any]:
    """
    Validates Corporate Identification Number (CIN) and extracts attributes:
    Listing status, industry code, state, year of incorporation, company type, registration number.
    """
    clean = cin.strip().upper()
    match = CIN_REGEX.match(clean)
    if not match:
        return {
            "is_valid": False,
            "error": "Invalid CIN format. Expected 21-character format (e.g. U72200TG2018PTC123456)."
        }
    
    listing_char, nic_code, state_code, year, class_code, reg_num = match.groups()
    is_listed = (listing_char == 'L')
    company_class = CIN_CLASS_CODES.get(class_code, "Corporate Entity")

    return {
        "is_valid": True,
        "normalized_value": clean,
        "is_listed": is_listed,
        "listing_status": "Listed" if is_listed else "Unlisted",
        "industry_nic": nic_code,
        "state_code": state_code,
        "incorporation_year": int(year),
        "class_code": class_code,
        "company_class": company_class,
        "registration_number": reg_num
    }

def normalize_company_name(name: str) -> str:
    """
    Normalizes company names for high-precision fuzzy matching:
    Converts to uppercase, expands standard corporate abbreviations, strips special characters.
    """
    if not name:
        return ""
    cleaned = name.upper().strip()
    cleaned = re.sub(r'[^A-Z0-9\s]', ' ', cleaned)
    
    # Common abbreviation normalization
    replacements = [
        (r'\bPVT\s+LTD\b', 'PRIVATE LIMITED'),
        (r'\bPVT\s+LIMITED\b', 'PRIVATE LIMITED'),
        (r'\bPRIVATE\s+LTD\b', 'PRIVATE LIMITED'),
        (r'\bLTD\b', 'LIMITED'),
        (r'\bCORP\b', 'CORPORATION'),
        (r'\bINC\b', 'INCORPORATED'),
        (r'\bCO\b', 'COMPANY'),
        (r'\bLLP\b', 'LIMITED LIABILITY PARTNERSHIP')
    ]
    for pattern, repl in replacements:
        cleaned = re.sub(pattern, repl, cleaned)
        
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def detect_identifier(query: str) -> Tuple[IdentifierType, str, Dict[str, Any]]:
    """
    Intelligently detects whether an input query is a GSTIN, PAN, CIN, or Company Name.
    Returns: (IdentifierType, normalized_query, validation_details)
    """
    raw = query.strip()
    compact = raw.upper().replace(" ", "").replace("-", "")

    # 1. Check GSTIN (15 chars)
    if len(compact) == 15 and compact[:2].isdigit():
        val = validate_gstin(compact)
        if val["is_valid"]:
            return IdentifierType.GSTIN, compact, val

    # 2. Check CIN (21 chars)
    if len(compact) == 21 and compact[0] in ['L', 'U'] and compact[1:6].isdigit():
        val = validate_cin(compact)
        if val["is_valid"]:
            return IdentifierType.CIN, compact, val

    # 3. Check PAN (10 chars)
    if len(compact) == 10 and compact[:5].isalpha() and compact[5:9].isdigit() and compact[9].isalpha():
        val = validate_pan(compact)
        if val["is_valid"]:
            return IdentifierType.PAN, compact, val

    # 4. Fallback to Company Name Search
    normalized_name = normalize_company_name(raw)
    return IdentifierType.COMPANY_NAME, normalized_name, {
        "is_valid": len(normalized_name) >= 2,
        "normalized_value": normalized_name,
        "original_query": raw
    }
