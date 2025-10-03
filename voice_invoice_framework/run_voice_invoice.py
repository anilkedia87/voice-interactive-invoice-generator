#!/usr/bin/env python3
"""
Voice Invoice Framework - Standalone Runner

Simple entry point that runs the existing working GUI without complex imports.
This ensures the framework works while maintaining the professional structure.
"""

import sys
import os
from pathlib import Path

def main():
    """Run the Voice Invoice application."""
    try:
        print("🚀 Starting Voice Interactive Invoice Generator Framework...")
        print("📦 Framework Version: 1.0.0")
        print("=" * 60)
        
        # Add paths to find our modules
        framework_root = Path(__file__).parent
        project_root = framework_root.parent
        
        # Add both the framework and original project paths
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(framework_root))
        
        # Try to import and run the working GUI
        try:
            from clean_voice_gui import CleanVoiceInvoiceGUI
            print("✅ Imported GUI from original location")
        except ImportError:
            try:
                # Try from the framework location
                sys.path.insert(0, str(framework_root / "voice_invoice" / "gui"))
                from clean_voice_gui import CleanVoiceInvoiceGUI
                print("✅ Imported GUI from framework location")
            except ImportError as e:
                print(f"❌ Could not import GUI: {e}")
                print("📋 Please ensure the GUI file is in the correct location")
                return 1
        
        # Initialize and run the application
        print("🎉 Launching Voice Interactive Invoice Generator...")
        app = CleanVoiceInvoiceGUI()
        app.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
