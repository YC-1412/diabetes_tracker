# Flask Application API

The main Flask application that handles all HTTP requests and routes.

## Application Overview

The Flask application is initialized in `diabetes_tracker.app` and provides RESTful API endpoints for diabetes tracking functionality.

## API Endpoints

All endpoints automatically extract their docstrings from the source code. The documentation below shows the extracted information along with request/response details.

### Authentication Endpoints

#### `POST /api/register`

::: diabetes_tracker.app.register
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
- `201`: User registered successfully
- `400`: Username and password are required
- `409`: Username already exists
- `500`: Server error

#### `POST /api/login`

::: diabetes_tracker.app.login
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
- `200`: Login successful
- `400`: Username and password are required
- `401`: Invalid credentials
- `500`: Server error

#### `POST /api/change-password`

::: diabetes_tracker.app.change_password
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Request Body:**
```json
{
  "username": "string",
  "old_password": "string",
  "new_password": "string"
}
```

**Response:**
- `200`: Password changed successfully
- `400`: Missing required fields or password too short
- `401`: Invalid old password or user not found
- `500`: Server error

### Data Management Endpoints

#### `POST /api/log-entry`

::: diabetes_tracker.app.log_entry
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Request Body:**
```json
{
  "username": "string",
  "blood_sugar": 120.0,
  "meal": "string",
  "exercise": "string",
  "date": "2024-01-01",
  "units": "mg/dL"
}
```

**Response:**
- `201`: Entry logged successfully with recommendation
- `400`: Missing required fields or invalid blood sugar range
- `500`: Server error

#### `GET /api/history/<username>`

::: diabetes_tracker.app.get_history
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Response:**
```json
{
  "history": [
    {
      "entry_id": "string",
      "username": "string",
      "blood_sugar": 120.0,
      "meal": "string",
      "exercise": "string",
      "date": "2024-01-01"
    }
  ],
  "units": "mg/dL"
}
```

#### `GET /api/chart-data/<username>`

::: diabetes_tracker.app.get_chart_data
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Response:**
```json
{
  "chart_data": {
    "labels": ["2024-01-01", "2024-01-02"],
    "data": [120.0, 130.0],
    "units": "mg/dL"
  }
}
```

#### `GET /api/user-stats/<username>`

::: diabetes_tracker.app.get_user_stats
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Response:**
```json
{
  "stats": {
    "total_entries": 10,
    "avg_blood_sugar": 120.0,
    "units": "mg/dL"
  }
}
```

### AI Recommendation Endpoints

#### `GET /api/recommendation/<username>`

::: diabetes_tracker.app.get_recommendation
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Response:**
```json
{
  "recommendation": "string"
}
```

#### `POST /api/meal-suggestions`

::: diabetes_tracker.app.get_meal_suggestions
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Request Body:**
```json
{
  "blood_sugar": 120.0,
  "preferences": "string"
}
```

**Response:**
```json
{
  "suggestions": "string"
}
```

#### `POST /api/exercise-recommendations`

::: diabetes_tracker.app.get_exercise_recommendations
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Request Body:**
```json
{
  "blood_sugar": 120.0,
  "current_exercise": "string"
}
```

**Response:**
```json
{
  "recommendations": "string"
}
```

### User Preferences Endpoints

#### `POST /api/update-units`

::: diabetes_tracker.app.update_units
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Request Body:**
```json
{
  "username": "string",
  "units": "mg/dL"
}
```

**Response:**
- `200`: Units updated successfully
- `400`: Missing required fields or invalid units
- `500`: Server error

#### `GET /api/user-preferences/<username>`

::: diabetes_tracker.app.get_user_preferences
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Response:**
```json
{
  "preferred_units": "mg/dL"
}
```

