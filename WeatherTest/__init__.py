import azure.functions as func
import logging
import json
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP endpoint to manually trigger weather check (for testing)
    """
    logging.info('Weather test endpoint called')
    
    try:
        # Import here to avoid startup issues
        from weather_api import WeatherAPI
        from alert_system import AlertSystem
        from notification_system import NotificationSystem
        from azure_storage import AzureWeatherStorage
        
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
