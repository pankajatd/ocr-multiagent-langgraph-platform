"""
Unit and Integration Tests for LangGraph Multi-Agent OCR System.
"""
import os
import pytest
from ocr_agentic_system.graph.workflow import OCRMultiAgentGraph
from ocr_agentic_system.agents.orchestrator_agent import OrchestratorAgent
from ocr_agentic_system.agents.error_resolver_agent import ErrorResolverAgent
from ocr_agentic_system.utils.synthetic_generator import create_synthetic_datasets

@pytest.fixture(scope="session")
def test_datasets():
    test_dir = os.path.join(os.getcwd(), "sample_data")
    return create_synthetic_datasets(test_dir)

@pytest.fixture
def workflow_graph():
    return OCRMultiAgentGraph()

def test_orchestrator_classification():
    orchestrator = OrchestratorAgent()
    
    # Test 1: Invoice text cues
    inv_text = "INVOICE #9821 Date: 2026-01-01 Subtotal: $100.00 Total: $110.00"
    doc_type, conf, reason = orchestrator.classify_and_route(
        task_override="auto",
        raw_text=inv_text,
        dimensions={"width": 600, "height": 800},
        boxes_count=10
    )
    assert doc_type == "invoice"
    assert conf >= 0.70

    # Test 2: License Plate geometry & token cues
    plate_text = "AB12CDE"
    doc_type, conf, reason = orchestrator.classify_and_route(
        task_override="auto",
        raw_text=plate_text,
        dimensions={"width": 520, "height": 130}, # Aspect ratio 4.0
        boxes_count=2
    )
    assert doc_type == "license_plate"

    # Test 3: Document long text cues
    doc_text = "ANNUAL REPORT 2026. This comprehensive document details the experimental findings and legal terms of the archival research framework."
    doc_type, conf, reason = orchestrator.classify_and_route(
        task_override="auto",
        raw_text=doc_text,
        dimensions={"width": 700, "height": 900},
        boxes_count=15
    )
    assert doc_type == "document"

def test_error_resolver_invoice_math_healing():
    resolver = ErrorResolverAgent()
    
    # Simulate an OCR decimal slip: $250.00 + $25.00 erroneously read as $2750.00
    mock_state = {
        "classified_type": "invoice",
        "validation_errors": [
            "Mathematical Mismatch: Subtotal (250.0) + Tax (25.0) = 275.0, but Grand Total is 2750.0."
        ],
        "extracted_data": {
            "financial_summary": {
                "subtotal": 250.0,
                "tax": 25.0,
                "grand_total": 2750.0
            }
        },
        "retry_count": 0,
        "max_retries": 2
    }

    repaired_data, is_valid, strategy, diagnosis = resolver.resolve(mock_state)
    assert is_valid is True
    assert strategy is None
    # Recomputed to 275.0
    assert repaired_data["financial_summary"]["grand_total"] == 275.0
    assert "recomputed Grand Total" in diagnosis

def test_error_resolver_plate_confusion_healing():
    resolver = ErrorResolverAgent()
    
    # UK Plate format: 2 letters, 2 digits, 3 letters.
    # Suppose OCR misread digit '0' as letter 'O': 'ABO2CDE'
    mock_state = {
        "classified_type": "license_plate",
        "validation_errors": ["Plate candidate contains character confusion"],
        "extracted_data": {
            "plate_number": "ABO2CDE"
        },
        "retry_count": 0,
        "max_retries": 2
    }

    repaired_data, is_valid, strategy, diagnosis = resolver.resolve(mock_state)
    assert is_valid is True
    assert repaired_data["plate_number"] == "AB02CDE"

def test_end_to_end_document_graph(workflow_graph, test_datasets):
    clean_doc = test_datasets["document_clean"]
    result = workflow_graph.run(clean_doc)
    
    assert result["status"] == "completed"
    final_out = result["final_output"]
    assert final_out["document_type"] == "document"
    assert final_out["workflow_status"] == "SUCCESS"
    assert "paragraphs" in final_out["extracted_data"]

def test_end_to_end_invoice_graph_with_error_resolution(workflow_graph, test_datasets):
    err_inv = test_datasets["invoice_with_math_error"]
    result = workflow_graph.run(err_inv)
    
    assert result["status"] == "completed"
    final_out = result["final_output"]
    assert final_out["document_type"] == "invoice"
    # Verify that error resolver was triggered and resolved the math discrepancy
    assert final_out["errors_resolved"] is True
    assert final_out["workflow_status"] == "SUCCESS"
    assert len(final_out["error_history"]) > 0

def test_end_to_end_license_plate(workflow_graph, test_datasets):
    plate_img = test_datasets["license_plate_clean"]
    result = workflow_graph.run(plate_img)
    
    assert result["status"] == "completed"
    final_out = result["final_output"]
    assert final_out["document_type"] == "license_plate"
    assert "plate_number" in final_out["extracted_data"]

def test_end_to_end_pdf_invoice(workflow_graph, test_datasets):
    pdf_file = test_datasets["invoice_pdf"]
    result = workflow_graph.run(pdf_file)
    
    assert result["status"] == "completed"
    final_out = result["final_output"]
    assert final_out["file_type"] == "pdf"
    assert final_out["document_type"] == "invoice"
    assert final_out["workflow_status"] == "SUCCESS"
    fin = final_out["extracted_data"]["financial_summary"]
    assert fin["grand_total"] == 495.00

def test_end_to_end_txt_document(workflow_graph, test_datasets):
    txt_file = test_datasets["text_document"]
    result = workflow_graph.run(txt_file)
    
    assert result["status"] == "completed"
    final_out = result["final_output"]
    assert final_out["file_type"] == "txt"
    assert final_out["document_type"] == "document"
    assert final_out["workflow_status"] == "SUCCESS"
    assert final_out["extracted_data"]["total_word_count"] > 20

def test_end_to_end_csv_invoice(workflow_graph, test_datasets):
    csv_file = test_datasets["invoice_csv"]
    result = workflow_graph.run(csv_file)
    
    assert result["status"] == "completed"
    final_out = result["final_output"]
    assert final_out["file_type"] == "csv"
    assert final_out["document_type"] == "invoice"
    assert final_out["workflow_status"] == "SUCCESS"
    fin = final_out["extracted_data"]["financial_summary"]
    assert fin["grand_total"] == 170.50
