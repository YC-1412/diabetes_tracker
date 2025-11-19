# Diabetes Tracker Documentation

Welcome to the Diabetes Tracker documentation! This is a comprehensive diabetes management application that combines user data logging with AI-powered recommendations using OpenAI's GPT model.

## Quick Start

Get started with Diabetes Tracker in minutes:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize the database**
   ```bash
   make init-db
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   Open your browser at `http://localhost:5001`

## Features

- **User Authentication**: Secure registration and login system
- **Data Logging**: Track blood sugar levels, meals, and exercise
- **AI Recommendations**: Personalized advice using OpenAI GPT
- **History Tracking**: View and analyze your diabetes data over time
- **Statistics Dashboard**: Monitor trends and patterns
- **Unit Conversion**: Support for both mg/dL and mmol/L units
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Documentation Structure

- **[Overview](overview.md)**: Complete project overview and setup instructions
- **[API Reference](api/app.md)**: Detailed API documentation for all endpoints and modules

## Getting Help

If you encounter any issues:

1. Check the [Overview](overview.md) page for common troubleshooting tips
2. Review the [API Reference](api/app.md) for endpoint details
3. Check the browser console for JavaScript errors
4. Verify all environment variables are set correctly

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Note**: This project is for educational and personal use. Please consult healthcare professionals for medical advice.

