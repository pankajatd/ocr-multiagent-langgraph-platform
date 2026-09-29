"""
Synthetic Test Image Generator:
Creates realistic test images for all three OCR domains:
1. Standard & Degraded Paper Documents (Archiving & Full-text search)
2. Clean & Inverted License Plates (Smart Traffic ANPR)
3. Clean & Glitched Invoices/Receipts (Automated accounting data entry & error self-healing)
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict

def create_synthetic_datasets(target_dir: str = "sample_data") -> Dict[str, str]:
    """Generates synthetic test images and returns their absolute filepaths."""
    os.makedirs(target_dir, exist_ok=True)
    generated_paths = {}

    # -------------------------------------------------------------
    # 1. Clean Paper Document
    # -------------------------------------------------------------
    doc_path = os.path.join(target_dir, "document_clean.png")
    doc_img = Image.new("RGB", (700, 900), color=(255, 255, 255))
    draw = ImageDraw.Draw(doc_img)
    
    # Text content
    draw.text((50, 40), "ANNUAL RESEARCH REPORT 2026", fill=(20, 20, 20))
    draw.text((50, 70), "Global Archival and Industrial Vision Systems", fill=(60, 60, 60))
    
    body_lines = [
        "1. EXECUTIVE SUMMARY",
        "Optical character recognition has transitioned from simple pattern matching",
        "to intelligent multi-agent orchestration frameworks. Modern pipelines combine",
        "adaptive computer vision with specialized domain agents to extract high-fidelity",
        "metadata from diverse document topologies.",
        "",
        "2. TECHNICAL ARCHITECTURE",
        "The system employs a decentralized agentic topology wherein each specialist handles",
        "domain-specific semantics such as tabular math reconciliation or license syntax.",
        "Crucially, autonomous error-healing agents intercept failures, adjust spatial",
        "filters, and reconcile extracted entities without workflow termination.",
        "",
        "3. CONCLUSION",
        "Deploying resilient OCR loops reduces manual review overhead by over eighty percent",
        "while ensuring continuous ingestion across high-throughput industrial streams."
    ]
    
    y = 120
    for line in body_lines:
        draw.text((50, y), line, fill=(30, 30, 30))
        y += 28

    doc_img.save(doc_path)
    generated_paths["document_clean"] = os.path.abspath(doc_path)

    # -------------------------------------------------------------
    # 2. Noisy / Skewed Paper Document (To test deskew and cleanup)
    # -------------------------------------------------------------
    noisy_doc_path = os.path.join(target_dir, "document_skewed_noisy.png")
    doc_cv = cv2.imread(doc_path)
    
    # Skew slightly by 3 degrees
    h, w = doc_cv.shape[:2]
    rot_mat = cv2.getRotationMatrix2D((w // 2, h // 2), 3.0, 1.0)
    skewed = cv2.warpAffine(doc_cv, rot_mat, (w, h), borderValue=(245, 245, 245))
    
    # Add mild Gaussian noise
    gauss = np.random.normal(0, 15, skewed.shape).astype('uint8')
    noisy = cv2.add(skewed, gauss)
    cv2.imwrite(noisy_doc_path, noisy)
    generated_paths["document_noisy"] = os.path.abspath(noisy_doc_path)

    # -------------------------------------------------------------
    # 3. Clean License Plate
    # -------------------------------------------------------------
    plate_path = os.path.join(target_dir, "license_plate_clean.png")
    plate_img = Image.new("RGB", (520, 140), color=(240, 242, 245))
    pdraw = ImageDraw.Draw(plate_img)
    
    # Outer plate border
    pdraw.rectangle([6, 6, 514, 134], outline=(20, 20, 20), width=5)
    # Blue EU/State side banner
    pdraw.rectangle([11, 11, 60, 129], fill=(0, 51, 153))
    pdraw.text((25, 45), "EU", fill=(255, 255, 255))
    # Registration plate text
    pdraw.text((120, 45), "AB12 CDE", fill=(10, 10, 10))
    
    plate_img.save(plate_path)
    generated_paths["license_plate_clean"] = os.path.abspath(plate_path)

    # -------------------------------------------------------------
    # 4. Inverted / Dark Background License Plate (To trigger auto-invert)
    # -------------------------------------------------------------
    plate_inv_path = os.path.join(target_dir, "license_plate_dark.png")
    plate_cv = cv2.imread(plate_path)
    dark_plate = cv2.bitwise_not(plate_cv)
    cv2.imwrite(plate_inv_path, dark_plate)
    generated_paths["license_plate_dark"] = os.path.abspath(plate_inv_path)

    # -------------------------------------------------------------
    # 5. Clean Accounting Invoice
    # -------------------------------------------------------------
    inv_path = os.path.join(target_dir, "invoice_clean.png")
    inv_img = Image.new("RGB", (650, 750), color=(255, 255, 255))
    idraw = ImageDraw.Draw(inv_img)

    idraw.text((40, 40), "APEX INDUSTRIAL SUPPLIES INC.", fill=(10, 10, 10))
    idraw.text((40, 70), "Invoice #: INV-2026-8802", fill=(40, 40, 40))
    idraw.text((40, 95), "Date: 2026-09-15", fill=(40, 40, 40))
    idraw.text((40, 120), "Bill To: Smart Vision Dynamics Ltd", fill=(40, 40, 40))

    idraw.line([(40, 160), (610, 160)], fill=(120, 120, 120), width=2)
    idraw.text((40, 175), "Item Description             Qty   Unit Price   Total", fill=(20, 20, 20))
    idraw.line([(40, 205), (610, 205)], fill=(180, 180, 180), width=1)

    items = [
        ("Industrial Optical Sensor", "2", "45.00", "90.00"),
        ("Embedded Edge Compute Module", "1", "110.00", "110.00"),
        ("High-Speed GigE Cable 5m", "4", "15.00", "60.00"),
    ]
    
    iy = 225
    for desc, q, up, tot in items:
        idraw.text((40, iy), f"{desc:<28}  {q:>3}   ${up:>7}   ${tot:>7}", fill=(30, 30, 30))
        iy += 35

    idraw.line([(40, 360), (610, 360)], fill=(120, 120, 120), width=2)
    idraw.text((380, 385), "Subtotal: $260.00", fill=(20, 20, 20))
    idraw.text((380, 415), "Tax (10%): $26.00", fill=(20, 20, 20))
    idraw.text((380, 455), "Grand Total: $286.00", fill=(10, 10, 10))

    inv_img.save(inv_path)
    generated_paths["invoice_clean"] = os.path.abspath(inv_path)

    # -------------------------------------------------------------
    # 6. Invoice with Mathematical Mismatch Error (To trigger Error Resolver)
    # (e.g. Subtotal $260.00 + Tax $26.00, but Grand Total erroneously printed as $2860.00 without decimal point)
    # -------------------------------------------------------------
    inv_err_path = os.path.join(target_dir, "invoice_with_math_error.png")
    inv_err_img = Image.new("RGB", (650, 750), color=(255, 255, 255))
    edraw = ImageDraw.Draw(inv_err_img)

    edraw.text((40, 40), "APEX INDUSTRIAL SUPPLIES INC.", fill=(10, 10, 10))
    edraw.text((40, 70), "Invoice #: INV-2026-9911", fill=(40, 40, 40))
    edraw.text((40, 95), "Date: 2026-09-18", fill=(40, 40, 40))
    
    edraw.line([(40, 160), (610, 160)], fill=(120, 120, 120), width=2)
    edraw.text((40, 175), "Item Description             Qty   Unit Price   Total", fill=(20, 20, 20))
    edraw.line([(40, 205), (610, 205)], fill=(180, 180, 180), width=1)

    edraw.text((40, 225), "Precision Camera Mount        1   $150.00   $150.00", fill=(30, 30, 30))
    edraw.text((40, 260), "Wide Angle Lens Assembly      1   $100.00   $100.00", fill=(30, 30, 30))

    edraw.line([(40, 360), (610, 360)], fill=(120, 120, 120), width=2)
    edraw.text((380, 385), "Subtotal: $250.00", fill=(20, 20, 20))
    edraw.text((380, 415), "Tax: $25.00", fill=(20, 20, 20))
    # Intentional discrepancy: 2750.00 instead of 275.00
    edraw.text((380, 455), "Grand Total: $2750.00", fill=(10, 10, 10))

    inv_err_img.save(inv_err_path)
    generated_paths["invoice_with_math_error"] = os.path.abspath(inv_err_path)

    return generated_paths

if __name__ == "__main__":
    paths = create_synthetic_datasets()
    print("Generated synthetic test files:")
    for k, p in paths.items():
        print(f" - {k}: {p}")
