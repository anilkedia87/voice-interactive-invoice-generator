#!/usr/bin/env python3
"""
Voice Interactive Invoice Generator
Talk to create invoices! Uses speech recognition and text-to-speech.
"""

import sys
import os
import json
from decimal import Decimal
from datetime import datetime
import threading
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.company import Company
from models.customer import Customer
from models.invoice import Invoice, InvoiceItem
from templates.invoice_template import InvoiceTemplate
from services.hsn_validator import HSNValidator

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠️  Voice features require: pip install speechrecognition pyttsx3 pyaudio")

class VoiceInvoiceGenerator:
    def __init__(self):
        self.config_file = "invoice_config.json"
        self.load_config()
        self.hsn_validator = HSNValidator()
        
        if VOICE_AVAILABLE:
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Initialize text-to-speech
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS voice
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 180)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
            
            # Adjust for ambient noise
            print("🎤 Adjusting microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
    def load_config(self):
        """Load configuration including last invoice number."""
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
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.speak(f"Warning: Could not save config: {e}")
    
    def speak(self, text):
        """Convert text to speech."""
        print(f"🤖 Assistant: {text}")
        if VOICE_AVAILABLE:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
    
    def listen(self, prompt="", timeout=10, phrase_time_limit=5):
        """Listen for speech input."""
        if not VOICE_AVAILABLE:
            return input(f"{prompt}: ").strip()
        
        self.speak(prompt)
        print("🎤 Listening... (speak now)")
        
        try:
            with self.microphone as source:
                # Listen for audio input
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            # Use Google's speech recognition
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"👤 You said: {text}")
                return text.strip()
            except sr.UnknownValueError:
                self.speak("Sorry, I couldn't understand that. Could you repeat?")
                return self.listen("Please say it again", timeout=5, phrase_time_limit=3)
            except sr.RequestError as e:
                self.speak("Sorry, there was an error with the speech service. Let me get text input instead.")
                return input(f"{prompt}: ").strip()
                
        except sr.WaitTimeoutError:
            self.speak("I didn't hear anything. Let me try text input.")
            return input(f"{prompt}: ").strip()
    
    def get_yes_no(self, question):
        """Get yes/no response via voice."""
        response = self.listen(f"{question} Please say yes or no").lower()
        
        # Handle various affirmative responses
        if any(word in response for word in ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'correct', 'right']):
            return True
        elif any(word in response for word in ['no', 'nope', 'nah', 'wrong', 'incorrect']):
            return False
        else:
            self.speak("I need a yes or no answer.")
            return self.get_yes_no(question)
    
    def get_number_input(self, prompt):
        """Get numeric input via voice with error handling."""
        while True:
            try:
                response = self.listen(prompt)
                
                # Handle spelled out numbers
                number_words = {
                    'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
                    'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
                    'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
                    'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
                    'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
                    'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
                    'eighty': '80', 'ninety': '90', 'hundred': '100', 'thousand': '1000'
                }
                
                # Replace spelled numbers with digits
                for word, digit in number_words.items():
                    response = response.replace(word, digit)
                
                # Extract numbers from response
                import re
                numbers = re.findall(r'\d+\.?\d*', response)
                
                if numbers:
                    return Decimal(numbers[0])
                else:
                    self.speak("I couldn't find a number in your response. Please say the number clearly.")
            except Exception:
                self.speak("Please say the number again.")
    
    def get_next_invoice_number(self):
        """Generate next invoice number automatically."""
        self.config["last_invoice_number"] += 1
        invoice_num = self.config["last_invoice_number"]
        return f"{self.config['invoice_prefix']}-{invoice_num:04d}"
    
    def setup_company_info(self):
        """Get company information via voice."""
        self.speak("Let's set up your company information. I'll ask you a few questions.")
        
        company_info = {}
        company_info['name'] = self.listen("What is your company name?")
        company_info['address'] = self.listen("What is your company address?")
        company_info['city'] = self.listen("What city are you in?")
        company_info['state'] = self.listen("What state are you in?")
        company_info['pincode'] = self.listen("What is your pincode or zip code?")
        
        has_gst = self.get_yes_no("Do you have a GST number?")
        if has_gst:
            company_info['gstin'] = self.listen("Please say your GST number")
        
        has_phone = self.get_yes_no("Would you like to add a phone number?")
        if has_phone:
            company_info['phone'] = self.listen("What is your phone number?")
        
        has_email = self.get_yes_no("Would you like to add an email address?")
        if has_email:
            company_info['email'] = self.listen("What is your email address?")
        
        # Bank details
        has_bank = self.get_yes_no("Would you like to add bank details for payments?")
        if has_bank:
            company_info['bank_name'] = self.listen("What is your bank name?")
            company_info['bank_account'] = self.listen("What is your account number?")
            company_info['ifsc_code'] = self.listen("What is your IFSC code?")
        
        # Remove empty values
        company_info = {k: v for k, v in company_info.items() if v and v.strip()}
        
        self.config['company_info'] = company_info
        self.save_config()
        
        self.speak("Great! Your company information has been saved.")
        return company_info
    
    def get_company_info(self):
        """Get company info (use saved or ask for new)."""
        if self.config.get('company_info'):
            company_name = self.config['company_info']['name']
            use_saved = self.get_yes_no(f"Should I use your saved company information for {company_name}?")
            
            if use_saved:
                self.speak(f"Perfect! Using {company_name} details.")
                return self.config['company_info']
        
        return self.setup_company_info()
    
    def get_customer_info(self):
        """Get customer information via voice."""
        self.speak("Now let's get the customer information.")
        
        customer_info = {}
        customer_info['name'] = self.listen("What is the customer's name?")
        customer_info['address'] = self.listen("What is the customer's address?")
        customer_info['city'] = self.listen("What city is the customer in?")
        customer_info['state'] = self.listen("What state is the customer in?")
        customer_info['pincode'] = self.listen("What is the customer's pincode?")
        
        has_gst = self.get_yes_no("Does the customer have a GST number?")
        if has_gst:
            customer_info['gstin'] = self.listen("Please say the customer's GST number")
        
        has_phone = self.get_yes_no("Would you like to add the customer's phone number?")
        if has_phone:
            customer_info['phone'] = self.listen("What is the customer's phone number?")
        
        # Remove empty values
        return {k: v for k, v in customer_info.items() if v and v.strip()}
    
    def get_items_info(self):
        """Get invoice items via voice."""
        self.speak("Now let's add the products or services to your invoice.")
        
        items = []
        item_number = 1
        
        while True:
            self.speak(f"Let's add item number {item_number}.")
            
            description = self.listen("What is the name or description of this item?")
            
            if not description or description.lower() in ['done', 'finished', 'no more', 'stop', 'end']:
                if items:
                    break
                else:
                    self.speak("You need at least one item for the invoice. Let's add one.")
                    continue
            
            # Auto-suggest HSN code
            suggested_hsn_info = self.hsn_validator.auto_suggest_hsn(description)
            if suggested_hsn_info:
                suggested_hsn = suggested_hsn_info['hsn_code']
                self.speak(f"Based on '{description}', I suggest HSN code {suggested_hsn} for {suggested_hsn_info['description']}")
                use_suggested = self.get_yes_no("Should I use this HSN code?")
                
                if use_suggested:
                    hsn_code = suggested_hsn
                    # Auto-suggest GST rate
                    suggested_gst = suggested_hsn_info['typical_gst']
                    self.speak(f"The typical GST rate for this item is {suggested_gst} percent")
                    use_suggested_gst = self.get_yes_no("Should I use this GST rate?")
                    
                    if use_suggested_gst:
                        gst_rate = Decimal(str(suggested_gst))
                    else:
                        gst_rate = self.get_number_input("What GST rate should I use? Say the percentage")
                else:
                    hsn_code = self.listen("What HSN or SAC code should I use?")
                    gst_rate = self.get_number_input("What GST rate should I use? Say the percentage")
            else:
                self.speak("I couldn't suggest an HSN code for this item.")
                hsn_code = self.listen("What HSN or SAC code should I use? You can say 9999 for general items")
                gst_rate = self.get_number_input("What GST rate should I use? Say the percentage")
            
            quantity = self.get_number_input("How many units of this item?")
            unit_price = self.get_number_input("What is the price per unit in rupees?")
            
            unit = self.listen("What is the unit of measurement? For example, pieces, kilograms, services")
            if not unit:
                unit = "Nos"
            
            # Optional discount
            has_discount = self.get_yes_no("Is there any discount on this item?")
            
            discount_percentage = Decimal('0')
            discount_amount = Decimal('0')
            
            if has_discount:
                discount_type = self.listen("Is it a percentage discount or fixed amount discount? Say percentage or amount")
                
                if 'percentage' in discount_type.lower() or 'percent' in discount_type.lower():
                    discount_percentage = self.get_number_input("What percentage discount?")
                else:
                    discount_amount = self.get_number_input("What is the discount amount in rupees?")
            
            item_data = {
                'description': description,
                'hsn_code': hsn_code,
                'quantity': quantity,
                'unit_price': unit_price,
                'unit': unit,
                'gst_rate': gst_rate,
                'discount_percentage': discount_percentage,
                'discount_amount': discount_amount
            }
            
            items.append(item_data)
            
            # Show running total
            item_obj = InvoiceItem(**item_data)
            self.speak(f"Item total is {float(item_obj.total_amount):.2f} rupees including GST")
            
            item_number += 1
            
            # Ask if more items
            if not self.get_yes_no("Would you like to add another item?"):
                break
        
        return items if items else None
    
    def create_invoice(self):
        """Create invoice with voice inputs."""
        self.speak("Welcome to the Voice Interactive Invoice Generator! Let's create your invoice together.")
        
        try:
            # Get company information
            company_data = self.get_company_info()
            
            # Get customer information
            customer_data = self.get_customer_info()
            
            # Get invoice items
            items_data = self.get_items_info()
            
            if not items_data:
                self.speak("No items were added. Cannot create invoice.")
                return None
            
            # Create objects
            company = Company(**company_data)
            customer = Customer(**customer_data)
            
            # Create items
            items = []
            for item_data in items_data:
                items.append(InvoiceItem(**item_data))
            
            # Create invoice with auto-generated number
            invoice = Invoice(company=company, customer=customer, items=items)
            
            # Override with our auto-generated invoice number
            invoice.invoice_number = self.get_next_invoice_number()
            
            # Save the updated config with new invoice number
            self.save_config()
            
            return invoice
            
        except KeyboardInterrupt:
            self.speak("Invoice creation cancelled.")
            return None
        except Exception as e:
            self.speak(f"Error creating invoice: {str(e)}")
            return None
    
    def announce_invoice_summary(self, invoice):
        """Announce invoice summary via voice."""
        self.speak("Excellent! Your invoice has been created successfully!")
        
        self.speak(f"Invoice number {invoice.invoice_number}")
        self.speak(f"Company: {invoice.company.name}")
        self.speak(f"Customer: {invoice.customer.name}")
        self.speak(f"Total items: {len(invoice.items)}")
        
        if invoice.is_interstate:
            self.speak("This is an interstate transaction, so IGST will be applied")
        else:
            self.speak("This is an intrastate transaction, so CGST and SGST will be applied")
        
        total_amount = float(invoice.total_invoice_amount)
        self.speak(f"The final amount is {total_amount:.2f} rupees")
        
        # Announce amount in words
        self.speak(f"In words: {invoice.total_amount_in_words}")
    
    def generate_files(self, invoice):
        """Generate invoice files and announce."""
        self.speak("Now I'm generating your invoice files.")
        
        try:
            template_engine = InvoiceTemplate()
            
            # Ensure output directory exists
            os.makedirs("output", exist_ok=True)
            
            # Generate filename with invoice number
            filename = f"invoice_{invoice.invoice_number.replace('-', '_')}"
            html_file = f"output/{filename}.html"
            
            # Generate HTML
            template_engine.save_html_invoice(invoice, html_file)
            self.speak(f"I've saved your invoice as {filename} dot H T M L in the output folder")
            
            # Try to generate PDF if weasyprint is available
            try:
                pdf_file = f"output/{filename}.pdf"
                template_engine.generate_pdf_invoice(invoice, pdf_file)
                self.speak("I've also created a PDF version for you")
            except ImportError:
                self.speak("For PDF generation, you can install weasyprint")
            except Exception:
                pass
            
            self.speak("You can open the HTML file in your web browser to view and print your professional invoice")
            
        except Exception as e:
            self.speak(f"There was an error generating the files: {str(e)}")
    
    def run(self):
        """Run the voice interactive invoice generator."""
        if not VOICE_AVAILABLE:
            self.speak("Voice features are not available. Please install required packages:")
            print("pip install speechrecognition pyttsx3 pyaudio")
            print("Note: On macOS you may need: brew install portaudio")
            print("On Ubuntu: sudo apt-get install portaudio19-dev python3-pyaudio")
            return
        
        try:
            invoice = self.create_invoice()
            
            if invoice:
                self.announce_invoice_summary(invoice)
                self.generate_files(invoice)
                
                self.speak("Your invoice has been created successfully! Would you like to create another one?")
                
                # Ask if user wants to create another
                if self.get_yes_no(""):
                    self.speak("Great! Let's create another invoice.")
                    self.run()
                else:
                    self.speak("Thank you for using the Voice Interactive Invoice Generator. Have a great day!")
            else:
                self.speak("Invoice creation was cancelled or failed. Goodbye!")
                
        except KeyboardInterrupt:
            self.speak("Voice invoice generator stopped by user. Goodbye!")
        except Exception as e:
            self.speak(f"An unexpected error occurred: {str(e)}")

def main():
    """Main function."""
    print("🎤 Voice Interactive Invoice Generator")
    print("=" * 40)
    
    if not VOICE_AVAILABLE:
        print("❌ Voice features not available!")
        print("📦 Install required packages:")
        print("   pip install speechrecognition pyttsx3")
        print("   # On macOS: brew install portaudio")
        print("   # On Ubuntu: sudo apt-get install portaudio19-dev python3-pyaudio")
        return
    
    generator = VoiceInvoiceGenerator()
    generator.run()

if __name__ == "__main__":
    main()
