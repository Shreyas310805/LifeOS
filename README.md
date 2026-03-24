# LifeOS - AI-Based Lifestyle & Health Tracker

A comprehensive web application for tracking and improving your health, fitness, nutrition, sleep, and overall lifestyle using AI-powered insights.

## Features

### Core Features
- 🏋️ **Workout Tracking** - Log workouts, track duration, calories, and progress
- 🥗 **Nutrition Logging** - Track meals, calories, macros, and eating habits
- 😴 **Sleep Monitoring** - Record sleep patterns and quality
- 💧 **Water Intake** - Track daily hydration
- 🎯 **Goal Setting** - Set and track health and fitness goals
- 📊 **Health Metrics** - Monitor weight, BMI, heart rate, blood pressure
- 😊 **Mood Tracking** - Log emotions and mental wellbeing
- 🤖 **AI Recommendations** - Get personalized health insights

### Technical Features
- User authentication and authorization
- RESTful API endpoints
- Database-backed persistence
- Responsive design
- Data visualization with charts
- Export/import functionality

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask sessions with password hashing
- **Database Migrations**: Flask-Migrate (Alembic)

## Project Structure

```
LifeOS/
├── app.py                  # Main Flask application
├── models.py              # Database models
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── migrations/           # Database migrations
├── static/               # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── templates/            # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   └── ...
└── uploads/              # User uploaded files
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Shreyas310805/LifeOS.git
cd LifeOS
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and update the values
# At minimum, change the SECRET_KEY
```

### Step 5: Initialize Database

```bash
# Initialize the database
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade

# Or simply run (creates tables without migrations)
python app.py
```

### Step 6: Create Admin User (Optional)

```bash
flask create-admin
```

### Step 7: Run the Application

```bash
# Development mode
python app.py

# Or using Flask CLI
flask run
```

The application will be available at `http://localhost:5000`

## Database Models

### User
- Profile information
- Authentication credentials
- Preferences and settings

### HealthMetric
- Weight, BMI, body fat percentage
- Heart rate, blood pressure
- Daily steps and calories burned

### Goal
- Goal title, description, category
- Target values and deadlines
- Progress tracking

### Workout
- Workout type, duration, intensity
- Calories burned, distance
- Exercise details

### Meal
- Meal type (breakfast, lunch, dinner, snack)
- Nutritional information (calories, macros)
- Ingredients and recipes

### SleepRecord
- Sleep duration and quality
- Sleep stages (deep, light, REM)
- Sleep disturbances

### WaterIntake
- Hydration tracking
- Daily water consumption

### MoodEntry
- Emotional state tracking
- Energy and stress levels
- Contributing factors

### AIRecommendation
- Personalized AI insights
- Health and fitness recommendations

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Dashboard
- `GET /dashboard` - Main dashboard with overview

### Health Metrics
- `GET /health-metrics` - View health metrics history
- `POST /health-metrics/add` - Add new health metric
- `GET /api/weight-chart` - Get weight chart data

### Goals
- `GET /goals` - View all goals
- `POST /goals/add` - Create new goal
- `POST /goals/<id>/update` - Update goal progress

### Workouts
- `GET /workouts` - View workout history
- `POST /workouts/add` - Log new workout

### Nutrition
- `GET /nutrition` - View meal history
- `POST /nutrition/add` - Log new meal

### Sleep
- `GET /sleep` - View sleep records
- `POST /sleep/add` - Log sleep

### Quick Actions
- `POST /water/add` - Add water intake
- `POST /mood/add` - Log mood

### Profile
- `GET /profile` - View profile
- `POST /profile/update` - Update profile

## Database Migration Commands

```bash
# Initialize migrations (first time only)
flask db init

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# View migration history
flask db history

# View current revision
flask db current
```

## Production Deployment

### Using PostgreSQL

1. Install PostgreSQL
2. Create a database:
```sql
CREATE DATABASE lifeos_db;
CREATE USER lifeos_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE lifeos_db TO lifeos_user;
```

3. Update `.env`:
```
DATABASE_URL=postgresql://lifeos_user:your_password@localhost:5432/lifeos_db
FLASK_ENV=production
```

4. Run migrations:
```bash
flask db upgrade
```

### Security Considerations

- Change `SECRET_KEY` to a strong random string
- Use HTTPS in production
- Enable `SESSION_COOKIE_SECURE = True`
- Keep dependencies updated
- Use environment variables for sensitive data
- Implement rate limiting
- Add CSRF protection
- Regular database backups

### Deployment Platforms

**Heroku:**
```bash
# Add Procfile
echo "web: gunicorn app:app" > Procfile

# Add runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
heroku create lifeos-app
git push heroku main
heroku run flask db upgrade
```

**Railway/Render:**
- Connect your GitHub repository
- Set environment variables
- Deploy automatically on push

## Future Enhancements

- [ ] AI-powered meal planning
- [ ] Workout recommendations based on goals
- [ ] Social features (friends, challenges)
- [ ] Mobile app (React Native)
- [ ] Wearable device integration
- [ ] Advanced analytics and insights
- [ ] Export data to PDF/CSV
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Push notifications

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_models.py
```

## Troubleshooting

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
rm lifeos.db
flask db upgrade
```

### Migration Conflicts
```bash
# Remove migrations and start fresh
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Acknowledgments

- Flask documentation and community
- SQLAlchemy documentation
- All contributors and testers

## Support

For issues, questions, or contributions, please open an issue on GitHub or contact the maintainers.

---

**Happy Health Tracking! 🏃‍♂️💪🥗**