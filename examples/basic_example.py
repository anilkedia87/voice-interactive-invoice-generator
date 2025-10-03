"""
Basic Example: Simple Invoice Generation
This example shows how to create a basic invoice with the AI Agent.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_agent import InvoiceAIAgent


def main():
    print("=== Basic Invoice Generation Example ===\\n")
    
    # Initialize the AI Agent
    agent = InvoiceAIAgent()
    
    # Set up default company information
    company_info = {
        'name': 'Tech Solutions Pvt Ltd',
        'address': '123 Tech Park, Sector 15',
        'city': 'Gurgaon',
        'state': 'Haryana',
        'pincode': '122001',
        'gstin': '06AABCS1234C1ZS',
        'pan': 'AABCS1234C',
        'phone': '+91-124-4567890',
        'email': 'info@techsolutions.com',
        'website': 'www.techsolutions.com'
    }
    
    # Set default company
    agent.set_default_company(company_info)
    
    # Customer information
    customer_info = {
        'name': 'ABC Corporation',
        'address': '456 Business District',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'pincode': '400001',
        'gstin': '27AABCC1234D1ZF',
        'phone': '+91-22-9876543210',
        'email': 'accounts@abccorp.com'
    }
    
    # Items for the invoice
    items = [
        {
            'description': 'Website Development Service',
            'quantity': 1,
            'unit_price': 150000,
            'hsn_code': '998342',
            'gst_rate': 18,
            'unit': 'Service'
        },
        {
            'description': 'Domain Registration (1 year)',
            'quantity': 1,
            'unit_price': 1500,
            'hsn_code': '998342',
            'gst_rate': 18,
            'discount_percentage': 10
        },
        {
            'description': 'SSL Certificate',
            'quantity': 1,
            'unit_price': 5000,
            'hsn_code': '998342',
            'gst_rate': 18
        }
    ]
    
    print("Creating invoice...")
    
    # Create invoice
    invoice = agent.create_invoice_from_items(
        items=items,
        customer_info=customer_info,
        invoice_config={
            'notes': 'Thank you for your business!',
            'terms_and_conditions': '1. Payment due within 30 days\\n2. Late payment may incur additional charges',
            'payment_terms_days': 30
        }
    )
    
    print(f"Invoice created successfully!")
    print(f"Invoice Number: {invoice.invoice_number}")
    print(f"Invoice Date: {invoice.invoice_date}")
    print(f"Due Date: {invoice.due_date}")
    print(f"Total Amount: ₹{invoice.total_invoice_amount:,.2f}")
    print(f"Is Interstate: {invoice.is_interstate}")
    print()
    
    # Display invoice summary
    print("=== Invoice Summary ===")
    summary = agent.generator.get_invoice_summary(invoice)
    
    print(f"Total Items: {summary['totals']['total_items']}")
    print(f"Gross Amount: ₹{summary['totals']['total_gross_amount']:,.2f}")
    print(f"Total Discount: ₹{summary['totals']['total_discount']:,.2f}")
    print(f"Taxable Amount: ₹{summary['totals']['total_taxable_amount']:,.2f}")
    
    if invoice.is_interstate:
        print(f"IGST: ₹{summary['totals']['total_igst']:,.2f}")
    else:
        print(f"CGST: ₹{summary['totals']['total_cgst']:,.2f}")
        print(f"SGST: ₹{summary['totals']['total_sgst']:,.2f}")
    
    print(f"Total Tax: ₹{summary['totals']['total_tax']:,.2f}")
    print(f"Final Amount: ₹{summary['totals']['total_amount']:,.2f}")
    print()
    
    # Generate invoice files
    print("Generating invoice files...")
    try:
        output_files = agent.generate_invoice_files(
            invoice=invoice,
            output_dir="../output",
            formats=["html"]  # Only HTML for now to avoid PDF dependency issues
        )
        
        for format_type, file_path in output_files.items():
            print(f"{format_type.upper()} file saved: {file_path}")
    
    except Exception as e:
        print(f"Error generating files: {e}")
    
    print("\\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
