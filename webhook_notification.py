import requests
import json
import logging
from datetime import datetime

class WebhookNotification:
    """Alternative notification method using HTTP webhooks"""
    
    def __init__(self):
        # You can use services like:
        # - Zapier webhooks
        # - Microsoft Power Automate
        # - IFTTT
        # - Slack webhooks
        # - Discord webhooks
        self.webhook_url = "https://hooks.zapier.com/hooks/catch/your-webhook-id/"
        
    def send_alert(self, alert):
        """Send alert via webhook"""
        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "alert_type": alert['type'],
                "city": alert['city'],
                "severity": alert['severity'],
                "message": alert['message'],
                "temperature": alert['weather_data']['temperature'],
                "wind_speed": alert['weather_data']['wind_speed'],
                "conditions": alert['weather_data']['weather_description']
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info(f"Webhook alert sent for {alert['city']}: {alert['type']}")
                return True
            else:
                logging.error(f"Webhook failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Webhook notification failed: {e}")
            return False
    
    def send_alerts(self, alerts):
        """Send multiple alerts"""
        for alert in alerts:
            self.send_alert(alert)
