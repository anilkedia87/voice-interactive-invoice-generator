#!/usr/bin/env python3
"""
Optimized Voice Invoice - Better Single Word Recognition
Specially designed to handle short responses like YES, NO, QUIT better
"""

import sys
import os
import json
from decimal import Decimal
from datetime import datetime
import time

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


class OptimizedVoiceInvoice:
    def __init__(self):
        self.config_file = "invoice_config.json"
        self.load_config()
        self.hsn_validator = HSNValidator()
        
        if VOICE_AVAILABLE:
            self.setup_voice()
            print("✅ Voice setup complete - optimized for single words")
        else:
            print("❌ Voice not available - text only mode")
    
    def setup_voice(self):
        """Setup voice optimized for single word recognition."""
        self.recognizer = sr.Recognizer()
        
        # Optimized settings for single words
        self.recognizer.energy_threshold = 150  # Very sensitive
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.1  # Quick adaptation
        self.recognizer.dynamic_energy_ratio = 1.2  # More responsive
        self.recognizer.pause_threshold = 0.4   # Quick response for short words
        self.recognizer.phrase_threshold = 0.1   # Very short phrases OK
        self.recognizer.non_speaking_duration = 0.3  # Quick silence detection
        
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        
        # Setup female voice
        voices = self.tts_engine.getProperty('voices')
        if voices:
            for voice in voices:
                if any(word in voice.name.lower() for word in ['female', 'woman', 'zira', 'samantha']):
                    self.tts_engine.setProperty('voice', voice.id)
                    print(f"🗣️ Using female voice: {voice.name}")
                    break
        
        self.tts_engine.setProperty('rate', 140)  # Slower for clarity
        self.tts_engine.setProperty('volume', 0.8)
        
        # Thorough calibration
        print("🎤 Calibrating microphone for single words (be quiet for 3 seconds)...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=3)
    
    def speak(self, text):
        """Speak text."""
        print(f"🤖 {text}")
        if VOICE_AVAILABLE:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except:
                pass
    
    def listen_for_single_word(self, prompt, expected_words=None, timeout=20):
        """Optimized listening for single words like yes/no."""
        self.speak(prompt)
        
        if not VOICE_AVAILABLE:
            return input("👤 Type response: ").strip()
        
        if expected_words:
            print(f"💡 Expected words: {', '.join(expected_words)}")
        
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                print(f"🎤 Listening for single word... (Attempt {attempts}/{max_attempts})")
                print("📢 Speak CLEARLY and LOUDLY")
                
                with self.microphone as source:
                    # Multiple listening strategies for single words
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=3  # Very short for single words
                    )
                
                print("🤔 Processing speech...")
                
                # Try multiple recognition engines
                recognized_text = None
                
                # Strategy 1: Google Speech API (best for single words)
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    recognized_text = text.strip().lower()
                    print(f"👤 Google heard: '{recognized_text}'")
                except sr.RequestError:
                    print("⚠️ Google API unavailable")
                except sr.UnknownValueError:
                    print("🤔 Google couldn't understand")
                
                # Strategy 2: Try offline recognition if Google failed
                if not recognized_text:
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        recognized_text = text.strip().lower()
                        print(f"👤 Offline heard: '{recognized_text}'")
                    except:
                        print("🤔 Offline recognition failed")
                
                # Strategy 3: Fuzzy matching for expected words
                if recognized_text and expected_words:
                    # Check for partial matches
                    for expected in expected_words:
                        if expected.lower() in recognized_text or recognized_text in expected.lower():
                            print(f"✅ Matched '{expected}' from '{recognized_text}'")
                            return expected.lower()
                    
                    # Check for phonetic similarities
                    if self.is_phonetically_similar(recognized_text, expected_words):
                        matched_word = self.get_closest_match(recognized_text, expected_words)
                        print(f"✅ Phonetic match: '{matched_word}' from '{recognized_text}'")
                        return matched_word.lower()
                
                if recognized_text:
                    return recognized_text
                
            except sr.WaitTimeoutError:
                print(f"⏰ No speech detected in attempt {attempts}")
                if attempts < max_attempts:
                    print("🔄 Trying again... Please speak louder!")
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"❌ Error in attempt {attempts}: {e}")
        
        # Final fallback
        print("🖊️ Voice recognition failed. Please type your response:")
        return input("👤 Type here: ").strip().lower()
    
    def is_phonetically_similar(self, heard, expected_words):
        """Check if heard word sounds similar to expected words."""
        heard = heard.lower()
        
        # Common phonetic variations
        phonetic_map = {
            'yes': ['yep', 'yeah', 'ya', 'yea', 'yas', 'yess', 'es'],
            'no': ['nope', 'na', 'nah', 'know', 'now', 'not'],
            'quit': ['exit', 'stop', 'end', 'quite', 'quick'],
            'ok': ['okay', 'k', 'kay'],
            'hello': ['helo', 'hullo', 'halo']
        }
        
        for expected in expected_words:
            variations = phonetic_map.get(expected.lower(), [])
            if any(var in heard or heard in var for var in variations):
                return True
        
        return False
    
    def get_closest_match(self, heard, expected_words):
        """Get the closest phonetic match."""
        heard = heard.lower()
        
        phonetic_map = {
            'yes': ['yep', 'yeah', 'ya', 'yea', 'yas', 'yess', 'es'],
            'no': ['nope', 'na', 'nah', 'know', 'now', 'not'],
            'quit': ['exit', 'stop', 'end', 'quite', 'quick'],
        }
        
        for expected in expected_words:
            variations = phonetic_map.get(expected.lower(), [])
            if any(var in heard or heard in var for var in variations):
                return expected
        
        return expected_words[0] if expected_words else heard
    
    def get_yes_no(self, question):
        """Get yes/no with optimized single word recognition."""
        response = self.listen_for_single_word(
            f"{question} (Say YES or NO clearly)", 
            expected_words=['yes', 'no', 'quit'], 
            timeout=25
        )
        
        if not response:
            print("❓ No response - defaulting to NO")
            return False
        
        response = response.lower()
        
        # Check for quit commands first
        if any(word in response for word in ['quit', 'exit', 'stop', 'end', 'cancel']):
            print("👋 Quitting...")
            return None
        
        # Check yes responses
        if any(word in response for word in ['yes', 'y', 'yeah', 'yep', 'yea', 'ok', 'sure']):
            print("✅ Got YES")
            return True
        
        # Check no responses  
        if any(word in response for word in ['no', 'n', 'nope', 'nah', 'not']):
            print("❌ Got NO")
            return False
        
        # If unclear, ask for confirmation
        print(f"🤔 I heard '{response}' - not sure if that's yes or no")
        return self.get_yes_no("Please say YES or NO very clearly")
    
    def listen_for_text(self, prompt, timeout=25):
        """Listen for longer text responses."""
        self.speak(prompt)
        
        if not VOICE_AVAILABLE:
            return input("👤 Type response: ").strip()
        
        try:
            print("🎤 Listening for your response... (speak clearly)")
            
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=8
                )
            
            print("🤔 Processing...")
            
            # Try Google first
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"👤 You said: '{text}'")
                return text.strip()
            except:
                # Try offline
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    print(f"👤 You said (offline): '{text}'")
                    return text.strip()
                except:
                    pass
        
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Fallback
        print("🖊️ Please type your response:")
        return input("👤 Type here: ").strip()
    
    def create_quick_invoice(self):
        """Create invoice with optimized voice recognition."""
        print("\n" + "="*60)
        print("🎤 OPTIMIZED VOICE INVOICE GENERATOR")
        print("="*60)
        
        self.speak("Let's create an invoice! I'm specially optimized for single word responses like YES and NO.")
        
        # Company info
        if self.config.get("company_info"):
            company_name = self.config["company_info"]["name"]
            use_saved = self.get_yes_no(f"Should I use your saved company '{company_name}'?")
            
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
            
            print(f"\n🎉 SUCCESS!")
            print(f"📄 Invoice: {invoice.invoice_number}")
            print(f"💰 Total: ₹{invoice.total_amount}")
            print(f"📁 Files: {html_file}, {pdf_file}")
            
            self.speak(f"Great! Invoice {invoice.invoice_number} created successfully for {invoice.total_amount} rupees!")
            
        except Exception as e:
            print(f"❌ Error creating invoice: {e}")
    
    def get_company_info(self):
        """Get company info with optimized voice."""
        name = self.listen_for_text("What is your company name?")
        if not name or name.lower() in ['quit', 'exit']:
            return None
        
        city = self.listen_for_text("What city is your company in?")
        if not city:
            city = "Unknown"
        
        state = self.listen_for_text("What state is your company in?")
        if not state:
            state = "Unknown"
        
        # Save for future use
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
    
    def get_customer_info(self):
        """Get customer info with optimized voice."""
        name = self.listen_for_text("What is the customer's name?")
        if not name or name.lower() in ['quit', 'exit']:
            return None
        
        city = self.listen_for_text("What city is the customer in?")
        if not city:
            city = "Unknown"
        
        state = self.listen_for_text("What state is the customer in?")  
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
        """Get item info with optimized voice."""
        description = self.listen_for_text("What item or service are you selling?")
        if not description or description.lower() in ['quit', 'exit']:
            return None
        
        # Auto-suggest HSN
        suggested_hsn_info = self.hsn_validator.auto_suggest_hsn(description)
        hsn_code = "9999"
        gst_rate = 18
        
        if suggested_hsn_info:
            hsn_code = suggested_hsn_info['hsn_code']
            gst_rate = suggested_hsn_info['typical_gst']
            
            use_suggested = self.get_yes_no(f"I suggest HSN code {hsn_code} with {gst_rate}% GST. Should I use this?")
            if use_suggested is None:
                return None
            
            if not use_suggested:
                hsn_code = "9999"
                gst_rate = 18
                print("💡 Using default HSN 9999 with 18% GST")
        
        # Get price
        price_input = self.listen_for_text("What is the price per unit?")
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
    
    def test_single_words(self):
        """Test single word recognition."""
        print("\n🧪 SINGLE WORD RECOGNITION TEST")
        print("="*40)
        
        test_words = ['yes', 'no', 'hello', 'quit']
        
        for word in test_words:
            print(f"\n📢 Test: Please say '{word.upper()}'")
            response = self.listen_for_single_word(f"Say '{word}' clearly", [word])
            
            if response and word in response.lower():
                print(f"✅ SUCCESS: Recognized '{word}' correctly!")
            else:
                print(f"❌ FAILED: Expected '{word}' but got '{response}'")
        
        print("\n🏁 Single word test complete!")


def main():
    """Main function."""
    print("🎤 Optimized Voice Invoice Generator")
    print("Specially designed for better YES/NO recognition")
    print("Say 'quit' or 'exit' anytime to stop")
    
    try:
        app = OptimizedVoiceInvoice()
        
        print("\nWhat would you like to do?")
        print("1. Create Invoice")
        print("2. Test Single Word Recognition")
        
        choice = input("Enter 1 or 2: ").strip()
        
        if choice == "2":
            app.test_single_words()
        else:
            app.create_quick_invoice()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
