"""
Company model for invoice generation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Company:
    """Represents the company/seller information for the invoice."""
    
    name: str
    address: str
    city: str
    state: str
    pincode: str
    country: str = "India"
    gstin: Optional[str] = None  # GST Identification Number
    pan: Optional[str] = None   # PAN Number
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None
    
    def __post_init__(self):
        """Validate company data after initialization."""
        if not self.name:
            raise ValueError("Company name is required")
        if not self.address:
            raise ValueError("Company address is required")
        
    def get_full_address(self) -> str:
        """Get formatted full address."""
        return f"{self.address}, {self.city}, {self.state} - {self.pincode}, {self.country}"
    
    def is_gst_registered(self) -> bool:
        """Check if company is GST registered."""
        return self.gstin is not None and len(self.gstin) == 15
