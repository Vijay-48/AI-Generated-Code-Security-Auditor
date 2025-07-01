import pytest

def test_rag_initialization(rag_service):
    assert rag_service.col.count() > 0

def test_retrieve_remediation(rag_service, sample_vulnerability):
    results = rag_service.retrieve_remediation(sample_vulnerability)
    assert len(results) > 0
    assert results[0]["metadata"]["cwe"] == "CWE-78"
    assert "remediation_code" in results[0]

def test_get_pattern_by_cwe(rag_service):
    pattern = rag_service.get_pattern_by_cwe("CWE-89")
    assert pattern is not None
    assert "SELECT" in pattern["remediation_code"]

def test_add_remediation_pattern(rag_service):
    new_pattern = {
        "cwe_id": "CWE-123",
        "title": "Test Vulnerability",
        "description": "Test description",
        "pattern": "Test pattern",
        "remediation": "# Test remediation code",
        "languages": ["python"],
        "severity": "MEDIUM"
    }
    initial_count = rag_service.col.count()
    rag_service.add_remediation_pattern(new_pattern)
    assert rag_service.col.count() == initial_count + 1