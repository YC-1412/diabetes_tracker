# Unit Converter Module

Handles conversion between mg/dL and mmol/L units for blood glucose measurements.

## UnitConverter Class

::: diabetes_tracker.modules.unit_converter.UnitConverter
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      members:
        - mg_dl_to_mmol_l
        - mmol_l_to_mg_dl
        - convert_to_user_units
        - get_validation_range
        - format_value_with_units
      show_root_full_path: false
      show_object_full_path: false

## Conversion Factor

The conversion factor used is: **1 mmol/L = 18.018 mg/dL**

## Validation Ranges

- **mg/dL**: 50.0 - 500.0
- **mmol/L**: 2.8 - 27.8 (converted from mg/dL range)

## Usage Example

```python
from diabetes_tracker.modules.unit_converter import UnitConverter

# Convert mg/dL to mmol/L
mg_dl_value = 120.0
mmol_l_value = UnitConverter.mg_dl_to_mmol_l(mg_dl_value)
print(f"{mg_dl_value} mg/dL = {mmol_l_value} mmol/L")

# Convert mmol/L to mg/dL
mmol_l_value = 6.7
mg_dl_value = UnitConverter.mmol_l_to_mg_dl(mmol_l_value)
print(f"{mmol_l_value} mmol/L = {mg_dl_value} mg/dL")

# Generic conversion
converted = UnitConverter.convert_to_user_units(120.0, "mg/dL", "mmol/L")
print(f"120.0 mg/dL = {converted} mmol/L")

# Get validation range
min_val, max_val = UnitConverter.get_validation_range("mg/dL")
print(f"Valid range for mg/dL: {min_val} - {max_val}")

# Format with units
formatted = UnitConverter.format_value_with_units(120.0, "mg/dL")
print(formatted)  # Output: "120.0 mg/dL"
```

## Common Conversions

| mg/dL | mmol/L |
|-------|--------|
| 70    | 3.9    |
| 100   | 5.6    |
| 120   | 6.7    |
| 140   | 7.8    |
| 180   | 10.0   |

