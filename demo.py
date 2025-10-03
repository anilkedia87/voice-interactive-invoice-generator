#!/usr/bin/env python3
"""
Simple Invoice Demo - Direct Implementation
Creates a sample invoice without complex imports.
"""

import sys
import os
from decimal import Decimal
from datetime import date

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Direct imports to avoid relative import issues
from models.company import Company
from models.customer import Customer
from models.invoice import Invoice, InvoiceItem
from services.gst_calculator import GSTCalculator
from templates.invoice_template import InvoiceTemplate

def main():
    print("🧾 Invoice Automation System - Demo")
    print("=" * 40)
    
    try:
        # Create company
        company = Company(
            name="Tech Solutions Pvt Ltd",
            address="123 Tech Park, Sector 15",
            city="Gurgaon", 
            state="Haryana",
            pincode="122001",
            gstin="06AABCS1234C1ZS",
            phone="+91-124-4567890",
            email="info@techsolutions.com"
        )
        
        # Create customer  
        customer = Customer(
            name="ABC Corporation",
            address="456 Business District", 
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            gstin="27AABCC1234D1ZF"
        )
        
        # Create invoice items
        item1 = InvoiceItem(
            description="Website Development Service",
            hsn_code="998342",
            quantity=Decimal('1'),
            unit_price=Decimal('150000'),
            gst_rate=Decimal('18'),
            unit="Service"
        )
        
        item2 = InvoiceItem(
            description="Domain Registration",
            hsn_code="998342", 
            quantity=Decimal('1'),
            unit_price=Decimal('1500'),
            gst_rate=Decimal('18'),
            discount_percentage=Decimal('10')
        )
        
        # Create invoice
        invoice = Invoice(
            company=company,
            customer=customer,
            items=[item1, item2]
        )
        
        print("✅ Invoice created successfully!")
        print(f"Invoice Number: {invoice.invoice_number}")
        print(f"Company: {invoice.company.name}")
        print(f"Customer: {invoice.customer.name}")
        print(f"Total Items: {len(invoice.items)}")
        print(f"Transaction Type: {'Interstate' if invoice.is_interstate else 'Intrastate'}")
        print()
        
        # Show calculations
        print("💰 Invoice Breakdown:")
        print(f"Gross Amount:   ₹{invoice.total_gross_amount:,.2f}")
        print(f"Total Discount: ₹{invoice.total_discount_amount:,.2f}")
        print(f"Taxable Amount: ₹{invoice.total_taxable_amount:,.2f}")
        
        if invoice.is_interstate:
            print(f"IGST:          ₹{invoice.total_igst_amount:,.2f}")
        else:
            print(f"CGST:          ₹{invoice.total_cgst_amount:,.2f}")
            print(f"SGST:          ₹{invoice.total_sgst_amount:,.2f}")
        
        print(f"Total Tax:      ₹{invoice.total_tax_amount:,.2f}")
        print(f"Final Amount:   ₹{invoice.total_invoice_amount:,.2f}")
        print()
        
        # Amount in words
        print(f"Amount in Words: {invoice.total_amount_in_words}")
        print()
        
        # Generate HTML
        print("📁 Generating HTML invoice...")
        template_engine = InvoiceTemplate()
        
        # Ensure output directory exists
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        html_file = os.path.join(output_dir, f"invoice_{invoice.invoice_number.replace('-', '_')}.html")
        template_engine.save_html_invoice(invoice, html_file)
        
        print(f"📄 HTML Invoice saved: {html_file}")
        print("You can open this file in a web browser to view the professional invoice.")
        print()
        
        # Show tax summary
        print("📊 Tax Summary by GST Rate:")
        tax_summary = invoice.get_tax_summary()
        for rate, summary in tax_summary.items():
            print(f"  {rate}% GST: ₹{summary['taxable_amount']:,.2f} taxable, ₹{summary['total_tax']:,.2f} tax")
        
        print()
        print("✨ Demo completed successfully!")
        print("The Invoice Automation System is working perfectly!")
        
        return invoice
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    invoice = main()
