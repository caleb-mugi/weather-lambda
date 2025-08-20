import os
from dotenv import load_dotenv

load_dotenv()

# Weather API Configuration (using OpenWeatherMap - free tier)
WEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# Arizona cities to monitor (you can modify this list)
CITIES = [
    {"name": "Phoenix", "lat": 33.4484, "lon": -112.0740},
    {"name": "Tucson", "lat": 32.2226, "lon": -110.9747},
    {"name": "Scottsdale", "lat": 33.4942, "lon": -111.9261},
    {"name": "Mesa", "lat": 33.4152, "lon": -111.8315}
]

# Email Configuration
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_APP_PASSWORD')  # Use app password for Gmail
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# SMS Configuration - DISABLED
# SMS notifications have been removed per user request

# Alert Triggers for Arizona
ALERT_TRIGGERS = {
    "extreme_heat_evening": {
        "description": "Temperature above 101°F after 5 PM with wind",
        "conditions": {
            "temp_threshold": 101,  # Fahrenheit
            "time_after": 17,  # 5 PM in 24-hour format
            "wind_speed_min": 10  # mph
        }
    },
    "dust_storm_warning": {
        "description": "High winds with low visibility conditions",
        "conditions": {
            "wind_speed_min": 25,  # mph
            "visibility_max": 5  # miles
        }
    },
    "extreme_heat_day": {
        "description": "Temperature above 115°F during daytime",
        "conditions": {
            "temp_threshold": 115,  # Fahrenheit
            "time_between": (10, 18)  # 10 AM to 6 PM
        }
    },
    "monsoon_alert": {
        "description": "Heavy rain with strong winds",
        "conditions": {
            "rain_threshold": 0.5,  # inches per hour
            "wind_speed_min": 20  # mph
        }
    }
}

# Database
DATABASE_PATH = "weather_history.db"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "weather_alerts.log"
