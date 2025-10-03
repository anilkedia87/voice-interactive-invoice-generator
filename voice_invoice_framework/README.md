# 🎤 Voice Interactive Invoice Generator Framework

A professional, voice-controlled invoice generation framework with a modern GUI interface. Generate GST-compliant invoices using natural speech commands with beautiful, user-friendly interface.

![Framework Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Features

### 🎙️ Voice Recognition
- **Advanced Speech-to-Text**: Google Speech API with Sphinx fallback
- **Smart Voice Commands**: CONFIRM/SKIP instead of problematic yes/no
- **Ambient Noise Calibration**: Automatic microphone adjustment
- **Retry Logic**: 3-attempt retry system with graceful fallbacks
- **Text Input Fallback**: Manual input when voice recognition fails

### 🖥️ Modern GUI Interface
- **Dark Theme Design**: Professional, eye-friendly interface
- **Large, Readable Fonts**: 12-24pt fonts for accessibility
- **Real-time Conversation**: Live display of voice interactions
- **Responsive Layout**: 1200x800 window with proper scaling
- **Status Indicators**: Clear system status and progress tracking

### 📊 Invoice Generation
- **GST Compliance**: Indian tax system compliant invoicing
- **Professional Templates**: HTML and PDF export options
- **HSN Code Validation**: Automatic HSN code verification
- **Multi-item Support**: Handle multiple products/services
- **Automatic Calculations**: GST, totals, and tax breakdowns

### 🔧 Framework Architecture
- **Modular Design**: Clean separation of concerns
- **Configuration Management**: JSON-based settings and preferences
- **Professional Structure**: Proper Python package organization
- **Extensible**: Easy to add new features and customizations
- **Error Handling**: Comprehensive error management and logging

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/voice-invoice-framework.git
   cd voice-invoice-framework
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python -m voice_invoice_framework.voice_invoice
   ```

   Or using the console script:
   ```bash
   voice-invoice
   ```

### Development Installation
```bash
pip install -e .[dev]
pre-commit install
```

## 🎯 Usage

### Basic Voice Invoice Creation

1. **Start the Application**
   - Click "🚀 Start Invoice Creation"
   - Speak clearly when prompted

2. **Company Information**
   - Provide company name, address, GSTIN
   - Use "CONFIRM" to proceed or "SKIP" to skip fields

3. **Customer Details**
   - Customer name, address, contact information
   - Voice recognition with text fallback

4. **Invoice Items**
   - Product/service description
   - Quantity, price per unit, GST rate
   - Automatic HSN code validation

5. **Generate Invoice**
   - Professional PDF/HTML output
   - GST-compliant formatting
   - Automatic file naming

### Voice Commands

| Command | Purpose |
|---------|---------|
| `CONFIRM` | Proceed with current value |
| `SKIP` | Skip current field |
| Clear speech | Provide information |
| Stop button | End conversation |

## 🏗️ Framework Structure

```
voice_invoice_framework/
├── voice_invoice/
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # Main entry point
│   ├── core/                    # Core application logic
│   │   ├── __init__.py
│   │   ├── application.py       # Main app class
│   │   └── voice_gui.py         # GUI framework base
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── company.py           # Company model
│   │   ├── customer.py          # Customer model
│   │   └── invoice.py           # Invoice model
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── gst_calculator.py    # GST calculations
│   │   ├── hsn_validator.py     # HSN validation
│   │   └── invoice_generator.py # Invoice generation
│   ├── gui/                     # User interface
│   │   ├── __init__.py
│   │   └── clean_voice_gui.py   # Main GUI application
│   ├── templates/               # Invoice templates
│   │   ├── __init__.py
│   │   └── invoice_template.py  # HTML/PDF templates
│   ├── utils/                   # Utilities
│   │   ├── __init__.py
│   │   ├── voice_manager.py     # Voice handling
│   │   └── config_manager.py    # Configuration
│   ├── config/                  # Configuration files
│   ├── docs/                    # Documentation
│   ├── examples/                # Example usage
│   └── tests/                   # Unit tests
├── setup.py                     # Package setup
├── pyproject.toml               # Modern Python packaging
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── LICENSE                      # MIT License
└── .gitignore                   # Git ignore rules
```

## ⚙️ Configuration

The framework uses JSON-based configuration with sensible defaults:

### Voice Settings
```json
{
  "voice": {
    "energy_threshold": 300,
    "pause_threshold": 0.8,
    "timeout": 5,
    "max_attempts": 3,
    "tts_rate": 200,
    "tts_volume": 0.9
  }
}
```

### GUI Settings
```json
{
  "gui": {
    "theme": "dark",
    "window_width": 1200,
    "window_height": 800,
    "font_size": 12
  }
}
```

Configuration files are stored in:
- **Linux/macOS**: `~/.voice_invoice/config/`
- **Windows**: `%USERPROFILE%\\.voice_invoice\\config\\`

## 🔧 Development

### Setting up Development Environment

1. **Clone and install in development mode:**
   ```bash
   git clone https://github.com/yourusername/voice-invoice-framework.git
   cd voice-invoice-framework
   pip install -e .[dev]
   ```

2. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

3. **Run tests:**
   ```bash
   pytest
   ```

### Code Style
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit**: Automated checks

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run the test suite: `pytest`
5. Submit a pull request

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Memory**: 512MB RAM minimum
- **Microphone**: For voice input functionality

### Python Dependencies
```
SpeechRecognition>=3.8.1    # Voice recognition
pyttsx3>=2.90               # Text-to-speech
reportlab>=3.6.0            # PDF generation
Pillow>=8.3.0               # Image processing
tkinter                     # GUI framework (usually included)
```

### Optional Dependencies
```
pyaudio                     # Better audio support
portaudio                   # Audio I/O library
espeak / espeak-ng         # TTS engine (Linux)
```

## 🎨 Screenshots

### Main Interface
*Modern dark theme with professional styling*

### Voice Recognition
*Real-time conversation display with status indicators*

### Invoice Generation
*Professional GST-compliant invoice output*

## 🐛 Troubleshooting

### Common Issues

**Voice Recognition Not Working**
- Check microphone permissions
- Ensure internet connection (for Google Speech API)
- Try the "Test Voice Recognition" button
- Fallback to text input if needed

**Import Errors**
- Install all requirements: `pip install -r requirements.txt`
- Check Python version: `python --version`
- Virtual environment recommended

**GUI Not Starting**
- Ensure Tkinter is installed: `python -m tkinter`
- Check display settings on Linux: `echo $DISPLAY`
- Update graphics drivers

**TTS Errors**
- Install additional TTS engines
- Check audio system permissions
- Try different voice settings

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/voice-invoice-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/voice-invoice-framework/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/voice-invoice-framework/wiki)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SpeechRecognition**: Anthony Zhang for the excellent speech recognition library
- **pyttsx3**: Natesh M Bhat for the cross-platform TTS library
- **ReportLab**: For professional PDF generation capabilities
- **Community**: All contributors and users who help improve this framework

## 🔄 Version History

### v1.0.0 (Current)
- ✅ Complete voice recognition system
- ✅ Modern GUI with dark theme
- ✅ GST-compliant invoice generation
- ✅ Professional framework structure
- ✅ Comprehensive documentation
- ✅ Package distribution ready

### Future Roadmap
- 📱 Web interface support
- 🌍 Multi-language support
- 📊 Advanced reporting features
- 🔌 Plugin system
- ☁️ Cloud integration options

---

**Made with ❤️ for the Python community**

*Professional voice-controlled invoicing has never been this easy!*
