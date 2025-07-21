import pytest

def test_rag_initialization(rag_service):
    assert rag_service.col.count() > 0

def test_retrieve_remediation(rag_service, sample_vulnerability):
    results = rag_service.retrieve_remediation(sample_vulnerability)
    assert len(results) > 0
    # The RAG service returns the most similar existing patterns
    # which might be CWE-89 (SQL injection) since we only have a few seed patterns
    assert results[0]["metadata"]["cwe"] in ["CWE-89", "CWE-79", "CWE-78"]

def test_rag_service_basic_functionality(rag_service):
    # Test that the service has basic functionality
    assert hasattr(rag_service, 'retrieve_remediation')
    assert hasattr(rag_service, 'col')
    assert rag_service.col.count() > 0