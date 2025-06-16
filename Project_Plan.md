# Project Title
A Conversational Assistant for Diabetes Management Using GPT.

# Project Overview
The system consists of four components:

1. Web Interface

    Users can input daily blood sugar levels, meals, and physical activity. A clean, intuitive interface allows for quick updates and history review.

2. Database

    A relational database such as PostgreSQL (hosted via managed services like AWS RDS or Google Cloud SQL) stores user logs. This allows:

    - Personalizing recommendations over time
    - Building future features like trend visualizations or alerts

3. GPT-based Recommendation Engine

    Each daily log is sent to OpenAI’s GPT API, where a custom prompt contextualizes the user’s data and requests a recommendation. The model returns conversational advice, e.g., ”Your sugar levels looked good today. For tomorrow, consider more fiber with breakfast and staying hydrated.”

4. Cloud Hosting and Scalability

    The backend API and frontend will be deployed using cloud platforms like AWS Elastic Beanstalk or Google App Engine. Cloud object storage (e.g., AWS S3 or Google Cloud Storage) will hold any backups or supplementary user data. This approach ensures scalability, security, and easy maintenance, with built-in tools for authentication, encryption, and data privacy compliance.

5. (Optional Advanced Feature)

    Over time, the assistant could incorporate fine-tuning or retrieval-augmented generation (RAG) to better
reflect user preferences or behavior patterns.

# Feasibility & Tools

The stack includes:

- Frontend: HTML/CSS, or optionally Streamlit for simplicity
- Backend: Flask/FastAPI (Python)
- Database: PostgreSQL via AWS RDS or Google Cloud SQL
- AI: OpenAI GPT-4-turbo API
- Deployment: AWS Elastic Beanstalk or Google App Engine
- Optional: Fine-tuning using OpenAI if time and data permit

# Functional and Non-Functional Requirements
## Functional Requirements
1. The system shall allow users to register and log in securely.
2. The system shall allow users to input daily blood sugar levels, meals, and exercise.
3. The system shall store all user inputs in a cloud-hosted database.
4. The system shall call an LLM API (e.g., OpenAI GPT-4) with the user data to retrieve personalized recommendations.
5. The system shall display AI-generated diet and activity suggestions to users.
6. The system shall allow users to view their historical data.

## Non-Functional Requirements
1. The system shall ensure secure data handling (HTTPS, authentication).
2. The UI shall be intuitive and responsive.
3. The system shall process API responses and return results to users within 5 seconds.
4. The system shall be scalable for up to 100 users.
5. The system shall have a modular architecture for future enhancements.