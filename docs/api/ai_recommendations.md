# AI Recommendations Module

Handles AI-powered recommendations using OpenAI GPT.

## AIRecommendationEngine Class

::: diabetes_tracker.modules.ai_recommendations.AIRecommendationEngine
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      members:
        - get_recommendation
        - get_meal_suggestions
        - get_exercise_recommendations
      show_root_full_path: false
      show_object_full_path: false

## Configuration

The module requires an `OPENAI_API_KEY` environment variable to use AI-powered recommendations. If not set, it will fall back to basic recommendations.

## Usage Example

```python
from diabetes_tracker.modules.ai_recommendations import AIRecommendationEngine
import os

# Set API key (or use environment variable)
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

# Initialize
ai_engine = AIRecommendationEngine()

# Get personalized recommendation
recommendation = ai_engine.get_recommendation(
    username="john_doe",
    blood_sugar=120.0,
    meal="Grilled chicken with vegetables",
    exercise="30 minutes walking"
)
print(recommendation)

# Get meal suggestions
meal_suggestions = ai_engine.get_meal_suggestions(
    blood_sugar=150.0,
    preferences="Low carb, vegetarian"
)
print(meal_suggestions)

# Get exercise recommendations
exercise_recs = ai_engine.get_exercise_recommendations(
    blood_sugar=100.0,
    current_exercise="Walking"
)
print(exercise_recs)
```

## Fallback Behavior

If the OpenAI API key is not configured or the API call fails, the module will automatically fall back to basic recommendations based on blood sugar levels:

- **Low (< 70 mg/dL)**: Recommendations for raising blood sugar
- **Normal (70-100 mg/dL)**: General maintenance recommendations
- **Elevated (100-140 mg/dL)**: Suggestions for maintaining healthy levels
- **High (> 140 mg/dL)**: Recommendations for lowering blood sugar

