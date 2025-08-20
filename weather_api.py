import requests
import logging
from datetime import datetime
from config import WEATHER_API_KEY, WEATHER_API_URL, CITIES

class WeatherAPI:
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.base_url = WEATHER_API_URL
        
    def get_weather_data(self, city_info):
        """Fetch weather data for a specific city"""
        try:
            # Check if API key is valid
            if not self.api_key or self.api_key == "your_new_api_key_here":
                logging.error(f"Invalid API key for {city_info['name']}. Please set OPENWEATHER_API_KEY in .env file")
                return self._create_mock_data(city_info)
            
            params = {
                'lat': city_info['lat'],
                'lon': city_info['lon'],
                'appid': self.api_key,
                'units': 'imperial'  # Fahrenheit
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather information
            weather_info = {
                'city': city_info['name'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'visibility': data.get('visibility', 10000) / 1609.34,  # Convert to miles
                'weather_main': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'timestamp': datetime.now().isoformat(),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).isoformat(),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).isoformat()
            }
            
            # Add rain data if available
            if 'rain' in data:
                weather_info['rain_1h'] = data['rain'].get('1h', 0) * 0.0393701  # Convert mm to inches
            else:
                weather_info['rain_1h'] = 0
                
            return weather_info
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching weather data for {city_info['name']}: {e}")
            return self._create_mock_data(city_info)
        except KeyError as e:
            logging.error(f"Error parsing weather data for {city_info['name']}: {e}")
            return self._create_mock_data(city_info)
    
    def _create_mock_data(self, city_info):
        """Create mock weather data for testing when API is unavailable"""
        import random
        
        # Arizona-like weather conditions for testing
        base_temps = {"Phoenix": 105, "Tucson": 102, "Scottsdale": 106, "Mesa": 104}
        base_temp = base_temps.get(city_info['name'], 100)
        
        # Create conditions that might trigger alerts for testing
        current_hour = datetime.now().hour
        temp = base_temp + random.randint(-5, 10)
        wind = random.randint(5, 25)
        
        # If it's after 5 PM, make temperature high enough to trigger alert
        if current_hour >= 17 and city_info['name'] == 'Phoenix':
            temp = 105  # Above 101°F threshold
            wind = 15   # Above 10 mph threshold
        
        mock_data = {
            'city': city_info['name'],
            'temperature': temp,
            'feels_like': temp + random.randint(0, 15),
            'humidity': random.randint(10, 30),  # Low humidity for Arizona
            'pressure': random.randint(1010, 1020),
            'wind_speed': wind,
            'wind_direction': random.randint(0, 360),
            'visibility': random.randint(8, 10),
            'weather_main': random.choice(['Clear', 'Clouds', 'Dust']),
            'weather_description': random.choice(['clear sky', 'few clouds', 'dust']),
            'rain_1h': 0,  # Rarely rains in Arizona
            'timestamp': datetime.now().isoformat(),
            'sunrise': datetime.now().replace(hour=6, minute=0).isoformat(),
            'sunset': datetime.now().replace(hour=19, minute=30).isoformat()
        }
        
        logging.info(f"Using mock data for {city_info['name']}: {mock_data['temperature']:.1f}°F")
        return mock_data
    
    def get_all_cities_weather(self):
        """Fetch weather data for all configured cities"""
        weather_data = []
        
        for city in CITIES:
            data = self.get_weather_data(city)
            if data:
                weather_data.append(data)
                
        return weather_data
