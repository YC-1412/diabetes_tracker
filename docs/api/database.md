# Database Module

Manages data storage and retrieval using PostgreSQL database.

## Database Models

### User Model

::: diabetes_tracker.modules.database.User
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### DiabetesEntry Model

::: diabetes_tracker.modules.database.DiabetesEntry
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## DataManager Class

::: diabetes_tracker.modules.database.DataManager
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      members:
        - save_entry
        - get_user_history
        - get_chart_data
        - get_user_stats
        - get_recent_entries
        - get_user_preferred_units
        - update_user_preferred_units
        - delete_entry
        - get_db_session
      show_root_full_path: false
      show_object_full_path: false

## Usage Example

```python
from diabetes_tracker.modules.database import DataManager

# Initialize
data_manager = DataManager()

# Save an entry
entry_id = data_manager.save_entry(
    username="john_doe",
    blood_sugar=120.0,
    meal="Grilled chicken with vegetables",
    exercise="30 minutes walking",
    date="2024-01-01"
)

# Get user history
history = data_manager.get_user_history("john_doe")
for entry in history:
    print(f"Blood sugar: {entry['blood_sugar']} mg/dL")

# Get user statistics
stats = data_manager.get_user_stats("john_doe")
print(f"Total entries: {stats['total_entries']}")
print(f"Average blood sugar: {stats['avg_blood_sugar']} mg/dL")

# Update preferred units
data_manager.update_user_preferred_units("john_doe", "mmol/L")
```

