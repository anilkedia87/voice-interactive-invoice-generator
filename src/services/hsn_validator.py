"""
HSN Code Validator Service
Handles validation and lookup of HSN codes for GST compliance.
"""

from typing import Dict, Optional, List
import re


class HSNValidator:
    """Service for validating and managing HSN codes."""
    
    # Comprehensive HSN codes database with keywords for auto-suggestion
    HSN_DATABASE = {
        # Food items
        "1001": {"description": "Wheat and meslin", "typical_gst": 0, "keywords": ["wheat", "meslin", "grain"]},
        "1006": {"description": "Rice", "typical_gst": 5, "keywords": ["rice", "basmati", "paddy"]},
        "1701": {"description": "Cane or beet sugar", "typical_gst": 5, "keywords": ["sugar", "cane", "beet", "sweetener"]},
        "1704": {"description": "Sugar confectionery", "typical_gst": 18, "keywords": ["candy", "chocolate", "confectionery", "sweet"]},
        "0713": {"description": "Dried leguminous vegetables", "typical_gst": 0, "keywords": ["dal", "pulse", "lentil", "chickpea", "bean"]},
        "0901": {"description": "Coffee", "typical_gst": 5, "keywords": ["coffee", "beans", "instant coffee"]},
        "0902": {"description": "Tea", "typical_gst": 5, "keywords": ["tea", "chai", "green tea", "black tea"]},
        
        # Textiles & Garments
        "5208": {"description": "Woven fabrics of cotton", "typical_gst": 5, "keywords": ["cotton", "fabric", "cloth", "textile"]},
        "6109": {"description": "T-shirts, singlets and other vests", "typical_gst": 12, "keywords": ["tshirt", "t-shirt", "shirt", "vest", "singlet", "top", "blouse"]},
        "6203": {"description": "Men's or boys' suits, ensembles", "typical_gst": 12, "keywords": ["suit", "blazer", "jacket", "trouser", "pant", "formal wear"]},
        "6204": {"description": "Women's or girls' suits, ensembles", "typical_gst": 12, "keywords": ["dress", "skirt", "kurti", "saree", "ladies wear", "women wear"]},
        "6115": {"description": "Pantyhose, tights, stockings, socks", "typical_gst": 12, "keywords": ["socks", "stocking", "pantyhose", "hosiery"]},
        "6402": {"description": "Footwear with outer soles", "typical_gst": 18, "keywords": ["shoes", "sandal", "footwear", "boot", "slipper", "chappal"]},
        
        # Electronics & Computers
        "8471": {"description": "Automatic data processing machines", "typical_gst": 18, "keywords": ["computer", "laptop", "desktop", "pc", "processor", "cpu"]},
        "8517": {"description": "Telephone sets, mobile phones", "typical_gst": 18, "keywords": ["mobile", "phone", "smartphone", "telephone", "cell phone"]},
        "8528": {"description": "Monitors and projectors", "typical_gst": 18, "keywords": ["monitor", "screen", "display", "projector", "tv", "television"]},
        "8504": {"description": "Electrical transformers", "typical_gst": 18, "keywords": ["transformer", "electrical", "power supply", "adapter"]},
        "8519": {"description": "Sound recording apparatus", "typical_gst": 18, "keywords": ["speaker", "audio", "sound", "music system", "headphone"]},
        "8473": {"description": "Parts of machines of heading 8471", "typical_gst": 18, "keywords": ["keyboard", "mouse", "computer parts", "accessories"]},
        
        # Automobiles & Vehicles
        "8703": {"description": "Motor cars and other motor vehicles", "typical_gst": 28, "keywords": ["car", "automobile", "vehicle", "sedan", "hatchback"]},
        "8711": {"description": "Motorcycles", "typical_gst": 28, "keywords": ["motorcycle", "bike", "scooter", "two wheeler"]},
        "8708": {"description": "Parts and accessories of motor vehicles", "typical_gst": 28, "keywords": ["auto parts", "spare parts", "car parts", "vehicle parts"]},
        
        # Chemicals & Cosmetics
        "2915": {"description": "Saturated acyclic monocarboxylic acids", "typical_gst": 18, "keywords": ["chemical", "acid", "industrial chemical"]},
        "3004": {"description": "Medicaments", "typical_gst": 12, "keywords": ["medicine", "drug", "pharmaceutical", "tablet", "capsule", "syrup"]},
        "3307": {"description": "Perfumes and cosmetics", "typical_gst": 18, "keywords": ["perfume", "cosmetic", "makeup", "beauty", "cream", "lotion"]},
        "3401": {"description": "Soap; organic surface-active products", "typical_gst": 18, "keywords": ["soap", "detergent", "shampoo", "cleaning"]},
        
        # Furniture & Household
        "9401": {"description": "Seats", "typical_gst": 18, "keywords": ["chair", "seat", "sofa", "bench", "stool"]},
        "9403": {"description": "Other furniture", "typical_gst": 18, "keywords": ["furniture", "table", "desk", "cabinet", "wardrobe", "bed"]},
        "7013": {"description": "Glassware", "typical_gst": 18, "keywords": ["glass", "glassware", "tumbler", "bottle", "jar"]},
        "6912": {"description": "Ceramic tableware", "typical_gst": 18, "keywords": ["ceramic", "plate", "cup", "bowl", "pottery"]},
        
        # Books & Stationery
        "4901": {"description": "Printed books, brochures", "typical_gst": 5, "keywords": ["book", "novel", "textbook", "magazine", "publication"]},
        "4802": {"description": "Uncoated paper", "typical_gst": 12, "keywords": ["paper", "sheet", "notebook", "copy"]},
        "9608": {"description": "Ball point pens", "typical_gst": 18, "keywords": ["pen", "pencil", "marker", "stationery"]},
        
        # Services (SAC codes)
        "998341": {"description": "Information technology software services", "typical_gst": 18, "keywords": ["software", "development", "programming", "app", "website"]},
        "998342": {"description": "Information technology consulting services", "typical_gst": 18, "keywords": ["consulting", "it service", "technical", "support"]},
        "998343": {"description": "Information technology support services", "typical_gst": 18, "keywords": ["support", "maintenance", "repair", "troubleshooting"]},
        "997213": {"description": "Legal services", "typical_gst": 18, "keywords": ["legal", "lawyer", "attorney", "court", "law"]},
        "997212": {"description": "Accounting and auditing services", "typical_gst": 18, "keywords": ["accounting", "audit", "tax", "financial", "bookkeeping"]},
        "996511": {"description": "Transportation of goods by road", "typical_gst": 5, "keywords": ["transport", "delivery", "shipping", "logistics", "courier"]},
        "997311": {"description": "Architectural services", "typical_gst": 18, "keywords": ["architecture", "design", "planning", "construction design"]},
        "998313": {"description": "Market research and public opinion polling", "typical_gst": 18, "keywords": ["research", "survey", "marketing", "analysis"]},
        
        # Jewelry & Precious metals
        "7113": {"description": "Articles of jewelry", "typical_gst": 3, "keywords": ["jewelry", "gold", "silver", "ornament", "jewellery"]},
        "7108": {"description": "Gold", "typical_gst": 3, "keywords": ["gold", "precious metal"]},
        
        # Toys & Games  
        "9503": {"description": "Toys", "typical_gst": 18, "keywords": ["toy", "game", "doll", "puzzle", "plaything"]},
        
        # Agricultural products
        "0713": {"description": "Dried leguminous vegetables", "typical_gst": 0, "keywords": ["pulse", "dal", "lentil", "chickpea", "gram"]},
        "1207": {"description": "Oil seeds", "typical_gst": 5, "keywords": ["seeds", "oil seeds", "mustard", "sesame"]},
        
        # Default/General
        "9999": {"description": "General/Other items", "typical_gst": 18, "keywords": ["other", "general", "miscellaneous"]}
    }
    
    @classmethod
    def validate_hsn_format(cls, hsn_code: str) -> bool:
        """
        Validate HSN code format.
        HSN codes can be 4, 6, or 8 digits for goods.
        SAC codes are 6 digits for services.
        """
        if not hsn_code:
            return False
        
        # Remove any spaces or special characters
        clean_code = re.sub(r'[^0-9]', '', hsn_code)
        
        # Check if it's a valid length (4, 6, or 8 digits)
        return len(clean_code) in [4, 6, 8] and clean_code.isdigit()
    
    @classmethod
    def get_hsn_info(cls, hsn_code: str) -> Optional[Dict]:
        """Get information about an HSN code."""
        clean_code = re.sub(r'[^0-9]', '', hsn_code)
        
        if not cls.validate_hsn_format(clean_code):
            return None
        
        # Look for exact match first
        if clean_code in cls.HSN_DATABASE:
            return cls.HSN_DATABASE[clean_code]
        
        # For longer codes, try to find parent category
        if len(clean_code) > 4:
            parent_code = clean_code[:4]
            if parent_code in cls.HSN_DATABASE:
                info = cls.HSN_DATABASE[parent_code].copy()
                info["description"] += " (sub-category)"
                return info
        
        return None
    
    @classmethod
    def suggest_gst_rate(cls, hsn_code: str) -> Optional[float]:
        """Suggest GST rate based on HSN code."""
        info = cls.get_hsn_info(hsn_code)
        return info["typical_gst"] if info else None
    
    @classmethod
    def search_hsn_codes(cls, search_term: str) -> List[Dict]:
        """Search for HSN codes by description."""
        search_term = search_term.lower()
        results = []
        
        for code, info in cls.HSN_DATABASE.items():
            if search_term in info["description"].lower():
                results.append({
                    "hsn_code": code,
                    "description": info["description"],
                    "typical_gst": info["typical_gst"]
                })
        
        return results
    
    @classmethod
    def add_custom_hsn(cls, hsn_code: str, description: str, typical_gst: float):
        """Add a custom HSN code to the database."""
        clean_code = re.sub(r'[^0-9]', '', hsn_code)
        
        if not cls.validate_hsn_format(clean_code):
            raise ValueError(f"Invalid HSN code format: {hsn_code}")
        
        if not (0 <= typical_gst <= 100):
            raise ValueError(f"GST rate must be between 0 and 100: {typical_gst}")
        
        cls.HSN_DATABASE[clean_code] = {
            "description": description,
            "typical_gst": typical_gst
        }
    
    @classmethod
    def auto_suggest_hsn(cls, item_description: str) -> Optional[Dict]:
        """
        Automatically suggest HSN code based on item description.
        
        Args:
            item_description: Description of the item/service
            
        Returns:
            Dictionary with suggested HSN code info or None
        """
        if not item_description:
            return None
        
        description_lower = item_description.lower().strip()
        
        # Score each HSN code based on keyword matches
        suggestions = []
        
        for hsn_code, info in cls.HSN_DATABASE.items():
            score = 0
            keywords = info.get('keywords', [])
            
            # Check for exact matches first (higher score)
            for keyword in keywords:
                if keyword in description_lower:
                    # Exact match gets higher score
                    if keyword == description_lower:
                        score += 10
                    # Partial match gets lower score
                    elif keyword in description_lower:
                        score += 5
                    
                    # Bonus points for word boundaries
                    if f' {keyword} ' in f' {description_lower} ':
                        score += 3
                    
                    # Starting word gets bonus
                    if description_lower.startswith(keyword):
                        score += 2
            
            if score > 0:
                suggestions.append({
                    'hsn_code': hsn_code,
                    'description': info['description'],
                    'typical_gst': info['typical_gst'],
                    'score': score,
                    'keywords': keywords
                })
        
        # Sort by score (highest first)
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        # Return the best match if any
        if suggestions:
            best_match = suggestions[0]
            return {
                'hsn_code': best_match['hsn_code'],
                'description': best_match['description'],
                'typical_gst': best_match['typical_gst'],
                'confidence': min(best_match['score'] * 10, 100)  # Convert to percentage
            }
        
        return None
    
    @classmethod
    def get_multiple_suggestions(cls, item_description: str, limit: int = 3) -> List[Dict]:
        """
        Get multiple HSN code suggestions for an item.
        
        Args:
            item_description: Description of the item/service
            limit: Maximum number of suggestions to return
            
        Returns:
            List of suggested HSN codes with confidence scores
        """
        if not item_description:
            return []
        
        description_lower = item_description.lower().strip()
        suggestions = []
        
        for hsn_code, info in cls.HSN_DATABASE.items():
            score = 0
            keywords = info.get('keywords', [])
            
            for keyword in keywords:
                if keyword in description_lower:
                    if keyword == description_lower:
                        score += 10
                    else:
                        score += 3
                    
                    if f' {keyword} ' in f' {description_lower} ':
                        score += 2
                    
                    if description_lower.startswith(keyword):
                        score += 1
            
            if score > 0:
                suggestions.append({
                    'hsn_code': hsn_code,
                    'description': info['description'],
                    'typical_gst': info['typical_gst'],
                    'confidence': min(score * 8, 100),
                    'match_keywords': [kw for kw in keywords if kw in description_lower]
                })
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:limit]
    
    @classmethod
    def get_all_hsn_codes(cls) -> Dict[str, Dict]:
        """Get all HSN codes in the database."""
        return cls.HSN_DATABASE.copy()
    
    @classmethod
    def is_service_code(cls, hsn_code: str) -> bool:
        """Check if the HSN code is actually a SAC (Service) code."""
        clean_code = re.sub(r'[^0-9]', '', hsn_code)
        
        # SAC codes typically start with 99 and are 6 digits
        return len(clean_code) == 6 and clean_code.startswith('99')
