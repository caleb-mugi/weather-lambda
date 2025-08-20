import sqlite3
import json
import logging
from datetime import datetime
from config import DATABASE_PATH

class WeatherDatabase:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create weather_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    temperature REAL,
                    feels_like REAL,
                    humidity INTEGER,
                    pressure REAL,
                    wind_speed REAL,
                    wind_direction REAL,
                    visibility REAL,
                    weather_main TEXT,
                    weather_description TEXT,
                    rain_1h REAL,
                    timestamp TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create alerts_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    city TEXT NOT NULL,
                    message TEXT,
                    severity TEXT,
                    weather_data TEXT,
                    email_sent BOOLEAN DEFAULT 0,
                    sms_sent BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info("Database initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
    
    def store_weather_data(self, weather_data_list):
        """Store weather data in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for data in weather_data_list:
                cursor.execute('''
                    INSERT INTO weather_history 
                    (city, temperature, feels_like, humidity, pressure, wind_speed, 
                     wind_direction, visibility, weather_main, weather_description, 
                     rain_1h, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['city'], data['temperature'], data['feels_like'],
                    data['humidity'], data['pressure'], data['wind_speed'],
                    data['wind_direction'], data['visibility'], data['weather_main'],
                    data['weather_description'], data['rain_1h'], data['timestamp']
                ))
            
            conn.commit()
            conn.close()
            logging.info(f"Stored weather data for {len(weather_data_list)} cities")
            
        except Exception as e:
            logging.error(f"Error storing weather data: {e}")
    
    def store_alert(self, alert, email_sent=False, sms_sent=False):
        """Store alert information in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts_history 
                (alert_type, city, message, severity, weather_data, email_sent, sms_sent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert['type'], alert['city'], alert['message'], alert['severity'],
                json.dumps(alert['weather_data']), email_sent, sms_sent
            ))
            
            conn.commit()
            conn.close()
            logging.info(f"Stored alert: {alert['type']} for {alert['city']}")
            
        except Exception as e:
            logging.error(f"Error storing alert: {e}")
    
    def get_recent_weather(self, city=None, hours=24):
        """Get recent weather data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if city:
                cursor.execute('''
                    SELECT * FROM weather_history 
                    WHERE city = ? AND created_at > datetime('now', '-{} hours')
                    ORDER BY created_at DESC
                '''.format(hours), (city,))
            else:
                cursor.execute('''
                    SELECT * FROM weather_history 
                    WHERE created_at > datetime('now', '-{} hours')
                    ORDER BY created_at DESC
                '''.format(hours))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
            
        except Exception as e:
            logging.error(f"Error retrieving weather data: {e}")
            return []
    
    def get_recent_alerts(self, hours=24):
        """Get recent alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM alerts_history 
                WHERE created_at > datetime('now', '-{} hours')
                ORDER BY created_at DESC
            '''.format(hours))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
            
        except Exception as e:
            logging.error(f"Error retrieving alerts: {e}")
            return []
