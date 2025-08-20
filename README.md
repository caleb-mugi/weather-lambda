# Arizona Weather Alert System

A Python application that monitors weather conditions across Arizona cities and sends alerts via email and SMS when dangerous conditions are detected.

## Features

- **Real-time Weather Monitoring**: Fetches weather data from OpenWeatherMap API every hour
- **Arizona-Specific Alert Triggers**:
  - Extreme heat (>101°F) after 5 PM with wind
  - Dust storm warnings (high winds + low visibility)
  - Critical daytime heat (>115°F)
  - Monsoon alerts (heavy rain + strong winds)
- **Email Notifications**: Detailed email alerts with weather conditions
- **Weather History Storage**: SQLite database for historical data
- **Detailed Reporting**: Rich HTML emails with current conditions

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

#### OpenWeatherMap (Free)
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key (1000 calls/day limit)

#### Gmail (Email)
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Google Account → Security → App passwords
3. Use the app password (not your regular password)

### 3. Configure Environment

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```env
OPENWEATHER_API_KEY=your_api_key_here
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password
RECIPIENT_EMAIL=alerts@yourdomain.com
```

## Usage

### Run Once (Testing)
```bash
python main.py once
```

### Continuous Monitoring
```bash
python main.py schedule
```

### View History
```bash
python main.py history        # Last 24 hours
python main.py history 48     # Last 48 hours
```

## Alert Triggers

### 1. Extreme Heat Evening
- **Condition**: Temperature > 101°F after 5 PM with wind > 10 mph
- **Severity**: HIGH
- **Purpose**: Warns of dangerous evening heat with wind that prevents cooling

### 2. Dust Storm Warning
- **Condition**: Wind speed > 25 mph with visibility < 5 miles
- **Severity**: HIGH
- **Purpose**: Alerts for Arizona's dangerous dust storms (haboobs)

### 3. Extreme Heat Day
- **Condition**: Temperature > 115°F between 10 AM - 6 PM
- **Severity**: CRITICAL
- **Purpose**: Life-threatening daytime heat warnings

### 4. Monsoon Alert
- **Condition**: Rain > 0.5 inches/hour with wind > 20 mph
- **Severity**: MEDIUM
- **Purpose**: Arizona monsoon season flash flood warnings

## Monitored Cities

- Phoenix
- Tucson
- Scottsdale
- Mesa

*You can modify the cities list in `config.py`*

## File Structure

```
weather-lambda/
├── main.py                 # Main application entry point
├── config.py              # Configuration and settings
├── weather_api.py         # OpenWeatherMap API integration
├── alert_system.py        # Alert logic and triggers
├── notification_system.py # Email and SMS notifications
├── database.py           # SQLite database operations
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your actual environment variables (create this)
├── weather_history.db   # SQLite database (auto-created)
├── weather_alerts.log   # Application logs (auto-created)
└── README.md           # This file
```

## Deployment Options

### Local Deployment
Run continuously on your local machine:
```bash
python main.py schedule
```

### Cloud Deployment
- **AWS Lambda**: Use with CloudWatch Events for scheduling
- **Google Cloud Functions**: Use with Cloud Scheduler
- **Azure Functions**: Use with Timer Triggers
- **Heroku**: Use with Heroku Scheduler add-on

### Cron Job (Linux/Mac)
Add to crontab for hourly checks:
```bash
0 * * * * cd /path/to/weather-lambda && python main.py once
```

## Customization

### Adding New Cities
Edit `CITIES` in `config.py`:
```python
CITIES = [
    {"name": "Flagstaff", "lat": 35.1983, "lon": -111.6513},
    # Add more cities...
]
```

### Custom Alert Triggers
Modify `ALERT_TRIGGERS` in `config.py`:
```python
"custom_alert": {
    "description": "Your custom condition",
    "conditions": {
        "temp_threshold": 95,
        "humidity_max": 20
    }
}
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify your OpenWeatherMap API key is active
2. **Email Not Sending**: Check Gmail app password and 2FA settings
3. **SMS Not Sending**: Verify Twilio credentials and phone number format
4. **Database Errors**: Ensure write permissions in the application directory

### Logs
Check `weather_alerts.log` for detailed error information.

