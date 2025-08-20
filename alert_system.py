import logging
from datetime import datetime
from config import ALERT_TRIGGERS

class AlertSystem:
    def __init__(self):
        self.triggers = ALERT_TRIGGERS
        
    def check_alerts(self, weather_data):
        """Check weather data against all alert triggers"""
        alerts = []
        current_hour = datetime.now().hour
        
        for data in weather_data:
            city_alerts = self._check_city_alerts(data, current_hour)
            alerts.extend(city_alerts)
            
        return alerts
    
    def _check_city_alerts(self, weather_data, current_hour):
        """Check alert conditions for a specific city"""
        alerts = []
        
        # Check extreme heat evening alert
        if self._check_extreme_heat_evening(weather_data, current_hour):
            alerts.append({
                'type': 'extreme_heat_evening',
                'city': weather_data['city'],
                'message': f"EXTREME HEAT ALERT: {weather_data['city']} - {weather_data['temperature']:.1f}°F with {weather_data['wind_speed']:.1f} mph winds after 5 PM",
                'severity': 'HIGH',
                'weather_data': weather_data
            })
        
        # Check dust storm warning
        if self._check_dust_storm(weather_data):
            alerts.append({
                'type': 'dust_storm_warning',
                'city': weather_data['city'],
                'message': f"DUST STORM WARNING: {weather_data['city']} - High winds ({weather_data['wind_speed']:.1f} mph) with reduced visibility ({weather_data['visibility']:.1f} miles)",
                'severity': 'HIGH',
                'weather_data': weather_data
            })
        
        # Check extreme daytime heat
        if self._check_extreme_heat_day(weather_data, current_hour):
            alerts.append({
                'type': 'extreme_heat_day',
                'city': weather_data['city'],
                'message': f"EXTREME HEAT WARNING: {weather_data['city']} - Dangerous temperature of {weather_data['temperature']:.1f}°F",
                'severity': 'CRITICAL',
                'weather_data': weather_data
            })
        
        # Check monsoon alert
        if self._check_monsoon(weather_data):
            alerts.append({
                'type': 'monsoon_alert',
                'city': weather_data['city'],
                'message': f"MONSOON ALERT: {weather_data['city']} - Heavy rain ({weather_data['rain_1h']:.2f} in/hr) with strong winds ({weather_data['wind_speed']:.1f} mph)",
                'severity': 'MEDIUM',
                'weather_data': weather_data
            })
            
        return alerts
    
    def _check_extreme_heat_evening(self, data, current_hour):
        """Check for extreme heat after 5 PM with wind"""
        trigger = self.triggers['extreme_heat_evening']['conditions']
        return (
            data['temperature'] > trigger['temp_threshold'] and
            current_hour >= trigger['time_after'] and
            data['wind_speed'] >= trigger['wind_speed_min']
        )
    
    def _check_dust_storm(self, data):
        """Check for dust storm conditions"""
        trigger = self.triggers['dust_storm_warning']['conditions']
        return (
            data['wind_speed'] >= trigger['wind_speed_min'] and
            data['visibility'] <= trigger['visibility_max']
        )
    
    def _check_extreme_heat_day(self, data, current_hour):
        """Check for extreme daytime heat"""
        trigger = self.triggers['extreme_heat_day']['conditions']
        time_range = trigger['time_between']
        return (
            data['temperature'] > trigger['temp_threshold'] and
            time_range[0] <= current_hour <= time_range[1]
        )
    
    def _check_monsoon(self, data):
        """Check for monsoon conditions"""
        trigger = self.triggers['monsoon_alert']['conditions']
        return (
            data['rain_1h'] >= trigger['rain_threshold'] and
            data['wind_speed'] >= trigger['wind_speed_min']
        )
