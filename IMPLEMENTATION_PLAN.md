# 📋 Implementation Plan: LangGraph Multi-Agent OCR & Self-Healing Platform

## 1. Executive Overview
The **LangGraph Multi-Agent OCR Platform** is an enterprise-grade, agentic vision pipeline engineered for document text extraction, intelligent domain classification, and **autonomous error resolution**. Built upon LangGraph's cyclical state-graph paradigm, the architecture enables self-correcting feedback loops that intercept optical character recognition failures, resolve character confusion, and rebalance mathematical discrepancies without workflow termination.

---

## 2. Target Business Domains

1. **📄 Paper Document Digitizer (Archiving & Semantic Search)**
   - Target: Historical paper documents, research papers, legal agreements.
   - Goals: Structural layout analysis (headings, body paragraphs, bullet lists), reading order determination, and generation of inverted full-text search indexes with term frequencies.

2. **🚗 License Plate Recognition (Smart Traffic ANPR / ALPR)**
   - Target: Traffic enforcement cameras, automated tolling gates, parking facilities.
   - Goals: High-speed alphanumeric plate extraction, jurisdiction syntax validation (US, UK, EU, Generic), and telemetry generation (lane allocation, speed tags, watchlist verification).

3. **🧾 Invoice & Receipt Scanner (Automated ERP Data Entry)**
   - Target: Accounts payable, expense reports, billing receipts.
   - Goals: Extraction of merchant names, invoice IDs, billing dates, itemized line tables, and **mathematical audit verification** ($\sum \text{items} = \text{Subtotal}$, $\text{Subtotal} + \text{Tax} = \text{Grand Total}$).

4. **🩺 Self-Correction & Error Resolution Agent**
   - Target: Flawed scans, glare, contrast loss, optical character confusion, and math errors.
   - Goals: Intercept validation failures, apply computer vision re-filtering (CLAHE, deskew, morphological cleanup, color inversion) or semantic constraint repairs, and re-enter the LangGraph workflow safely.

---

## 3. Technology Stack & Framework Selection

| Layer | Component | Selection Rationale |
| :--- | :--- | :--- |
| **Agentic Framework** | **LangGraph (`StateGraph`)** | Supports cyclical graphs, conditional edges, explicit state management, and self-healing retry loops. |
| **Data Contract** | **Pydantic v2 & `typing.TypedDict`** | Strict type safety for multi-agent state sharing. |
| **OCR Core** | **RapidOCR (ONNX Runtime)** | Fast, CPU/GPU accelerated text detection and recognition with zero external C++ binary dependencies. |
| **Computer Vision** | **OpenCV (`cv2`) & Pillow** | Adaptive thresholding, Hough transform deskewing, CLAHE, bilateral filtering, and morphological transformations. |
| **User Interface** | **Streamlit** | Real-time web visualization, side-by-side enhancement comparison, and live audit tracking. |
| **CLI & Telemetry** | **Rich Console** | Colored terminal tables, JSON formatting, and progress indicators. |
| **Testing** | **Pytest** | Automated regression testing for agent routing, math healing, and syntax verification. |

---

## 4. State Management Schema (`OCRWorkflowState`)

The shared LangGraph state retains comprehensive execution history:

```python
class OCRWorkflowState(TypedDict, total=False):
    # Input Data
    image_path: str
    task_type: Literal["auto", "document", "license_plate", "invoice"]
    
    # Image Quality Metrics & Preprocessing
    image_metadata: Dict[str, Any]
    preprocessed_image_path: str
    preprocessing_history: List[str]
    quality_metrics: Dict[str, Any]
    
    # Orchestration & Classification
    classified_type: Literal["document", "license_plate", "invoice", "unknown"]
    classification_confidence: float
    routing_reason: str
    
    # Raw Engine Extractions
    ocr_raw_boxes: List[Dict[str, Any]]
    full_raw_text: str
    average_ocr_confidence: float
    
    # Domain Specialist Extractions
    extracted_data: Dict[str, Any]
    
    # Validation & Error Handling
    is_valid: bool
    validation_errors: List[str]
    retry_count: int
    max_retries: int
    error_history: List[ErrorRecord]
    active_resolution_strategy: Optional[str]
    
    # Final Payload
    final_output: Dict[str, Any]
    status: str
```

---

## 5. Architectural Flow & Node Breakdown

1. **`preprocessor_node`**:
   - Assesses image blur (Laplacian variance), contrast (std dev), and skew (Hough lines).
   - If an `active_resolution_strategy` is signaled by the Error Resolver, applies specialized filters (e.g. `aggressive_clahe`, `invert_colors`, `morphological_cleanup`).
   - Otherwise applies standard adaptive contrast enhancement and deskewing.

2. **`ocr_node`**:
   - Executes RapidOCR on the enhanced image.
   - Extracts bounding coordinates, text tokens, and per-token confidence scores.

3. **`orchestrator_node`**:
   - Analyzes aspect ratio, keyword heuristics, and token count.
   - Dispatches to the appropriate specialist agent (`doc_specialist`, `plate_specialist`, `invoice_specialist`).

4. **`specialist_nodes`**:
   - Parse domain-specific entities.
   - Perform strict validation (word counts for docs, format regex for plates, math check for invoices).
   - Flag validation errors if thresholds are breached.

5. **`validation_evaluator_edge` (Conditional Router)**:
   - If `validation_errors` is empty $\rightarrow$ proceed to `postprocessor_node`.
   - If errors exist $\rightarrow$ divert execution to `error_resolver_node`.

6. **`error_resolver_node` (Self-Healing Loop)**:
   - Diagnoses root causes (decimal omission, character ambiguity, or severe optical noise).
   - If resolvable in-memory: repairs fields, marks `is_valid = True`, and continues.
   - If optical re-filtering needed: sets `active_resolution_strategy`, increments retry counter, and loops back to `preprocessor_node`!
   - If `retry_count >= max_retries`: applies best-effort fallback to prevent infinite loops.

7. **`postprocessor_node`**:
   - Compiles final JSON, creates Markdown representations, and marks status as `SUCCESS`.

---

## 6. Implementation Phases & Milestones

* **Phase 1: Environment & Engine Setup** *(Completed)*
  - Initialized isolated Python 3.11 virtual environment.
  - Installed LangGraph, RapidOCR, OpenCV, Pydantic, Pillow, and Rich.
* **Phase 2: Agent Architecture Development** *(Completed)*
  - Implemented Preprocessor, Orchestrator, Document Digitizer, License Plate Recognizer, Invoice Scanner, and Error Resolver.
* **Phase 3: LangGraph Topology & Self-Healing Loop** *(Completed)*
  - Built `OCRMultiAgentGraph` with conditional branches and cyclical retry edges.
* **Phase 4: Synthetic Datasets & Unit Testing** *(Completed)*
  - Generated realistic clean and corrupted test images for all 3 domains.
  - Verified 100% test pass rate across 6 test suites via pytest.
* **Phase 5: User Interfaces (Web UI & CLI)** *(Completed)*
  - Delivered interactive Streamlit dashboard (`run_ocr_app.py ui`) and colored CLI (`run_ocr_app.py --demo`).
