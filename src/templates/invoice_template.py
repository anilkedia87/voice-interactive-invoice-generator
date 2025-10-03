"""
Invoice Template System
Generates HTML and PDF invoices with professional formatting.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import os
from decimal import Decimal

from models import Invoice


class InvoiceTemplate:
    """Service for generating invoice templates."""
    
    def __init__(self):
        self.template_dir = os.path.dirname(__file__)
    
    def generate_html_invoice(self, invoice: Invoice, template_name: str = "standard") -> str:
        """
        Generate HTML invoice from invoice data.
        
        Args:
            invoice: Invoice object
            template_name: Name of the template to use
            
        Returns:
            HTML string of the invoice
        """
        if template_name == "standard":
            return self._generate_standard_html(invoice)
        elif template_name == "modern":
            return self._generate_modern_html(invoice)
        else:
            raise ValueError(f"Unknown template: {template_name}")
    
    def _generate_standard_html(self, invoice: Invoice) -> str:
        """Generate standard HTML invoice template."""
        
        # Get tax summary for display
        tax_summary = invoice.get_tax_summary()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice - {invoice.invoice_number}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
            line-height: 1.4;
        }}
        
        .invoice-container {{
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #ddd;
            padding: 20px;
        }}
        
        .invoice-header {{
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        .invoice-title {{
            font-size: 24px;
            font-weight: bold;
            margin: 0;
            color: #2c3e50;
        }}
        
        .company-details, .customer-details {{
            width: 48%;
            display: inline-block;
            vertical-align: top;
            margin-bottom: 20px;
        }}
        
        .customer-details {{
            text-align: right;
        }}
        
        .details-box {{
            border: 1px solid #ddd;
            padding: 15px;
            background-color: #f9f9f9;
        }}
        
        .section-title {{
            font-weight: bold;
            font-size: 14px;
            color: #2c3e50;
            margin-bottom: 8px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 3px;
        }}
        
        .invoice-info {{
            margin: 20px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
        }}
        
        .invoice-info-item {{
            display: inline-block;
            width: 32%;
            margin-bottom: 5px;
        }}
        
        .items-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .items-table th,
        .items-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        .items-table th {{
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            text-align: center;
        }}
        
        .items-table td.number {{
            text-align: right;
        }}
        
        .items-table td.center {{
            text-align: center;
        }}
        
        .totals-section {{
            float: right;
            width: 300px;
            margin-top: 20px;
        }}
        
        .totals-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .totals-table td {{
            padding: 5px 10px;
            border: 1px solid #ddd;
        }}
        
        .totals-table .label {{
            font-weight: bold;
            background-color: #f8f9fa;
            width: 60%;
        }}
        
        .totals-table .amount {{
            text-align: right;
            width: 40%;
        }}
        
        .total-row {{
            font-weight: bold;
            font-size: 16px;
            background-color: #2c3e50 !important;
            color: white !important;
        }}
        
        .tax-summary {{
            clear: both;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        
        .tax-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        
        .tax-table th,
        .tax-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        
        .tax-table th {{
            background-color: #34495e;
            color: white;
        }}
        
        .amount-in-words {{
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            background-color: #f9f9f9;
        }}
        
        .notes-section {{
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            background-color: #fff3cd;
        }}
        
        .signature-section {{
            margin-top: 40px;
            text-align: right;
        }}
        
        .clearfix {{
            clear: both;
        }}
        
        @media print {{
            body {{
                padding: 0;
            }}
            .invoice-container {{
                border: none;
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="invoice-container">
        <!-- Header -->
        <div class="invoice-header">
            <h1 class="invoice-title">TAX INVOICE</h1>
        </div>
        
        <!-- Company and Customer Details -->
        <div class="company-details">
            <div class="details-box">
                <div class="section-title">BILL FROM:</div>
                <strong>{invoice.company.name}</strong><br>
                {invoice.company.get_full_address()}<br>
                {f'GSTIN: {invoice.company.gstin}<br>' if invoice.company.gstin else ''}
                {f'PAN: {invoice.company.pan}<br>' if invoice.company.pan else ''}
                {f'Phone: {invoice.company.phone}<br>' if invoice.company.phone else ''}
                {f'Email: {invoice.company.email}' if invoice.company.email else ''}
            </div>
        </div>
        
        <div class="customer-details">
            <div class="details-box">
                <div class="section-title">BILL TO:</div>
                <strong>{invoice.customer.name}</strong><br>
                {invoice.customer.get_full_address()}<br>
                {f'GSTIN: {invoice.customer.gstin}<br>' if invoice.customer.gstin else ''}
                {f'Phone: {invoice.customer.phone}<br>' if invoice.customer.phone else ''}
                {f'Email: {invoice.customer.email}' if invoice.customer.email else ''}
            </div>
        </div>
        
        <div class="clearfix"></div>
        
        <!-- Invoice Information -->
        <div class="invoice-info">
            <div class="invoice-info-item">
                <strong>Invoice No:</strong> {invoice.invoice_number}
            </div>
            <div class="invoice-info-item">
                <strong>Invoice Date:</strong> {invoice.invoice_date.strftime('%d-%m-%Y')}
            </div>
            <div class="invoice-info-item">
                <strong>Due Date:</strong> {invoice.due_date.strftime('%d-%m-%Y') if invoice.due_date else 'N/A'}
            </div>
            <div class="invoice-info-item">
                <strong>Place of Supply:</strong> {invoice.place_of_supply}
            </div>
            <div class="invoice-info-item">
                <strong>Transaction Type:</strong> {'Interstate' if invoice.is_interstate else 'Intrastate'}
            </div>
            <div class="invoice-info-item">
                <strong>Reverse Charge:</strong> {'Yes' if invoice.reverse_charge else 'No'}
            </div>
        </div>
        
        <!-- Items Table -->
        <table class="items-table">
            <thead>
                <tr>
                    <th style="width: 5%;">S.No</th>
                    <th style="width: 30%;">Description</th>
                    <th style="width: 10%;">HSN Code</th>
                    <th style="width: 8%;">Qty</th>
                    <th style="width: 8%;">Unit</th>
                    <th style="width: 12%;">Rate (₹)</th>
                    <th style="width: 12%;">Discount (₹)</th>
                    <th style="width: 15%;">Taxable Amount (₹)</th>
                </tr>
            </thead>
            <tbody>
        """
        
        # Add items to the table
        for i, item in enumerate(invoice.items, 1):
            html_content += f"""
                <tr>
                    <td class="center">{i}</td>
                    <td>{item.description}</td>
                    <td class="center">{item.hsn_code}</td>
                    <td class="number">{item.quantity}</td>
                    <td class="center">{item.unit}</td>
                    <td class="number">₹{item.unit_price:,.2f}</td>
                    <td class="number">₹{item.total_discount:,.2f}</td>
                    <td class="number">₹{item.taxable_amount:,.2f}</td>
                </tr>
            """
        
        html_content += """
            </tbody>
        </table>
        
        <!-- Totals Section -->
        <div class="totals-section">
            <table class="totals-table">
        """
        
        # Add totals
        html_content += f"""
                <tr>
                    <td class="label">Gross Amount:</td>
                    <td class="amount">₹{invoice.total_gross_amount:,.2f}</td>
                </tr>
                <tr>
                    <td class="label">Total Discount:</td>
                    <td class="amount">₹{invoice.total_discount_amount:,.2f}</td>
                </tr>
                <tr>
                    <td class="label">Taxable Amount:</td>
                    <td class="amount">₹{invoice.total_taxable_amount:,.2f}</td>
                </tr>
        """
        
        # Add tax lines based on transaction type
        if invoice.is_interstate:
            html_content += f"""
                <tr>
                    <td class="label">IGST:</td>
                    <td class="amount">₹{invoice.total_igst_amount:,.2f}</td>
                </tr>
            """
        else:
            html_content += f"""
                <tr>
                    <td class="label">CGST:</td>
                    <td class="amount">₹{invoice.total_cgst_amount:,.2f}</td>
                </tr>
                <tr>
                    <td class="label">SGST:</td>
                    <td class="amount">₹{invoice.total_sgst_amount:,.2f}</td>
                </tr>
            """
        
        html_content += f"""
                <tr class="total-row">
                    <td class="label">Total Amount:</td>
                    <td class="amount">₹{invoice.total_invoice_amount:,.2f}</td>
                </tr>
            </table>
        </div>
        
        <div class="clearfix"></div>
        
        <!-- Amount in Words -->
        <div class="amount-in-words">
            <strong>Amount in Words:</strong> {invoice.total_amount_in_words}
        </div>
        
        <!-- Tax Summary -->
        <div class="tax-summary">
            <div class="section-title">TAX SUMMARY</div>
            <table class="tax-table">
                <thead>
                    <tr>
                        <th>GST Rate (%)</th>
                        <th>Taxable Amount (₹)</th>
        """
        
        if invoice.is_interstate:
            html_content += "<th>IGST (₹)</th>"
        else:
            html_content += "<th>CGST (₹)</th><th>SGST (₹)</th>"
        
        html_content += """
                        <th>Total Tax (₹)</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add tax summary rows
        for rate, summary in tax_summary.items():
            html_content += f"""
                    <tr>
                        <td>{rate}%</td>
                        <td>₹{summary['taxable_amount']:,.2f}</td>
            """
            
            if invoice.is_interstate:
                html_content += f"<td>₹{summary['igst_amount']:,.2f}</td>"
            else:
                html_content += f"<td>₹{summary['cgst_amount']:,.2f}</td>"
                html_content += f"<td>₹{summary['sgst_amount']:,.2f}</td>"
            
            html_content += f"""
                        <td>₹{summary['total_tax']:,.2f}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </div>
        """
        
        # Add notes if present
        if invoice.notes:
            html_content += f"""
        <div class="notes-section">
            <div class="section-title">NOTES</div>
            {invoice.notes}
        </div>
            """
        
        # Add terms and conditions if present
        if invoice.terms_and_conditions:
            html_content += f"""
        <div class="notes-section">
            <div class="section-title">TERMS AND CONDITIONS</div>
            {invoice.terms_and_conditions}
        </div>
            """
        
        # Add bank details if available
        if invoice.company.bank_name or invoice.company.bank_account:
            html_content += f"""
        <div class="notes-section">
            <div class="section-title">BANK DETAILS</div>
            {f'Bank Name: {invoice.company.bank_name}<br>' if invoice.company.bank_name else ''}
            {f'Account Number: {invoice.company.bank_account}<br>' if invoice.company.bank_account else ''}
            {f'IFSC Code: {invoice.company.ifsc_code}' if invoice.company.ifsc_code else ''}
        </div>
            """
        
        html_content += f"""
        <!-- Signature Section -->
        <div class="signature-section">
            <br><br>
            <strong>For {invoice.company.name}</strong><br><br><br>
            _________________________<br>
            Authorized Signatory
        </div>
        
        <div style="margin-top: 20px; text-align: center; font-size: 10px; color: #666;">
            This is a computer-generated invoice and does not require a physical signature.
        </div>
    </div>
