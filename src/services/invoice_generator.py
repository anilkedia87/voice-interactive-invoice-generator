"""
Invoice Generator Service
Main service for generating invoices with all business logic.
"""

from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import json
import uuid

from models import Invoice, InvoiceItem, Company, Customer
from services.gst_calculator import GSTCalculator
from services.hsn_validator import HSNValidator


class InvoiceGenerator:
    """Main service for generating invoices."""
    
    def __init__(self):
        self.gst_calculator = GSTCalculator()
        self.hsn_validator = HSNValidator()
    
    def create_invoice(
        self,
        company_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        items_data: List[Dict[str, Any]],
        invoice_config: Optional[Dict[str, Any]] = None
    ) -> Invoice:
        """
        Create a complete invoice from input data.
        
        Args:
            company_data: Dictionary with company information
            customer_data: Dictionary with customer information
            items_data: List of dictionaries with item information
            invoice_config: Optional invoice configuration
            
        Returns:
            Complete Invoice object
        """
        # Create company object
        company = self._create_company(company_data)
        
        # Create customer object
        customer = self._create_customer(customer_data)
        
        # Create invoice items
        items = self._create_invoice_items(items_data)
        
        # Create invoice
        invoice = Invoice(
            company=company,
            customer=customer,
            items=items
        )
        
        # Apply invoice configuration if provided
        if invoice_config:
            self._apply_invoice_config(invoice, invoice_config)
        
        return invoice
    
    def _create_company(self, data: Dict[str, Any]) -> Company:
        """Create Company object from data dictionary."""
        required_fields = ['name', 'address', 'city', 'state', 'pincode']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Company {field} is required")
        
        # Validate GSTIN if provided
        if 'gstin' in data and data['gstin']:
            is_valid, error = self.gst_calculator.validate_gstin(data['gstin'])
            if not is_valid:
                raise ValueError(f"Invalid company GSTIN: {error}")
        
        return Company(**data)
    
    def _create_customer(self, data: Dict[str, Any]) -> Customer:
        """Create Customer object from data dictionary."""
        required_fields = ['name', 'address', 'city', 'state', 'pincode']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Customer {field} is required")
        
        # Validate GSTIN if provided
        if 'gstin' in data and data['gstin']:
            is_valid, error = self.gst_calculator.validate_gstin(data['gstin'])
            if not is_valid:
                raise ValueError(f"Invalid customer GSTIN: {error}")
        
        return Customer(**data)
    
    def _create_invoice_items(self, items_data: List[Dict[str, Any]]) -> List[InvoiceItem]:
        """Create list of InvoiceItem objects from data."""
        if not items_data:
            raise ValueError("At least one item is required")
        
        items = []
        
        for i, item_data in enumerate(items_data):
            try:
                # Validate required fields
                required_fields = ['description', 'hsn_code', 'quantity', 'unit_price']
                for field in required_fields:
                    if field not in item_data or item_data[field] is None:
                        raise ValueError(f"Item {field} is required")
                
                # Validate HSN code
                hsn_code = str(item_data['hsn_code'])
                if not self.hsn_validator.validate_hsn_format(hsn_code):
                    raise ValueError(f"Invalid HSN code format: {hsn_code}")
                
                # Set default values
                item_data.setdefault('unit', 'Nos')
                item_data.setdefault('gst_rate', 18)  # Default GST rate
                item_data.setdefault('discount_percentage', 0)
                item_data.setdefault('discount_amount', 0)
                
                # Validate GST rate
                gst_rate = float(item_data['gst_rate'])
                if not self.gst_calculator.validate_gst_rate(gst_rate):
                    # Suggest nearest valid rate
                    suggested_rate = self.gst_calculator.suggest_nearest_gst_rate(gst_rate)
                    print(f"Warning: GST rate {gst_rate}% is not standard. Consider using {suggested_rate}%")
                
                # Create invoice item
                item = InvoiceItem(**item_data)
                items.append(item)
                
            except Exception as e:
                raise ValueError(f"Error in item {i + 1}: {str(e)}")
        
        return items
    
    def _apply_invoice_config(self, invoice: Invoice, config: Dict[str, Any]):
        """Apply configuration settings to invoice."""
        if 'invoice_number' in config:
            invoice.invoice_number = config['invoice_number']
        
        if 'invoice_date' in config:
            if isinstance(config['invoice_date'], str):
                invoice.invoice_date = date.fromisoformat(config['invoice_date'])
            else:
                invoice.invoice_date = config['invoice_date']
        
        if 'due_date' in config:
            if isinstance(config['due_date'], str):
                invoice.due_date = date.fromisoformat(config['due_date'])
            else:
                invoice.due_date = config['due_date']
        elif 'payment_terms_days' in config:
            days = int(config['payment_terms_days'])
            invoice.due_date = invoice.invoice_date + timedelta(days=days)
        
        if 'place_of_supply' in config:
            invoice.place_of_supply = config['place_of_supply']
        
        if 'reverse_charge' in config:
            invoice.reverse_charge = bool(config['reverse_charge'])
        
        if 'notes' in config:
            invoice.notes = config['notes']
        
        if 'terms_and_conditions' in config:
            invoice.terms_and_conditions = config['terms_and_conditions']
    
    def create_quick_invoice(
        self,
        company_name: str,
        customer_name: str,
        items: List[Dict[str, Any]]
    ) -> Invoice:
        """
        Create a quick invoice with minimal information.
        Useful for simple invoicing scenarios.
        """
        # Default company data
        company_data = {
            'name': company_name,
            'address': 'Business Address',
            'city': 'City',
            'state': 'State',
            'pincode': '000000',
            'country': 'India'
        }
        
        # Default customer data
        customer_data = {
            'name': customer_name,
            'address': 'Customer Address',
            'city': 'City',
            'state': 'State',
            'pincode': '000000',
            'country': 'India'
        }
        
        return self.create_invoice(company_data, customer_data, items)
    
    def validate_invoice_data(self, invoice_data: Dict[str, Any]) -> List[str]:
        """
        Validate complete invoice data and return list of validation errors.
        
        Args:
            invoice_data: Complete invoice data dictionary
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate company data
        if 'company' not in invoice_data:
            errors.append("Company information is required")
        else:
            company_data = invoice_data['company']
            required_fields = ['name', 'address', 'city', 'state', 'pincode']
            for field in required_fields:
                if field not in company_data or not company_data[field]:
                    errors.append(f"Company {field} is required")
            
            # Validate company GSTIN
            if 'gstin' in company_data and company_data['gstin']:
                is_valid, error = self.gst_calculator.validate_gstin(company_data['gstin'])
                if not is_valid:
                    errors.append(f"Invalid company GSTIN: {error}")
        
        # Validate customer data
        if 'customer' not in invoice_data:
            errors.append("Customer information is required")
        else:
            customer_data = invoice_data['customer']
            required_fields = ['name', 'address', 'city', 'state', 'pincode']
            for field in required_fields:
                if field not in customer_data or not customer_data[field]:
                    errors.append(f"Customer {field} is required")
            
            # Validate customer GSTIN
            if 'gstin' in customer_data and customer_data['gstin']:
                is_valid, error = self.gst_calculator.validate_gstin(customer_data['gstin'])
                if not is_valid:
                    errors.append(f"Invalid customer GSTIN: {error}")
        
        # Validate items data
        if 'items' not in invoice_data or not invoice_data['items']:
            errors.append("At least one item is required")
        else:
            items_data = invoice_data['items']
            for i, item_data in enumerate(items_data):
                item_prefix = f"Item {i + 1}"
                
                # Required fields
                required_fields = ['description', 'hsn_code', 'quantity', 'unit_price']
                for field in required_fields:
                    if field not in item_data or item_data[field] is None:
                        errors.append(f"{item_prefix}: {field} is required")
                
                # Validate HSN code
                if 'hsn_code' in item_data:
                    hsn_code = str(item_data['hsn_code'])
                    if not self.hsn_validator.validate_hsn_format(hsn_code):
                        errors.append(f"{item_prefix}: Invalid HSN code format")
                
                # Validate numeric fields
                if 'quantity' in item_data:
                    try:
                        quantity = float(item_data['quantity'])
                        if quantity <= 0:
                            errors.append(f"{item_prefix}: Quantity must be greater than 0")
                    except (ValueError, TypeError):
                        errors.append(f"{item_prefix}: Invalid quantity value")
                
                if 'unit_price' in item_data:
                    try:
                        unit_price = float(item_data['unit_price'])
                        if unit_price < 0:
                            errors.append(f"{item_prefix}: Unit price cannot be negative")
                    except (ValueError, TypeError):
                        errors.append(f"{item_prefix}: Invalid unit price value")
                
                if 'gst_rate' in item_data:
                    try:
                        gst_rate = float(item_data['gst_rate'])
                        if not self.gst_calculator.validate_gst_rate(gst_rate):
                            errors.append(f"{item_prefix}: Invalid GST rate")
                    except (ValueError, TypeError):
                        errors.append(f"{item_prefix}: Invalid GST rate value")
        
        return errors
    
    def get_invoice_summary(self, invoice: Invoice) -> Dict[str, Any]:
        """Get a summary of the invoice with all calculated values."""
        return {
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date.isoformat(),
            'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
            'company': {
                'name': invoice.company.name,
                'gstin': invoice.company.gstin
            },
            'customer': {
                'name': invoice.customer.name,
                'gstin': invoice.customer.gstin
            },
            'totals': {
                'total_items': len(invoice.items),
                'total_quantity': sum(item.quantity for item in invoice.items),
                'total_gross_amount': float(invoice.total_gross_amount),
                'total_discount': float(invoice.total_discount_amount),
                'total_taxable_amount': float(invoice.total_taxable_amount),
                'total_cgst': float(invoice.total_cgst_amount),
                'total_sgst': float(invoice.total_sgst_amount),
                'total_igst': float(invoice.total_igst_amount),
                'total_tax': float(invoice.total_tax_amount),
                'total_amount': float(invoice.total_invoice_amount)
            },
            'tax_summary': invoice.get_tax_summary(),
            'is_interstate': invoice.is_interstate,
            'total_amount_in_words': invoice.total_amount_in_words
        }
