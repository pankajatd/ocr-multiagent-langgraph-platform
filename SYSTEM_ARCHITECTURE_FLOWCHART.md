# 🔄 System Architecture & Flowchart: LangGraph Multi-Agent OCR

This document details the architectural blueprints, cyclical state transitions, agent sequence interactions, and the self-healing error resolution logic.

---

## 1. High-Level Multi-Agent Architecture

```mermaid
flowchart TD
    User([User Image Upload / Camera Stream]) --> Preprocessor["🛠️ Preprocessor Agent\n(Deskew, CLAHE, Noise Cleanup, Inversion)"]
    
    subgraph Core_Pipeline ["Agentic Processing Engine"]
        Preprocessor --> OCR["👁️ Unified OCR Engine\n(RapidOCR ONNX + Tesseract Fallback)"]
        OCR --> Orchestrator["🧠 Orchestrator Agent\n(Intent & Domain Classification)"]
        
        Orchestrator -->|Document Cues| DocAgent["📄 Document Digitizer Agent\n(Layout, Paragraphs, Search Index)"]
        Orchestrator -->|Vehicle Plate Cues| PlateAgent["🚗 License Plate Agent\n(ANPR & Smart Traffic Telemetry)"]
        Orchestrator -->|Financial Cues| InvAgent["🧾 Invoice Scanner Agent\n(Accounting & Math Audit)"]
        
        DocAgent --> CheckValidation{"Validation Check\n(Confidence, Math, Syntax)"}
        PlateAgent --> CheckValidation
        InvAgent --> CheckValidation
    end

    subgraph Self_Healing_Loop ["Autonomous Self-Correction Subsystem"]
        CheckValidation -->|Discrepancy / Low Conf| ErrorResolver["🩺 Error Resolver Agent\n(Diagnosis & Strategy Selector)"]
        
        ErrorResolver -->|Need Optical Enhancement\n(e.g., Aggressive CLAHE, Invert)| Preprocessor
        ErrorResolver -->|In-Memory Reconciled\n(Math Fix, Char Confusion)| Postprocessor["📦 Postprocessor Agent\n(Packaging, Markdown, Search Index)"]
    end

    CheckValidation -->|All Valid| Postprocessor
    Postprocessor --> Output([Structured JSON & Telemetry Delivered])
    
    style Self_Healing_Loop fill:#fef3c7,stroke:#d97706,stroke-width:2px;
    style Core_Pipeline fill:#f0f9ff,stroke:#0284c7,stroke-width:2px;
```

---

## 2. Cyclical LangGraph State Machine

The following state diagram illustrates how state transitions between nodes and how the graph resolves errors cyclically:

```mermaid
stateDiagram-v2
    [*] --> Initialized: Receive image_path & task_type
    
    Initialized --> Preprocessed: Preprocessor applies adaptive CV filters
    Preprocessed --> OCRExtracted: RapidOCR extracts tokens & bounding boxes
    OCRExtracted --> Routed: Orchestrator identifies document class
    
    state Specialist_Execution {
        [*] --> DocProcessing: Route == 'document'
        [*] --> PlateProcessing: Route == 'license_plate'
        [*] --> InvoiceProcessing: Route == 'invoice'
        
        DocProcessing --> Validating
        PlateProcessing --> Validating
        InvoiceProcessing --> Validating
    }
    
    Routed --> Specialist_Execution
    
    Validating --> Completed: Is Valid == True
    Validating --> ResolvingError: Is Valid == False (Discrepancy Detected)
    
    state ResolvingError {
        [*] --> DiagnoseCause
        DiagnoseCause --> RepairData: In-Memory Fix (Math, Char Swap)
        DiagnoseCause --> RequestRefilter: Optical Defect (Dark, Blurry)
    }
    
    RepairData --> Completed: Healed & Continues
    RequestRefilter --> Preprocessed: Loop back (Retry Count < Max Retries)
    RequestRefilter --> Completed: Max Retries Reached (Best-Effort Graceful)
    
    Completed --> [*]: Output Structured Artifacts
```

---

## 3. Sequence Diagram of Agent Collaboration

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Orch as 🧠 Orchestrator Agent
    participant Prep as 🛠️ Preprocessor Agent
    participant OCR as 👁️ RapidOCR Engine
    participant Spec as 🎯 Specialist Agent
    participant ErrRes as 🩺 Error Resolver Agent
    participant Post as 📦 Postprocessor Agent

    User->>Prep: Provide Image (e.g. Invoice with Math Glitch)
    Prep->>OCR: Enhanced Image Array
    OCR->>Orch: Raw Text & Bounding Boxes
    Orch->>Spec: Route to Invoice Specialist
    Spec->>Spec: Calculate Subtotal + Tax vs Grand Total
    Note over Spec: Discrepancy Found! $250 + $25 != $2750
    Spec->>ErrRes: Forward State with Validation Failure
    
    rect rgb(254, 243, 199)
        Note over ErrRes: Self-Correction Evaluation
        ErrRes->>ErrRes: Diagnose Decimal Slip ($2750 -> $275.0)
        ErrRes->>ErrRes: Reconcile Equation & Log Event
        ErrRes->>Post: Forward Healed State (is_valid = True)
    end
    
    Post->>User: Deliver Clean JSON, Audit Log & Status: SUCCESS
```

---

## 4. Error Resolver Decision Logic Tree

```mermaid
flowchart TD
    ErrStart([Validation Error Intercepted]) --> CheckRetries{Retry Count >= Max Retries?}
    
    CheckRetries -->|Yes| GracefulExit[Apply Best-Effort Fallback & Continue]
    CheckRetries -->|No| IdentifyDomain{Classified Domain}
    
    IdentifyDomain -->|Invoice| CheckMath{Error Type?}
    CheckMath -->|Math Mismatch| RebalanceMath[Deduce Missing Decimal or Recompute Grand Total]
    CheckMath -->|Missing Total| InferFromItems[Infer Grand Total from Line Items Sum]
    CheckMath -->|Unreadable| RequestCLAHE[Request 'aggressive_clahe' Image Filter]
    
    IdentifyDomain -->|License Plate| CheckPlate{Plate Issue?}
    CheckPlate -->|Char Ambiguity| SwapConfusion[Swap 'O'->'0' or 'I'->'1' based on syntax]
    CheckPlate -->|Dark / Inverted| InvertColors[Request 'invert_colors' Image Filter]
    CheckPlate -->|Broken Contours| OtsuBinarize[Request 'binarize_otsu' Filter]
    
    IdentifyDomain -->|Document| CheckDoc{Document Issue?}
    CheckDoc -->|High Gibberish| SanitizeStream[Sanitize Non-ASCII noise & symbols]
    CheckDoc -->|Faded Ink| MorphCleanup[Request 'morphological_cleanup']

    RebalanceMath --> MarkResolved[Mark is_valid=True & Continue]
    InferFromItems --> MarkResolved
    SwapConfusion --> MarkResolved
    SanitizeStream --> MarkResolved
    
    RequestCLAHE --> IncrementRetry[Increment retry_count & Loop back to Preprocessor]
    InvertColors --> IncrementRetry
    OtsuBinarize --> IncrementRetry
    MorphCleanup --> IncrementRetry
```