</body>
</html>
        """
        
        return html_content.strip()
    
    def _generate_modern_html(self, invoice: Invoice) -> str:
        """Generate modern HTML invoice template with enhanced styling."""
        # This would contain a more modern template design
        # For brevity, returning the standard template for now
        return self._generate_standard_html(invoice)
    
    def save_html_invoice(self, invoice: Invoice, output_path: str, template_name: str = "standard") -> str:
        """
        Save HTML invoice to file.
        
        Args:
            invoice: Invoice object
            output_path: Path to save the HTML file
            template_name: Template to use
            
        Returns:
            Path of the saved file
        """
        html_content = self.generate_html_invoice(invoice, template_name)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_pdf_invoice(self, invoice: Invoice, output_path: str, template_name: str = "standard") -> str:
        """
        Generate PDF invoice (requires weasyprint or similar library).
        
        Args:
            invoice: Invoice object
            output_path: Path to save the PDF file
            template_name: Template to use
            
        Returns:
            Path of the saved PDF file
        """
        try:
            from weasyprint import HTML, CSS
            
            html_content = self.generate_html_invoice(invoice, template_name)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(output_path)
            
            return output_path
            
        except ImportError:
            raise ImportError("weasyprint is required for PDF generation. Install with: pip install weasyprint")
        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")
    
    def get_available_templates(self) -> list:
        """Get list of available templates."""
        return ["standard", "modern"]
