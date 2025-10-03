"""
Interactive Invoice Generator
This example provides an interactive command-line interface for creating invoices.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_agent import InvoiceAIAgent
from decimal import Decimal


class InteractiveInvoiceGenerator:
    """Interactive command-line interface for invoice generation."""
    
    def __init__(self):
        self.agent = InvoiceAIAgent()
        self.company_set = False
    
    def run(self):
        """Run the interactive generator."""
        print("🧾 Welcome to the Interactive Invoice Generator!")
        print("=" * 50)
        
        while True:
            self.show_menu()
            choice = input("\\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.setup_company()
            elif choice == '2':
                self.create_quick_invoice()
            elif choice == '3':
                self.create_detailed_invoice()
            elif choice == '4':
                self.search_hsn_codes()
            elif choice == '5':
                self.calculate_totals_only()
            elif choice == '6':
                self.generate_sample()
            elif choice == '7':
                print("\\n👋 Thank you for using Invoice Generator!")
                break
            else:
                print("\\n❌ Invalid choice. Please try again.")
            
            input("\\nPress Enter to continue...")
    
    def show_menu(self):
        """Display the main menu."""
        print("\\n" + "=" * 50)
        print("📋 MAIN MENU")
        print("=" * 50)
        print("1. 🏢 Setup Company Information")
        print("2. ⚡ Create Quick Invoice (Single Item)")
        print("3. 📊 Create Detailed Invoice (Multiple Items)")
        print("4. 🔍 Search HSN Codes")
        print("5. 🧮 Calculate Totals Only")
        print("6. 📄 Generate Sample Invoice")
        print("7. 🚪 Exit")
        
        if self.company_set:
            print("\\n✅ Company information is set")
        else:
            print("\\n⚠️  Company information not set (required for invoices)")
    
    def setup_company(self):
        """Setup company information."""
        print("\\n🏢 Company Information Setup")
        print("-" * 30)
        
        company_info = {}
        
        company_info['name'] = input("Company Name: ").strip()
        company_info['address'] = input("Address: ").strip()
        company_info['city'] = input("City: ").strip()
        company_info['state'] = input("State: ").strip()
        company_info['pincode'] = input("Pincode: ").strip()
        company_info['gstin'] = input("GSTIN (optional): ").strip() or None
        company_info['phone'] = input("Phone (optional): ").strip() or None
        company_info['email'] = input("Email (optional): ").strip() or None
        
        try:
            self.agent.set_default_company(company_info)
            self.company_set = True
            print("\\n✅ Company information saved successfully!")
        except ValueError as e:
            print(f"\\n❌ Error: {e}")
    
    def create_quick_invoice(self):
        """Create a quick invoice with single item."""
        if not self.company_set:
            print("\\n⚠️  Please setup company information first!")
            return
        
        print("\\n⚡ Quick Invoice Creation")
        print("-" * 25)
        
        try:
            # Get item details
            description = input("Item Description: ").strip()
            quantity = float(input("Quantity: ").strip())
            unit_price = float(input("Unit Price (₹): ").strip())
            customer_name = input("Customer Name: ").strip()
            
            # Optional fields
            hsn_code = input("HSN Code (optional, will auto-suggest): ").strip() or None
            gst_rate = input("GST Rate % (optional, will auto-suggest): ").strip()
            gst_rate = float(gst_rate) if gst_rate else None
            
            discount = input("Discount % (optional): ").strip()
            discount = float(discount) if discount else None
            
            print("\\n🔄 Generating invoice...")
            
            invoice = self.agent.create_quick_invoice(
                item_description=description,
                quantity=quantity,
                unit_price=unit_price,
                customer_name=customer_name,
                hsn_code=hsn_code,
                gst_rate=gst_rate,
                discount=discount
            )
            
            self.display_invoice_summary(invoice)
            
            # Ask if user wants to generate files
            if input("\\nGenerate HTML file? (y/n): ").strip().lower() == 'y':
                files = self.agent.generate_invoice_files(invoice, formats=["html"])
                if "html" in files:
                    print(f"📄 HTML file saved: {files['html']}")
        
        except ValueError as e:
            print(f"\\n❌ Error: {e}")
        except Exception as e:
            print(f"\\n❌ Unexpected error: {e}")
    
    def create_detailed_invoice(self):
        """Create a detailed invoice with multiple items."""
        if not self.company_set:
            print("\\n⚠️  Please setup company information first!")
            return
        
        print("\\n📊 Detailed Invoice Creation")
        print("-" * 28)
        
        try:
            # Get customer info
            print("Customer Information:")
            customer_info = {}
            customer_info['name'] = input("  Name: ").strip()
            customer_info['address'] = input("  Address: ").strip()
            customer_info['city'] = input("  City: ").strip()
            customer_info['state'] = input("  State: ").strip()
            customer_info['pincode'] = input("  Pincode: ").strip()
            customer_info['gstin'] = input("  GSTIN (optional): ").strip() or None
            
            # Get items
            items = []
            item_count = 1
            
            print("\\nItem Information (press Enter on description to finish):")
            
            while True:
                print(f"\\nItem {item_count}:")
                description = input("  Description: ").strip()
                
                if not description:
                    break
                
                quantity = float(input("  Quantity: ").strip())
                unit_price = float(input("  Unit Price (₹): ").strip())
                hsn_code = input("  HSN Code: ").strip()
                gst_rate = float(input("  GST Rate %: ").strip())
                
                discount = input("  Discount % (optional): ").strip()
                discount = float(discount) if discount else 0
                
                items.append({
                    'description': description,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'hsn_code': hsn_code,
                    'gst_rate': gst_rate,
                    'discount_percentage': discount
                })
                
                item_count += 1
            
            if not items:
                print("\\n⚠️  No items entered!")
                return
            
            print("\\n🔄 Generating invoice...")
            
            invoice = self.agent.create_invoice_from_items(
                items=items,
                customer_info=customer_info
            )
            
            self.display_invoice_summary(invoice)
            
            # Ask if user wants to generate files
            if input("\\nGenerate HTML file? (y/n): ").strip().lower() == 'y':
                files = self.agent.generate_invoice_files(invoice, formats=["html"])
                if "html" in files:
                    print(f"📄 HTML file saved: {files['html']}")
        
        except ValueError as e:
            print(f"\\n❌ Error: {e}")
        except Exception as e:
            print(f"\\n❌ Unexpected error: {e}")
    
    def search_hsn_codes(self):
        """Search for HSN codes."""
        print("\\n🔍 HSN Code Search")
        print("-" * 18)
        
        query = input("Enter search term (e.g., 'laptop', 'software'): ").strip()
        
        if not query:
            print("\\n⚠️  Please enter a search term!")
            return
        
        results = self.agent.search_hsn_codes(query)
        
        if results:
            print(f"\\n📋 Found {len(results)} matching HSN codes:")
            print("-" * 50)
            for result in results:
                print(f"HSN: {result['hsn_code']} | GST: {result['typical_gst']}% | {result['description']}")
        else:
            print("\\n❌ No matching HSN codes found.")
    
    def calculate_totals_only(self):
        """Calculate totals without creating full invoice."""
        print("\\n🧮 Calculate Totals Only")
        print("-" * 23)
        
        try:
            items = []
            item_count = 1
            
            print("Enter items to calculate totals:")
            
            while True:
                print(f"\\nItem {item_count}:")
                description = input("  Description: ").strip()
                
                if not description:
                    break
                
                quantity = float(input("  Quantity: ").strip())
                unit_price = float(input("  Unit Price (₹): ").strip())
                gst_rate = float(input("  GST Rate %: ").strip())
                
                discount = input("  Discount % (optional): ").strip()
                discount = float(discount) if discount else 0
                
                items.append({
                    'description': description,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'hsn_code': '9999',  # Default
                    'gst_rate': gst_rate,
                    'discount_percentage': discount
                })
                
                item_count += 1
            
            if not items:
                print("\\n⚠️  No items entered!")
                return
            
            is_interstate = input("\\nIs this interstate transaction? (y/n): ").strip().lower() == 'y'
            
            totals = self.agent.calculate_invoice_totals(items, is_interstate)
            
            print("\\n💰 Calculation Results:")
            print("-" * 25)
            print(f"Gross Amount:    ₹{totals['gross_amount']:,.2f}")
            print(f"Discount Amount: ₹{totals['discount_amount']:,.2f}")
            print(f"Taxable Amount:  ₹{totals['taxable_amount']:,.2f}")
            
            if is_interstate:
                print(f"IGST:            ₹{totals['igst_amount']:,.2f}")
            else:
                print(f"CGST:            ₹{totals['cgst_amount']:,.2f}")
                print(f"SGST:            ₹{totals['sgst_amount']:,.2f}")
            
            print(f"Total Tax:       ₹{totals['total_tax']:,.2f}")
            print(f"Final Amount:    ₹{totals['total_amount']:,.2f}")
        
        except ValueError as e:
            print(f"\\n❌ Error: {e}")
        except Exception as e:
            print(f"\\n❌ Unexpected error: {e}")
    
    def generate_sample(self):
        """Generate a sample invoice."""
        print("\\n📄 Generating Sample Invoice...")
        
        try:
            invoice = self.agent.generate_sample_invoice()
            self.display_invoice_summary(invoice)
            
            # Generate HTML file
            files = self.agent.generate_invoice_files(invoice, formats=["html"])
            if "html" in files:
                print(f"\\n📄 Sample HTML file saved: {files['html']}")
        
        except Exception as e:
            print(f"\\n❌ Error generating sample: {e}")
    
    def display_invoice_summary(self, invoice):
        """Display invoice summary."""
        print("\\n✅ Invoice Generated Successfully!")
        print("=" * 40)
        print(f"Invoice Number: {invoice.invoice_number}")
        print(f"Date: {invoice.invoice_date}")
        print(f"Customer: {invoice.customer.name}")
        print(f"Items: {len(invoice.items)}")
        print(f"Transaction Type: {'Interstate' if invoice.is_interstate else 'Intrastate'}")
        print("\\n💰 Amount Breakdown:")
        print(f"  Gross Amount:   ₹{invoice.total_gross_amount:,.2f}")
        print(f"  Discount:       ₹{invoice.total_discount_amount:,.2f}")
        print(f"  Taxable Amount: ₹{invoice.total_taxable_amount:,.2f}")
        print(f"  Total Tax:      ₹{invoice.total_tax_amount:,.2f}")
        print(f"  Final Amount:   ₹{invoice.total_invoice_amount:,.2f}")
        print("\\n📝 Amount in Words:")
        print(f"  {invoice.total_amount_in_words}")


def main():
    """Main function to run the interactive generator."""
    generator = InteractiveInvoiceGenerator()
    generator.run()


if __name__ == "__main__":
    main()
