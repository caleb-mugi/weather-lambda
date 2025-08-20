import azure.functions as func
import logging
import json
from datetime import datetime

# Create the Azure Functions app
app = func.FunctionApp()

@app.timer_trigger(schedule="0 */2 * * * *", arg_name="mytimer", run_on_startup=False,
              use_monitor=False)
def weather_alert_timer(mytimer: func.TimerRequest) -> None:
    """
    Azure Function triggered every 2 minutes to check weather and send alerts
    CRON: "0 */2 * * * *" = every 2 minutes at second 0
    """
    utc_timestamp = datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    try:
        # Import here to avoid startup issues
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

@app.http_trigger(route="weather/status", auth_level=func.AuthLevel.FUNCTION)
def weather_status(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP endpoint to check recent weather data and alerts
    """
    logging.info('Weather status endpoint called')
    
    try:
        storage = AzureWeatherStorage()
        
        # Get recent weather data (last 24 hours)
        recent_weather = storage.get_recent_weather(hours=24)
        recent_alerts = storage.get_recent_alerts(hours=24)
        
        response_data = {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "recent_weather_count": len(recent_weather),
            "recent_alerts_count": len(recent_alerts),
            "recent_weather": recent_weather[-10:],  # Last 10 entries
            "recent_alerts": recent_alerts
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in weather status endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.http_trigger(route="weather/test", auth_level=func.AuthLevel.FUNCTION)
def weather_test(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP endpoint to manually trigger weather check (for testing)
    """
    logging.info('Weather test endpoint called')
    
    try:
        # Run the same logic as the timer trigger
        weather_api = WeatherAPI()
        alert_system = AlertSystem()
        notification_system = NotificationSystem()
        storage = AzureWeatherStorage()
        
        weather_data = weather_api.get_all_cities_weather()
        
        if not weather_data:
            return func.HttpResponse(
                json.dumps({"status": "error", "message": "No weather data retrieved"}),
                status_code=500,
                mimetype="application/json"
            )
        
        storage.store_weather_data(weather_data)
        alerts = alert_system.check_alerts(weather_data)
        
        if alerts:
            notification_system.send_alerts(alerts)
            for alert in alerts:
                storage.store_alert(alert)
        
        response_data = {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "weather_data_count": len(weather_data),
            "alerts_triggered": len(alerts),
            "cities_checked": [data['city'] for data in weather_data],
            "alerts": [{"city": alert['city'], "type": alert['type'], "severity": alert['severity']} for alert in alerts]
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in weather test endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
