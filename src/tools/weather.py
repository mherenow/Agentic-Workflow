from src.tools.registry import BaseTool
from typing import Dict, Any
import requests
import json

class WeatherTool(BaseTool):
    """Tool for getting weather information using OpenWeatherMap API."""
    
    def __init__(self, api_key: str = None):
        # Use a free weather API that doesn't require registration
        # We'll use wttr.in which provides weather data without API key
        self.base_url = "https://wttr.in"
    
    @property
    def name(self) -> str:
        return "weather"
    
    @property
    def description(self) -> str:
        return "Get current weather information for a specified location"
    
    def execute(self, location: str) -> Dict[str, Any]:
        """Get weather information for a location."""
        try:
            # Clean the location input
            location = location.strip()
            
            if not location:
                return {
                    "success": False,
                    "error": "Location cannot be empty"
                }
            
            # Use wttr.in API to get weather data in JSON format
            url = f"{self.base_url}/{location}?format=j1"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather information
            current = data.get("current_condition", [{}])[0]
            weather_info = {
                "location": location,
                "temperature_c": current.get("temp_C", "N/A"),
                "temperature_f": current.get("temp_F", "N/A"),
                "condition": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
                "humidity": current.get("humidity", "N/A"),
                "wind_speed_kmh": current.get("windspeedKmph", "N/A"),
                "wind_direction": current.get("winddir16Point", "N/A"),
                "feels_like_c": current.get("FeelsLikeC", "N/A"),
                "feels_like_f": current.get("FeelsLikeF", "N/A"),
                "visibility": current.get("visibility", "N/A"),
                "pressure": current.get("pressure", "N/A")
            }
            
            # Format the result as a readable string
            result = f"""Weather in {location}:
Temperature: {weather_info['temperature_c']}°C ({weather_info['temperature_f']}°F)
Condition: {weather_info['condition']}
Feels like: {weather_info['feels_like_c']}°C ({weather_info['feels_like_f']}°F)
Humidity: {weather_info['humidity']}%
Wind: {weather_info['wind_speed_kmh']} km/h {weather_info['wind_direction']}
Visibility: {weather_info['visibility']} km
Pressure: {weather_info['pressure']} mb"""
            
            return {
                "success": True,
                "result": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to fetch weather data: {str(e)}"
            }
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return {
                "success": False,
                "error": f"Failed to parse weather data: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Weather lookup failed: {str(e)}"
            }
