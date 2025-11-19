# Authentication Module

Handles user authentication, registration, and password management.

## AuthManager Class

::: diabetes_tracker.modules.auth.AuthManager
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      members:
        - register_user
        - login_user
        - change_password
        - user_exists
        - get_user_info
        - get_db_session
      show_root_full_path: false
      show_object_full_path: false

## Usage Example

```python
from diabetes_tracker.modules.auth import AuthManager
from diabetes_tracker.modules.database import DataManager

# Initialize
data_manager = DataManager()
auth_manager = AuthManager(data_manager)

# Register a new user
success = auth_manager.register_user("john_doe", "secure_password123")
if success:
    print("User registered successfully")

# Login
success = auth_manager.login_user("john_doe", "secure_password123")
if success:
    print("Login successful")

# Change password
success = auth_manager.change_password(
    "john_doe", 
    "secure_password123", 
    "new_secure_password456"
)
```

