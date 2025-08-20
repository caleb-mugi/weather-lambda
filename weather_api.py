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
            return None
        except KeyError as e:
            logging.error(f"Error parsing weather data for {city_info['name']}: {e}")
            return None
    
    def get_all_cities_weather(self):
        """Fetch weather data for all configured cities"""
        weather_data = []
        
        for city in CITIES:
            data = self.get_weather_data(city)
            if data:
                weather_data.append(data)
                
        return weather_data
