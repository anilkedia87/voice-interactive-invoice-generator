"""
Voice Interactive Invoice Generator Framework

A professional framework for voice-controlled invoice generation with modern GUI.

Main Entry Point:
    Run this module to start the Voice Invoice application.
    
Example:
    python -m voice_invoice_framework.voice_invoice
    
Features:
    - Voice recognition and text-to-speech
    - Modern dark theme GUI interface  
    - GST-compliant Indian invoice generation
    - Professional PDF and HTML export
    - Configurable settings and preferences
"""

import sys
import os
from pathlib import Path

# Add the framework to Python path
framework_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(framework_root))

def main():
    """Main entry point for the Voice Invoice application."""
    try:
        from voice_invoice_framework.voice_invoice.core.application import VoiceInvoiceApp
        
        print("🚀 Starting Voice Interactive Invoice Generator...")
        print("📦 Framework Version: 1.0.0")
        print("=" * 60)
        
        app = VoiceInvoiceApp()
        app.run()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("📋 Please ensure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
