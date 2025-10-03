#!/usr/bin/env python3
"""
Interactive Invoice Generator
Fully interactive system that asks for all details and creates professional invoices.
"""

import sys
import os
import json
from decimal import Decimal
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.company import Company
from models.customer import Customer
from models.invoice import Invoice, InvoiceItem
from templates.invoice_template import InvoiceTemplate

class InteractiveInvoiceGenerator:
    def __init__(self):
        self.config_file = "invoice_config.json"
        self.load_config()
    
    def load_config(self):
        """Load configuration including last invoice number."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "last_invoice_number": 0,
                    "company_info": None,
                    "invoice_prefix": "INV"
                }
        except Exception:
            self.config = {
                "last_invoice_number": 0,
                "company_info": None,
                "invoice_prefix": "INV"
            }
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get_next_invoice_number(self):
        """Generate next invoice number automatically."""
        self.config["last_invoice_number"] += 1
        invoice_num = self.config["last_invoice_number"]
        return f"{self.config['invoice_prefix']}-{invoice_num:04d}"
    
    def get_input(self, prompt, required=True, default=None):
        """Get user input with validation."""
        while True:
            if default:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()
            
            if user_input or not required:
                return user_input
            
            if required:
                print("❌ This field is required. Please enter a value.")
    
    def get_decimal_input(self, prompt, required=True):
        """Get decimal input with validation."""
        while True:
            try:
                value = self.get_input(prompt, required)
                if not value and not required:
                    return Decimal('0')
                return Decimal(str(value))
            except Exception:
                print("❌ Please enter a valid number.")
    
    def setup_company_info(self):
        """Get company information from user."""
        print("\\n🏢 COMPANY INFORMATION")
        print("=" * 30)
        print("Enter your business details:")
        
        company_info = {}
        company_info['name'] = self.get_input("Company Name")
        company_info['address'] = self.get_input("Address")
        company_info['city'] = self.get_input("City")
        company_info['state'] = self.get_input("State")
        company_info['pincode'] = self.get_input("Pincode")
        company_info['gstin'] = self.get_input("GSTIN (15 digits, optional)", required=False)
        company_info['pan'] = self.get_input("PAN Number (optional)", required=False)
        company_info['phone'] = self.get_input("Phone Number (optional)", required=False)
        company_info['email'] = self.get_input("Email Address (optional)", required=False)
        company_info['website'] = self.get_input("Website (optional)", required=False)
        
        # Bank details
        print("\\n🏦 Bank Details (optional):")
        company_info['bank_name'] = self.get_input("Bank Name", required=False)
        company_info['bank_account'] = self.get_input("Account Number", required=False)
        company_info['ifsc_code'] = self.get_input("IFSC Code", required=False)
        
        # Remove empty values
        company_info = {k: v for k, v in company_info.items() if v}
        
        self.config['company_info'] = company_info
        self.save_config()
        
        print("\\n✅ Company information saved!")
        return company_info
    
    def get_company_info(self):
        """Get company info (use saved or ask for new)."""
        if self.config.get('company_info'):
            print(f"\\n🏢 Using saved company: {self.config['company_info']['name']}")
            use_saved = self.get_input("Use saved company info? (y/n)", default="y").lower()
            
            if use_saved == 'y':
                return self.config['company_info']
        
        return self.setup_company_info()
    
    def get_customer_info(self):
        """Get customer information from user."""
        print("\\n👤 CUSTOMER INFORMATION")
        print("=" * 25)
        print("Enter customer details:")
        
        customer_info = {}
        customer_info['name'] = self.get_input("Customer Name")
        customer_info['address'] = self.get_input("Address")
        customer_info['city'] = self.get_input("City")
        customer_info['state'] = self.get_input("State")
        customer_info['pincode'] = self.get_input("Pincode")
        customer_info['gstin'] = self.get_input("Customer GSTIN (optional)", required=False)
        customer_info['phone'] = self.get_input("Phone Number (optional)", required=False)
        customer_info['email'] = self.get_input("Email Address (optional)", required=False)
        
        # Remove empty values
        return {k: v for k, v in customer_info.items() if v}
    
    def get_items_info(self):
        """Get invoice items from user."""
        print("\\n📦 INVOICE ITEMS")
        print("=" * 18)
        print("Enter products/services (press Enter on description to finish):")
        
        items = []
        item_number = 1
        
        while True:
            print(f"\\n--- Item {item_number} ---")
            description = self.get_input("Item Description (Enter to finish)", required=False)
            
            if not description:
                break
            
            # Auto-suggest HSN codes based on description
            from services.hsn_validator import HSNValidator
            
            suggestions = HSNValidator.get_multiple_suggestions(description, limit=3)
            
            if suggestions:
                print("\\n🤖 AI Suggested HSN Codes based on your item:")
                for i, suggestion in enumerate(suggestions, 1):
                    confidence_icon = "🎯" if suggestion['confidence'] > 70 else "💡" if suggestion['confidence'] > 40 else "❓"
                    print(f"  {confidence_icon} {i}. {suggestion['hsn_code']} - {suggestion['description']} (GST: {suggestion['typical_gst']}%) - {suggestion['confidence']}% match")
                
                # Use the best suggestion as default
                suggested_hsn = suggestions[0]['hsn_code']
                suggested_gst = suggestions[0]['typical_gst']
                
                print(f"\\n✨ Best match: {suggested_hsn} (GST: {suggested_gst}%)")
                hsn_code = self.get_input("HSN/SAC Code", default=suggested_hsn)
                
                # Auto-suggest GST rate based on selected HSN
                if hsn_code == suggested_hsn:
                    default_gst = suggested_gst
                else:
                    # Look up GST rate for manually entered HSN
                    hsn_info = HSNValidator.get_hsn_info(hsn_code)
                    default_gst = hsn_info['typical_gst'] if hsn_info else 18
            else:
                print("\\n💡 Common HSN/SAC Codes:")
                print("  • 8471 - Computers/Laptops (18%)")
                print("  • 8517 - Mobile Phones (18%)")  
                print("  • 6109 - T-shirts/Garments (12%)")
                print("  • 998342 - IT Services (18%)")
                print("  • 998341 - Software Services (18%)")
                print("  • 9999 - General/Other (18%)")
                
                hsn_code = self.get_input("HSN/SAC Code", default="9999")
                default_gst = 18
            quantity = self.get_decimal_input("Quantity")
            unit_price = self.get_decimal_input("Unit Price (₹)")
            unit = self.get_input("Unit", default="Nos")
            
            # GST Rate with AI suggestion
            print("\\n💡 Common GST Rates: 0%, 5%, 12%, 18%, 28%")
            try:
                # Use the default_gst from HSN suggestion if available
                if default_gst:
                    print(f"🤖 Suggested GST Rate: {default_gst}% (based on HSN code)")
                    user_gst = self.get_input(f"GST Rate (%) [Press Enter for {default_gst}%]", required=False)
                    gst_rate = Decimal(str(user_gst)) if user_gst else Decimal(str(default_gst))
                else:
                    raise NameError  # Fall back to manual input
            except (NameError, UnboundLocalError):
                gst_rate = self.get_decimal_input("GST Rate (%)", required=True)
            
            # Optional discount
            discount_type = self.get_input("Discount type (% or amount)? Enter 'p' for %, 'a' for amount, or Enter for no discount", required=False)
            
            discount_percentage = Decimal('0')
            discount_amount = Decimal('0')
            
            if discount_type.lower() == 'p':
                discount_percentage = self.get_decimal_input("Discount Percentage (%)")
            elif discount_type.lower() == 'a':
                discount_amount = self.get_decimal_input("Discount Amount (₹)")
            
            item_data = {
                'description': description,
                'hsn_code': hsn_code,
                'quantity': quantity,
                'unit_price': unit_price,
                'unit': unit,
                'gst_rate': gst_rate,
                'discount_percentage': discount_percentage,
                'discount_amount': discount_amount
            }
            
            items.append(item_data)
            
            # Show running total
            item_obj = InvoiceItem(**item_data)
            print(f"\\n📊 Item Total: ₹{item_obj.total_amount:,.2f} (including GST)")
            
            item_number += 1
        
        if not items:
            print("❌ No items entered!")
            return None
        
        return items
    
    def create_invoice(self):
        """Create invoice with user inputs."""
        print("🧾 INTERACTIVE INVOICE GENERATOR")
        print("=" * 40)
        
        try:
            # Get company information
            company_data = self.get_company_info()
            
            # Get customer information
            customer_data = self.get_customer_info()
            
            # Get invoice items
            items_data = self.get_items_info()
            
            if not items_data:
                return None
            
            # Create objects
            company = Company(**company_data)
            customer = Customer(**customer_data)
            
            # Create items
            items = []
            for item_data in items_data:
                items.append(InvoiceItem(**item_data))
            
            # Create invoice with auto-generated number
            invoice = Invoice(company=company, customer=customer, items=items)
            
            # Override with our auto-generated invoice number
            invoice.invoice_number = self.get_next_invoice_number()
            
            # Save the updated config with new invoice number
            self.save_config()
            
            return invoice
            
        except Exception as e:
            print(f"❌ Error creating invoice: {e}")
            return None
    
    def display_invoice_summary(self, invoice):
        """Display invoice summary."""
        print("\\n" + "=" * 50)
        print("✅ INVOICE CREATED SUCCESSFULLY!")
        print("=" * 50)
        
        print(f"📋 Invoice Number: {invoice.invoice_number}")
        print(f"📅 Date: {invoice.invoice_date}")
        print(f"🏢 Company: {invoice.company.name}")
        print(f"👤 Customer: {invoice.customer.name}")
        print(f"📦 Items: {len(invoice.items)}")
        print(f"🔄 Transaction: {'Interstate (IGST)' if invoice.is_interstate else 'Intrastate (CGST+SGST)'}")
        
        print("\\n💰 AMOUNT BREAKDOWN:")
        print(f"  Gross Amount:   ₹{invoice.total_gross_amount:>10,.2f}")
        print(f"  Total Discount: ₹{invoice.total_discount_amount:>10,.2f}")
        print(f"  Taxable Amount: ₹{invoice.total_taxable_amount:>10,.2f}")
        
        if invoice.is_interstate:
            print(f"  IGST:           ₹{invoice.total_igst_amount:>10,.2f}")
        else:
            print(f"  CGST:           ₹{invoice.total_cgst_amount:>10,.2f}")
            print(f"  SGST:           ₹{invoice.total_sgst_amount:>10,.2f}")
        
        print(f"  Total Tax:      ₹{invoice.total_tax_amount:>10,.2f}")
        print(f"  {'='*20}")
        print(f"  FINAL AMOUNT:   ₹{invoice.total_invoice_amount:>10,.2f}")
        
        print(f"\\n💬 Amount in Words:")
        print(f"   {invoice.total_amount_in_words}")
    
    def generate_files(self, invoice):
        """Generate invoice files."""
        print("\\n📁 Generating invoice files...")
        
        try:
            template_engine = InvoiceTemplate()
            
            # Ensure output directory exists
            os.makedirs("output", exist_ok=True)
            
            # Generate filename with invoice number
            filename = f"invoice_{invoice.invoice_number.replace('-', '_')}"
            html_file = f"output/{filename}.html"
            
            # Generate HTML
            template_engine.save_html_invoice(invoice, html_file)
            print(f"📄 HTML Invoice: {html_file}")
            
            # Try to generate PDF if weasyprint is available
            try:
                pdf_file = f"output/{filename}.pdf"
                template_engine.generate_pdf_invoice(invoice, pdf_file)
                print(f"📑 PDF Invoice: {pdf_file}")
            except ImportError:
                print("💡 Install 'weasyprint' for PDF generation: pip install weasyprint")
            except Exception as e:
                print(f"⚠️  PDF generation failed: {e}")
            
            print("\\n🌐 Open the HTML file in your web browser to view and print!")
            
        except Exception as e:
            print(f"❌ Error generating files: {e}")
    
    def run(self):
        """Run the interactive invoice generator."""
        try:
            invoice = self.create_invoice()
            
            if invoice:
                self.display_invoice_summary(invoice)
                self.generate_files(invoice)
                
                print("\\n🎉 SUCCESS! Your invoice has been generated!")
                print(f"📊 This is invoice number {self.config['last_invoice_number']}")
                
                # Ask if user wants to create another
                another = self.get_input("\\nCreate another invoice? (y/n)", default="n").lower()
                if another == 'y':
                    print("\\n" + "="*50)
                    self.run()
            else:
                print("❌ Invoice creation cancelled.")
                
        except KeyboardInterrupt:
            print("\\n\\n👋 Invoice generation cancelled by user.")
        except Exception as e:
            print(f"\\n❌ Unexpected error: {e}")

def main():
    """Main function."""
    generator = InteractiveInvoiceGenerator()
    generator.run()

if __name__ == "__main__":
    main()
