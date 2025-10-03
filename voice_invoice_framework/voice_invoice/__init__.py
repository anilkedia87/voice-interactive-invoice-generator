"""
Voice Interactive Invoice Generator Framework

A modern, extensible framework for creating professional GST invoices using voice commands.
Built with Python, featuring speech recognition, text-to-speech, and beautiful GUI interface.

Author: Anil Kedia
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Anil Kedia"
__email__ = "anil@example.com"
__license__ = "MIT"

from .core.application import VoiceInvoiceApp
from .models.invoice import Invoice, InvoiceItem
from .models.company import Company
from .models.customer import Customer

__all__ = [
    'VoiceInvoiceApp',
    'Invoice',
    'InvoiceItem', 
    'Company',
    'Customer'
]
