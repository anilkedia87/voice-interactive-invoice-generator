"""
Invoice and InvoiceItem models for invoice generation.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
import uuid

from .company import Company
from .customer import Customer


@dataclass
class InvoiceItem:
    """Represents a single item in an invoice."""
    
    description: str
    hsn_code: str
    quantity: Decimal
    unit_price: Decimal
    unit: str = "Nos"
    gst_rate: Decimal = Decimal('0')  # GST percentage (e.g., 18 for 18%)
    discount_percentage: Decimal = Decimal('0')  # Discount percentage
    discount_amount: Decimal = Decimal('0')  # Fixed discount amount
    
    def __post_init__(self):
        """Validate and convert types after initialization."""
        self.quantity = Decimal(str(self.quantity))
        self.unit_price = Decimal(str(self.unit_price))
        self.gst_rate = Decimal(str(self.gst_rate))
        self.discount_percentage = Decimal(str(self.discount_percentage))
        self.discount_amount = Decimal(str(self.discount_amount))
        
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        if self.gst_rate < 0 or self.gst_rate > 100:
            raise ValueError("GST rate must be between 0 and 100")
    
    @property
    def gross_amount(self) -> Decimal:
        """Calculate gross amount (quantity × unit_price)."""
        return (self.quantity * self.unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def total_discount(self) -> Decimal:
        """Calculate total discount amount."""
        percentage_discount = (self.gross_amount * self.discount_percentage / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        return (percentage_discount + self.discount_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def taxable_amount(self) -> Decimal:
        """Calculate taxable amount (gross_amount - discount)."""
        return (self.gross_amount - self.total_discount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def cgst_amount(self) -> Decimal:
        """Calculate CGST amount (Central GST)."""
        cgst_rate = self.gst_rate / 2
        return (self.taxable_amount * cgst_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def sgst_amount(self) -> Decimal:
        """Calculate SGST amount (State GST)."""
        sgst_rate = self.gst_rate / 2
        return (self.taxable_amount * sgst_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def igst_amount(self) -> Decimal:
        """Calculate IGST amount (Integrated GST) - used for inter-state transactions."""
        return (self.taxable_amount * self.gst_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def total_tax_amount(self) -> Decimal:
        """Calculate total tax amount."""
        return (self.cgst_amount + self.sgst_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def total_amount(self) -> Decimal:
        """Calculate total amount including taxes."""
        return (self.taxable_amount + self.total_tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@dataclass
class Invoice:
    """Represents a complete GST invoice."""
    
    company: Company
    customer: Customer
    items: List[InvoiceItem] = field(default_factory=list)
    invoice_number: str = ""
    invoice_date: date = field(default_factory=date.today)
    due_date: Optional[date] = None
    place_of_supply: str = ""
    reverse_charge: bool = False
    notes: str = ""
    terms_and_conditions: str = ""
    
    def __post_init__(self):
        """Initialize invoice after creation."""
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        if not self.place_of_supply:
            self.place_of_supply = self.customer.state
        if not self.items:
            self.items = []
    
    def _generate_invoice_number(self) -> str:
        """Generate a unique invoice number."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"INV-{timestamp}"
    
    def add_item(self, item: InvoiceItem):
        """Add an item to the invoice."""
        self.items.append(item)
    
    def remove_item(self, index: int):
        """Remove an item from the invoice by index."""
        if 0 <= index < len(self.items):
            del self.items[index]
    
    @property
    def is_interstate(self) -> bool:
        """Check if this is an interstate transaction."""
        # First check if both have GSTIN and compare state codes from GSTIN
        if self.company.gstin and self.customer.gstin:
            company_state_code = self.company.gstin[:2]
            customer_state_code = self.customer.gstin[:2]
            return company_state_code != customer_state_code
        
        # If no GSTIN available, compare states directly (normalize case)
        company_state = self.company.state.strip().upper()
        customer_state = self.customer.state.strip().upper()
        
        # Handle common state name variations
        state_mapping = {
            'ODISHA': 'ODISHA',
            'ORISSA': 'ODISHA',
            'WEST BENGAL': 'WESTBENGAL',
            'WESTBENGAL': 'WESTBENGAL',
            'TAMIL NADU': 'TAMILNADU',
            'TAMILNADU': 'TAMILNADU',
            'UTTAR PRADESH': 'UTTARPRADESH',
            'UTTARPRADESH': 'UTTARPRADESH',
            'MADHYA PRADESH': 'MADHYAPRADESH',
            'MADHYAPRADESH': 'MADHYAPRADESH',
            'HIMACHAL PRADESH': 'HIMACHALPRADESH',
            'HIMACHALPRADESH': 'HIMACHALPRADESH',
            'ANDHRA PRADESH': 'ANDHRAPRADESH',
            'ANDHRAPRADESH': 'ANDHRAPRADESH',
            'JAMMU AND KASHMIR': 'JAMMUKASHMIR',
            'JAMMUKASHMIR': 'JAMMUKASHMIR',
            'J&K': 'JAMMUKASHMIR'
        }
        
        # Normalize state names
        company_state_normalized = state_mapping.get(company_state, company_state)
        customer_state_normalized = state_mapping.get(customer_state, customer_state)
        
        # Interstate if states are different
        return company_state_normalized != customer_state_normalized
    
    @property
    def total_gross_amount(self) -> Decimal:
        """Calculate total gross amount for all items."""
        return sum(item.gross_amount for item in self.items)
    
    @property
    def total_discount_amount(self) -> Decimal:
        """Calculate total discount amount for all items."""
        return sum(item.total_discount for item in self.items)
    
    @property
    def total_taxable_amount(self) -> Decimal:
        """Calculate total taxable amount for all items."""
        return sum(item.taxable_amount for item in self.items)
    
    @property
    def total_cgst_amount(self) -> Decimal:
        """Calculate total CGST amount."""
        if self.is_interstate:
            return Decimal('0')
        return sum(item.cgst_amount for item in self.items)
    
    @property
    def total_sgst_amount(self) -> Decimal:
        """Calculate total SGST amount."""
        if self.is_interstate:
            return Decimal('0')
        return sum(item.sgst_amount for item in self.items)
    
    @property
    def total_igst_amount(self) -> Decimal:
        """Calculate total IGST amount."""
        if not self.is_interstate:
            return Decimal('0')
        return sum(item.igst_amount for item in self.items)
    
    @property
    def total_tax_amount(self) -> Decimal:
        """Calculate total tax amount."""
        if self.is_interstate:
            return self.total_igst_amount
        return self.total_cgst_amount + self.total_sgst_amount
    
    @property
    def total_invoice_amount(self) -> Decimal:
        """Calculate total invoice amount."""
        return (self.total_taxable_amount + self.total_tax_amount).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    
    @property
    def total_amount_in_words(self) -> str:
        """Convert total amount to words (Indian currency format)."""
        return self._amount_to_words(self.total_invoice_amount)
    
    def _amount_to_words(self, amount: Decimal) -> str:
        """Convert amount to words in Indian format."""
        # This is a simplified version. In production, you might want to use a library like num2words
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", 
                "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def convert_hundreds(num):
            result = ""
            if num >= 100:
                result += ones[num // 100] + " Hundred "
                num %= 100
            if num >= 20:
                result += tens[num // 10] + " "
                num %= 10
            elif num >= 10:
                result += teens[num - 10] + " "
                return result
            if num > 0:
                result += ones[num] + " "
            return result
        
        if amount == 0:
            return "Zero Rupees Only"
        
        rupees = int(amount)
        paise = int((amount - rupees) * 100)
        
        result = ""
        if rupees >= 10000000:  # Crore
            crores = rupees // 10000000
            result += convert_hundreds(crores) + "Crore "
            rupees %= 10000000
        
        if rupees >= 100000:  # Lakh
            lakhs = rupees // 100000
            result += convert_hundreds(lakhs) + "Lakh "
            rupees %= 100000
        
        if rupees >= 1000:  # Thousand
            thousands = rupees // 1000
            result += convert_hundreds(thousands) + "Thousand "
            rupees %= 1000
        
        if rupees > 0:
            result += convert_hundreds(rupees)
        
        result += "Rupees"
        
        if paise > 0:
            result += " and " + convert_hundreds(paise) + "Paise"
        
        return result.strip() + " Only"
    
    def get_tax_summary(self) -> Dict[str, Any]:
        """Get tax summary by GST rates."""
        tax_summary = {}
        
        for item in self.items:
            rate = float(item.gst_rate)
            if rate not in tax_summary:
                tax_summary[rate] = {
                    'taxable_amount': Decimal('0'),
                    'cgst_amount': Decimal('0'),
                    'sgst_amount': Decimal('0'),
                    'igst_amount': Decimal('0'),
                    'total_tax': Decimal('0')
                }
            
            tax_summary[rate]['taxable_amount'] += item.taxable_amount
            if self.is_interstate:
                tax_summary[rate]['igst_amount'] += item.igst_amount
            else:
                tax_summary[rate]['cgst_amount'] += item.cgst_amount
                tax_summary[rate]['sgst_amount'] += item.sgst_amount
            
            tax_summary[rate]['total_tax'] += item.total_tax_amount
        
        return tax_summary
