"""
AI Agent for Invoice Automation
Main interface for generating invoices based on user inputs.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from datetime import date, datetime, timedelta
from decimal import Decimal

from models import Invoice, InvoiceItem, Company, Customer
from services import InvoiceGenerator, GSTCalculator, HSNValidator
from templates import InvoiceTemplate


class InvoiceAIAgent:
    """
    AI Agent for automated invoice generation.
    
    This is the main interface for users to interact with the invoice automation system.
    It provides intelligent defaults, validation, and easy-to-use methods for creating
    professional GST-compliant invoices.
    """
    
    def __init__(self, default_company: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI Agent.
        
        Args:
            default_company: Default company information to use for all invoices
        """
        self.generator = InvoiceGenerator()
        self.template_engine = InvoiceTemplate()
        self.gst_calculator = GSTCalculator()
        self.hsn_validator = HSNValidator()
        
        self.default_company = default_company
        self.invoice_counter = 1
        
        # Default settings
        self.default_settings = {
            'payment_terms_days': 30,
            'default_gst_rate': 18,
            'currency': 'INR',
            'template': 'standard',
            'auto_suggest_hsn': True,
            'auto_suggest_gst': True
        }
    
    def create_invoice_from_items(
        self,
        items: List[Dict[str, Any]],
        customer_info: Dict[str, Any],
        company_info: Optional[Dict[str, Any]] = None,
        invoice_config: Optional[Dict[str, Any]] = None
    ) -> Invoice:
        """
        Create invoice from simple item list and customer info.
        
        Args:
            items: List of items with keys: description, quantity, unit_price, hsn_code, gst_rate, discount
            customer_info: Customer information dictionary
            company_info: Company information (uses default if not provided)
            invoice_config: Invoice configuration options
            
        Returns:
            Complete Invoice object
        
        Example:
            items = [
                {
                    "description": "Laptop Computer",
                    "quantity": 2,
                    "unit_price": 50000,
                    "hsn_code": "8471",
                    "gst_rate": 18,
                    "discount": 5  # 5% discount
                }
            ]
        """
        # Use default company if none provided
        if company_info is None:
            if self.default_company is None:
                raise ValueError("No company information provided and no default company set")
            company_info = self.default_company.copy()
        
        # Process and enhance items
        processed_items = self._process_items(items)
        
        # Create invoice configuration
        config = self._create_invoice_config(invoice_config)
        
        # Generate invoice
        invoice = self.generator.create_invoice(
            company_data=company_info,
            customer_data=customer_info,
            items_data=processed_items,
            invoice_config=config
        )
        
        return invoice
    
    def create_quick_invoice(
        self,
        item_description: str,
        quantity: Union[int, float],
        unit_price: Union[int, float],
        customer_name: str,
        hsn_code: Optional[str] = None,
        gst_rate: Optional[float] = None,
        discount: Optional[float] = None
    ) -> Invoice:
        """
        Create a quick invoice with a single item.
        
        Args:
            item_description: Description of the item/service
            quantity: Quantity of items
            unit_price: Price per unit
            customer_name: Name of the customer
            hsn_code: HSN code (will auto-suggest if not provided)
            gst_rate: GST rate (will auto-suggest if not provided)
            discount: Discount percentage
            
        Returns:
            Complete Invoice object
        """
        # Auto-suggest HSN code if not provided
        if hsn_code is None and self.default_settings['auto_suggest_hsn']:
            hsn_code = self._suggest_hsn_code(item_description)
        
        # Auto-suggest GST rate if not provided
        if gst_rate is None and self.default_settings['auto_suggest_gst']:
            if hsn_code:
                suggested_rate = self.hsn_validator.suggest_gst_rate(hsn_code)
                gst_rate = suggested_rate if suggested_rate is not None else self.default_settings['default_gst_rate']
            else:
                gst_rate = self.default_settings['default_gst_rate']
        
        # Create item
        item = {
            'description': item_description,
            'quantity': quantity,
            'unit_price': unit_price,
            'hsn_code': hsn_code or '9999',  # Default HSN code
            'gst_rate': gst_rate,
            'discount_percentage': discount or 0
        }
        
        # Create customer info
        customer_info = {
            'name': customer_name,
            'address': 'Customer Address',
            'city': 'City',
            'state': 'State',
            'pincode': '000000'
        }
        
        return self.create_invoice_from_items([item], customer_info)
    
    def generate_invoice_files(
        self,
        invoice: Invoice,
        output_dir: str = "./output",
        formats: List[str] = ["html", "pdf"],
        template_name: str = "standard"
    ) -> Dict[str, str]:
        """
        Generate invoice files in specified formats.
        
        Args:
            invoice: Invoice object to generate files for
            output_dir: Directory to save files
            formats: List of formats to generate ("html", "pdf")
            template_name: Template to use
            
        Returns:
            Dictionary mapping format to file path
        """
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = {}
        base_filename = f"invoice_{invoice.invoice_number.replace('-', '_')}"
        
        if "html" in formats:
            html_path = os.path.join(output_dir, f"{base_filename}.html")
            self.template_engine.save_html_invoice(invoice, html_path, template_name)
            generated_files["html"] = html_path
        
        if "pdf" in formats:
            try:
                pdf_path = os.path.join(output_dir, f"{base_filename}.pdf")
                self.template_engine.generate_pdf_invoice(invoice, pdf_path, template_name)
                generated_files["pdf"] = pdf_path
            except ImportError:
                print("Warning: PDF generation requires weasyprint. Install with: pip install weasyprint")
            except Exception as e:
                print(f"Warning: Could not generate PDF: {e}")
        
        return generated_files
    
    def calculate_invoice_totals(
        self,
        items: List[Dict[str, Any]],
        is_interstate: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate invoice totals without creating full invoice object.
        
        Args:
            items: List of items
            is_interstate: Whether this is an interstate transaction
            
        Returns:
            Dictionary with calculated totals
        """
        processed_items = self._process_items(items)
        
        totals = {
            'gross_amount': Decimal('0'),
            'discount_amount': Decimal('0'),
            'taxable_amount': Decimal('0'),
            'cgst_amount': Decimal('0'),
            'sgst_amount': Decimal('0'),
            'igst_amount': Decimal('0'),
            'total_tax': Decimal('0'),
            'total_amount': Decimal('0')
        }
        
        for item_data in processed_items:
            item = InvoiceItem(**item_data)
            
            totals['gross_amount'] += item.gross_amount
            totals['discount_amount'] += item.total_discount
            totals['taxable_amount'] += item.taxable_amount
            
            if is_interstate:
                totals['igst_amount'] += item.igst_amount
            else:
                totals['cgst_amount'] += item.cgst_amount
                totals['sgst_amount'] += item.sgst_amount
        
        totals['total_tax'] = totals['igst_amount'] if is_interstate else totals['cgst_amount'] + totals['sgst_amount']
        totals['total_amount'] = totals['taxable_amount'] + totals['total_tax']
        
        # Convert to float for JSON serialization
        return {k: float(v) for k, v in totals.items()}
    
    def validate_invoice_data(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate invoice data and return validation results with suggestions.
        
        Args:
            invoice_data: Complete invoice data
            
        Returns:
            Validation results with errors and suggestions
        """
        errors = self.generator.validate_invoice_data(invoice_data)
        suggestions = []
        
        # Add intelligent suggestions
        if 'items' in invoice_data:
            for i, item in enumerate(invoice_data['items']):
                item_suggestions = self._get_item_suggestions(item, i + 1)
                suggestions.extend(item_suggestions)
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions
        }
    
    def search_hsn_codes(self, query: str) -> List[Dict[str, Any]]:
        """Search for HSN codes by description."""
        return self.hsn_validator.search_hsn_codes(query)
    
    def get_gst_info(self, hsn_code: str) -> Optional[Dict[str, Any]]:
        """Get GST information for an HSN code."""
        return self.hsn_validator.get_hsn_info(hsn_code)
    
    def set_default_company(self, company_info: Dict[str, Any]):
        """Set default company information."""
        # Validate company data
        errors = []
        required_fields = ['name', 'address', 'city', 'state', 'pincode']
        for field in required_fields:
            if field not in company_info or not company_info[field]:
                errors.append(f"Company {field} is required")
        
        if errors:
            raise ValueError(f"Invalid company data: {', '.join(errors)}")
        
        # Validate GSTIN if provided
        if 'gstin' in company_info and company_info['gstin']:
            is_valid, error = self.gst_calculator.validate_gstin(company_info['gstin'])
            if not is_valid:
                raise ValueError(f"Invalid GSTIN: {error}")
        
        self.default_company = company_info
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update default settings."""
        self.default_settings.update(settings)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        return self.default_settings.copy()
    
    def export_invoice_json(self, invoice: Invoice) -> str:
        """Export invoice as JSON string."""
        return json.dumps(self.generator.get_invoice_summary(invoice), indent=2, default=str)
    
    def import_invoice_json(self, json_data: str) -> Invoice:
        """Import invoice from JSON string."""
        data = json.loads(json_data)
        # This would need to be implemented based on the JSON structure
        # For now, raise NotImplementedError
        raise NotImplementedError("JSON import feature coming soon")
    
    def _process_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and enhance item data."""
        processed_items = []
        
        for item in items:
            processed_item = item.copy()
            
            # Set default values
            processed_item.setdefault('unit', 'Nos')
            processed_item.setdefault('discount_percentage', 0)
            processed_item.setdefault('discount_amount', 0)
            
            # Auto-suggest GST rate if not provided
            if 'gst_rate' not in processed_item and self.default_settings['auto_suggest_gst']:
                if 'hsn_code' in processed_item:
                    suggested_rate = self.hsn_validator.suggest_gst_rate(processed_item['hsn_code'])
                    processed_item['gst_rate'] = suggested_rate if suggested_rate is not None else self.default_settings['default_gst_rate']
                else:
                    processed_item['gst_rate'] = self.default_settings['default_gst_rate']
            
            # Handle discount field (convert to discount_percentage if needed)
            if 'discount' in processed_item:
                processed_item['discount_percentage'] = processed_item['discount']
                del processed_item['discount']
            
            processed_items.append(processed_item)
        
        return processed_items
    
    def _create_invoice_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create invoice configuration with defaults."""
        invoice_config = {}
        
        if config:
            invoice_config.update(config)
        
        # Set defaults
        if 'payment_terms_days' not in invoice_config:
            invoice_config['payment_terms_days'] = self.default_settings['payment_terms_days']
        
        return invoice_config
    
    def _suggest_hsn_code(self, description: str) -> Optional[str]:
        """Suggest HSN code based on item description."""
        # Simple keyword-based suggestion
        description_lower = description.lower()
        
        # Common mappings
        mappings = {
            'laptop': '8471',
            'computer': '8471',
            'mobile': '8517',
            'phone': '8517',
            'shirt': '6109',
            'tshirt': '6109',
            't-shirt': '6109',
            'software': '998341',
            'consulting': '998342',
            'service': '998342'
        }
        
        for keyword, hsn in mappings.items():
            if keyword in description_lower:
                return hsn
        
        return None
    
    def _get_item_suggestions(self, item: Dict[str, Any], item_number: int) -> List[str]:
        """Get suggestions for improving item data."""
        suggestions = []
        
        # HSN code suggestions
        if 'hsn_code' not in item or not item['hsn_code']:
            if 'description' in item:
                suggested_hsn = self._suggest_hsn_code(item['description'])
                if suggested_hsn:
                    suggestions.append(f"Item {item_number}: Consider HSN code {suggested_hsn} for '{item['description']}'")
        
        # GST rate suggestions
        if 'hsn_code' in item and item['hsn_code']:
            hsn_info = self.hsn_validator.get_hsn_info(item['hsn_code'])
            if hsn_info and 'gst_rate' in item:
                if item['gst_rate'] != hsn_info['typical_gst']:
                    suggestions.append(
                        f"Item {item_number}: Typical GST rate for HSN {item['hsn_code']} is {hsn_info['typical_gst']}%, "
                        f"you have {item['gst_rate']}%"
                    )
        
        return suggestions
    
    def generate_sample_invoice(self) -> Invoice:
        """Generate a sample invoice for testing purposes."""
        sample_company = {
            'name': 'Sample Company Pvt Ltd',
            'address': '123 Business Street',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
            'gstin': '27AABCS1234C1ZS',
            'phone': '+91-98765-43210',
            'email': 'info@samplecompany.com'
        }
        
        sample_customer = {
            'name': 'Sample Customer',
            'address': '456 Customer Road',
            'city': 'Delhi',
            'state': 'Delhi',
            'pincode': '110001',
            'gstin': '07AABCC1234D1ZF'
        }
        
        sample_items = [
            {
                'description': 'Laptop Computer',
                'quantity': 2,
                'unit_price': 50000,
                'hsn_code': '8471',
                'gst_rate': 18,
                'discount_percentage': 5
            },
            {
                'description': 'Software License',
                'quantity': 1,
                'unit_price': 10000,
                'hsn_code': '998341',
                'gst_rate': 18
            }
        ]
        
        return self.create_invoice_from_items(sample_items, sample_customer, sample_company)
