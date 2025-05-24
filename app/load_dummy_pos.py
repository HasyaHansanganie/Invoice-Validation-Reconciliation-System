import csv
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import PurchaseOrder
from datetime import datetime

def load_dummy_pos():
    
    """Load dummy purchase order data from CSV into the database."""
    db: Session = SessionLocal()
    
    try:
        # Open the dummy PO CSV file
        with open("dummy_data/dummy_po.csv", mode='r') as file:
            reader = csv.DictReader(file)
            count = 0  # Track how many records inserted

            for row in reader:
                # Skip if the PO number already exists in DB (to avoid duplicates)
                existing = db.query(PurchaseOrder).filter_by(po_number=row["po_number"]).first()
                if existing:
                    print(f"PO {row['po_number']} already exists. Skipping.")
                    continue

                # Create a new PurchaseOrder object
                po = PurchaseOrder(
                    po_number=row["po_number"],
                    vendor=row["vendor"],
                    total_amount=float(row["total_amount"]),
                    date=datetime.strptime(row["date"], "%Y-%m-%d")
                )

                # Add to session
                db.add(po)
                count += 1

            # Commit all new records to the DB
            db.commit()
            print(f"Loaded {count} dummy purchase orders into the database.")

    except FileNotFoundError:
        print("CSV file not found. Please make sure 'dummy_data/dummy_po.csv' exists.")
    except Exception as e:
        print(f"Error occurred while loading dummy POs: {e}")
    finally:
        db.close()

# Run the function if the script is executed directly
if __name__ == "__main__":
    load_dummy_pos()
