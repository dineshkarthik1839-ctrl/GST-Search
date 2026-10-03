import pytest
from app.services.identifier_service import (
    validate_gstin, validate_pan, validate_cin,
    detect_identifier, IdentifierType, normalize_company_name,
    calculate_gstin_checksum
)
from app.core.security import hash_identifier, mask_pan, sanitize_log_message

def test_gstin_validation_valid():
    gstin = "27ABCDE1234F1Z5"
    res = validate_gstin(gstin)
    assert res["is_valid"] is True
    assert res["state_code"] == "27"
    assert res["state_name"] == "Maharashtra"
    assert res["embedded_pan"] == "ABCDE1234F"

def test_gstin_validation_invalid_length():
    res = validate_gstin("27ABCDE1234F1Z")
    assert res["is_valid"] is False

def test_pan_validation_corporate():
    pan = "AAACH5432R" # 4th character 'C' indicates Company
    res = validate_pan(pan)
    assert res["is_valid"] is True
    assert res["entity_code"] == "C"
    assert res["entity_type"] == "Company"
    assert res["is_corporate"] is True
    assert res["masked_pan"] == "AAACH****R"

def test_pan_validation_individual():
    pan = "ABCPE1234F"
    res = validate_pan(pan)
    assert res["is_valid"] is True
    assert res["entity_code"] == "P"
    assert res["entity_type"] == "Person / Individual"
    assert res["is_corporate"] is False

def test_pan_validation_invalid():
    res = validate_pan("12345ABCDE")
    assert res["is_valid"] is False

def test_cin_validation_valid():
    cin = "U72200TG2018PTC123456"
    res = validate_cin(cin)
    assert res["is_valid"] is True
    assert res["is_listed"] is False
    assert res["state_code"] == "TG"
    assert res["incorporation_year"] == 2018
    assert res["class_code"] == "PTC"
    assert res["company_class"] == "Private Limited Company"

def test_cin_validation_invalid():
    res = validate_cin("INVALIDCIN123")
    assert res["is_valid"] is False

def test_identifier_auto_detection():
    # GSTIN
    t1, norm1, _ = detect_identifier("27ABCDE1234F1Z5")
    assert t1 == IdentifierType.GSTIN
    assert norm1 == "27ABCDE1234F1Z5"

    # CIN
    t2, norm2, _ = detect_identifier("U72200TG2018PTC123456")
    assert t2 == IdentifierType.CIN

    # PAN
    t3, norm3, _ = detect_identifier("ABCDE1234F")
    assert t3 == IdentifierType.PAN

    # Company Name
    t4, norm4, _ = detect_identifier("ABC Technologies Pvt Ltd")
    assert t4 == IdentifierType.COMPANY_NAME
    assert "PRIVATE LIMITED" in norm4

def test_normalize_company_name():
    assert normalize_company_name("Infosys Pvt Ltd") == "INFOSYS PRIVATE LIMITED"
    assert normalize_company_name("Tata Sons Ltd.") == "TATA SONS LIMITED"

def test_pan_security_mask_and_hash():
    pan = "ABCDE1234F"
    masked = mask_pan(pan)
    hashed = hash_identifier(pan)
    assert masked == "ABCDE****F"
    assert len(hashed) == 64 # SHA-256
    assert pan not in hashed

def test_sanitize_log_message():
    raw_log = "Processing query for user with PAN ABCDE1234F and secret token=my_secret_token"
    sanitized = sanitize_log_message(raw_log)
    assert "ABCDE1234F" not in sanitized
    assert "ABCDE****F" in sanitized
    assert "my_secret_token" not in sanitized
