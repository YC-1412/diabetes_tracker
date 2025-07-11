import os
import openai


class AIRecommendationEngine:
    """Handles AI-powered recommendations using OpenAI GPT"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            print("Warning: OPENAI_API_KEY not found in environment variables")

    def get_recommendation(
        self, username: str, blood_sugar: float, meal: str, exercise: str
    ) -> str:
        """Generate personalized recommendation based on user data"""

        # If no API key, return a basic recommendation
        if not self.api_key:
            return self._get_basic_recommendation(blood_sugar, meal, exercise)

        try:
            # Create context for the AI
            context = self._create_context(username, blood_sugar, meal, exercise)

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful diabetes management assistant.
                        Provide personalized, friendly, and actionable advice based on the user's data.
                        Focus on practical suggestions for diet, exercise, and lifestyle changes.
                        Keep responses conversational and encouraging, but also informative.""",
                    },
                    {"role": "user", "content": context},
                ],
                max_tokens=300,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._get_basic_recommendation(blood_sugar, meal, exercise)

    def _create_context(
        self, username: str, blood_sugar: float, meal: str, exercise: str
    ) -> str:
        """Create context string for AI recommendation"""

        # Analyze blood sugar level
        blood_sugar_status = self._analyze_blood_sugar(blood_sugar)

        context = f"""
        User: {username}

        Today's Data:
        - Blood Sugar Level: {blood_sugar} mg/dL ({blood_sugar_status})
        - Meal: {meal}
        - Exercise: {exercise}

        Please provide personalized advice for diabetes management based on this data.
        Consider the blood sugar level, meal choices, and exercise routine.
        Give specific, actionable recommendations for diet, exercise, and lifestyle.
        """

        return context

    def _analyze_blood_sugar(self, blood_sugar: float) -> str:
        """Analyze blood sugar level and return status"""
        if blood_sugar < 70:
            return "Low (Hypoglycemia)"
        elif blood_sugar < 100:
            return "Normal (Fasting)"
        elif blood_sugar < 140:
            return "Normal (Post-meal)"
        elif blood_sugar < 200:
            return "Elevated"
        else:
            return "High (Hyperglycemia)"

    def _get_basic_recommendation(
        self, blood_sugar: float, meal: str, exercise: str
    ) -> str:
        """Provide basic recommendation when AI is not available"""

        status = self._analyze_blood_sugar(blood_sugar)

        if blood_sugar < 70:
            return f"Your blood sugar is low ({blood_sugar} mg/dL). Consider having a small snack with carbohydrates and protein. Monitor your levels closely and consult your healthcare provider if this happens frequently."

        elif blood_sugar > 200:
            return f"Your blood sugar is elevated ({blood_sugar} mg/dL). Consider increasing your physical activity, monitoring your carbohydrate intake, and staying hydrated. If this persists, consult your healthcare provider."

        else:
            return f"Your blood sugar level of {blood_sugar} mg/dL looks good! Keep up with your current routine. Remember to maintain regular meal times, stay active, and monitor your levels consistently."

    def get_meal_suggestions(self, blood_sugar: float, preferences: str = "") -> str:
        """Get meal suggestions based on blood sugar level"""

        if not self.api_key:
            return self._get_basic_meal_suggestions(blood_sugar)

        try:
            context = f"""
            Blood sugar level: {blood_sugar} mg/dL
            User preferences: {preferences}

            Provide 3-4 meal suggestions that would be appropriate for this blood sugar level.
            Include breakfast, lunch, dinner, and snack options. Focus on balanced nutrition
            with appropriate carbohydrate content for diabetes management.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a nutrition expert specializing in diabetes management. Provide practical meal suggestions.",
                    },
                    {"role": "user", "content": context},
                ],
                max_tokens=400,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error getting meal suggestions: {e}")
            return self._get_basic_meal_suggestions(blood_sugar)

    def _get_basic_meal_suggestions(self, blood_sugar: float) -> str:
        """Basic meal suggestions when AI is not available"""

        if blood_sugar < 100:
            return """
            Meal Suggestions for Normal Blood Sugar:

            Breakfast: Oatmeal with berries and nuts, or whole grain toast with avocado
            Lunch: Grilled chicken salad with mixed greens and olive oil dressing
            Dinner: Baked salmon with quinoa and steamed vegetables
            Snacks: Greek yogurt with berries, or apple with almond butter
            """
        elif blood_sugar < 140:
            return """
            Meal Suggestions for Post-Meal Normal Blood Sugar:

            Breakfast: Greek yogurt with granola and fruit
            Lunch: Turkey and vegetable wrap with whole grain tortilla
            Dinner: Lean beef stir-fry with brown rice and vegetables
            Snacks: Hummus with carrot sticks, or mixed nuts
            """
        else:
            return """
            Meal Suggestions for Elevated Blood Sugar:

            Breakfast: Scrambled eggs with spinach and whole grain toast
            Lunch: Grilled fish with quinoa and roasted vegetables
            Dinner: Chicken breast with sweet potato and green beans
            Snacks: Cottage cheese with cucumber, or hard-boiled eggs
            """

    def get_exercise_recommendations(
        self, blood_sugar: float, current_exercise: str
    ) -> str:
        """Get exercise recommendations based on blood sugar level"""

        if not self.api_key:
            return self._get_basic_exercise_recommendations(
                blood_sugar, current_exercise
            )

        try:
            context = f"""
            Blood sugar level: {blood_sugar} mg/dL
            Current exercise: {current_exercise}

            Provide exercise recommendations that are safe and beneficial for this blood sugar level.
            Include both aerobic and strength training suggestions, with appropriate intensity levels.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fitness expert specializing in diabetes management. Provide safe and effective exercise recommendations.",
                    },
                    {"role": "user", "content": context},
                ],
                max_tokens=300,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error getting exercise recommendations: {e}")
            return self._get_basic_exercise_recommendations(
                blood_sugar, current_exercise
            )

    def _get_basic_exercise_recommendations(
        self, blood_sugar: float, current_exercise: str
    ) -> str:
        """Basic exercise recommendations when AI is not available"""

        if blood_sugar < 70:
            return "Your blood sugar is low. Avoid intense exercise until your levels stabilize. Consider light walking or gentle stretching after having a snack."

        elif blood_sugar > 250:
            return "Your blood sugar is high. Avoid intense exercise and check for ketones if you have type 1 diabetes. Light walking may help lower blood sugar gradually."

        else:
            return f"Great time for exercise! Your blood sugar of {blood_sugar} mg/dL is in a safe range. Consider 30 minutes of moderate activity like walking, swimming, or cycling. Don't forget to monitor your levels during and after exercise."
