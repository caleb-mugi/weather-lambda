import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (
    EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL
)

class NotificationSystem:
    def __init__(self):
        self.email_configured = all([EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL])
    
    def send_alerts(self, alerts):
        """Send all alerts via email"""
        if not alerts:
            return
            
        for alert in alerts:
            self._send_email_alert(alert)
    
    def _send_email_alert(self, alert):
        """Send email notification"""
        if not self.email_configured:
            logging.warning("Email not configured, skipping email alert")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = RECIPIENT_EMAIL
            msg['Subject'] = f"Arizona Weather Alert - {alert['severity']} - {alert['city']}"
            
            # Create detailed email body
            body = self._create_email_body(alert)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email with improved connection handling
            server = None
            email_sent = False
            try:
                # Use STARTTLS with shorter timeout and better error handling
                server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                text = msg.as_string()
                server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)
                logging.info(f"Email alert sent successfully for {alert['city']}")
                email_sent = True
            except smtplib.SMTPAuthenticationError as auth_error:
                logging.error(f"Email authentication failed: {auth_error}")
                email_sent = False
            except smtplib.SMTPConnectError as conn_error:
                logging.error(f"Failed to connect to SMTP server: {conn_error}")
                email_sent = False
            except Exception as e:
                logging.error(f"Email sending failed: {e}")
                email_sent = False
            finally:
                if server:
                    try:
                        server.quit()
                    except:
                        pass
            
            if email_sent:
                logging.info(f"Email alert sent for {alert['city']}: {alert['type']}")
            else:
                logging.warning(f"Email alert FAILED for {alert['city']}: {alert['type']}")
            
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")
    
    
    def _create_email_body(self, alert):
        """Create detailed HTML email body"""
        weather = alert['weather_data']
        
        severity_colors = {
            'CRITICAL': '#FF0000',
            'HIGH': '#FF6600',
            'MEDIUM': '#FFAA00',
            'LOW': '#00AA00'
        }
        
        color = severity_colors.get(alert['severity'], '#666666')
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 5px solid {color}; padding-left: 20px; margin-bottom: 20px;">
                <h2 style="color: {color}; margin-top: 0;">Arizona Weather Alert - {alert['severity']}</h2>
                <h3>{alert['message']}</h3>
            </div>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                <h4>Current Weather Conditions - {weather['city']}</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;"><strong>Temperature:</strong></td>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;">{weather['temperature']:.1f}°F (feels like {weather['feels_like']:.1f}°F)</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;"><strong>Wind:</strong></td>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;">{weather['wind_speed']:.1f} mph</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;"><strong>Humidity:</strong></td>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;">{weather['humidity']}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;"><strong>Visibility:</strong></td>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;">{weather['visibility']:.1f} miles</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;"><strong>Conditions:</strong></td>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;">{weather['weather_description'].title()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;"><strong>Rain (1hr):</strong></td>
                        <td style="padding: 5px; border-bottom: 1px solid #ddd;">{weather['rain_1h']:.2f} inches</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Time:</strong></td>
                        <td style="padding: 5px;">{weather['timestamp'][:19].replace('T', ' ')}</td>
                    </tr>
                </table>
            </div>
            
            <div style="margin-top: 20px; padding: 10px; background-color: #e8f4f8; border-radius: 5px;">
                <p><strong>Safety Recommendations:</strong></p>
                <ul>
                    <li>Stay hydrated and avoid prolonged outdoor exposure</li>
                    <li>Check on elderly neighbors and pets</li>
                    <li>Avoid outdoor activities during extreme conditions</li>
                    <li>Keep windows and doors closed during dust storms</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html_body
