"""
GUI Module

User interface components for the Voice Invoice Framework.
"""

# Import main GUI classes
try:
    from .clean_voice_gui import CleanVoiceInvoiceGUI
    __all__ = ['CleanVoiceInvoiceGUI']
except ImportError:
    # Graceful handling if GUI components are not available
    __all__ = []
