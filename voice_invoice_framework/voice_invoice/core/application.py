"""
Core Application Module

Main application entry point and framework initialization.
"""

import sys
from pathlib import Path

class VoiceInvoiceApp:
    """
    Main application class for the Voice Interactive Invoice Generator.
    
    This class serves as the entry point for the framework and handles
    application initialization, configuration, and lifecycle management.
    """
    
    def __init__(self, config=None):
        """
        Initialize the Voice Invoice Application.
        
        Args:
            config (dict, optional): Application configuration parameters
        """
        self.config = config or {}
        self.gui = None
        
    def run(self):
        """
        Start the Voice Invoice Application GUI.
        """
        try:
            # Import the working GUI from the framework
            sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))
            from clean_voice_gui import CleanVoiceInvoiceGUI
            self.gui = CleanVoiceInvoiceGUI()
            self.gui.run()
        except ImportError:
            # Fallback to the original location
            sys.path.insert(0, "/Users/anil/invoice_automation")
            from clean_voice_gui import CleanVoiceInvoiceGUI
            self.gui = CleanVoiceInvoiceGUI()
            self.gui.run()
        
    def get_version(self):
        """Get the framework version."""
        return "1.0.0"
