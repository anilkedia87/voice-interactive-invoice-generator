#!/usr/bin/env python3
"""
Simple Voice Invoice - No Loops, Better Recognition
Fixed version that prevents continuous loops and handles single words better
"""

import sys
import os
import json
from decimal import Decimal
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.invoice import Company, Customer, Invoice, InvoiceItem
from services.hsn_validator import HSNValidator
from services.invoice_generator import InvoiceGenerator

# Voice dependencies
VOICE_AVAILABLE = True
try:
    import speech_recognition as sr
    import pyttsx3
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠️  Voice features require: pip install speechrecognition pyttsx3 pyaudio")


class SimpleVoiceInvoice:
    def __init__(self):
        self.config_file = "invoice_config.json"
        self.load_config()
        self.hsn_validator = HSNValidator()
        
        if VOICE_AVAILABLE:
            self.setup_voice()
            print("✅ Voice setup complete")
        else:
            print("❌ Voice not available - text only mode")
    
    def setup_voice(self):
        """Setup voice with optimized settings."""
        self.recognizer = sr.Recognizer()
        
        # Balanced settings - wait for user but prevent loops
        self.recognizer.energy_threshold = 200  # Lower threshold - more sensitive
        self.recognizer.dynamic_energy_threshold = True  # Auto adjust
        self.recognizer.pause_threshold = 0.8   # Wait longer before stopping
        self.recognizer.phrase_threshold = 0.3   # Allow longer phrases
        
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        
        # Setup female voice
        voices = self.tts_engine.getProperty('voices')
        if voices:
            for voice in voices:
                if any(word in voice.name.lower() for word in ['female', 'woman', 'zira', 'samantha']):
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.7)
        
        # Proper calibration for better recognition
        print("🎤 Calibrating microphone (please be quiet for 2 seconds)...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
    
    def speak(self, text):
        """Speak text."""
        print(f"🤖 {text}")
        if VOICE_AVAILABLE:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except:
                pass
    
    def listen_once(self, prompt, timeout=15):
        """Listen for input once - no loops."""
        self.speak(prompt)
        
        if not VOICE_AVAILABLE:
            return input("👤 Type response: ").strip()
        
        try:
            print("🎤 Listening... (speak now, I'm waiting for you)")
            
            with self.microphone as source:
                # Longer timeout to wait for user response
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("🤔 Processing...")
            
            # Try Google first
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"👤 You said: {text}")
                return text.strip()
            except:
                # Try offline for simple words
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    print(f"👤 You said (offline): {text}")
                    return text.strip()
                except:
                    pass
        
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within 15 seconds")
            print("🎤 Let me try listening again...")
            # Try one more time with longer timeout
            try:
                with self.microphone as source:
                    print("🎤 Second attempt - please speak now...")
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
                
                text = self.recognizer.recognize_google(audio)
                print(f"👤 You said: {text}")
                return text.strip()
            except:
                print("⏰ Still no speech detected")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Only fall back to text input after giving voice a good chance
        print("🖊️ Please type your response (voice recognition didn't work):")
        return input("👤 Type here: ").strip()
    
    def get_yes_no(self, question):
        """Get yes/no with fallback."""
        response = self.listen_once(f"{question} (yes/no)")
        
        if not response:
            return False
        
        response = response.lower()
        
        # Check for quit commands
        if any(word in response for word in ['quit', 'exit', 'stop', 'end', 'cancel']):
            print("👋 Exiting...")
            return None
        
        # Check yes/no
        if any(word in response for word in ['yes', 'y', 'yeah', 'ok', 'sure']):
            return True
        elif any(word in response for word in ['no', 'n', 'nope']):
            return False
        
        print("❓ Couldn't understand - defaulting to 'no'")
        return False
    
    def create_quick_invoice(self):
        """Create invoice with minimal questions."""
        print("\n" + "="*50)
        print("🎤 QUICK VOICE INVOICE GENERATOR")
        print("="*50)
        
        self.speak("Let's create a quick invoice!")
        
        # Company info
        if self.config.get("company_info"):
            company_name = self.config["company_info"]["name"]
            use_saved = self.get_yes_no(f"Use saved company '{company_name}'?")
            
            if use_saved is None:  # User wants to quit
                return
            elif use_saved:
                company_info = self.config["company_info"]
                print(f"✅ Using {company_name}")
            else:
                company_info = self.get_company_info()
        else:
            company_info = self.get_company_info()
        
        if not company_info:
            return
        
        # Customer info
        customer_info = self.get_customer_info()
        if not customer_info:
            return
        
        # One item
        item = self.get_item_info()
        if not item:
            return
        
        # Create invoice
        try:
            invoice = self.create_invoice_object(company_info, customer_info, [item])
            
            # Generate files
            generator = InvoiceGenerator()
            html_file, pdf_file = generator.generate_invoice(invoice)
            
            print(f"\n✅ SUCCESS!")
            print(f"📄 Invoice: {invoice.invoice_number}")
            print(f"💰 Total: ₹{invoice.total_amount}")
            print(f"📁 Files: {html_file}, {pdf_file}")
            
            self.speak(f"Invoice {invoice.invoice_number} created successfully for {invoice.total_amount} rupees!")
            
        except Exception as e:
            print(f"❌ Error creating invoice: {e}")
    
    def get_company_info(self):
        """Get company info quickly."""
        name = self.listen_once("What's your company name?")
        if not name or name.lower() in ['quit', 'exit']:
            return None
        
        city = self.listen_once("Company city?")
        if not city:
            city = "Unknown"
        
        state = self.listen_once("Company state?")
        if not state:
            state = "Unknown"
        
        return {
            "name": name,
            "address": f"{city}, {state}",
            "city": city,
            "state": state,
            "pincode": "000000",
            "gst_number": None,
            "phone": None
        }
    
    def get_customer_info(self):
        """Get customer info quickly."""
        name = self.listen_once("Customer name?")
        if not name or name.lower() in ['quit', 'exit']:
            return None
        
        city = self.listen_once("Customer city?")
        if not city:
            city = "Unknown"
        
        state = self.listen_once("Customer state?")  
        if not state:
            state = "Unknown"
        
        return {
            "name": name,
            "address": f"{city}, {state}",
            "city": city,
            "state": state,
            "pincode": "000000",
            "gst_number": None,
            "phone": None
        }
    
    def get_item_info(self):
        """Get one item info."""
        description = self.listen_once("What item are you selling?")
        if not description or description.lower() in ['quit', 'exit']:
            return None
        
        # Auto-suggest HSN
        suggested_hsn_info = self.hsn_validator.auto_suggest_hsn(description)
        hsn_code = "9999"
        gst_rate = 18
        
        if suggested_hsn_info:
            hsn_code = suggested_hsn_info['hsn_code']
            gst_rate = suggested_hsn_info['typical_gst']
            print(f"💡 Auto-selected: HSN {hsn_code}, GST {gst_rate}%")
        
        # Get price
        price_input = self.listen_once("What's the price?")
        try:
            price = float(price_input)
        except:
            print("❓ Couldn't understand price, using ₹100")
            price = 100
        
        return {
            "description": description,
            "hsn_code": hsn_code,
            "quantity": 1,
            "rate": price,
            "gst_rate": gst_rate,
            "discount": 0
        }
    
    def create_invoice_object(self, company_info, customer_info, items):
        """Create invoice object."""
        company = Company(
            name=company_info["name"],
            address=company_info["address"],
            city=company_info["city"],
            state=company_info["state"],
            pincode=company_info["pincode"]
        )
        
        customer = Customer(
            name=customer_info["name"],
            address=customer_info["address"],
            city=customer_info["city"],
            state=customer_info["state"],
            pincode=customer_info["pincode"]
        )
        
        # Generate invoice number
        self.config["last_invoice_number"] += 1
        invoice_number = f"INV-{self.config['last_invoice_number']:04d}"
        
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
        
        self.save_config()
        return invoice
    
    def load_config(self):
        """Load config."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {"last_invoice_number": 0}
        except:
            self.config = {"last_invoice_number": 0}
    
    def save_config(self):
        """Save config."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")


def main():
    """Main function."""
    print("🎤 Simple Voice Invoice Generator (Fixed)")
    print("Say 'quit' or 'exit' anytime to stop")
    
    try:
        app = SimpleVoiceInvoice()
        app.create_quick_invoice()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
