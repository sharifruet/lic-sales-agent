"""Internationalization service for multi-language support."""
from typing import Dict, Optional
from pathlib import Path
import json


class I18nService:
    """Service for internationalization and translation."""
    
    def __init__(self, translations_path: Optional[Path] = None):
        self.translations_path = translations_path or Path(__file__).parent.parent.parent / "translations"
        self.translations_path.mkdir(exist_ok=True)
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_language = "en"
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files."""
        # Load default English translations
        default_file = self.translations_path / "en.json"
        if default_file.exists():
            with open(default_file, 'r', encoding='utf-8') as f:
                self.translations["en"] = json.load(f)
        else:
            # Create default English translations
            self.translations["en"] = self._get_default_translations()
            self._save_translations("en")
        
        # Load other languages
        for lang_file in self.translations_path.glob("*.json"):
            if lang_file.stem != "en":
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_file.stem] = json.load(f)
    
    def _get_default_translations(self) -> Dict[str, str]:
        """Get default English translations."""
        return {
            "greeting": "Hello! I'm an AI life insurance agent. How can I help you today?",
            "intro": "I'm here to help you understand life insurance options and find the right coverage for you.",
            "ask_name": "What's your name?",
            "ask_age": "How old are you?",
            "ask_phone": "What's your phone number?",
            "ask_nid": "What's your National ID number?",
            "ask_address": "What's your address?",
            "thank_you": "Thank you for your information!",
            "policy_info": "Here are some policies that might interest you:",
            "interested": "That sounds great! I'd be happy to help you with that.",
            "not_interested": "I understand. Feel free to reach out if you have questions in the future.",
            "goodbye": "Thank you for your time. Have a great day!",
            "error": "I'm sorry, I didn't understand that. Could you please repeat?",
            "processing": "Let me check that for you...",
        }
    
    def _save_translations(self, language: str):
        """Save translations to file."""
        lang_file = self.translations_path / f"{language}.json"
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(self.translations[language], f, indent=2, ensure_ascii=False)
    
    def translate(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """Translate a key to the specified language."""
        lang = language or self.default_language
        
        # Get translation
        translation = self.translations.get(lang, {}).get(key, "")
        
        # Fallback to English if not found
        if not translation:
            translation = self.translations.get(self.default_language, {}).get(key, key)
        
        # Format with kwargs if provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError:
                pass
        
        return translation
    
    def set_language(self, language: str):
        """Set default language."""
        if language in self.translations:
            self.default_language = language
    
    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages."""
        return list(self.translations.keys())
    
    def add_translation(self, language: str, key: str, value: str):
        """Add or update a translation."""
        if language not in self.translations:
            self.translations[language] = {}
        
        self.translations[language][key] = value
        self._save_translations(language)

