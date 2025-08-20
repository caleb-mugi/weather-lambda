#!/usr/bin/env python3
"""
Arizona Weather Alert System
Monitors weather conditions and sends alerts via email and SMS
"""

import logging
import schedule
import time
from datetime import datetime
from weather_api import WeatherAPI
from alert_system import AlertSystem
from notification_system import NotificationSystem
from database import WeatherDatabase
from config import LOG_LEVEL, LOG_FILE

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class WeatherAlertApp:
    def __init__(self):
        self.weather_api = WeatherAPI()
        self.alert_system = AlertSystem()
        self.notification_system = NotificationSystem()
        self.database = WeatherDatabase()
        
    def check_weather_and_alerts(self):
        """Main function to check weather and send alerts"""
        logging.info("Starting weather check...")
        
        try:
            # Fetch weather data for all cities
            weather_data = self.weather_api.get_all_cities_weather()
            
            if not weather_data:
                logging.warning("No weather data retrieved")
                return
            
            # Store weather data in database
            self.database.store_weather_data(weather_data)
            
            # Check for alerts
            alerts = self.alert_system.check_alerts(weather_data)
            
            if alerts:
                logging.info(f"Found {len(alerts)} alerts")
                
                # Send notifications
                self.notification_system.send_alerts(alerts)
                
                # Store alerts in database
                for alert in alerts:
                    self.database.store_alert(alert, email_sent=True, sms_sent=False)
                    
            else:
                logging.info("No alerts triggered")
                
            # Log current conditions
            for data in weather_data:
                logging.info(f"{data['city']}: {data['temperature']:.1f}°F, "
                           f"Wind: {data['wind_speed']:.1f}mph, "
                           f"Conditions: {data['weather_description']}")
                
        except Exception as e:
            logging.error(f"Error in weather check: {e}")
    
    def run_once(self):
        """Run the weather check once"""
        print("Running weather check...")
        self.check_weather_and_alerts()
        print("Weather check completed.")
    
    def run_scheduler(self):
        """Run the scheduler for continuous monitoring"""
        print("Starting Arizona Weather Alert System...")
        print("Checking weather every hour...")
        
        # Schedule weather checks every hour
        schedule.every().hour.do(self.check_weather_and_alerts)
        
        # Run initial check
        self.check_weather_and_alerts()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks
    
    def show_recent_data(self, hours=24):
        """Show recent weather data and alerts"""
        print(f"\n=== Recent Weather Data (Last {hours} hours) ===")
        weather_data = self.database.get_recent_weather(hours=hours)
        
        if weather_data:
            for row in weather_data[-10:]:  # Show last 10 entries
                print(f"{row[1]}: {row[2]:.1f}°F, Wind: {row[6]:.1f}mph - {row[12]}")
        else:
            print("No recent weather data found")
        
        print(f"\n=== Recent Alerts (Last {hours} hours) ===")
        alerts = self.database.get_recent_alerts(hours=hours)
        
        if alerts:
            for alert in alerts:
                print(f"{alert[1]} - {alert[2]} ({alert[4]}) - {alert[7]}")
        else:
            print("No recent alerts found")

def main():
    """Main entry point"""
    import sys
    
    app = WeatherAlertApp()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "once":
            app.run_once()
        elif command == "history":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            app.show_recent_data(hours)
        elif command == "schedule":
            app.run_scheduler()
        else:
            print("Usage:")
            print("  python main.py once      - Run weather check once")
            print("  python main.py schedule  - Run continuous monitoring")
            print("  python main.py history [hours] - Show recent data")
    else:
        print("Arizona Weather Alert System")
        print("Usage:")
        print("  python main.py once      - Run weather check once")
        print("  python main.py schedule  - Run continuous monitoring")
        print("  python main.py history [hours] - Show recent data")

if __name__ == "__main__":
    main()
