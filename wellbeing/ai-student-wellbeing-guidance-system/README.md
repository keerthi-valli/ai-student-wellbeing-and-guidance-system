# AI-Driven Student Wellbeing and Guidance System

## Project Overview
A comprehensive Flask-based web application designed to support student wellbeing, academic growth, and career development. The system leverages AI to analyze emotional states, provide personalized roadmaps, and offer smart emergency support.

## Features
- **Digital Diary**: Secure journaling with AI-powered sentiment analysis.
- **Wellbeing Monitoring**: Real-time stress and mood tracking with visual analytics.
- **Smart Emergency Support**: tiered risk assessment (Stable, Elevated, Critical) with automated counselor alerts for critical situations.
- **Academic Guidance**: Personalized study roadmaps and progress tracking for students.
- **Employee Skill Development**: Skill gap analysis and professional growth roadmaps for employees.

## Tech Stack
- **Backend**: Python, Flask, MongoDB
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap, Chart.js)
- **AI/ML**: Google Gemini API (for content analysis and recommendations)
- **Database**: MongoDB (via PyMongo)

## Setup Instructions
1. **Clone the repository**
   ```bash
   git clone https://github.com/Shaikshannu28/ai-student-wellbeing-guidance-system.git
   cd ai-student-wellbeing-guidance-system
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory and add your secrets:
   ```
   SECRET_KEY=your_secret_key
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/student_wellbeing?retryWrites=true&w=majority
   GOOGLE_API_KEY=your_google_api_key
   ```

5. **MongoDB Atlas Setup & Migration**
   - Create a cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
   - Whitelist your IP address (Network Access).
   - Create a database user (Database Access).
   - Get your connection string (Connect -> Connect your application).
   - Update `MONGO_URI` in `.env` with this string.
   - **Migrate Local Data**:
     Run the migration script to copy your local data to Atlas:
     ```bash
     python migrate_db.py
     ```

6. **Run the Application**
   ```bash
   python app.py
   ```
   Access the app at `http://localhost:5000`.

## Deployment
[Deployment instructions to be added]

## License
MIT License
