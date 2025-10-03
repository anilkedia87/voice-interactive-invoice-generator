"""
Customer model for invoice generation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    """Represents the customer/buyer information for the invoice."""
    
    name: str
    address: str
    city: str
    state: str
    pincode: str
    country: str = "India"
    gstin: Optional[str] = None  # GST Identification Number
    phone: Optional[str] = None
    email: Optional[str] = None
    
    def __post_init__(self):
        """Validate customer data after initialization."""
        if not self.name:
            raise ValueError("Customer name is required")
        if not self.address:
            raise ValueError("Customer address is required")
    
    def get_full_address(self) -> str:
        """Get formatted full address."""
        return f"{self.address}, {self.city}, {self.state} - {self.pincode}, {self.country}"
    
    def is_gst_registered(self) -> bool:
        """Check if customer is GST registered."""
        return self.gstin is not None and len(self.gstin) == 15
    
    def get_state_code(self) -> str:
        """Get state code from GSTIN if available."""
        if self.is_gst_registered():
            return self.gstin[:2]
        return ""
