import os
import requests
from dotenv import load_dotenv

load_dotenv()

class WeatherTool:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, city):
        """Get current weather for a city."""
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'  # Use metric units
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant weather information
            weather_info = {
                'city': data['name'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed']
            }
            
            # Format the response in a more natural way
            response = {
                'status': 'success',
                'data': weather_info,
                'message': f"The current weather in {weather_info['city']} is {weather_info['description']}. "
                          f"The temperature is {weather_info['temperature']}°C, "
                          f"feels like {weather_info['feels_like']}°C. "
                          f"Humidity is {weather_info['humidity']}% and "
                          f"wind speed is {weather_info['wind_speed']} m/s."
            }
            
            return response
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f"Error getting weather information: {str(e)}"
            } 