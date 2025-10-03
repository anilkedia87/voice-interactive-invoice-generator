"""
Setup Configuration for Voice Invoice Framework

Professional Python package setup with all necessary metadata and dependencies.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="voice-invoice-framework",
    version="1.0.0",
    author="Voice Invoice Team",
    author_email="contact@voiceinvoice.dev",
    description="Professional voice-controlled invoice generation framework with modern GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/voice-invoice-framework",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/voice-invoice-framework/issues",
        "Source": "https://github.com/yourusername/voice-invoice-framework",
        "Documentation": "https://github.com/yourusername/voice-invoice-framework/wiki",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: GTK",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "voice-invoice=voice_invoice_framework.voice_invoice.__main__:main",
        ],
    },
    package_data={
        "voice_invoice_framework": [
            "voice_invoice/templates/*.html",
            "voice_invoice/templates/*.css",
            "voice_invoice/config/*.json",
            "voice_invoice/docs/*.md",
            "*.md",
            "*.txt",
            "*.yml",
            "*.yaml",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "invoice",
        "voice-recognition", 
        "speech-to-text",
        "text-to-speech",
        "gst",
        "billing",
        "accounting",
        "gui",
        "tkinter",
        "automation",
        "business",
        "framework",
    ],
)
