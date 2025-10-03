# 🧾 GST Invoice System - User Guide

## 🚀 Quick Start
Run the interactive invoice generator:
```bash
python3 interactive_invoice.py
```

## 💰 GST Calculation Logic

### ✅ **Intrastate Transaction (Same State)**
- **When:** Company and customer are in the same state
- **GST Type:** CGST + SGST  
- **Example:** Both in Odisha → 5% GST = 2.5% CGST + 2.5% SGST

### ✅ **Interstate Transaction (Different States)**
- **When:** Company and customer are in different states
- **GST Type:** IGST
- **Example:** Company in Odisha, Customer in West Bengal → 5% IGST

## 📋 **Auto-Incrementing Invoice Numbers**

The system automatically:
- ✅ Tracks the last invoice number in `invoice_config.json`
- ✅ Increments by 1 for each new invoice
- ✅ Uses format: `INV-0001`, `INV-0002`, `INV-0003`, etc.
- ✅ Saves your company info for reuse

## 🏢 **Company Information Storage**

First time setup saves:
- Company details
- Bank information  
- GST registration
- Contact information

Subsequent invoices ask: "Use saved company info? (y/n)"

## 📦 **Common HSN/SAC Codes**

| Code | Description | Typical GST |
|------|-------------|-------------|
| 6109 | T-shirts, Shirts, Garments | 5% or 12% |
| 8471 | Computers, Laptops | 18% |
| 8517 | Mobile Phones | 18% |
| 998342 | IT Services | 18% |
| 998341 | Software Services | 18% |
| 9999 | General/Other items | Variable |

## 💡 **GST Rate Guidelines**

| Rate | Common Items |
|------|--------------|
| 0% | Basic food items, books |
| 5% | Essential items, sugar, tea |
| 12% | Computers, processed foods |
| 18% | Most goods and services |
| 28% | Luxury items, automobiles |

## 📄 **Generated Files**

Each invoice creates:
- `output/invoice_INV_XXXX.html` - Professional HTML invoice
- Automatic backup of invoice numbers
- Company info saved for reuse

## 🎯 **Key Features**

✅ **Smart State Detection:** Automatically determines CGST+SGST vs IGST  
✅ **Auto-Increment:** Invoice numbers increase automatically  
✅ **Company Memory:** Remembers your business details  
✅ **Multi-Item Support:** Add multiple products/services  
✅ **Discount Handling:** Percentage or fixed amount discounts  
✅ **Professional Output:** Tax-compliant invoice format  
✅ **Amount in Words:** Indian currency format conversion

---

**🧾 Ready to create professional GST invoices! Run `python3 interactive_invoice.py` to start! ✨**
