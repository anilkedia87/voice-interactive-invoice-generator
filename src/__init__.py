"""
Main package initialization for Invoice Automation System.
"""

from .models import Invoice, InvoiceItem, Company, Customer
from .services import GSTCalculator, InvoiceGenerator, HSNValidator
from .templates import InvoiceTemplate
from .ai_agent import InvoiceAIAgent

__version__ = "1.0.0"
__author__ = "Invoice Automation System"

__all__ = [
    'Invoice', 'InvoiceItem', 'Company', 'Customer',
    'GSTCalculator', 'InvoiceGenerator', 'HSNValidator',
    'InvoiceTemplate', 'InvoiceAIAgent'
]
