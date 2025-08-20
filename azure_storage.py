import os
import json
import logging
from datetime import datetime, timedelta
from azure.data.tables import TableServiceClient, TableEntity
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from config import CITIES

class AzureWeatherStorage:
    def __init__(self):
        # Get connection string from environment variable
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        
        if not self.connection_string:
            logging.warning("Azure Storage connection string not found. Using local fallback.")
            self.use_azure = False
            self.local_data = {"weather": [], "alerts": []}
        else:
            try:
                self.use_azure = True
                self.table_service = TableServiceClient.from_connection_string(self.connection_string)
                self.weather_table_name = "WeatherHistory"
                self.alerts_table_name = "AlertsHistory"
                self._ensure_tables_exist()
            except Exception as e:
                logging.error(f"Failed to initialize Azure Storage: {e}")
                logging.warning("Falling back to local storage")
                self.use_azure = False
                self.local_data = {"weather": [], "alerts": []}
    
    def _ensure_tables_exist(self):
        """Create tables if they don't exist"""
        if not self.use_azure:
            return
            
        try:
            self.table_service.create_table(self.weather_table_name)
        except ResourceExistsError:
            pass
        except Exception as e:
            logging.error(f"Error creating weather table: {e}")
            
        try:
            self.table_service.create_table(self.alerts_table_name)
        except ResourceExistsError:
            pass
        except Exception as e:
            logging.error(f"Error creating alerts table: {e}")
    
    def store_weather_data(self, weather_data_list):
        """Store weather data in Azure Table Storage or local fallback"""
        if not self.use_azure:
            # Local fallback
            for data in weather_data_list:
                data['stored_at'] = datetime.utcnow().isoformat()
                self.local_data["weather"].append(data)
            logging.info(f"Stored weather data locally for {len(weather_data_list)} cities")
            return
        
        try:
            weather_table = self.table_service.get_table_client(self.weather_table_name)
            
            for data in weather_data_list:
                # Create entity for Azure Table Storage
                entity = TableEntity()
                entity['PartitionKey'] = data['city']
                entity['RowKey'] = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
                
                # Add weather data
                entity['Temperature'] = data['temperature']
                entity['FeelsLike'] = data['feels_like']
                entity['Humidity'] = data['humidity']
                entity['Pressure'] = data['pressure']
                entity['WindSpeed'] = data['wind_speed']
                entity['WindDirection'] = data['wind_direction']
                entity['Visibility'] = data['visibility']
                entity['WeatherMain'] = data['weather_main']
                entity['WeatherDescription'] = data['weather_description']
                entity['Rain1h'] = data['rain_1h']
                entity['Timestamp'] = data['timestamp']
                entity['Sunrise'] = data['sunrise']
                entity['Sunset'] = data['sunset']
                
                weather_table.create_entity(entity)
            
            logging.info(f"Stored weather data in Azure for {len(weather_data_list)} cities")
            
        except Exception as e:
            logging.error(f"Error storing weather data in Azure: {e}")
            # Fallback to local storage
            if not hasattr(self, 'local_data'):
                self.local_data = {"weather": [], "alerts": []}
            for data in weather_data_list:
                data['stored_at'] = datetime.utcnow().isoformat()
                self.local_data["weather"].append(data)
            logging.info(f"Stored weather data locally as fallback for {len(weather_data_list)} cities")
    
    def store_alert(self, alert):
        """Store alert in Azure Table Storage or local fallback"""
        if not self.use_azure:
            # Local fallback
            alert_data = {
                **alert,
                'stored_at': datetime.utcnow().isoformat(),
                'email_sent': True,
                'sms_sent': False
            }
            self.local_data["alerts"].append(alert_data)
            logging.info(f"Stored alert locally: {alert['type']} for {alert['city']}")
            return
        
        try:
            alerts_table = self.table_service.get_table_client(self.alerts_table_name)
            
            # Create entity for Azure Table Storage
            entity = TableEntity()
            entity['PartitionKey'] = alert['city']
            entity['RowKey'] = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
            
            # Add alert data
            entity['AlertType'] = alert['type']
            entity['Message'] = alert['message']
            entity['Severity'] = alert['severity']
            entity['WeatherData'] = json.dumps(alert['weather_data'])
            entity['EmailSent'] = True
            entity['SmsSent'] = False
            
            alerts_table.create_entity(entity)
            
            logging.info(f"Stored alert in Azure: {alert['type']} for {alert['city']}")
            
        except Exception as e:
            logging.error(f"Error storing alert in Azure: {e}")
            # Fallback to local storage
            if not hasattr(self, 'local_data'):
                self.local_data = {"weather": [], "alerts": []}
            alert_data = {
                **alert,
                'stored_at': datetime.utcnow().isoformat(),
                'email_sent': True,
                'sms_sent': False
            }
            self.local_data["alerts"].append(alert_data)
            logging.info(f"Stored alert locally as fallback: {alert['type']} for {alert['city']}")
    
    def get_recent_weather(self, city=None, hours=24):
        """Get recent weather data"""
        if not self.use_azure:
            # Local fallback
            cutoff_time = datetime() - timedelta(hours=hours)
            recent_data = []
            
            for data in self.local_data["weather"]:
                stored_time = datetime.fromisoformat(data.get('stored_at', '1970-01-01'))
                if stored_time > cutoff_time:
                    if not city or data['city'] == city:
                        recent_data.append(data)
            
            return recent_data
        
        try:
            weather_table = self.table_service.get_table_client(self.weather_table_name)
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            if city:
                # Query specific city
                filter_query = f"PartitionKey eq '{city}' and Timestamp ge datetime'{cutoff_time.isoformat()}'"
            else:
                # Query all cities
                filter_query = f"Timestamp ge datetime'{cutoff_time.isoformat()}'"
            
            entities = weather_table.query_entities(filter_query)
            
            results = []
            for entity in entities:
                results.append({
                    'city': entity['PartitionKey'],
                    'temperature': entity.get('Temperature', 0),
                    'wind_speed': entity.get('WindSpeed', 0),
                    'weather_description': entity.get('WeatherDescription', ''),
                    'timestamp': entity.get('Timestamp', ''),
                    'stored_at': entity['Timestamp'].isoformat() if hasattr(entity['Timestamp'], 'isoformat') else str(entity['Timestamp'])
                })
            
            return results
            
        except Exception as e:
            logging.error(f"Error retrieving weather data from Azure: {e}")
            return []
    
    def get_recent_alerts(self, hours=24):
        """Get recent alerts"""
        if not self.use_azure:
            # Local fallback
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_alerts = []
            
            for alert in self.local_data["alerts"]:
                stored_time = datetime.fromisoformat(alert.get('stored_at', '1970-01-01'))
                if stored_time > cutoff_time:
                    recent_alerts.append({
                        'city': alert['city'],
                        'type': alert['type'],
                        'message': alert['message'],
                        'severity': alert['severity'],
                        'stored_at': alert['stored_at']
                    })
            
            return recent_alerts
        
        try:
            alerts_table = self.table_service.get_table_client(self.alerts_table_name)
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            filter_query = f"Timestamp ge datetime'{cutoff_time.isoformat()}'"
            
            entities = alerts_table.query_entities(filter_query)
            
            results = []
            for entity in entities:
                results.append({
                    'city': entity['PartitionKey'],
                    'type': entity.get('AlertType', ''),
                    'message': entity.get('Message', ''),
                    'severity': entity.get('Severity', ''),
                    'stored_at': entity['Timestamp'].isoformat() if hasattr(entity['Timestamp'], 'isoformat') else str(entity['Timestamp'])
                })
            
            return results
            
        except Exception as e:
            logging.error(f"Error retrieving alerts from Azure: {e}")
            return []
