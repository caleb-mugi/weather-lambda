import azure.functions as func
import logging
import json
from datetime import datetime

def main(mytimer: func.TimerRequest) -> None:
    """
    Azure Function triggered every hour to check weather and send alerts
    """
    utc_timestamp = datetime.utcnow().isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    try:
        logging.info("Starting timer function execution")
        
        # Import here to avoid startup issues
        logging.info("Importing modules...")
        from weather_api import WeatherAPI
        from alert_system import AlertSystem
        from notification_system import NotificationSystem
        from azure_storage import AzureWeatherStorage
        logging.info("Modules imported successfully")
        
        # Initialize components
        logging.info("Initializing components...")
        weather_api = WeatherAPI()
        logging.info("WeatherAPI initialized")
        alert_system = AlertSystem()
        logging.info("AlertSystem initialized")
        notification_system = NotificationSystem()
        logging.info("NotificationSystem initialized")
        storage = AzureWeatherStorage()
        logging.info("AzureWeatherStorage initialized")
        
        # Fetch weather data for all cities
        logging.info("Fetching weather data...")
        weather_data = weather_api.get_all_cities_weather()
        logging.info(f"Weather data retrieved: {len(weather_data) if weather_data else 0} cities")
        
        if not weather_data:
            logging.warning("No weather data retrieved")
            return
        
        # Store weather data in Azure Table Storage
        logging.info("Storing weather data...")
        storage.store_weather_data(weather_data)
        logging.info("Weather data stored successfully")
        
        # Check for alerts
        logging.info("Checking for alerts...")
        alerts = alert_system.check_alerts(weather_data)
        logging.info(f"Alert check completed: {len(alerts)} alerts found")
        
        if alerts:
            logging.info(f"Processing {len(alerts)} alerts")
            
            # Send email notifications
            logging.info("Sending email notifications...")
            notification_system.send_alerts(alerts)
            logging.info("Email notifications sent")
            
            # Store alerts in Azure Table Storage
            logging.info("Storing alerts...")
            for alert in alerts:
                storage.store_alert(alert)
            logging.info("Alerts stored successfully")
                
        else:
            logging.info("No alerts triggered")
            
        # Log current conditions
        logging.info("Current weather conditions:")
        for data in weather_data:
            logging.info(f"{data['city']}: {data['temperature']:.1f}°F, "
                       f"Wind: {data['wind_speed']:.1f}mph, "
                       f"Conditions: {data['weather_description']}")
                       
        logging.info("Timer function execution completed successfully")
                       
    except Exception as e:
        logging.error(f"Error in weather check: {e}")
        logging.error(f"Exception type: {type(e).__name__}")
        logging.error(f"Exception args: {e.args}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        # Don't raise the exception - let the function complete successfully
