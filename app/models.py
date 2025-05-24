from sqlalchemy import Column, Integer, String, Date, DECIMAL
from .database import Base

# SQLAlchemy model for purchase_orders table
class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, nullable=False)
    vendor = Column(String(100))
    total_amount = Column(DECIMAL(10, 2))
    date = Column(Date)

# SQLAlchemy model for invoices table
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50))
    vendor = Column(String(100))
    amount = Column(DECIMAL(10, 2))
    date = Column(Date)
    file_path = Column(String(255))
    s3_url = Column(String(255))
    validation_status = Column(String(50))
