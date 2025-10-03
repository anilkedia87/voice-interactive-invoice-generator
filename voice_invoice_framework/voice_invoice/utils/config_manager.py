"""
Configuration Manager Module

Handles application configuration, settings, and preferences.
Provides centralized configuration management with defaults.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Manages application configuration and settings.
    
    Features:
    - JSON-based configuration files
    - Default configuration fallbacks
    - Environment variable overrides
    - User preferences persistence
    - Validation and schema support
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the Configuration Manager.
        
        Args:
            config_dir (str, optional): Custom configuration directory
        """
        self.config_dir = Path(config_dir) if config_dir else self._get_default_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.user_prefs_file = self.config_dir / "user_preferences.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configurations
        self._default_config = self._get_default_config()
        self._user_config = self._load_user_config()
        self._user_preferences = self._load_user_preferences()
        
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory."""
        # Use user's home directory for config
        home_dir = Path.home()
        return home_dir / ".voice_invoice" / "config"
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get the default application configuration."""
        return {
            "application": {
                "name": "Voice Interactive Invoice Generator",
                "version": "1.0.0",
                "debug": False,
                "log_level": "INFO"
            },
            "voice": {
                "enabled": True,
                "energy_threshold": 300,
                "pause_threshold": 0.8,
                "phrase_threshold": 0.3,
                "timeout": 5,
                "phrase_time_limit": 10,
                "max_attempts": 3,
                "tts_rate": 200,
                "tts_volume": 0.9,
                "tts_voice_gender": "female",
                "calibrate_on_start": True
            },
            "gui": {
                "theme": "dark",
                "window_width": 1200,
                "window_height": 800,
                "font_family": "Helvetica",
                "font_size": 12,
                "console_font_family": "Consolas",
                "console_font_size": 12,
                "colors": {
                    "primary": "#2c3e50",
                    "secondary": "#34495e", 
                    "accent": "#3498db",
                    "success": "#27ae60",
                    "warning": "#f39c12",
                    "error": "#e74c3c",
                    "text": "#ecf0f1",
                    "text_secondary": "#bdc3c7"
                }
            },
            "invoice": {
                "default_gst_rate": 18.0,
                "currency": "INR",
                "currency_symbol": "₹",
                "date_format": "%d/%m/%Y",
                "invoice_number_prefix": "INV",
                "auto_calculate_totals": True,
                "decimal_places": 2
            },
            "company": {
                "default_company_name": "",
                "default_address": "",
                "default_gstin": "",
                "default_phone": "",
                "default_email": ""
            },
            "export": {
                "default_format": "pdf",
                "output_directory": "invoices",
                "filename_template": "{invoice_number}_{date}_{customer_name}",
                "open_after_export": True
            },
            "backup": {
                "enabled": True,
                "backup_directory": "backups",
                "max_backups": 10,
                "auto_backup": True
            }
        }
        
    def _load_user_config(self) -> Dict[str, Any]:
        """Load user configuration from file."""
        if not self.config_file.exists():
            # Create default config file
            self._save_user_config(self._default_config)
            return self._default_config.copy()
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # Merge with defaults (defaults take precedence for missing keys)
            merged_config = self._merge_configs(self._default_config, user_config)
            return merged_config
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️  Error loading config file: {e}")
            print("📁 Using default configuration")
            return self._default_config.copy()
            
    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences from file."""
        if not self.user_prefs_file.exists():
            return {}
            
        try:
            with open(self.user_prefs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️  Error loading preferences: {e}")
            return {}
            
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge user config with defaults.
        
        Args:
            default (dict): Default configuration
            user (dict): User configuration
            
        Returns:
            dict: Merged configuration
        """
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged
        
    def _save_user_config(self, config: Dict[str, Any]):
        """Save user configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error saving config: {e}")
            
    def _save_user_preferences(self):
        """Save user preferences to file."""
        try:
            with open(self.user_prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self._user_preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error saving preferences: {e}")
            
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path.
        
        Args:
            key_path (str): Dot-separated key path (e.g., 'voice.timeout')
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        keys = key_path.split('.')
        value = self._user_config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path: str, value: Any, save: bool = True):
        """
        Set configuration value by dot-separated key path.
        
        Args:
            key_path (str): Dot-separated key path
            value (Any): Value to set
            save (bool): Whether to save to file immediately
        """
        keys = key_path.split('.')
        config = self._user_config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        # Set the value
        config[keys[-1]] = value
        
        if save:
            self._save_user_config(self._user_config)
            
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get user preference value.
        
        Args:
            key (str): Preference key
            default (Any): Default value if not found
            
        Returns:
            Any: Preference value
        """
        return self._user_preferences.get(key, default)
        
    def set_preference(self, key: str, value: Any, save: bool = True):
        """
        Set user preference value.
        
        Args:
            key (str): Preference key
            value (Any): Preference value
            save (bool): Whether to save immediately
        """
        self._user_preferences[key] = value
        
        if save:
            self._save_user_preferences()
            
    def get_voice_config(self) -> Dict[str, Any]:
        """Get voice-specific configuration."""
        return self.get('voice', {})
        
    def get_gui_config(self) -> Dict[str, Any]:
        """Get GUI-specific configuration."""
        return self.get('gui', {})
        
    def get_invoice_config(self) -> Dict[str, Any]:
        """Get invoice-specific configuration."""
        return self.get('invoice', {})
        
    def get_company_config(self) -> Dict[str, Any]:
        """Get company-specific configuration."""
        return self.get('company', {})
        
    def reset_to_defaults(self, save: bool = True):
        """
        Reset configuration to defaults.
        
        Args:
            save (bool): Whether to save immediately
        """
        self._user_config = self._default_config.copy()
        
        if save:
            self._save_user_config(self._user_config)
            
    def export_config(self, filepath: str):
        """
        Export current configuration to a file.
        
        Args:
            filepath (str): Export file path
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._user_config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuration exported to: {filepath}")
        except Exception as e:
            print(f"⚠️  Error exporting config: {e}")
            
    def import_config(self, filepath: str, save: bool = True):
        """
        Import configuration from a file.
        
        Args:
            filepath (str): Import file path
            save (bool): Whether to save immediately
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                
            # Merge with defaults to ensure all required keys exist
            self._user_config = self._merge_configs(self._default_config, imported_config)
            
            if save:
                self._save_user_config(self._user_config)
                
            print(f"✅ Configuration imported from: {filepath}")
        except Exception as e:
            print(f"⚠️  Error importing config: {e}")
            
    def validate_config(self) -> bool:
        """
        Validate current configuration.
        
        Returns:
            bool: True if configuration is valid
        """
        # Basic validation - ensure required sections exist
        required_sections = ['application', 'voice', 'gui', 'invoice']
        
        for section in required_sections:
            if section not in self._user_config:
                print(f"⚠️  Missing required config section: {section}")
                return False
                
        # Additional validation logic can be added here
        return True
        
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information and status."""
        return {
            "config_dir": str(self.config_dir),
            "config_file": str(self.config_file),
            "preferences_file": str(self.user_prefs_file),
            "config_exists": self.config_file.exists(),
            "preferences_exist": self.user_prefs_file.exists(),
            "is_valid": self.validate_config(),
            "version": self.get('application.version', '1.0.0')
        }
