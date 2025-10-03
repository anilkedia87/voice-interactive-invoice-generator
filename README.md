# 🎤 Voice Interactive Invoice Generator

A modern, beautiful GUI application that creates professional GST invoices using voice commands. Built with Python and Tkinter, featuring speech recognition, text-to-speech capabilities, and a stunning dark theme interface.

## ✨ Features

- **🤖 AI-Powered Interface**: Intelligent invoice generation with auto-suggestions
- **💰 GST Compliance**: Handles CGST, SGST, IGST calculations automatically
- **📊 HSN Code Support**: Built-in HSN code database with validation
- **🎨 Professional Templates**: Generate HTML and PDF invoices
- **⚡ Quick Invoice**: Create invoices with minimal inputs
- **🔍 Smart Validation**: Comprehensive data validation with helpful suggestions
- **💡 Auto-Suggestions**: Automatic HSN code and GST rate suggestions
- **🌐 Interstate Detection**: Automatic detection of interstate vs intrastate transactions

## 🚀 Quick Start

### Installation

1. Clone or download this repository
2. Install Python 3.7 or higher
3. Install requirements:

```bash
pip install -r requirements.txt
```

### Basic Usage

#### Option 1: Run the Demo
```bash
python3 demo.py
```
This will generate a sample invoice to test the system.

#### Option 2: Create Your Own Invoice
1. Edit `create_invoice.py` with your business details
2. Run it:
```bash
python3 create_invoice.py
```

#### Option 3: Use in Your Code
```python
import sys
import os
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.company import Company
from models.customer import Customer  
from models.invoice import Invoice, InvoiceItem
from templates.invoice_template import InvoiceTemplate

# Create company
company = Company(
    name="Your Company Pvt Ltd",
    address="123 Business Street", 
    city="Mumbai",
    state="Maharashtra",
    pincode="400001",
    gstin="27AABCS1234C1ZS"
)

# Create customer
customer = Customer(
    name="Customer Name",
    address="Customer Address",
    city="Delhi", 
    state="Delhi",
    pincode="110001"
)

# Create items
item = InvoiceItem(
    description="Website Development",
    hsn_code="998342",
    quantity=Decimal('1'),
    unit_price=Decimal('50000'), 
    gst_rate=Decimal('18')
)

# Create and generate invoice
invoice = Invoice(company=company, customer=customer, items=[item])
template = InvoiceTemplate()
template.save_html_invoice(invoice, "my_invoice.html")
```

## 📁 Project Structure

```
invoice_automation/
├── src/
│   ├── models/          # Data models (Invoice, Company, Customer, etc.)
│   ├── services/        # Business logic (GST calculations, validation)
│   ├── templates/       # Invoice templates (HTML/PDF generation)
│   └── ai_agent.py      # Main AI Agent interface
├── examples/
│   ├── basic_example.py      # Simple invoice creation
│   ├── quick_example.py      # Quick invoice demo
│   └── interactive_example.py # Interactive CLI tool
├── output/              # Generated invoices will be saved here
└── requirements.txt
```

## 🎯 Examples

### 1. Run Demo
```bash
python3 demo.py
```

### 2. Create Your Invoice  
```bash
python3 create_invoice.py
```

### 3. Create Multiple Items Invoice

```python
from src.ai_agent import InvoiceAIAgent

agent = InvoiceAIAgent()
# ... set company info ...

items = [
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

customer_info = {
    'name': 'Customer Name',
    'address': 'Customer Address',
    'city': 'Delhi',
    'state': 'Delhi',
    'pincode': '110001',
    'gstin': '07AABCC1234D1ZF'
}

invoice = agent.create_invoice_from_items(items, customer_info)
```

## 🧮 GST Calculation Features

### Automatic GST Type Detection
- **Intrastate**: CGST + SGST (when company and customer are in same state)
- **Interstate**: IGST (when company and customer are in different states)

### Supported GST Rates
- 0% (Exempt items)
- 3% (Precious metals)
- 5% (Essential items)
- 12% (Processed foods, computers)
- 18% (Most goods and services)
- 28% (Luxury items, automobiles)

### HSN Code Database
Built-in database includes:
- Electronics (8471, 8517, 8528)
- Textiles (6109, 6203, 6204)  
- Services (998341, 998342, 998343)
- Food items (1001, 1006, 1701)
- And many more...

## 📋 Invoice Features

### Professional Invoice Layout
- Company and customer details
- Itemized billing with HSN codes
- GST breakdown by rate
- Amount in words (Indian format)
- Tax summary table
- Terms and conditions
- Digital signature section

### Supported Formats
- **HTML**: Always available, great for viewing and printing
- **PDF**: Requires weasyprint library installation

## 🔧 Advanced Features

### Data Validation
```python
# Validate complete invoice data
validation_result = agent.validate_invoice_data(invoice_data)
print(validation_result['errors'])      # List of validation errors
print(validation_result['suggestions']) # Intelligent suggestions
```

### HSN Code Search
```python
# Search for HSN codes
results = agent.search_hsn_codes("laptop")
for result in results:
    print(f"HSN: {result['hsn_code']} - {result['description']}")
```

### Calculate Totals Only
```python
# Calculate totals without creating full invoice
totals = agent.calculate_invoice_totals(items, is_interstate=False)
print(f"Total Amount: ₹{totals['total_amount']}")
```

## 💡 Tips and Best Practices

### 1. HSN Code Selection
- Use 4-digit codes for broader categories
- Use 6 or 8-digit codes for specific items
- Services typically use SAC codes (6 digits starting with 99)

### 2. GST Rate Guidelines
- Check current GST rates as they may change
- Use the built-in suggestions for common items
- Validate rates with your CA for complex scenarios

### 3. GSTIN Validation
- Always validate GSTIN format (15 characters)
- First 2 digits represent state code
- System automatically detects interstate transactions

### 4. Discount Handling
- Supports both percentage and fixed amount discounts
- Discounts are applied before GST calculation
- Multiple discount types can be combined

## 🛠️ Customization

### Adding Custom HSN Codes
```python
from src.services import HSNValidator

HSNValidator.add_custom_hsn(
    hsn_code="1234",
    description="Custom Item",
    typical_gst=18
)
```

### Custom Invoice Templates
The template system is extensible. You can create custom HTML templates by modifying the `InvoiceTemplate` class.

## 📄 PDF Generation Setup

For PDF generation, install weasyprint:

```bash
# On Ubuntu/Debian
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
pip install weasyprint

# On macOS
brew install python3 pango libffi
pip install weasyprint

# Then uncomment weasyprint in requirements.txt
```

## ⚖️ Legal Compliance

This system is designed to help create GST-compliant invoices for Indian businesses. However:

- Always consult with your Chartered Accountant for complex scenarios
- Verify GST rates as they may change over time
- Ensure proper business registration and compliance
- This tool assists with invoice generation but doesn't provide legal advice

## 🤝 Contributing

This is a complete invoice automation system. You can extend it by:

1. Adding more HSN codes to the database
2. Creating new invoice templates
3. Adding support for additional tax types
4. Improving the AI suggestions
5. Adding more export formats

## 📞 Support

For questions about GST compliance, consult with a qualified Chartered Accountant or tax professional.

## 📝 License

This project is provided as-is for educational and business purposes. Use at your own discretion and ensure compliance with local tax laws.

---

**Happy Invoicing! 🧾✨**
