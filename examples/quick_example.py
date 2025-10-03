"""
Quick Invoice Example
This example shows how to create a quick invoice with minimal inputs.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_agent import InvoiceAIAgent


def main():
    print("=== Quick Invoice Generation Example ===\\n")
    
    # Initialize the AI Agent with default company
    default_company = {
        'name': 'My Business',
        'address': '123 Business Street',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'pincode': '560001',
        'gstin': '29AABCS1234C1ZS',
        'phone': '+91-80-12345678',
        'email': 'contact@mybusiness.com'
    }
    
    agent = InvoiceAIAgent(default_company=default_company)
    
    print("Creating a quick invoice for a laptop sale...")
    
    # Create a quick invoice with minimal inputs
    invoice = agent.create_quick_invoice(
        item_description="Laptop - Dell Inspiron 15",
        quantity=1,
        unit_price=65000,
        customer_name="John Smith",
        hsn_code="8471",  # HSN for computers
        gst_rate=18,
        discount=5  # 5% discount
    )
    
    print(f"\\n✅ Invoice created successfully!")
    print(f"Invoice Number: {invoice.invoice_number}")
    print(f"Customer: {invoice.customer.name}")
    print(f"Item: {invoice.items[0].description}")
    print(f"Quantity: {invoice.items[0].quantity}")
    print(f"Unit Price: ₹{invoice.items[0].unit_price:,.2f}")
    print(f"Discount: {invoice.items[0].discount_percentage}%")
    print(f"GST Rate: {invoice.items[0].gst_rate}%")
    print(f"Final Amount: ₹{invoice.total_invoice_amount:,.2f}")
    
    # Show calculation breakdown
    item = invoice.items[0]
    print("\\n=== Calculation Breakdown ===")
    print(f"Gross Amount: ₹{item.gross_amount:,.2f}")
    print(f"Discount: ₹{item.total_discount:,.2f}")
    print(f"Taxable Amount: ₹{item.taxable_amount:,.2f}")
    print(f"CGST (9%): ₹{item.cgst_amount:,.2f}")
    print(f"SGST (9%): ₹{item.sgst_amount:,.2f}")
    print(f"Total: ₹{item.total_amount:,.2f}")
    
    # Generate HTML file
    print("\\nGenerating HTML invoice...")
    try:
        files = agent.generate_invoice_files(invoice, formats=["html"])
        if "html" in files:
            print(f"📄 HTML invoice saved: {files['html']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\\n=== Quick example completed! ===")


if __name__ == "__main__":
    main()
