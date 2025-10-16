# GPT API Setup Guide

This guide will help you set up OpenAI's GPT API for the AI-powered recommendations in your diabetes tracker application.

## Prerequisites

- An OpenAI account (sign up at https://platform.openai.com/)
- A valid OpenAI API key
- Python 3.9 or higher
- The diabetes tracker project set up and running

## Step 1: Get Your OpenAI API Key

1. **Visit OpenAI Platform**: Go to https://platform.openai.com/
2. **Sign in or Create Account**: Use your existing account or create a new one
3. **Navigate to API Keys**: Click on your profile -> "API Keys"
4. **Create New Key**: Click "Create new secret key"
5. **Copy the Key**: Save the API key securely (you won't be able to see it again)

## Step 2: Configure Your Environment

1. **Copy Environment Template**:
   ```bash
   cp env.example .env
   ```

2. **Edit the .env File**:
   ```bash
   # Add your OpenAI API key
   OPENAI_API_KEY=your-actual-api-key-here
   
   # Make sure your database settings are also configured
   DB_HOST=your-database-host
   DB_PORT=5432
   DB_NAME=diabetes_tracker
   DB_USER=your-database-user
   DB_PASSWORD=your-database-password
   ```

## Step 3: Install Dependencies

Update your Python packages to include the latest OpenAI SDK:

```bash
# For production
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

## Step 4: Test the Integration

Run the GPT integration test to verify everything is working:

```bash
# Using the Makefile
make test-gpt

# Or directly
python test_gpt_integration.py
```

You should see output like:
```
Testing GPT API Integration...
==================================================
API Key found: sk-12345678...
AI Recommendation Engine initialized successfully

Testing basic recommendation...
Basic recommendation generated successfully
Recommendation: Your blood sugar level of 120 mg/dL looks good! Keep up with your current routine...

Testing meal suggestions...
Meal suggestions generated successfully
Suggestions: Here are some meal suggestions for your blood sugar level...

Testing exercise recommendations...
Exercise recommendations generated successfully
Recommendations: Great time for exercise! Your blood sugar of 120 mg/dL is in a safe range...

==================================================
All GPT API integration tests passed!
```

## Step 5: Use the AI Features

Once the integration is working, you can use the AI features in your application:

### Available AI Functions

1. **Personalized Recommendations**: Get advice based on blood sugar, meals, and exercise
2. **Meal Suggestions**: Receive nutrition advice for your current glucose status
3. **Exercise Guidance**: Get safe exercise recommendations based on blood sugar levels

### Example Usage

```python
from diabetes_tracker.modules.ai_recommendations import AIRecommendationEngine

# Initialize the AI engine
ai_engine = AIRecommendationEngine()

# Get a personalized recommendation
recommendation = ai_engine.get_recommendation(
    username="John",
    blood_sugar=120.0,
    meal="Grilled chicken salad",
    exercise="30 minutes walking"
)

# Get meal suggestions
meal_suggestions = ai_engine.get_meal_suggestions(
    blood_sugar=120.0,
    preferences="Low carb, vegetarian"
)

# Get exercise recommendations
exercise_recs = ai_engine.get_exercise_recommendations(
    blood_sugar=120.0,
    current_exercise="Walking"
)
```

## Model Information

The application uses **GPT-4.1 nano (gpt-4o-mini)** which provides:
- Fast response times
- Cost-effective pricing
- High-quality recommendations
- Context-aware responses

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Make sure you've added the API key to your `.env` file
   - Restart your application after adding the key

2. **"Invalid API key"**
   - Verify your API key is correct
   - Check if your OpenAI account has sufficient credits

3. **"Rate limit exceeded"**
   - Wait a moment and try again
   - Consider upgrading your OpenAI plan if this happens frequently

4. **"Module not found" errors**
   - Make sure you've installed the requirements: `pip install -r requirements.txt`
   - Check that you're in the correct virtual environment

### Getting Help

- Check the OpenAI documentation: https://platform.openai.com/docs
- Review the test output for specific error messages
- Ensure your `.env` file is properly formatted

## Security Notes

- **Never commit your API key** to version control
- **Keep your API key secure** and don't share it
- **Monitor your usage** on the OpenAI platform to avoid unexpected charges
- **Use environment variables** (as shown above) to keep keys secure

## Cost Considerations

- GPT-4.1 nano is cost-effective for this use case
- Typical usage for diabetes recommendations costs less than $1/month
- Monitor your usage on the OpenAI platform dashboard
- Set up billing alerts to avoid unexpected charges 