# 🚀 Quick Start Guide

## Running the Voice Invoice Framework

### Method 1: Standalone Runner (Recommended)
```bash
cd voice_invoice_framework
python3 run_voice_invoice.py
```

### Method 2: Framework Module
```bash
cd voice_invoice_framework
python3 -m voice_invoice_framework.voice_invoice
```

### Method 3: Direct Execution
```bash
./run_voice_invoice.py
```

## Framework Structure Overview

```
voice_invoice_framework/
├── 🎯 run_voice_invoice.py      # Main entry point (use this!)
├── 📦 setup.py                 # Package installation
├── 📋 requirements.txt         # Dependencies
├── 📖 README.md               # Comprehensive documentation
├── ⚖️ LICENSE                 # MIT License
├── 📝 pyproject.toml          # Modern Python packaging
└── voice_invoice/             # Core framework package
    ├── 🏛️ core/               # Application core
    ├── 📊 models/             # Data models  
    ├── ⚙️ services/           # Business logic
    ├── 🖥️ gui/               # User interface
    ├── 📄 templates/          # Invoice templates
    ├── 🔧 utils/              # Utilities
    ├── ⚙️ config/             # Configuration
    ├── 📚 docs/               # Documentation
    ├── 🔬 examples/           # Usage examples
    └── 🧪 tests/              # Unit tests
```

## Key Features Working

✅ **Voice Recognition**: CONFIRM/SKIP commands  
✅ **Modern GUI**: Dark theme, large fonts  
✅ **Invoice Generation**: GST-compliant PDF/HTML  
✅ **Professional Structure**: Clean framework organization  
✅ **Error Handling**: Graceful fallbacks  
✅ **Configuration**: JSON-based settings  

## Installation for Development

```bash
# Clone or navigate to the framework
cd voice_invoice_framework

# Install in development mode
pip install -e .

# Or install from setup.py
pip install .
```

## Quick Test

1. Run: `python3 run_voice_invoice.py`
2. Click "🚀 Start Invoice Creation"  
3. Speak clearly or use text input
4. Use "CONFIRM" and "SKIP" for yes/no questions
5. Generate professional invoices!

🎉 **Enjoy your voice-controlled invoicing framework!**
