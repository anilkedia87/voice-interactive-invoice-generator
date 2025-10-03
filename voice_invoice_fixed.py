#!/usr/bin/env python3
"""
Fixed Voice Interactive Invoice Generator with GUI
Fixes:
- Prevents continuous loops
- Better single word recognition
- Improved timeout handling
- Better error recovery
"""

import sys
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

# Voice dependencies - gracefully handle if not installed
VOICE_AVAILABLE = True
try:
    import speech_recognition as sr
    import pyttsx3
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠️  Voice features require: pip install speechrecognition pyttsx3 pyaudio")


class VoiceInvoiceGUI:
    def __init__(self):
        self.config_file = "invoice_config.json"
        self.load_config()
        self.hsn_validator = HSNValidator()
        
        # Control variables to prevent loops
        self.is_listening = False
        self.conversation_active = False
        self.max_retry_attempts = 2  # Reduced from 3
        
        # Initialize GUI
        self.setup_gui()
        
        if VOICE_AVAILABLE:
            self.setup_voice()
        else:
            self.log_message("⚠️ Voice features not available. Install: pip install speechrecognition pyttsx3 pyaudio", "warning")
    
    def setup_gui(self):
        """Initialize the GUI interface."""
        self.root = tk.Tk()
        self.root.title("🎤 Voice Interactive Invoice Generator")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎤 Voice Interactive Invoice Generator (Fixed)", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready to start", 
                                     font=('Arial', 11), foreground='green')
        self.status_label.grid(row=0, column=0)
        
        # Messages frame
        messages_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="10")
        messages_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrolled text for messages
        self.message_display = scrolledtext.ScrolledText(
            messages_frame, 
            width=80, 
            height=25,
            font=('Arial', 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.message_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for different message types
        self.message_display.tag_configure("assistant", foreground="blue", font=('Arial', 10, 'bold'))
        self.message_display.tag_configure("user", foreground="green", font=('Arial', 10, 'bold'))
        self.message_display.tag_configure("error", foreground="red", font=('Arial', 10, 'bold'))
        self.message_display.tag_configure("warning", foreground="orange", font=('Arial', 10, 'bold'))
        self.message_display.tag_configure("success", foreground="darkgreen", font=('Arial', 10, 'bold'))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Buttons
        self.start_btn = ttk.Button(control_frame, text="🚀 Start Invoice Creation", 
                                   command=self.start_invoice_creation)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop", 
                                  command=self.stop_conversation, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.test_voice_btn = ttk.Button(control_frame, text="🧪 Test Voice", 
                                        command=self.test_voice)
        self.test_voice_btn.grid(row=0, column=2, padx=(0, 10))
        
        self.clear_btn = ttk.Button(control_frame, text="🗑️ Clear", 
                                   command=self.clear_messages)
        self.clear_btn.grid(row=0, column=3)
        
        # Text input for fallback
        input_frame = ttk.LabelFrame(main_frame, text="Text Input (Always Available)", padding="5")
        input_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.text_input = ttk.Entry(input_frame, width=60, font=('Arial', 10))
        self.text_input.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        self.text_input.bind('<Return>', self.on_text_input)
        
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.on_text_input)
        self.send_btn.grid(row=0, column=1)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="💡 Tip: You can always type responses in the text box if voice recognition fails",
                               font=('Arial', 9), foreground='gray')
        instructions.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        messages_frame.columnconfigure(0, weight=1)
        messages_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)
        
        # Variables for conversation state
        self.waiting_for_input = False
        self.current_response = None
        self.stop_requested = False
    
    def setup_voice(self):
        """Initialize voice recognition and text-to-speech."""
        try:
            # Initialize speech recognition with conservative settings
            self.recognizer = sr.Recognizer()
            
            # Balanced settings - more patient but still prevent loops
            self.recognizer.energy_threshold = 250  # More sensitive
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8  # Wait longer before stopping  
            self.recognizer.phrase_threshold = 0.3  # Allow longer phrases
            self.recognizer.non_speaking_duration = 0.5  # Reasonable silence detection
            
            self.microphone = sr.Microphone()
            
            # Initialize text-to-speech with female voice
            try:
                self.tts_engine = pyttsx3.init()
                self.setup_female_voice()
            except Exception as e:
                self.log_message(f"⚠️ TTS initialization issue: {str(e)}", "warning")
                self.tts_engine = None
            
            # Proper ambient noise adjustment
            self.log_message("🎤 Calibrating microphone (please be quiet for 2 seconds)...", "assistant")
            self.update_status("Calibrating microphone...")
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            self.log_message("✅ Voice setup completed!", "success")
            self.update_status("Voice ready")
            
        except Exception as e:
            self.log_message(f"❌ Voice setup failed: {str(e)}", "error")
            self.update_status("Voice setup failed")
    
    def setup_female_voice(self):
        """Configure TTS to use female voice with optimal settings."""
        try:
            if not self.tts_engine:
                return
                
            voices = self.tts_engine.getProperty('voices')
            female_voice_found = False
            
            if voices:
                # Search for female voices
                female_keywords = ['female', 'woman', 'zira', 'hazel', 'kate', 'samantha']
                
                for voice in voices:
                    voice_name_lower = voice.name.lower()
                    
                    for keyword in female_keywords:
                        if keyword in voice_name_lower:
                            self.tts_engine.setProperty('voice', voice.id)
                            female_voice_found = True
                            self.log_message(f"🗣️ Using female voice: {voice.name}", "assistant")
                            break
                    
                    if female_voice_found:
                        break
                
                if not female_voice_found:
                    self.tts_engine.setProperty('voice', voices[0].id)
                    self.log_message(f"🗣️ Using default voice: {voices[0].name}", "assistant")
            
            # Optimal voice parameters
            self.tts_engine.setProperty('rate', 150)    # Slower for clarity
            self.tts_engine.setProperty('volume', 0.7)   # Moderate volume
            
        except Exception as e:
            self.log_message(f"⚠️ Voice configuration issue: {str(e)}", "warning")
            self.tts_engine = None
    
    def log_message(self, message, msg_type="normal"):
        """Add a message to the display with appropriate formatting."""
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
            
            # Speak assistant messages
            if msg_type == "assistant" and VOICE_AVAILABLE and not self.stop_requested:
                self.speak_async(message)
        except Exception as e:
            print(f"Error logging message: {e}")
    
    def speak_async(self, text):
        """Speak text asynchronously with improved error handling."""
        def speak():
            try:
                if not self.stop_requested and hasattr(self, 'tts_engine'):
                    # Check if engine is busy
                    if hasattr(self.tts_engine, '_inLoop') and self.tts_engine._inLoop:
                        return  # Skip if already speaking
                    
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
            except Exception as e:
                # Silently handle TTS errors to avoid console spam
                pass
        
        if VOICE_AVAILABLE and hasattr(self, 'tts_engine'):
            thread = threading.Thread(target=speak, daemon=True)
            thread.start()
    
    def update_status(self, status_text, color="black"):
        """Update the status label."""
        try:
            self.status_label.config(text=status_text, foreground=color)
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
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log_message("🛑 Conversation stopped by user", "warning")
    
    def on_text_input(self, event=None):
        """Handle text input."""
        text = self.text_input.get().strip()
        if text and self.waiting_for_input:
            self.log_message(text, "user")
            self.current_response = text
            self.text_input.delete(0, tk.END)
            self.waiting_for_input = False
    
    def get_voice_input(self, prompt, timeout=15):
        """Get voice input with improved error handling and loop prevention."""
        if not VOICE_AVAILABLE or self.stop_requested:
            return self.get_text_input(prompt)
        
        self.log_message(prompt, "assistant")
        
        # Prevent multiple simultaneous listening sessions
        if self.is_listening:
            return self.get_text_input("Please use text input (voice is busy)")
        
        self.is_listening = True
        
        try:
            for attempt in range(self.max_retry_attempts):
                if self.stop_requested:
                    return None
                
                self.update_status("🎤 Listening... (speak now or type below)", "blue")
                
                try:
                    with self.microphone as source:
                        # Longer timeout to wait for user properly
                        audio = self.recognizer.listen(
                            source, 
                            timeout=timeout, 
                            phrase_time_limit=10  # Longer phrase limit
                        )
                    
                    self.update_status("🤔 Processing...", "orange")
                    
                    # Try recognition
                    try:
                        text = self.recognizer.recognize_google(audio, language='en-US')
                        text = text.strip()
                        
                        if text:  # Make sure we got something
                            self.log_message(text, "user")
                            self.update_status("✅ Voice recognized", "green")
                            return text
                        
                    except sr.RequestError:
                        # Try offline recognition for simple words
                        try:
                            text = self.recognizer.recognize_sphinx(audio)
                            text = text.strip()
                            if text:
                                self.log_message(f"{text} (offline)", "user")
                                return text
                        except:
                            pass
                        
                except sr.WaitTimeoutError:
                    if attempt == 0:  # First attempt
                        self.log_message("⏰ No speech detected, trying again...", "warning")
                    else:
                        self.log_message("⏰ Still no speech detected", "warning")
                    
                except sr.UnknownValueError:
                    self.log_message("🤔 Couldn't understand that clearly", "warning")
                    
                except Exception as e:
                    self.log_message(f"❌ Recognition error: {str(e)}", "error")
                    break
                
                # Give user guidance between attempts
                if attempt < self.max_retry_attempts - 1:
                    self.log_message("Please speak louder and clearer, or use text input below", "assistant")
                    time.sleep(1)  # Longer delay between attempts
        
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
        
        # Wait for user input with timeout to prevent infinite loops
        start_time = time.time()
        timeout = 60  # 60 second timeout for text input
        
        while self.waiting_for_input and not self.stop_requested:
            self.root.update()
            
            if self.current_response is not None:
                return self.current_response
            
            # Check for timeout
            if time.time() - start_time > timeout:
                self.log_message("⏰ Input timeout - please try again", "warning")
                self.waiting_for_input = False
                return ""
            
            time.sleep(0.1)  # Small delay to prevent CPU spinning
        
        return self.current_response or ""
    
    def get_yes_no(self, question):
        """Get yes/no response with better single-word recognition."""
        max_attempts = 2
        
        for attempt in range(max_attempts):
            if self.stop_requested:
                return False
            
            response = self.get_voice_input(f"{question} (Say 'yes' or 'no')", timeout=10)
            
            if not response:
                continue
            
            response_lower = response.lower().strip()
            
            # Check for yes responses
            if any(word in response_lower for word in ['yes', 'y', 'yeah', 'yep', 'sure', 'ok', 'okay', 'true', 'correct']):
                return True
            # Check for no responses  
            elif any(word in response_lower for word in ['no', 'n', 'nope', 'nah', 'not', 'false', 'incorrect']):
                return False
            # Check for quit/exit commands
            elif any(word in response_lower for word in ['quit', 'exit', 'stop', 'cancel', 'end']):
                self.stop_conversation()
                return False
            else:
                if attempt < max_attempts - 1:
                    self.log_message("Please say 'yes' or 'no' clearly, or type it below", "assistant")
        
        # If we can't get a clear answer, default to no
        self.log_message("Defaulting to 'no'", "assistant")
        return False
    
    def test_voice(self):
        """Simple voice test."""
        if not VOICE_AVAILABLE:
            messagebox.showerror("Error", "Voice features not available")
            return
        
        def run_test():
            self.log_message("🧪 Testing voice recognition...", "assistant")
            self.log_message("Please say 'hello' when prompted", "assistant")
            
            response = self.get_voice_input("Say 'hello'")
            
            if response and 'hello' in response.lower():
                self.log_message("✅ Voice test successful!", "success")
            else:
                self.log_message(f"⚠️ Got: '{response}' - try speaking closer to microphone", "warning")
        
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    def start_invoice_creation(self):
        """Start the invoice creation process."""
        def run_creation():
            self.conversation_active = True
            self.stop_requested = False
            
            try:
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
                
                self.log_message("🚀 Starting invoice creation...", "assistant")
                self.create_simple_invoice()
                
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}", "error")
            finally:
                self.conversation_active = False
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.update_status("Ready")
        
        thread = threading.Thread(target=run_creation, daemon=True)
        thread.start()
    
    def create_simple_invoice(self):
        """Simplified invoice creation to avoid loops."""
        try:
            # Welcome message
            self.log_message("Welcome! Let's create your invoice quickly.", "assistant")
            
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
            
            if self.stop_requested:
                return
            
            # Customer info
            customer_info = self.get_basic_customer_info()
            
            if self.stop_requested:
                return
            
            # Single item for now
            self.log_message("Let's add one item to your invoice", "assistant")
            item = self.get_single_item()
            
            if not item or self.stop_requested:
                return
            
            # Create and save invoice
            invoice = self.create_invoice_from_data(company_info, customer_info, [item])
            
            generator = InvoiceGenerator()
            html_file, pdf_file = generator.generate_invoice(invoice)
            
            self.log_message("🎉 Invoice created successfully!", "success")
            self.log_message(f"📄 Invoice: {invoice.invoice_number}", "success")
            self.log_message(f"💰 Total: ₹{invoice.total_amount}", "success")
            
        except Exception as e:
            self.log_message(f"❌ Error creating invoice: {str(e)}", "error")
    
    def get_basic_company_info(self):
        """Get basic company info quickly."""
        name = self.get_voice_input("Company name?")
        if self.stop_requested: return None
        
        city = self.get_voice_input("Company city?")
        if self.stop_requested: return None
        
        state = self.get_voice_input("Company state?")
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
    
    def get_basic_customer_info(self):
        """Get basic customer info quickly."""
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
    
    def get_single_item(self):
        """Get one item quickly."""
        description = self.get_voice_input("Item description?")
        if self.stop_requested: return None
        
        # Auto-suggest HSN
        suggested_hsn_info = self.hsn_validator.auto_suggest_hsn(description)
        hsn_code = "9999"  # Default
        gst_rate = 18  # Default
        
        if suggested_hsn_info:
            hsn_code = suggested_hsn_info['hsn_code']
            gst_rate = suggested_hsn_info['typical_gst']
            self.log_message(f"Using HSN {hsn_code} with {gst_rate}% GST", "success")
        
        quantity = 1  # Default
        rate_input = self.get_voice_input("Price per unit?")
        if self.stop_requested: return None
        
        try:
            rate = float(rate_input)
        except:
            rate = 100  # Default
        
        return {
            "description": description,
            "hsn_code": hsn_code,
            "quantity": quantity,
            "rate": rate,
            "gst_rate": gst_rate,
            "discount": 0
        }
    
    def create_invoice_from_data(self, company_info, customer_info, items):
        """Create invoice from data."""
        company = Company(
            name=company_info["name"],
            address=company_info["address"],
            city=company_info["city"],
            state=company_info["state"],
            pincode=company_info["pincode"],
            gst_number=company_info.get("gst_number"),
            phone=company_info.get("phone")
        )
        
        customer = Customer(
            name=customer_info["name"],
            address=customer_info["address"],
            city=customer_info["city"],
            state=customer_info["state"],
            pincode=customer_info["pincode"],
            gst_number=customer_info.get("gst_number"),
            phone=customer_info.get("phone")
        )
        
        # Generate invoice number
        self.config["last_invoice_number"] += 1
        invoice_number = f"{self.config['invoice_prefix']}-{self.config['last_invoice_number']:04d}"
        
        invoice = Invoice(invoice_number=invoice_number, company=company, customer=customer)
        
        # Add items
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
        
        # Save config
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
        self.log_message("🛑 Use the 'Stop' button or say 'quit' anytime to stop.", "assistant")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("👋 Goodbye!", "assistant")


def main():
    """Main function."""
    if not VOICE_AVAILABLE:
        print("⚠️  Voice features require: pip install speechrecognition pyttsx3 pyaudio")
    
    app = VoiceInvoiceGUI()
    app.run()


if __name__ == "__main__":
    main()
