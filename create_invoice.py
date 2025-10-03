#!/usr/bin/env python3
"""
Simple Invoice Creator
Easy-to-use script for creating invoices with your inputs.
"""

import sys
import os
from decimal import Decimal

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.company import Company
from models.customer import Customer
from models.invoice import Invoice, InvoiceItem
from templates.invoice_template import InvoiceTemplate

def create_your_invoice():
    """Create an invoice with your business details."""
    
    print("🧾 Invoice Generator - Create Your Invoice")
    print("=" * 45)
    
    # YOUR COMPANY DETAILS - MODIFY THESE
    company = Company(
        name="Kedia Brothers",                # ✏️ Change this
        address="Pabitradiha",                # ✏️ Change this  
        city="Keonjhar",                      # ✏️ Change this
        state="Odisha",                       # ✏️ Change this
        pincode="758001",                     # ✏️ Change this
        gstin="00AABCS1234C1ZS",              # ✏️ Change this (optional)
        phone="+91-7059791147",              # ✏️ Change this (optional)
        email="anilkedia@email.com"          # ✏️ Change this (optional)
    )
    
    # CUSTOMER DETAILS - MODIFY THESE
    customer = Customer(
        name="Customer Name",                  # ✏️ Change this
        address="Customer Address",            # ✏️ Change this
        city="Customer City",                  # ✏️ Change this
        state="Customer State",                # ✏️ Change this
        pincode="000000",                      # ✏️ Change this
        gstin="00AABCC1234D1ZF"               # ✏️ Change this (optional)
    )
    
    # INVOICE ITEMS - MODIFY THESE
    items = [
        InvoiceItem(
            description="Product/Service 1",    # ✏️ Change this
            hsn_code="9999",                   # ✏️ Change this (HSN/SAC code)
            quantity=Decimal('1'),             # ✏️ Change this
            unit_price=Decimal('10000'),       # ✏️ Change this (price per unit)
            gst_rate=Decimal('18'),            # ✏️ Change this (GST %)
            unit="Nos"                         # ✏️ Change this (Nos, Service, Kg, etc.)
        ),
        InvoiceItem(
            description="Product/Service 2",    # ✏️ Change this
            hsn_code="9999",                   # ✏️ Change this
            quantity=Decimal('2'),             # ✏️ Change this
            unit_price=Decimal('5000'),        # ✏️ Change this
            gst_rate=Decimal('18'),            # ✏️ Change this
            discount_percentage=Decimal('10')   # ✏️ Optional: discount %
        )
        # ✏️ Add more items as needed
    ]
    
    # Create the invoice
    invoice = Invoice(
        company=company,
        customer=customer, 
        items=items
    )
    
    # Display invoice summary
    print("✅ Invoice Created!")
    print(f"Invoice Number: {invoice.invoice_number}")
    print(f"Date: {invoice.invoice_date}")
    print(f"Company: {invoice.company.name}")
    print(f"Customer: {invoice.customer.name}")
    print(f"Items: {len(invoice.items)}")
    print(f"Total Amount: ₹{invoice.total_invoice_amount:,.2f}")
    print(f"Type: {'Interstate' if invoice.is_interstate else 'Intrastate'}")
    
    # Generate HTML file
    print("\\n📁 Generating invoice file...")
    template_engine = InvoiceTemplate()
    
    os.makedirs("output", exist_ok=True)
    html_file = f"output/my_invoice_{invoice.invoice_number.replace('-', '_')}.html"
    
    template_engine.save_html_invoice(invoice, html_file)
    print(f"📄 Invoice saved: {html_file}")
    print("Open this file in your web browser to view and print!")
    
    return invoice

if __name__ == "__main__":
    print("📝 INSTRUCTIONS:")
    print("1. Edit this file and change the company, customer, and item details")
    print("2. Run the script to generate your invoice")
    print("3. Open the generated HTML file to view/print your invoice\\n")
    
    try:
        invoice = create_your_invoice()
        print("\\n🎉 Success! Your invoice has been generated.")
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        print("Please check your details and try again.")
