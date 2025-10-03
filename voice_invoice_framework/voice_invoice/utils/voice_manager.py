"""
Voice Manager Module

Handles all voice recognition and text-to-speech functionality.
Clean abstraction for voice interactions with fallback support.
"""

import threading
import time
from typing import Optional, Dict, Any

# Voice dependencies with graceful fallback
VOICE_AVAILABLE = True
try:
    import speech_recognition as sr
    import pyttsx3
except ImportError:
    VOICE_AVAILABLE = False


class VoiceManager:
    """
    Manages voice recognition and text-to-speech functionality.
    
    Features:
    - Speech recognition with Google Speech API and Sphinx fallback
    - Text-to-speech with configurable voice settings
    - Ambient noise calibration
    - Retry logic with timeout handling
    - Thread-safe operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Voice Manager.
        
        Args:
            config (dict, optional): Voice configuration parameters
        """
        self.config = config or self._get_default_config()
        self.is_available = VOICE_AVAILABLE
        
        if not self.is_available:
            print("⚠️  Voice libraries not available. Text input only.")
            return
            
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configure recognition parameters
        self._configure_recognition()
        
        # Initialize TTS engine (per-use to avoid conflicts)
        self.tts_lock = threading.Lock()
        
        # Calibrate ambient noise
        self._calibrate_ambient_noise()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default voice configuration."""
        return {
            'energy_threshold': 300,
            'pause_threshold': 0.8,
            'phrase_threshold': 0.3,
            'timeout': 5,
            'phrase_time_limit': 10,
            'tts_rate': 200,
            'tts_volume': 0.9,
            'tts_voice_gender': 'female'
        }
        
    def _configure_recognition(self):
        """Configure speech recognition parameters."""
        if not self.is_available:
            return
            
        self.recognizer.energy_threshold = self.config['energy_threshold']
        self.recognizer.pause_threshold = self.config['pause_threshold']
        self.recognizer.phrase_threshold = self.config['phrase_threshold']
        
    def _calibrate_ambient_noise(self):
        """Calibrate for ambient noise."""
        if not self.is_available:
            return
            
        try:
            print("🎤 Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"✅ Microphone calibrated. Energy threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            print(f"⚠️  Could not calibrate microphone: {e}")
            
    def _create_tts_engine(self):
        """Create a new TTS engine for thread safety."""
        if not self.is_available:
            return None
            
        try:
            engine = pyttsx3.init()
            
            # Configure voice settings
            engine.setProperty('rate', self.config['tts_rate'])
            engine.setProperty('volume', self.config['tts_volume'])
            
            # Set voice gender preference
            voices = engine.getProperty('voices')
            if voices:
                preferred_voice = None
                gender_pref = self.config['tts_voice_gender'].lower()
                
                for voice in voices:
                    if gender_pref in voice.name.lower():
                        preferred_voice = voice.id
                        break
                
                if preferred_voice:
                    engine.setProperty('voice', preferred_voice)
                    
            return engine
        except Exception as e:
            print(f"⚠️  Could not initialize TTS engine: {e}")
            return None
            
    def speak(self, text: str) -> bool:
        """
        Speak the given text using text-to-speech.
        
        Args:
            text (str): Text to speak
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            print(f"🔊 [TTS]: {text}")
            return False
            
        with self.tts_lock:
            engine = self._create_tts_engine()
            if not engine:
                return False
                
            try:
                engine.say(text)
                engine.runAndWait()
                return True
            except Exception as e:
                print(f"⚠️  TTS Error: {e}")
                return False
            finally:
                try:
                    engine.stop()
                except:
                    pass
                    
    def listen(self, prompt: str = None, timeout: Optional[int] = None) -> Optional[str]:
        """
        Listen for voice input and convert to text.
        
        Args:
            prompt (str, optional): Prompt to speak before listening
            timeout (int, optional): Listening timeout in seconds
            
        Returns:
            str: Recognized text, or None if failed
        """
        if not self.is_available:
            if prompt:
                print(f"🔊 [TTS]: {prompt}")
            return None
            
        if prompt:
            self.speak(prompt)
            
        timeout = timeout or self.config['timeout']
        phrase_time_limit = self.config['phrase_time_limit']
        
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
            print("🔄 Processing speech...")
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"✅ Recognized: {text}")
                return text.strip()
            except sr.UnknownValueError:
                print("❓ Could not understand audio")
            except sr.RequestError as e:
                print(f"⚠️  Google API error: {e}")
                
                # Fallback to Sphinx
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    print(f"✅ Recognized (Sphinx): {text}")
                    return text.strip()
                except sr.UnknownValueError:
                    print("❓ Could not understand audio (Sphinx)")
                except sr.RequestError as e:
                    print(f"⚠️  Sphinx error: {e}")
                    
        except sr.WaitTimeoutError:
            print("⏰ Listening timeout")
        except Exception as e:
            print(f"⚠️  Voice recognition error: {e}")
            
        return None
        
    def get_confirmation(self, prompt: str, max_attempts: int = 3) -> bool:
        """
        Get confirmation using CONFIRM/SKIP keywords.
        
        Args:
            prompt (str): Confirmation prompt
            max_attempts (int): Maximum number of attempts
            
        Returns:
            bool: True for CONFIRM, False for SKIP
        """
        for attempt in range(max_attempts):
            full_prompt = f"{prompt} Say 'CONFIRM' to proceed or 'SKIP' to skip."
            response = self.listen(full_prompt)
            
            if response:
                response = response.upper().strip()
                if 'CONFIRM' in response:
                    return True
                elif 'SKIP' in response:
                    return False
                    
            print(f"⚠️  Please say 'CONFIRM' or 'SKIP'. Attempt {attempt + 1}/{max_attempts}")
            
        print("❌ No valid response received. Defaulting to SKIP.")
        return False
        
    def get_voice_input(self, prompt: str, max_attempts: int = 3, timeout: int = 10) -> Optional[str]:
        """
        Get voice input with retry logic.
        
        Args:
            prompt (str): Input prompt
            max_attempts (int): Maximum number of attempts
            timeout (int): Timeout per attempt
            
        Returns:
            str: Voice input or None if failed
        """
        for attempt in range(max_attempts):
            response = self.listen(prompt, timeout)
            if response:
                return response
                
            if attempt < max_attempts - 1:
                retry_prompt = f"I didn't catch that. Attempt {attempt + 2}/{max_attempts}."
                print(retry_prompt)
                
        return None
        
    def is_voice_available(self) -> bool:
        """Check if voice functionality is available."""
        return self.is_available
