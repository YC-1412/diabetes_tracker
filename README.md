[![Ruff Lint](https://github.com/YC-1412/diabetes_tracker/actions/workflows/ruff.yml/badge.svg)](https://github.com/YC-1412/diabetes_tracker/actions/workflows/ruff.yml)

# Diabetes Tracker - AI-Powered Management Assistant

A comprehensive diabetes management application that combines user data logging with AI-powered recommendations using OpenAI's GPT model.

## Features

- **User Authentication**: Secure registration and login system
- **Data Logging**: Track blood sugar levels, meals, and exercise
- **AI Recommendations**: Personalized advice using OpenAI GPT
- **History Tracking**: View and analyze your diabetes data over time
- **Statistics Dashboard**: Monitor trends and patterns
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Project Structure

```
diabetes_tracker/
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
├── pyproject.toml        # Modern Python project configuration
├── Makefile              # Development commands
├── .flake8               # Flake8 configuration
├── .env.example           # Environment variables template
├── .github/workflows/    # GitHub Actions CI/CD
│   └── ci.yml           # Continuous integration workflow
├── src/                  # Source code package
│   └── diabetes_tracker/ # Main application package
│       ├── __init__.py   # Package initialization
│       ├── app.py        # Main Flask application
│       ├── init_db.py    # Database initialization script
│       ├── modules/      # Backend modules
│       │   ├── __init__.py
│       │   ├── auth.py           # Authentication management
│       │   ├── database.py       # Data storage and retrieval
│       │   └── ai_recommendations.py # AI recommendation engine
│       ├── templates/    # HTML templates
│       │   └── index.html        # Main application page
│       └── static/       # Static assets
│           ├── css/
│           │   └── style.css     # Application styling
│           └── js/
│               └── app.js        # Frontend JavaScript
├── tests/              # Test suite
│   ├── __init__.py
│   ├── run_tests.py      # Run all tests
│   ├── test_app.py       # Application tests
│   └── test_chart.py     # Chart tests
└── archive/           # Legacy and utility scripts
    ├── migrate_csv_to_db.py
    ├── test_db_connection.py
    └── diagnose_db_connection.py


```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- PostgreSQL database (local or remote)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd diabetes_tracker
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   # For production
   pip install -r requirements.txt
   
   # For development (includes testing tools)
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env file and add your database configuration
   # Update the following variables:
   # - DB_HOST: Your PostgreSQL host (e.g., your EC2 instance IP)
   # - DB_PORT: PostgreSQL port (default: 5432)
   # - DB_NAME: Database name (default: diabetes_tracker)
   # - DB_USER: Database username (default: postgres)
   # - DB_PASSWORD: Database password
   # - OPENAI_API_KEY: Your OpenAI API key (optional)
   ```

5. **Set up the database**
   ```bash
   # Initialize the database (creates tables)
   make init-db
   
   # If you have existing CSV data, migrate it to PostgreSQL
   make migrate-csv
   
   # Or run the complete setup (init + migrate if CSV exists)
   make setup-db
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   Open your web browser and go to: `http://localhost:5001`

## Development

### Quick Start

The project includes a Makefile for common development tasks:

```bash
# Show all available commands
make help

# Install development dependencies
make install-dev

# Run linting
make lint

# Format code
make format

# Run tests
make test

# Run tests with coverage
make test-cov

# Run security checks
make security

# Run all CI checks locally
make ci

# Clean up generated files
make clean

# Database commands
make init-db          # Initialize PostgreSQL database
make migrate-csv      # Migrate CSV data to PostgreSQL
make check-db         # Check database connection
make setup-db         # Complete database setup
```

### Code Quality

The project uses several tools to maintain code quality:

- **Flake8**: Linting and style checking
- **Black**: Code formatting
- **isort**: Import sorting
- **Bandit**: Security linting
- **Safety**: Dependency vulnerability checking

### Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/diabetes_tracker --cov-report=html

# Run specific test file
pytest test_app.py -v
```

### Continuous Integration

The project includes GitHub Actions workflows that run on every push and pull request:

- **Linting**: Flake8 checks for code style and syntax
- **Testing**: Runs tests across multiple Python versions
- **Security**: Bandit and Safety checks for vulnerabilities
- **Coverage**: Code coverage reporting

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### Database Configuration
- `DB_HOST`: PostgreSQL host (e.g., your EC2 instance IP or localhost)
- `DB_PORT`: PostgreSQL port (default: 5432)
- `DB_NAME`: Database name (default: diabetes_tracker)
- `DB_USER`: Database username (default: postgres)
- `DB_PASSWORD`: Database password

#### Application Configuration
- `OPENAI_API_KEY`: Your OpenAI API key (required for AI recommendations)
- `FLASK_ENV`: Set to `development` or `production`
- `FLASK_DEBUG`: Set to `True` for development, `False` for production

### Database Setup

#### Local PostgreSQL Setup
1. Install PostgreSQL on your system
2. Create a database:
   ```sql
   CREATE DATABASE diabetes_tracker;
   ```
3. Update your `.env` file with local database credentials

#### AWS EC2 PostgreSQL Setup
1. Connect to your EC2 instance
2. Install PostgreSQL:
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```
3. Start PostgreSQL service:
   ```bash
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```
4. Configure PostgreSQL for remote connections:
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   ALTER USER postgres PASSWORD 'your-secure-password';
   CREATE DATABASE diabetes_tracker;
   \q
   ```
5. Edit PostgreSQL configuration:
   ```bash
   sudo nano /etc/postgresql/*/main/postgresql.conf
   # Change: listen_addresses = '*'
   
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   # Add: host all all 0.0.0.0/0 md5
   ```
6. Restart PostgreSQL:
   ```bash
   sudo systemctl restart postgresql
   ```
7. Configure your EC2 security group to allow connections on port 5432
8. Update your `.env` file with EC2 database credentials

### OpenAI API Setup

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Add the key to your `.env` file

**Note**: The application works without an OpenAI API key, but will provide basic recommendations instead of AI-powered ones.

## Usage

### Getting Started

1. **Register a new account** or **login** with existing credentials
2. **Log your first entry** with:
   - Blood sugar level (mg/dL)
   - Meal description
   - Exercise activities
   - Date
3. **View AI recommendations** based on your data
4. **Track your history** and monitor trends

### Features Overview

#### Dashboard
- View statistics including total entries, average blood sugar, and weekly activity
- Quick access to all features

#### Data Logging
- Log daily blood sugar readings
- Record meals and exercise
- Automatic date validation
- Real-time feedback

#### AI Recommendations
- Personalized advice based on your data
- Diet and exercise suggestions
- Blood sugar management tips
- Context-aware recommendations

#### History Tracking
- View all your logged entries
- Chronological organization
- Detailed entry information

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login

### Data Management
- `POST /api/log-entry` - Log new diabetes entry
- `GET /api/history/<username>` - Get user history
- `GET /api/recommendation/<username>` - Get AI recommendation

## Data Storage

The application currently uses CSV files for data storage:
- `data/users.csv` - User accounts and authentication
- `data/diabetes_entries.csv` - Diabetes tracking data

This makes it easy to:
- Back up data
- Export to other systems
- Analyze with external tools
- Migrate to a database later

## Security Features

- Password hashing using SHA-256
- Input validation and sanitization
- CORS protection
- Secure session management

## Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests and linting: `make ci`
5. Commit your changes: `git commit -m 'Add your feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Write tests for new features
- Update documentation as needed

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **OpenAI API errors**
   - Check your API key in the `.env` file
   - Verify your OpenAI account has credits
   - The app works without API key (basic recommendations)

3. **Data not saving**
   - Check file permissions in the `data/` directory
   - Ensure the application has write access

4. **Port already in use**
   - Change the port in `app.py`: `app.run(port=5001)`

5. **Linting errors**
   - Run `make format` to auto-format code
   - Fix any remaining issues manually

### Getting Help

If you encounter issues:
1. Check the browser console for JavaScript errors
2. Check the Flask application logs
3. Verify all environment variables are set correctly
4. Ensure all dependencies are installed
5. Run `make ci` to check for code quality issues

## Future Enhancements

- Database integration (PostgreSQL, MySQL)
- Data visualization and charts
- Export functionality
- Mobile app version
- Advanced AI features
- Multi-user support
- Data backup and sync

## License

This project is for educational and personal use. Please consult healthcare professionals for medical advice.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.