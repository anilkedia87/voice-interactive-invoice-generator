#!/usr/bin/env python3
"""
Enhanced Voice Interactive Invoice Generator with GUI
Features:
- Female voice
- GUI display for messages
- Improved speech recognition
- Better error handling
"""

import sys
import os
import json
from decimal import Decimal
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue

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
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
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
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎤 Voice Interactive Invoice Generator", 
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
            height=20,
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
        self.start_btn = ttk.Button(control_frame, text="Start Invoice Creation", 
                                   command=self.start_invoice_creation)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.test_voice_btn = ttk.Button(control_frame, text="Test Voice Recognition", 
                                        command=self.test_voice)
        self.test_voice_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.clear_btn = ttk.Button(control_frame, text="Clear Messages", 
                                   command=self.clear_messages)
        self.clear_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Text input for fallback
        input_frame = ttk.LabelFrame(main_frame, text="Text Input (Fallback)", padding="5")
        input_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.text_input = ttk.Entry(input_frame, width=60, font=('Arial', 10))
        self.text_input.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        self.text_input.bind('<Return>', self.on_text_input)
        
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.on_text_input)
        self.send_btn.grid(row=0, column=1)
        
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
        
        # Start message processing
        self.process_messages()
    
    def setup_voice(self):
        """Initialize voice recognition and text-to-speech."""
        try:
            # Initialize speech recognition with enhanced settings
            self.recognizer = sr.Recognizer()
            
            # Enhanced recognition settings
            self.recognizer.energy_threshold = 300  # Minimum audio energy to consider recording
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.dynamic_energy_adjustment_damping = 0.15
            self.recognizer.dynamic_energy_ratio = 1.5
            self.recognizer.pause_threshold = 0.8  # Seconds of non-speaking audio before phrase is complete
            self.recognizer.operation_timeout = None  # No timeout for listening
            self.recognizer.phrase_threshold = 0.3  # Minimum length of phrase
            self.recognizer.non_speaking_duration = 0.5  # How much silence to detect before stopping
            
            self.microphone = sr.Microphone()
            
            # Initialize text-to-speech with female voice
            self.tts_engine = pyttsx3.init()
            self.setup_female_voice()
            
            # Adjust for ambient noise
            self.log_message("🎤 Calibrating microphone for ambient noise...", "assistant")
            self.update_status("Calibrating microphone...")
            
            with self.microphone as source:
                # Longer adjustment for better accuracy
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            self.log_message("✅ Voice setup completed successfully!", "success")
            self.update_status("Voice ready")
            
        except Exception as e:
            self.log_message(f"❌ Voice setup failed: {str(e)}", "error")
            self.update_status("Voice setup failed")
    
    def setup_female_voice(self):
        """Configure TTS to use female voice with optimal settings."""
        try:
            voices = self.tts_engine.getProperty('voices')
            female_voice_found = False
            
            if voices:
                # Search for female voices with priority
                female_keywords = ['female', 'woman', 'zira', 'hazel', 'kate', 'samantha', 'alex', 'victoria']
                
                for voice in voices:
                    voice_name_lower = voice.name.lower()
                    voice_id_lower = voice.id.lower()
                    
                    # Check for female indicators
                    for keyword in female_keywords:
                        if keyword in voice_name_lower or keyword in voice_id_lower:
                            self.tts_engine.setProperty('voice', voice.id)
                            female_voice_found = True
                            self.log_message(f"🗣️ Using female voice: {voice.name}", "assistant")
                            break
                    
                    if female_voice_found:
                        break
                
                if not female_voice_found:
                    # Use the first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
                    self.log_message(f"🗣️ Using default voice: {voices[0].name}", "assistant")
            
            # Set optimal voice parameters
            self.tts_engine.setProperty('rate', 160)    # Slightly slower for clarity
            self.tts_engine.setProperty('volume', 0.8)   # Clear but not too loud
            
        except Exception as e:
            self.log_message(f"⚠️ Voice configuration issue: {str(e)}", "warning")
    
    def log_message(self, message, msg_type="normal"):
        """Add a message to the display with appropriate formatting."""
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
        
        # Also speak the message if it's from assistant
        if msg_type == "assistant" and VOICE_AVAILABLE:
            self.speak_async(message)
    
    def speak_async(self, text):
        """Speak text asynchronously to avoid blocking the GUI."""
        def speak():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
        
        if VOICE_AVAILABLE:
            thread = threading.Thread(target=speak, daemon=True)
            thread.start()
    
    def update_status(self, status_text, color="black"):
        """Update the status label."""
        self.status_label.config(text=status_text, foreground=color)
        self.root.update_idletasks()
    
    def clear_messages(self):
        """Clear all messages from the display."""
        self.message_display.configure(state=tk.NORMAL)
        self.message_display.delete(1.0, tk.END)
        self.message_display.configure(state=tk.DISABLED)
    
    def on_text_input(self, event=None):
        """Handle text input as fallback."""
        text = self.text_input.get().strip()
        if text and self.waiting_for_input:
            self.log_message(text, "user")
            self.current_response = text
            self.text_input.delete(0, tk.END)
            self.waiting_for_input = False
    
    def get_voice_input(self, prompt, timeout=10):
        """Get voice input with enhanced recognition and GUI fallback."""
        if not VOICE_AVAILABLE:
            return self.get_text_input(prompt)
        
        self.log_message(prompt, "assistant")
        self.update_status("🎤 Listening... (speak now)", "blue")
        
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                self.log_message("🎤 Listening... (speak now)", "assistant")
                
                with self.microphone as source:
                    # Longer timeout for better user experience
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=10
                    )
                
                self.update_status("🤔 Processing speech...", "orange")
                
                # Try Google Speech Recognition first (most accurate)
                try:
                    text = self.recognizer.recognize_google(audio)
                    self.log_message(text, "user")
                    self.update_status("Voice recognized", "green")
                    return text.strip()
                except sr.RequestError:
                    # Fall back to offline recognition
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        self.log_message(text, "user")
                        self.update_status("Voice recognized (offline)", "green")
                        return text.strip()
                    except:
                        raise sr.UnknownValueError("Offline recognition also failed")
                        
            except sr.WaitTimeoutError:
                self.log_message("⏰ No speech detected within timeout", "warning")
                if attempt < max_attempts - 1:
                    self.log_message("Please speak louder or closer to the microphone", "assistant")
                    
            except sr.UnknownValueError:
                self.log_message("🤔 Sorry, I couldn't understand that", "warning")
                if attempt < max_attempts - 1:
                    self.log_message("Please speak clearly and try again", "assistant")
                    
            except Exception as e:
                self.log_message(f"❌ Speech recognition error: {str(e)}", "error")
                break
        
        # Fall back to text input
        self.update_status("Waiting for text input...", "orange")
        self.log_message("🖊️ Voice recognition failed. Please type your response in the text box below:", "assistant")
        return self.get_text_input("")
    
    def get_text_input(self, prompt):
        """Get text input from the GUI."""
        if prompt:
            self.log_message(prompt, "assistant")
        
        self.waiting_for_input = True
        self.current_response = None
        self.text_input.focus_set()
        
        # Wait for user input
        while self.waiting_for_input:
            self.root.update()
            if self.current_response is not None:
                return self.current_response
        
        return self.current_response or ""
    
    def get_yes_no(self, question):
        """Get yes/no response with voice recognition."""
        while True:
            response = self.get_voice_input(f"{question} (Say 'yes' or 'no')", timeout=15)
            response_lower = response.lower().strip()
            
            if any(word in response_lower for word in ['yes', 'y', 'yeah', 'yep', 'sure', 'ok', 'okay']):
                return True
            elif any(word in response_lower for word in ['no', 'n', 'nope', 'nah', 'not']):
                return False
            else:
                self.log_message("Please respond with 'yes' or 'no'", "assistant")
    
    def test_voice(self):
        """Test voice recognition functionality."""
        if not VOICE_AVAILABLE:
            messagebox.showerror("Error", "Voice features not available")
            return
        
        def run_test():
            self.log_message("🧪 Starting voice test...", "assistant")
            self.log_message("Please say 'Hello, this is a test' when prompted", "assistant")
            
            response = self.get_voice_input("Say: Hello, this is a test")
            
            if response:
                self.log_message(f"✅ Voice test successful! You said: '{response}'", "success")
            else:
                self.log_message("❌ Voice test failed - no response received", "error")
        
        # Run test in background thread
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    def start_invoice_creation(self):
        """Start the invoice creation process."""
        def run_creation():
            try:
                self.log_message("🚀 Starting invoice creation process...", "assistant")
                self.create_voice_invoice()
            except Exception as e:
                self.log_message(f"❌ Error creating invoice: {str(e)}", "error")
        
        # Disable start button during creation
        self.start_btn.config(state="disabled")
        
        # Run in background thread
        thread = threading.Thread(target=run_creation, daemon=True)
        thread.start()
    
    def create_voice_invoice(self):
        """Main voice invoice creation process."""
        try:
            self.log_message("Welcome to the Voice Interactive Invoice Generator!", "assistant")
            
            # Check for saved company info
            if self.config.get("company_info"):
                company_name = self.config["company_info"]["name"]
                use_saved = self.get_yes_no(f"Should I use your saved company information for {company_name}?")
                
                if use_saved:
                    company_info = self.config["company_info"]
                    self.log_message(f"✅ Using {company_name} details", "success")
                else:
                    company_info = self.get_company_info()
            else:
                company_info = self.get_company_info()
            
            # Get customer information
            self.log_message("Now let's get the customer information", "assistant")
            customer_info = self.get_customer_info()
            
            # Get invoice items
            self.log_message("Now let's add the products or services to your invoice", "assistant")
            items = self.get_invoice_items()
            
            if not items:
                self.log_message("❌ No items added. Invoice creation cancelled", "error")
                return
            
            # Create invoice
            invoice = self.create_invoice_from_data(company_info, customer_info, items)
            
            # Generate invoice file
            generator = InvoiceGenerator()
            html_file, pdf_file = generator.generate_invoice(invoice)
            
            self.log_message(f"🎉 Invoice created successfully!", "success")
            self.log_message(f"📄 Invoice Number: {invoice.invoice_number}", "success")
            self.log_message(f"💰 Total Amount: ₹{invoice.total_amount}", "success")
            self.log_message(f"📁 Files saved: {html_file}, {pdf_file}", "success")
            
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}", "error")
        finally:
            # Re-enable start button
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
    
    def get_company_info(self):
        """Get company information via voice."""
        self.log_message("Let's set up your company information", "assistant")
        
        company_name = self.get_voice_input("What is your company name?")
        address = self.get_voice_input("What is your company address?")
        city = self.get_voice_input("What city is your company in?")
        state = self.get_voice_input("What state is your company in?")
        pincode = self.get_voice_input("What is your company pincode?")
        
        has_gst = self.get_yes_no("Does your company have a GST number?")
        gst_number = None
        if has_gst:
            gst_number = self.get_voice_input("What is your GST number?")
        
        add_phone = self.get_yes_no("Would you like to add a phone number?")
        phone = None
        if add_phone:
            phone = self.get_voice_input("What is your phone number?")
        
        company_info = {
            "name": company_name,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "gst_number": gst_number,
            "phone": phone
        }
        
        # Save for future use
        self.config["company_info"] = company_info
        self.save_config()
        
        return company_info
    
    def get_customer_info(self):
        """Get customer information via voice."""
        customer_name = self.get_voice_input("What is the customer's name?")
        address = self.get_voice_input("What is the customer's address?")
        city = self.get_voice_input("What city is the customer in?")
        state = self.get_voice_input("What state is the customer in?")
        pincode = self.get_voice_input("What is the customer's pincode?")
        
        has_gst = self.get_yes_no("Does the customer have a GST number?")
        gst_number = None
        if has_gst:
            gst_number = self.get_voice_input("What is the customer's GST number?")
        
        add_phone = self.get_yes_no("Would you like to add the customer's phone number?")
        phone = None
        if add_phone:
            phone = self.get_voice_input("What is the customer's phone number?")
        
        return {
            "name": customer_name,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "gst_number": gst_number,
            "phone": phone
        }
    
    def get_invoice_items(self):
        """Get invoice items via voice."""
        items = []
        item_number = 1
        
        while True:
            self.log_message(f"Let's add item number {item_number}", "assistant")
            
            description = self.get_voice_input("What is the name or description of this item?")
            
            # Auto-suggest HSN code
            suggested_hsn_info = self.hsn_validator.auto_suggest_hsn(description)
            if suggested_hsn_info:
                suggested_hsn = suggested_hsn_info['hsn_code']
                self.log_message(f"Based on '{description}', I suggest HSN code {suggested_hsn} for {suggested_hsn_info['description']}", "assistant")
                use_suggested = self.get_yes_no("Should I use this HSN code?")
                
                if use_suggested:
                    hsn_code = suggested_hsn
                    suggested_gst = suggested_hsn_info['typical_gst']
                    self.log_message(f"The typical GST rate for this item is {suggested_gst}%", "assistant")
                    use_suggested_gst = self.get_yes_no("Should I use this GST rate?")
                    
                    if use_suggested_gst:
                        gst_rate = suggested_gst
                    else:
                        gst_rate_input = self.get_voice_input("What GST rate should I use? (say the number only)")
                        gst_rate = float(gst_rate_input)
                else:
                    hsn_code = self.get_voice_input("Please provide the HSN code")
                    gst_rate_input = self.get_voice_input("What is the GST rate? (say the number only)")
                    gst_rate = float(gst_rate_input)
            else:
                hsn_code = self.get_voice_input("Please provide the HSN code for this item")
                gst_rate_input = self.get_voice_input("What is the GST rate? (say the number only)")
                gst_rate = float(gst_rate_input)
            
            quantity_input = self.get_voice_input("What is the quantity?")
            quantity = float(quantity_input)
            
            rate_input = self.get_voice_input("What is the rate or price per unit?")
            rate = float(rate_input)
            
            has_discount = self.get_yes_no("Is there any discount on this item?")
            discount = 0
            if has_discount:
                discount_input = self.get_voice_input("What is the discount percentage?")
                discount = float(discount_input)
            
            # Create item
            item = {
                "description": description,
                "hsn_code": hsn_code,
                "quantity": quantity,
                "rate": rate,
                "gst_rate": gst_rate,
                "discount": discount
            }
            
            items.append(item)
            
            # Calculate item total for confirmation
            item_total = quantity * rate
            if discount > 0:
                item_total *= (1 - discount / 100)
            
            self.log_message(f"✅ Item {item_number} added: {description} - ₹{item_total:.2f}", "success")
            
            add_more = self.get_yes_no("Would you like to add another item?")
            if not add_more:
                break
            
            item_number += 1
        
        return items
    
    def create_invoice_from_data(self, company_info, customer_info, items):
        """Create invoice objects from collected data."""
        # Create company
        company = Company(
            name=company_info["name"],
            address=company_info["address"],
            city=company_info["city"],
            state=company_info["state"],
            pincode=company_info["pincode"],
            gst_number=company_info.get("gst_number"),
            phone=company_info.get("phone")
        )
        
        # Create customer
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
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            company=company,
            customer=customer
        )
        
        # Add items
        for item_data in items:
            item = InvoiceItem(
                description=item_data["description"],
                hsn_code=item_data["hsn_code"],
                quantity=Decimal(str(item_data["quantity"])),
                rate=Decimal(str(item_data["rate"])),
                gst_rate=Decimal(str(item_data["gst_rate"])),
                discount_percentage=Decimal(str(item_data["discount"]))
            )
            invoice.add_item(item)
        
        # Save config with updated invoice number
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
    
    def process_messages(self):
        """Process message queue for thread safety."""
        try:
            while True:
                message_type, message = self.message_queue.get_nowait()
                self.log_message(message, message_type)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def run(self):
        """Start the GUI application."""
        self.log_message("🎉 Welcome to Voice Interactive Invoice Generator!", "assistant")
        self.log_message("Click 'Start Invoice Creation' to begin or 'Test Voice Recognition' to check your setup", "assistant")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("👋 Goodbye!", "assistant")


def main():
    """Main function to start the GUI application."""
    if not VOICE_AVAILABLE:
        print("⚠️  Installing voice dependencies...")
        print("Run: pip install speechrecognition pyttsx3 pyaudio")
        print("Note: On macOS, you may need: brew install portaudio")
    
    app = VoiceInvoiceGUI()
    app.run()


if __name__ == "__main__":
    main()
