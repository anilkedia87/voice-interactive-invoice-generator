#!/usr/bin/env python3
"""
Clean Voice Invoice GUI - Professional Voice-Controlled Invoice Generator

A comprehensive voice-interactive GUI for generating GST-compliant invoices.
Features modern dark theme, robust voice recognition, and professional output.

Author: Anil Kedia
GitHub: @anilkedia87
Repository: voice-interactive-invoice-generator
Project: Voice Interactive Invoice Generator Framework v1.0.0
"""

import sys
import os
import json
import time
from decimal import Decimal
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import os
import json
from decimal import Decimal
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.invoice import Company, Customer, Invoice, InvoiceItem
from services.gst_calculator import GSTCalculator
from services.hsn_validator import HSNValidator
from services.invoice_generator import InvoiceGenerator
from templates.invoice_template import InvoiceTemplate

# Voice dependencies - gracefully handle if not installed
VOICE_AVAILABLE = True
try:
    import speech_recognition as sr
    import pyttsx3
except ImportError:
    VOICE_AVAILABLE = False


class CleanVoiceInvoiceGUI:
    def __init__(self):
        self.config_file = "invoice_config.json"
        self.load_config()
        self.hsn_validator = HSNValidator()
        
        # Control variables
        self.is_listening = False
        self.conversation_active = False
        self.max_retry_attempts = 2
        self.tts_engine = None  # Initialize as None
        
        # Initialize GUI
        self.setup_gui()
        
        if VOICE_AVAILABLE:
            self.setup_voice()
        else:
            self.log_message("⚠️ Voice features not available", "warning")
    
    def setup_gui(self):
        """Initialize the GUI interface."""
        self.root = tk.Tk()
        self.root.title("🎤 Voice Interactive Invoice Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')  # Dark blue-gray background
        
        # Configure modern styling
        self.root.tk_setPalette(background='#34495e', foreground='white', 
                               activeBackground='#3498db', activeForeground='white')
        
        # Main frame with modern styling
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
                # Title with gradient-like styling
        title_frame = tk.Frame(main_frame, bg='#3498db', relief='raised', bd=3)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 25))
        
        title_label = tk.Label(title_frame, text="🎤 Voice Interactive Invoice Generator", 
                              font=('Helvetica', 24, 'bold'), bg='#3498db', fg='white',
                              pady=15)
        title_label.pack(fill=tk.X)
        
        # Status frame with modern design
        status_frame = tk.LabelFrame(main_frame, text="📊 System Status", 
                                    font=('Helvetica', 12, 'bold'), fg='#ecf0f1', bg='#34495e',
                                    relief='groove', bd=2, padx=15, pady=10)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.status_label = tk.Label(status_frame, text="✅ Ready to start", 
                                    font=('Helvetica', 14, 'bold'), fg='#2ecc71', bg='#34495e')
        self.status_label.pack(pady=5)
        
        # Messages frame with modern design
        messages_frame = tk.LabelFrame(main_frame, text="💬 Voice Conversation", 
                                      font=('Helvetica', 12, 'bold'), fg='#ecf0f1', bg='#34495e',
                                      relief='groove', bd=2, padx=15, pady=10)
        messages_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Scrolled text for messages with modern styling
        self.message_display = scrolledtext.ScrolledText(
            messages_frame, 
            width=85, 
            height=22,
            font=('Consolas', 12),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#2c3e50',  # Dark background
            fg='#ecf0f1',  # Light text
            insertbackground='#3498db',  # Cursor color
            selectbackground='#3498db',  # Selection background
            relief='sunken',
            bd=2
        )
        self.message_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags for different message types with modern colors
        self.message_display.tag_configure("assistant", foreground="#3498db", font=('Consolas', 12, 'bold'))  # Blue
        self.message_display.tag_configure("user", foreground="#2ecc71", font=('Consolas', 12, 'bold'))       # Green
        self.message_display.tag_configure("error", foreground="#e74c3c", font=('Consolas', 12, 'bold'))      # Red
        self.message_display.tag_configure("warning", foreground="#f39c12", font=('Consolas', 12, 'bold'))    # Orange
        self.message_display.tag_configure("success", foreground="#27ae60", font=('Consolas', 12, 'bold'))    # Dark Green
        self.message_display.tag_configure("normal", foreground="#ecf0f1", font=('Consolas', 12))             # Light Gray
        
        # Control frame with modern styling
        control_frame = tk.Frame(main_frame, bg='#2c3e50')
        control_frame.grid(row=3, column=0, columnspan=2, pady=(15, 0))
        
                # Modern gradient-style buttons
        button_style = {
            'font': ('Helvetica', 12, 'bold'), 
            'width': 22, 
            'height': 2,
            'relief': 'flat',
            'bd': 0,
            'cursor': 'hand2'
        }
        
        self.start_btn = tk.Button(control_frame, text="🚀 Start Invoice Creation", 
                                  command=self.start_invoice_creation, **button_style,
                                  bg='#27ae60', fg='white', activebackground='#2ecc71')
        self.start_btn.grid(row=0, column=0, padx=10, pady=10)
        
        self.stop_btn = tk.Button(control_frame, text="🛑 Stop Conversation", 
                                 command=self.stop_conversation, **button_style,
                                 bg='#e74c3c', fg='white', activebackground='#ec7063',
                                 state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=10, pady=10)
        
        self.test_voice_btn = tk.Button(control_frame, text="🎤 Test Voice Recognition", 
                                       command=self.test_voice, **button_style,
                                       bg='#3498db', fg='white', activebackground='#5dade2')
        self.test_voice_btn.grid(row=0, column=2, padx=10, pady=10)
        
        self.clear_btn = tk.Button(control_frame, text="🗑️ Clear Messages", 
                                  command=self.clear_messages, **button_style,
                                  bg='#e67e22', fg='white', activebackground='#f39c12')
        self.clear_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Text input for fallback with modern design
        input_frame = tk.LabelFrame(main_frame, text="⌨️  Text Input (Fallback)", 
                                   font=('Helvetica', 11, 'bold'), fg='#ecf0f1', bg='#34495e',
                                   relief='groove', bd=2, padx=15, pady=10)
        input_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        # Create input container
        input_container = tk.Frame(input_frame, bg='#34495e')
        input_container.pack(fill=tk.X, pady=5)
        
        self.text_input = tk.Entry(input_container, font=('Consolas', 12), 
                                  bg='#2c3e50', fg='#ecf0f1', insertbackground='#3498db',
                                  relief='sunken', bd=2, width=70)
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.text_input.bind('<Return>', self.on_text_input)
        
        self.send_btn = tk.Button(input_container, text="📤 Send", command=self.on_text_input,
                                 font=('Helvetica', 11, 'bold'), bg='#16a085', fg='white',
                                 relief='flat', bd=0, width=12, cursor='hand2',
                                 activebackground='#1abc9c')
        self.send_btn.pack(side=tk.RIGHT)
        
        # Add footer
        footer_frame = tk.Frame(main_frame, bg='#2c3e50')
        footer_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        footer_label = tk.Label(footer_frame, 
                               text="💡 Tip: Speak clearly and wait for prompts. Use CONFIRM/SKIP for yes/no questions.",
                               font=('Helvetica', 10, 'italic'), fg='#bdc3c7', bg='#2c3e50')
        footer_label.pack(pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Messages frame should expand
        
        # Variables for conversation state
        self.waiting_for_input = False
        self.current_response = None
        self.stop_requested = False
    
    def setup_voice(self):
        """Initialize voice recognition and text-to-speech safely."""
        try:
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            
            # Optimized settings for single word recognition
            self.recognizer.energy_threshold = 200  # Lower for better sensitivity
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.6  # Shorter pause for single words
            self.recognizer.phrase_threshold = 0.2  # Lower for single words
            self.recognizer.non_speaking_duration = 0.4  # Shorter for single words
            
            self.microphone = sr.Microphone()
            
            # Initialize TTS safely
            try:
                self.tts_engine = pyttsx3.init()
                self.setup_female_voice_safe()
            except Exception as e:
                self.log_message("⚠️ TTS not available - text only mode", "warning")
                self.tts_engine = None
            
            # Calibrate microphone
            self.log_message("🎤 Calibrating microphone (be quiet for 2 seconds)...", "assistant")
            self.update_status("Calibrating microphone...")
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            self.log_message("✅ Voice setup completed!", "success")
            self.update_status("Voice ready")
            
        except Exception as e:
            self.log_message(f"❌ Voice setup failed: {str(e)}", "error")
            self.update_status("Voice setup failed")
    
    def setup_female_voice_safe(self):
        """Configure female voice safely without run loop errors."""
        if not self.tts_engine:
            return
            
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Search for female voices
                for voice in voices:
                    if any(keyword in voice.name.lower() for keyword in ['female', 'samantha', 'zira']):
                        self.tts_engine.setProperty('voice', voice.id)
                        self.log_message(f"🗣️ Using female voice: {voice.name}", "success")
                        break
            
            # Set speech parameters
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.7)
            
        except Exception:
            # If any error, disable TTS
            self.tts_engine = None
    
    def speak_safe(self, text):
        """Speak text safely without run loop errors."""
        def speak_worker():
            try:
                if self.tts_engine and not self.stop_requested:
                    # Create a new engine instance for each speech to avoid conflicts
                    temp_engine = pyttsx3.init()
                    temp_engine.setProperty('rate', 150)
                    temp_engine.setProperty('volume', 0.7)
                    temp_engine.say(text)
                    temp_engine.runAndWait()
                    del temp_engine  # Clean up
            except Exception:
                pass  # Silently handle any TTS errors
        
        if VOICE_AVAILABLE:
            thread = threading.Thread(target=speak_worker, daemon=True)
            thread.start()
    
    def speak_and_wait(self, text, wait_seconds=2):
        """Speak text and wait for completion before continuing."""
        if not VOICE_AVAILABLE or self.stop_requested:
            return
        
        try:
            # Create a new engine instance for each speech to avoid conflicts
            temp_engine = pyttsx3.init()
            
            # Try to find a female voice
            voices = temp_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if any(keyword in voice_name for keyword in ['female', 'zira', 'samantha', 'kate', 'hazel']):
                        temp_engine.setProperty('voice', voice.id)
                        break
            
            temp_engine.setProperty('rate', 140)  # Slightly slower for clarity
            temp_engine.setProperty('volume', 0.9)
            
            temp_engine.say(text)
            temp_engine.runAndWait()
            
            del temp_engine  # Clean up
            
            # Wait a bit after speaking before listening
            time.sleep(wait_seconds)
            
        except Exception:
            # If TTS fails, just wait a moment
            time.sleep(1)
    
    def log_message(self, message, msg_type="normal"):
        """Add a message to the display."""
        try:
            self.message_display.configure(state=tk.NORMAL)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if msg_type == "assistant":
                prefix = "🤖 Assistant: "
                tag = "assistant"
            elif msg_type == "user":
                prefix = "👤 You: "
                tag = "user"
            elif msg_type == "error":
                prefix = "❌ Error: "
                tag = "error"
            elif msg_type == "warning":
                prefix = "⚠️ Warning: "
                tag = "warning"
            elif msg_type == "success":
                prefix = "✅ Success: "
                tag = "success"
            else:
                prefix = ""
                tag = "normal"
            
            formatted_message = f"[{timestamp}] {prefix}{message}\n"
            
            self.message_display.insert(tk.END, formatted_message, tag)
            self.message_display.configure(state=tk.DISABLED)
            self.message_display.see(tk.END)
            self.root.update_idletasks()
            
            # Speak assistant messages safely
            if msg_type == "assistant":
                self.speak_safe(message)
                
        except Exception as e:
            print(f"Error logging message: {e}")
    
    def update_status(self, status_text, color="black"):
        """Update the status label with modern colors."""
        try:
            # Map colors to modern palette
            color_map = {
                "black": "#ecf0f1",
                "green": "#2ecc71", 
                "blue": "#3498db",
                "orange": "#f39c12",
                "red": "#e74c3c"
            }
            final_color = color_map.get(color, color)
            self.status_label.config(text=f"🔄 {status_text}", fg=final_color)
            self.root.update_idletasks()
        except:
            pass
    
    def clear_messages(self):
        """Clear all messages from the display."""
        self.message_display.configure(state=tk.NORMAL)
        self.message_display.delete(1.0, tk.END)
        self.message_display.configure(state=tk.DISABLED)
    
    def stop_conversation(self):
        """Stop the current conversation."""
        self.stop_requested = True
        self.conversation_active = False
        self.waiting_for_input = False
        self.is_listening = False
        self.update_status("Stopped", "red")
        self.start_btn.config(state="normal", bg='#27ae60')
        self.stop_btn.config(state="disabled", bg='#7f8c8d')
        self.log_message("🛑 Conversation stopped", "warning")
    
    def on_text_input(self, event=None):
        """Handle text input."""
        text = self.text_input.get().strip()
        if text and self.waiting_for_input:
            self.log_message(text, "user")
            self.current_response = text
            self.text_input.delete(0, tk.END)
            self.waiting_for_input = False
    
    def get_voice_input(self, prompt, timeout=15):
        """Get voice input with improved error handling."""
        if not VOICE_AVAILABLE or self.stop_requested:
            return self.get_text_input(prompt)
        
        # First speak the question, then display it
        self.speak_and_wait(prompt)
        self.log_message(prompt, "assistant")
        
        if self.is_listening:
            return self.get_text_input("Please use text input (voice is busy)")
        
        self.is_listening = True
        
        try:
            for attempt in range(self.max_retry_attempts):
                if self.stop_requested:
                    return None
                
                self.update_status("🎤 Listening... (speak clearly)", "blue")
                
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(
                            source, 
                            timeout=timeout, 
                            phrase_time_limit=10
                        )
                    
                    self.update_status("🤔 Processing...", "orange")
                    
                    try:
                        text = self.recognizer.recognize_google(audio, language='en-US')
                        text = text.strip()
                        
                        if text:
                            self.log_message(text, "user")
                            self.update_status("✅ Voice recognized", "green")
                            return text
                        
                    except sr.RequestError:
                        try:
                            text = self.recognizer.recognize_sphinx(audio)
                            text = text.strip()
                            if text:
                                self.log_message(f"{text} (offline)", "user")
                                return text
                        except:
                            pass
                        
                except sr.WaitTimeoutError:
                    if attempt == 0:
                        self.log_message("⏰ No speech detected, trying again...", "warning")
                    else:
                        self.log_message("⏰ Still no speech detected", "warning")
                    
                except sr.UnknownValueError:
                    self.log_message("🤔 Couldn't understand that clearly", "warning")
                    
                except Exception as e:
                    self.log_message(f"❌ Recognition error: {str(e)}", "error")
                    break
                
                if attempt < self.max_retry_attempts - 1:
                    self.log_message("Please speak louder or use text input below", "assistant")
                    time.sleep(1)
        
        finally:
            self.is_listening = False
        
        # Fall back to text input
        self.update_status("Please use text input", "orange")
        self.log_message("🖊️ Please type your response in the text box below:", "assistant")
        return self.get_text_input("")
    
    def get_text_input(self, prompt):
        """Get text input from the GUI."""
        if prompt:
            self.log_message(prompt, "assistant")
        
        self.waiting_for_input = True
        self.current_response = None
        self.text_input.focus_set()
        
        start_time = time.time()
        timeout = 60
        
        while self.waiting_for_input and not self.stop_requested:
            self.root.update()
            
            if self.current_response is not None:
                return self.current_response
            
            if time.time() - start_time > timeout:
                self.log_message("⏰ Input timeout", "warning")
                self.waiting_for_input = False
                return ""
            
            time.sleep(0.1)
        
        return self.current_response or ""
    
    def get_numbered_choice(self, question, options, default_choice=0):
        """Get choice using numbers (more reliable than words)."""
        max_attempts = 3
        
        # Build the prompt with numbered options
        options_text = ""
        for i, option in enumerate(options, 1):
            options_text += f" Say '{i}' for {option}."
        
        for attempt in range(max_attempts):
            if self.stop_requested:
                return default_choice
            
            prompt = f"{question}{options_text}"
            response = self.get_voice_input(prompt, timeout=10)
            
            if not response:
                if attempt < max_attempts - 1:
                    self.speak_and_wait("I didn't hear you. Let me try again.", 1)
                continue
            
            response_clean = response.lower().strip()
            
            # Check for number responses
            number_words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
            
            for i in range(1, len(options) + 1):
                if str(i) in response_clean or number_words[i-1] in response_clean:
                    self.log_message(f"Selected: {options[i-1]} ({i})", "user")
                    return i - 1  # Return 0-based index
            
            # Check for quit patterns
            if any(pattern in response_clean for pattern in ['quit', 'exit', 'stop', 'cancel', 'end']):
                self.stop_conversation()
                return default_choice
            
            # If still not recognized, provide feedback
            if attempt < max_attempts - 1:
                valid_numbers = ", ".join([f"'{i}'" for i in range(1, len(options) + 1)])
                self.speak_and_wait(f"I heard '{response}'. Please say {valid_numbers}.", 1)
                self.log_message(f"Unrecognized: '{response}'. Say {valid_numbers}", "assistant")
        
        self.speak_and_wait(f"I'll use the default option: {options[default_choice]}", 1)
        self.log_message(f"Defaulting to: {options[default_choice]}", "assistant")
        return default_choice

    def get_yes_no(self, question):
        """Get yes/no response using clear words."""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            if self.stop_requested:
                return False
            
            # Use clear, distinct words
            prompt = f"{question} Say 'CONFIRM' for YES or 'SKIP' for NO"
            response = self.get_voice_input(prompt, timeout=10)
            
            if not response:
                if attempt < max_attempts - 1:
                    self.speak_and_wait("I didn't hear you. Let me try again.", 1)
                continue
            
            response_clean = response.lower().strip()
            
            # Check for the main words
            if 'confirm' in response_clean:
                self.log_message("Selected: YES (CONFIRM)", "user")
                return True
            elif 'skip' in response_clean:
                self.log_message("Selected: NO (SKIP)", "user")
                return False
            
            # Backup patterns
            yes_patterns = ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'accept', 'proceed']
            no_patterns = ['no', 'nope', 'nah', 'not', 'cancel', 'decline']
            quit_patterns = ['quit', 'exit', 'stop', 'end']
            
            if any(pattern in response_clean for pattern in yes_patterns):
                self.log_message("Selected: YES", "user")
                return True
            elif any(pattern in response_clean for pattern in no_patterns):
                self.log_message("Selected: NO", "user")
                return False
            elif any(pattern in response_clean for pattern in quit_patterns):
                self.stop_conversation()
                return False
            
            # If still not recognized, provide feedback
            if attempt < max_attempts - 1:
                self.speak_and_wait(f"I heard '{response}'. Please say 'CONFIRM' for yes or 'SKIP' for no.", 1)
                self.log_message(f"Unrecognized: '{response}'. Say 'CONFIRM' or 'SKIP'", "assistant")
        
        self.speak_and_wait("I'll SKIP this since I couldn't understand", 1)
        self.log_message("Defaulting to NO after multiple attempts", "assistant")
        return False
    
    def test_voice(self):
        """Simple voice test."""
        if not VOICE_AVAILABLE:
            messagebox.showerror("Error", "Voice features not available")
            return
        
        def run_test():
            self.log_message("🧪 Testing voice recognition...", "assistant")
            response = self.get_voice_input("Please say 'hello test'")
            
            if response and 'hello' in response.lower():
                self.log_message("✅ Voice test successful!", "success")
            else:
                self.log_message(f"⚠️ Got: '{response}' - try speaking closer", "warning")
        
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    def start_invoice_creation(self):
        """Start invoice creation."""
        def run_creation():
            self.conversation_active = True
            self.stop_requested = False
            
            try:
                self.start_btn.config(state="disabled", bg='#7f8c8d')
                self.stop_btn.config(state="normal", bg='#e74c3c')
                
                self.log_message("🚀 Starting invoice creation...", "assistant")
                self.create_simple_invoice()
                
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}", "error")
            finally:
                self.conversation_active = False
                self.start_btn.config(state="normal", bg='#27ae60')
                self.stop_btn.config(state="disabled", bg='#7f8c8d')
                self.update_status("Ready")
        
        thread = threading.Thread(target=run_creation, daemon=True)
        thread.start()
    
    def create_simple_invoice(self):
        """Create invoice with simple flow."""
        try:
            self.log_message("Welcome! Let's create your invoice.", "assistant")
            
            # Company info
            if self.config.get("company_info"):
                company_name = self.config["company_info"]["name"]
                use_saved = self.get_yes_no(f"Use saved company '{company_name}'?")
                
                if self.stop_requested:
                    return
                
                if use_saved:
                    company_info = self.config["company_info"]
                else:
                    company_info = self.get_basic_company_info()
            else:
                company_info = self.get_basic_company_info()
            
            if self.stop_requested or not company_info:
                return
            
            # Customer info
            customer_info = self.get_basic_customer_info()
            
            if self.stop_requested or not customer_info:
                return
            
            # Single item
            self.log_message("Let's add one item", "assistant")
            item = self.get_complete_item_info()
            
            if not item or self.stop_requested:
                return
            
            # Create invoice
            invoice = self.create_invoice_from_data(company_info, customer_info, [item])
            
            # Generate invoice files
            template = InvoiceTemplate()
            
            # Create output directory
            output_dir = "generated_invoices"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate HTML file
            html_file = os.path.join(output_dir, f"{invoice.invoice_number}.html")
            template.save_html_invoice(invoice, html_file)
            
            # Try to generate PDF file
            try:
                pdf_file = os.path.join(output_dir, f"{invoice.invoice_number}.pdf")
                template.generate_pdf_invoice(invoice, pdf_file)
            except ImportError:
                pdf_file = None
                self.log_message("PDF generation requires weasyprint. Install with: pip install weasyprint", "warning")
            
            self.log_message("🎉 Invoice created successfully!", "success")
            self.log_message(f"📄 Invoice Number: {invoice.invoice_number}", "success")
            self.log_message(f"🏢 Company: {invoice.company.name}", "success")
            self.log_message(f"👤 Customer: {invoice.customer.name}", "success")
            self.log_message(f"� Items: {len(invoice.items)}", "success")
            self.log_message(f"�💰 Total Amount: ₹{invoice.total_invoice_amount}", "success")
            self.log_message(f"📁 HTML File: {html_file}", "success")
            if pdf_file:
                self.log_message(f"📁 PDF File: {pdf_file}", "success")
            
            # Show item details to confirm correct values were used
            for i, item in enumerate(invoice.items, 1):
                self.log_message(f"   Item {i}: {item.description} - Qty: {item.quantity}, Rate: ₹{item.unit_price}, GST: {item.gst_rate}%", "success")
            
        except Exception as e:
            self.log_message(f"❌ Error creating invoice: {str(e)}", "error")
    
    def get_basic_company_info(self):
        """Get basic company info."""
        name = self.get_voice_input("Company name?")
        if self.stop_requested: return None
        
        city = self.get_voice_input("Company city?")
        if self.stop_requested: return None
        
        state = self.get_voice_input("Company state?")
        if self.stop_requested: return None
        
        company_info = {
            "name": name,
            "address": f"{city}, {state}",
            "city": city,
            "state": state,
            "pincode": "000000",
            "gst_number": None,
            "phone": None
        }
        
        self.config["company_info"] = company_info
        self.save_config()
        
        return company_info
    
    def get_basic_customer_info(self):
        """Get basic customer info."""
        name = self.get_voice_input("Customer name?")
        if self.stop_requested: return None
        
        city = self.get_voice_input("Customer city?")
        if self.stop_requested: return None
        
        state = self.get_voice_input("Customer state?")
        if self.stop_requested: return None
        
        return {
            "name": name,
            "address": f"{city}, {state}",
            "city": city,
            "state": state,
            "pincode": "000000",
            "gst_number": None,
            "phone": None
        }
    
    def get_complete_item_info(self):
        """Get complete item information with all required questions."""
        self.log_message("Let's add an item to your invoice", "assistant")
        
        # 1. Item description
        description = self.get_voice_input("What is the item name or description?")
        if self.stop_requested: return None
        
        # 2. Quantity - IMPORTANT: Ask for quantity until we get a valid answer!
        quantity = None
        attempts = 0
        while quantity is None and attempts < 3:
            quantity_input = self.get_voice_input("What is the quantity? Please say the number clearly")
            if self.stop_requested: return None
            
            if quantity_input:
                try:
                    # Handle common word-to-number conversions
                    quantity_text = quantity_input.lower().strip()
                    number_words = {
                        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
                        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20
                    }
                    
                    if quantity_text in number_words:
                        quantity = float(number_words[quantity_text])
                    else:
                        quantity = float(quantity_input)
                    
                    if quantity <= 0:
                        self.log_message("Quantity must be greater than zero. Please try again.", "assistant")
                        quantity = None
                    else:
                        self.log_message(f"Got quantity: {quantity}", "user")
                except:
                    self.log_message(f"I heard '{quantity_input}' but couldn't understand it as a number. Please try again.", "assistant")
                    quantity = None
            else:
                self.log_message("I didn't hear any response. Please try again.", "assistant")
            
            attempts += 1
        
        if quantity is None:
            self.log_message("I couldn't get the quantity. Please type it in the text box below.", "assistant")
            quantity_input = self.get_text_input("Enter quantity:")
            try:
                quantity = float(quantity_input) if quantity_input else 1
            except:
                quantity = 1
        
        # 3. Price per unit - Ask clearly until we get a valid answer!
        rate = None
        attempts = 0
        while rate is None and attempts < 3:
            rate_input = self.get_voice_input("What is the price per unit in rupees? Please say the number clearly")
            if self.stop_requested: return None
            
            if rate_input:
                try:
                    rate = float(rate_input)
                    if rate < 0:
                        self.log_message("Price cannot be negative. Please try again.", "assistant")
                        rate = None
                    else:
                        self.log_message(f"Got price: ₹{rate} per unit", "user")
                except:
                    self.log_message(f"I heard '{rate_input}' but couldn't understand it as a price. Please try again.", "assistant")
                    rate = None
            else:
                self.log_message("I didn't hear any response. Please try again.", "assistant")
            
            attempts += 1
        
        if rate is None:
            self.log_message("I couldn't get the price. Please type it in the text box below.", "assistant")
            rate_input = self.get_text_input("Enter price per unit:")
            try:
                rate = float(rate_input) if rate_input else 100
            except:
                rate = 100
        
        # 4. HSN Code and GST - Ask with user control
        suggested_hsn_info = self.hsn_validator.auto_suggest_hsn(description)
        
        if suggested_hsn_info:
            suggested_hsn = suggested_hsn_info['hsn_code']
            suggested_gst = suggested_hsn_info['typical_gst']
            
            self.log_message(f"I suggest HSN code {suggested_hsn} with {suggested_gst}% GST for '{description}'", "assistant")
            use_suggested = self.get_yes_no("Should I use this suggested HSN code and GST rate?")
            
            if use_suggested:
                hsn_code = suggested_hsn
                gst_rate = suggested_gst
                self.log_message(f"✅ Using HSN {hsn_code} with {gst_rate}% GST", "success")
            else:
                # Ask user for custom HSN and GST
                hsn_code = self.get_voice_input("Please tell me the HSN code you want to use") or "9999"
                
                # Ask for GST until we get a valid answer
                gst_rate = None
                attempts = 0
                while gst_rate is None and attempts < 3:
                    gst_input = self.get_voice_input("What GST percentage should I apply? Just say the number like 5, 12, 18, or 28")
                    if self.stop_requested: return None
                    
                    if gst_input:
                        try:
                            gst_rate = float(gst_input)
                            if gst_rate < 0 or gst_rate > 100:
                                self.log_message("GST rate should be between 0 and 100. Please try again.", "assistant")
                                gst_rate = None
                            else:
                                self.log_message(f"Got GST rate: {gst_rate}%", "user")
                        except:
                            self.log_message(f"I heard '{gst_input}' but couldn't understand it as a GST rate. Please try again.", "assistant")
                            gst_rate = None
                    else:
                        self.log_message("I didn't hear any response. Please try again.", "assistant")
                    
                    attempts += 1
                
                if gst_rate is None:
                    self.log_message("I couldn't get the GST rate. Please type it in the text box below.", "assistant")
                    gst_input = self.get_text_input("Enter GST percentage (e.g., 18):")
                    try:
                        gst_rate = float(gst_input) if gst_input else 18
                    except:
                        gst_rate = 18
        else:
            # No suggestion available, ask user
            self.log_message("No HSN code suggestion available for this item", "assistant")
            hsn_code = self.get_voice_input("Please provide the HSN code for this item") or "9999"
            
            # Ask for GST until we get a valid answer
            gst_rate = None
            attempts = 0
            while gst_rate is None and attempts < 3:
                gst_input = self.get_voice_input("What GST percentage should I apply? Just say the number like 5, 12, 18, or 28")
                if self.stop_requested: return None
                
                if gst_input:
                    try:
                        gst_rate = float(gst_input)
                        if gst_rate < 0 or gst_rate > 100:
                            self.log_message("GST rate should be between 0 and 100. Please try again.", "assistant")
                            gst_rate = None
                        else:
                            self.log_message(f"Got GST rate: {gst_rate}%", "user")
                    except:
                        self.log_message(f"I heard '{gst_input}' but couldn't understand it as a GST rate. Please try again.", "assistant")
                        gst_rate = None
                else:
                    self.log_message("I didn't hear any response. Please try again.", "assistant")
                
                attempts += 1
            
            if gst_rate is None:
                self.log_message("I couldn't get the GST rate. Please type it in the text box below.", "assistant")
                gst_input = self.get_text_input("Enter GST percentage (e.g., 18):")
                try:
                    gst_rate = float(gst_input) if gst_input else 18
                except:
                    gst_rate = 18
        
        # 5. Discount (optional)
        has_discount = self.get_yes_no("Is there any discount on this item?")
        discount = 0
        if has_discount:
            discount = None
            attempts = 0
            while discount is None and attempts < 3:
                discount_input = self.get_voice_input("What is the discount percentage? Just say the number")
                if self.stop_requested: return None
                
                if discount_input:
                    try:
                        discount = float(discount_input)
                        if discount < 0 or discount > 100:
                            self.log_message("Discount should be between 0 and 100. Please try again.", "assistant")
                            discount = None
                        else:
                            self.log_message(f"Got discount: {discount}%", "user")
                    except:
                        self.log_message(f"I heard '{discount_input}' but couldn't understand it as a discount. Please try again.", "assistant")
                        discount = None
                else:
                    self.log_message("I didn't hear any response. Please try again.", "assistant")
                
                attempts += 1
            
            if discount is None:
                self.log_message("I couldn't get the discount. Please type it in the text box below.", "assistant")
                discount_input = self.get_text_input("Enter discount percentage:")
                try:
                    discount = float(discount_input) if discount_input else 0
                except:
                    discount = 0
        
        # Show summary
        item_total = quantity * rate
        if discount > 0:
            item_total *= (1 - discount / 100)
        
        self.log_message(f"📝 Item Summary:", "success")
        self.log_message(f"   Description: {description}", "success")
        self.log_message(f"   Quantity: {quantity}", "success")
        self.log_message(f"   Rate: ₹{rate} per unit", "success")
        self.log_message(f"   HSN Code: {hsn_code}", "success")
        self.log_message(f"   GST Rate: {gst_rate}%", "success")
        if discount > 0:
            self.log_message(f"   Discount: {discount}%", "success")
        self.log_message(f"   Total: ₹{item_total:.2f}", "success")
        
        return {
            "description": description,
            "hsn_code": hsn_code,
            "quantity": quantity,
            "rate": rate,
            "gst_rate": gst_rate,
            "discount": discount
        }
    
    def create_invoice_from_data(self, company_info, customer_info, items):
        """Create invoice from data."""
        company = Company(
            name=company_info["name"],
            address=company_info["address"],
            city=company_info["city"],
            state=company_info["state"],
            pincode=company_info["pincode"],
            gstin=company_info.get("gst_number"),
            phone=company_info.get("phone")
        )
        
        customer = Customer(
            name=customer_info["name"],
            address=customer_info["address"],
            city=customer_info["city"],
            state=customer_info["state"],
            pincode=customer_info["pincode"],
            gstin=customer_info.get("gst_number"),
            phone=customer_info.get("phone")
        )
        
        self.config["last_invoice_number"] += 1
        invoice_number = f"{self.config.get('invoice_prefix', 'INV')}-{self.config['last_invoice_number']:04d}"
        
        invoice = Invoice(invoice_number=invoice_number, company=company, customer=customer)
        
        for item_data in items:
            item = InvoiceItem(
                description=item_data["description"],
                hsn_code=item_data["hsn_code"],
                quantity=Decimal(str(item_data["quantity"])),
                unit_price=Decimal(str(item_data["rate"])),
                gst_rate=Decimal(str(item_data["gst_rate"])),
                discount_percentage=Decimal(str(item_data["discount"]))
            )
            invoice.add_item(item)
        
        self.save_config()
        return invoice
    
    def load_config(self):
        """Load configuration."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "last_invoice_number": 0,
                    "company_info": None,
                    "invoice_prefix": "INV"
                }
        except Exception:
            self.config = {
                "last_invoice_number": 0,
                "company_info": None,
                "invoice_prefix": "INV"
            }
    
    def save_config(self):
        """Save configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log_message(f"Warning: Could not save config: {e}", "warning")
    
    def run(self):
        """Start the GUI application."""
        self.log_message("🎉 Welcome! Click 'Start Invoice Creation' to begin.", "assistant")
        self.log_message("No more TTS errors - clean and stable system!", "success")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("👋 Goodbye!", "assistant")


def main():
    """Main function."""
    app = CleanVoiceInvoiceGUI()
    app.run()


if __name__ == "__main__":
    main()
