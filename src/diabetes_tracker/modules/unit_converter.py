"""
Unit conversion utilities for blood glucose measurements
"""


class UnitConverter:
    """Handles conversion between mg/dL and mmol/L units"""
    
    # Conversion factor: 1 mmol/L = 18.018 mg/dL
    CONVERSION_FACTOR = 18.018
    
    @classmethod
    def mg_dl_to_mmol_l(cls, mg_dl_value: float) -> float:
        """Convert mg/dL to mmol/L"""
        return round(mg_dl_value / cls.CONVERSION_FACTOR, 1)
    
    @classmethod
    def mmol_l_to_mg_dl(cls, mmol_l_value: float) -> float:
        """Convert mmol/L to mg/dL"""
        return round(mmol_l_value * cls.CONVERSION_FACTOR, 1)
    
    @classmethod
    def convert_to_user_units(cls, value: float, from_units: str, to_units: str) -> float:
        """Convert a value from one unit system to another"""
        if from_units == to_units:
            return value
        
        if from_units == 'mg/dL' and to_units == 'mmol/L':
            return cls.mg_dl_to_mmol_l(value)
        elif from_units == 'mmol/L' and to_units == 'mg/dL':
            return cls.mmol_l_to_mg_dl(value)
        else:
            raise ValueError(f"Unsupported unit conversion: {from_units} to {to_units}")
    
    @classmethod
    def get_validation_range(cls, units: str) -> tuple[float, float]:
        """Get validation range for blood sugar values based on units"""
        if units == 'mg/dL':
            return (50.0, 500.0)  # mg/dL range
        elif units == 'mmol/L':
            return (2.8, 27.8)  # mmol/L range (converted from mg/dL)
        else:
            raise ValueError(f"Unsupported units: {units}")
    
    @classmethod
    def format_value_with_units(cls, value: float, units: str) -> str:
        """Format a value with its units"""
        if units == 'mg/dL':
            return f"{value} mg/dL"
        elif units == 'mmol/L':
            return f"{value} mmol/L"
        else:
            return str(value)
