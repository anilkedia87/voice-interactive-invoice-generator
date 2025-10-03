"""
GST Calculator Service
Handles all GST-related calculations and validations.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Tuple, Optional
from enum import Enum


class GSTType(Enum):
    """Types of GST applicable."""
    CGST_SGST = "CGST_SGST"  # Intrastate transaction
    IGST = "IGST"            # Interstate transaction
    

class GSTCalculator:
    """Service for GST calculations and validations."""
    
    # Standard GST rates in India
    STANDARD_GST_RATES = [0, 3, 5, 12, 18, 28]
    
    # GST rate slabs with descriptions
    GST_SLABS = {
        0: "Exempt/Zero rated",
        3: "Gold, silver, cut and polished diamonds",
        5: "Essential items (sugar, tea, coffee, etc.)",
        12: "Computers, processed food, etc.",
        18: "Most goods and services",
        28: "Luxury items, automobiles, etc."
    }
    
    @classmethod
    def validate_gst_rate(cls, gst_rate: float) -> bool:
        """Validate if GST rate is valid."""
        return gst_rate in cls.STANDARD_GST_RATES or 0 <= gst_rate <= 100
    
    @classmethod
    def calculate_gst_breakdown(
        cls, 
        taxable_amount: Decimal, 
        gst_rate: Decimal, 
        is_interstate: bool = False
    ) -> Dict[str, Decimal]:
        """
        Calculate GST breakdown for a given taxable amount.
        
        Args:
            taxable_amount: The amount on which GST is calculated
            gst_rate: GST percentage (e.g., 18 for 18%)
            is_interstate: True for IGST, False for CGST+SGST
            
        Returns:
            Dictionary with GST breakdown
        """
        if taxable_amount < 0:
            raise ValueError("Taxable amount cannot be negative")
        
        if gst_rate < 0 or gst_rate > 100:
            raise ValueError("GST rate must be between 0 and 100")
        
        # Convert to Decimal for precise calculations
        taxable_amount = Decimal(str(taxable_amount))
        gst_rate = Decimal(str(gst_rate))
        
        result = {
            'taxable_amount': taxable_amount,
            'gst_rate': gst_rate,
            'cgst_rate': Decimal('0'),
            'sgst_rate': Decimal('0'),
            'igst_rate': Decimal('0'),
            'cgst_amount': Decimal('0'),
            'sgst_amount': Decimal('0'),
            'igst_amount': Decimal('0'),
            'total_tax': Decimal('0'),
            'total_amount': Decimal('0'),
            'gst_type': GSTType.IGST if is_interstate else GSTType.CGST_SGST
        }
        
        if is_interstate:
            # IGST applies for interstate transactions
            result['igst_rate'] = gst_rate
            result['igst_amount'] = (taxable_amount * gst_rate / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            result['total_tax'] = result['igst_amount']
        else:
            # CGST + SGST applies for intrastate transactions
            half_rate = gst_rate / 2
            result['cgst_rate'] = half_rate
            result['sgst_rate'] = half_rate
            
            result['cgst_amount'] = (taxable_amount * half_rate / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            result['sgst_amount'] = (taxable_amount * half_rate / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            result['total_tax'] = result['cgst_amount'] + result['sgst_amount']
        
        result['total_amount'] = (taxable_amount + result['total_tax']).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return result
    
    @classmethod
    def calculate_reverse_gst(
        cls,
        total_amount: Decimal,
        gst_rate: Decimal,
        is_interstate: bool = False
    ) -> Dict[str, Decimal]:
        """
        Calculate GST components when total amount (including GST) is known.
        
        Args:
            total_amount: Total amount including GST
            gst_rate: GST percentage
            is_interstate: True for IGST, False for CGST+SGST
            
        Returns:
            Dictionary with GST breakdown
        """
        if total_amount < 0:
            raise ValueError("Total amount cannot be negative")
        
        # Convert to Decimal for precise calculations
        total_amount = Decimal(str(total_amount))
        gst_rate = Decimal(str(gst_rate))
        
        # Calculate taxable amount: taxable_amount = total_amount / (1 + gst_rate/100)
        divisor = 1 + (gst_rate / 100)
        taxable_amount = (total_amount / divisor).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return cls.calculate_gst_breakdown(taxable_amount, gst_rate, is_interstate)
    
    @classmethod
    def calculate_discount_with_gst(
        cls,
        base_amount: Decimal,
        discount_percentage: Decimal,
        gst_rate: Decimal,
        is_interstate: bool = False
    ) -> Dict[str, Decimal]:
        """
        Calculate GST on discounted amount.
        
        Args:
            base_amount: Original amount before discount
            discount_percentage: Discount percentage
            gst_rate: GST percentage
            is_interstate: True for IGST, False for CGST+SGST
            
        Returns:
            Dictionary with complete calculation breakdown
        """
        base_amount = Decimal(str(base_amount))
        discount_percentage = Decimal(str(discount_percentage))
        
        # Calculate discount amount
        discount_amount = (base_amount * discount_percentage / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Calculate taxable amount after discount
        taxable_amount = base_amount - discount_amount
        
        # Calculate GST on taxable amount
        gst_breakdown = cls.calculate_gst_breakdown(taxable_amount, gst_rate, is_interstate)
        
        # Add discount information to the result
        result = gst_breakdown.copy()
        result.update({
            'base_amount': base_amount,
            'discount_percentage': discount_percentage,
            'discount_amount': discount_amount,
            'amount_after_discount': taxable_amount
        })
        
        return result
    
    @classmethod
    def get_gst_slab_info(cls, gst_rate: float) -> Optional[str]:
        """Get information about GST slab."""
        return cls.GST_SLABS.get(gst_rate)
    
    @classmethod
    def suggest_nearest_gst_rate(cls, rate: float) -> float:
        """Suggest the nearest valid GST rate."""
        if rate in cls.STANDARD_GST_RATES:
            return rate
        
        # Find the closest standard rate
        closest_rate = min(cls.STANDARD_GST_RATES, key=lambda x: abs(x - rate))
        return closest_rate
    
    @classmethod
    def validate_gstin(cls, gstin: str) -> Tuple[bool, Optional[str]]:
        """
        Validate GSTIN format and return validation result.
        
        Args:
            gstin: GST Identification Number
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not gstin:
            return False, "GSTIN cannot be empty"
        
        # Remove spaces and convert to uppercase
        gstin = gstin.replace(" ", "").upper()
        
        if len(gstin) != 15:
            return False, "GSTIN must be 15 characters long"
        
        # GSTIN Format: 99AAAAA9999A9A9
        # First 2 digits: State code (01-37)
        state_code = gstin[:2]
        if not state_code.isdigit() or not (1 <= int(state_code) <= 37):
            return False, "Invalid state code in GSTIN"
        
        # Next 10 characters: PAN of the business
        pan_part = gstin[2:12]
        if not (len(pan_part) == 10 and pan_part[:5].isalpha() and 
                pan_part[5:9].isdigit() and pan_part[9].isalpha()):
            return False, "Invalid PAN format in GSTIN"
        
        # 13th character: Entity code (1-9, A-Z except I and O)
        entity_code = gstin[12]
        if not (entity_code.isdigit() or entity_code.isalpha()):
            return False, "Invalid entity code in GSTIN"
        
        # 14th character: Check digit (0-9, A-Z)
        check_digit = gstin[13]
        if not (check_digit.isdigit() or check_digit.isalpha()):
            return False, "Invalid check digit in GSTIN"
        
        # 15th character: Default 'Z'
        if gstin[14] != 'Z':
            return False, "Last character of GSTIN must be 'Z'"
        
        return True, None
    
    @classmethod
    def get_state_from_gstin(cls, gstin: str) -> Optional[str]:
        """Extract state code from GSTIN."""
        if not gstin or len(gstin) < 2:
            return None
        
        state_codes = {
            '01': 'Jammu and Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab',
            '04': 'Chandigarh', '05': 'Uttarakhand', '06': 'Haryana',
            '07': 'Delhi', '08': 'Rajasthan', '09': 'Uttar Pradesh',
            '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh',
            '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram',
            '16': 'Tripura', '17': 'Meghalaya', '18': 'Assam',
            '19': 'West Bengal', '20': 'Jharkhand', '21': 'Odisha',
            '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
            '25': 'Daman and Diu', '26': 'Dadra and Nagar Haveli',
            '27': 'Maharashtra', '28': 'Andhra Pradesh', '29': 'Karnataka',
            '30': 'Goa', '31': 'Lakshadweep', '32': 'Kerala',
            '33': 'Tamil Nadu', '34': 'Puducherry', '35': 'Andaman and Nicobar Islands',
            '36': 'Telangana', '37': 'Andhra Pradesh'
        }
        
        state_code = gstin[:2]
        return state_codes.get(state_code)
