import os
import shutil
import csv
import re
import fitz  # PyMuPDF
from io import TextIOWrapper
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from dotenv import load_dotenv

from . import models
from .database import engine, get_db
from .s3_utils import upload_file_to_s3
from soap.soap_utils import validate_amount_with_soap

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Invoice Validation & Reconciliation API",
    version="1.0.0",
    description="API to upload invoice files (CSV/PDF), validate them using SOAP, store them in AWS S3, and reconcile against purchase orders."
)

# Enable CORS for local development / testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# Directory to store uploaded files locally
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Endpoint: Upload an invoice and extract metadata automatically
@app.post("/upload-invoice")
def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an invoice file (CSV or PDF), extract metadata automatically,
    validate the amount using SOAP, upload file to S3, and save everything to DB.
    """
    filename = file.filename.lower()

    # Step 1: Check file type and extract metadata
    if filename.endswith(".csv"):
        try:
            reader = csv.DictReader(TextIOWrapper(file.file, encoding='utf-8'))
            first_row = next(reader)
            invoice_number = first_row["invoice_number"]
            vendor = first_row["vendor"]
            amount = float(first_row["amount"])
            date_str = first_row["date"]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"CSV extraction error: {e}")

    elif filename.endswith(".pdf"):
        # Step 1: Save PDF temporarily
        temp_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(temp_path, "wb") as f:
            file.file.seek(0)
            f.write(file.file.read())

        try:
            doc = fitz.open(temp_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()  # Close the file before rename

            # Extract metadata from PDF
            invoice_number = re.search(r"Invoice Number[:\-]?\s*(\w+)", text)
            vendor = re.search(r"Vendor[:\-]?\s*(.+)", text)
            amount = re.search(r"Amount[:\-]?\s*([\d\.]+)", text)
            date_str = re.search(r"Date[:\-]?\s*(\d{4}-\d{2}-\d{2})", text)

            if not all([invoice_number, vendor, amount, date_str]):
                raise ValueError("Missing fields in PDF.")

            invoice_number = invoice_number.group(1).strip()
            vendor = vendor.group(1).strip()
            amount = float(amount.group(1).strip())
            date_str = date_str.group(1).strip()

            # Rename file now that we have invoice_number
            new_filename = f"{invoice_number}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, new_filename)
            os.rename(temp_path, file_path)

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF extraction error: {e}")

    else:
        raise HTTPException(status_code=415, detail="Unsupported file format. Please upload a CSV or PDF.")

    # Step 2: Save the file locally (CSV only; PDF was saved earlier)
    new_filename = f"{invoice_number}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    if filename.endswith(".csv"):
        file.file.seek(0)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    print(f"Saved file: {file_path}")

    # Step 3: Upload to AWS S3 or simulate
    s3_url = upload_file_to_s3(file_path, new_filename)
    print(f"S3 Upload URL: {s3_url}")

    # Step 4: Validate amount using SOAP
    validation_status = validate_amount_with_soap(amount)
    print(f"Validation status: {validation_status}")

    # Step 5: Save to DB
    invoice = models.Invoice(
        invoice_number=invoice_number,
        vendor=vendor,
        amount=amount,
        date=datetime.strptime(date_str, "%Y-%m-%d"),
        file_path=file_path,
        s3_url=s3_url,
        validation_status=validation_status
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    print(f"Invoice saved to DB (ID: {invoice.id})")

    return {
        "message": "Invoice uploaded and processed automatically",
        "invoice_id": invoice.id,
        "extracted": {
            "invoice_number": invoice_number,
            "vendor": vendor,
            "amount": amount,
            "date": date_str
        },
        "s3_url": s3_url,
        "validation_status": validation_status
    }

# Endpoint: Reconcile invoices against purchase orders
@app.get("/reconcile")
def reconcile(db: Session = Depends(get_db)):
    """
    Match invoices to purchase orders based on vendor and amount.
    Return reconciliation results (Matched/Unmatched).
    """
    results = []

    invoices = db.query(models.Invoice).all()
    pos = db.query(models.PurchaseOrder).all()

    for invoice in invoices:
        match = next(
            (po for po in pos if po.vendor == invoice.vendor and float(po.total_amount) == float(invoice.amount)),
            None
        )
        results.append({
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "amount": float(invoice.amount),
            "status": "Matched" if match else "Unmatched",
            "po_number": match.po_number if match else None
        })

    print(f"Reconciliation complete: {len(results)} invoices processed")
    return {"reconciliation": results}
