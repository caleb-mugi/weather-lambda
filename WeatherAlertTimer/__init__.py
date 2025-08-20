import azure.functions as func
import logging
from datetime import datetime

def main(mytimer: func.TimerRequest) -> None:
    """
    Azure Function triggered every 2 minutes to check weather and send alerts
    """
    utc_timestamp = datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    try:
        # Import here to avoid startup issues
        import sys
        import os
        
        # Add parent directory to path for imports
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
            
        from weather_api import WeatherAPI
        from alert_system import AlertSystem
        from notification_system import NotificationSystem
        from azure_storage import AzureWeatherStorage
        
        # Initialize components
        weather_api = WeatherAPI()
        alert_system = AlertSystem()
        notification_system = NotificationSystem()
        storage = AzureWeatherStorage()
        
        # Fetch weather data for all cities
        weather_data = weather_api.get_all_cities_weather()
        
        if not weather_data:
            logging.warning("No weather data retrieved")
            return
        
        # Store weather data in Azure Table Storage
        storage.store_weather_data(weather_data)
        
        # Check for alerts
        alerts = alert_system.check_alerts(weather_data)
        
        if alerts:
            logging.info(f"Found {len(alerts)} alerts")
            
            # Send email notifications
            notification_system.send_alerts(alerts)
            
            # Store alerts in Azure Table Storage
            for alert in alerts:
                storage.store_alert(alert)
                
        else:
            logging.info("No alerts triggered")
            
        # Log current conditions
        for data in weather_data:
            logging.info(f"{data['city']}: {data['temperature']:.1f}°F, "
                       f"Wind: {data['wind_speed']:.1f}mph, "
                       f"Conditions: {data['weather_description']}")
                       
    except Exception as e:
        logging.error(f"Error in weather check: {e}")
        raise
