from pydantic import BaseModel
from datetime import date
from typing import Optional

# Base schema for purchase orders (used for create/read)
class PurchaseOrderBase(BaseModel):
    po_number: str                       
    vendor: Optional[str]               
    total_amount: float               
    date: date                         
    
# Schema for creating a new purchase order
class PurchaseOrderCreate(PurchaseOrderBase):
    pass  # Inherits all fields from base

# Schema for reading a PO with its DB ID
class PurchaseOrder(PurchaseOrderBase):
    id: int                             # Auto-generated primary key

    class Config:
        orm_mode = True  # Enable ORM mode for SQLAlchemy compatibility


# Base schema for invoices (used for create/read)
class InvoiceBase(BaseModel):
    invoice_number: str          
    vendor: Optional[str]              
    amount: float                     
    date: date                     

# Schema for creating a new invoice
class InvoiceCreate(InvoiceBase):
    pass  

# Schema for reading an invoice with additional metadata
class Invoice(InvoiceBase):
    id: int                            
    file_path: Optional[str]           
    s3_url: Optional[str]             
    validation_status: Optional[str]   
    
    class Config:
        orm_mode = True  
