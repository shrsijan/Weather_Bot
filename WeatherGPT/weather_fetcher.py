import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_weather(location):
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        return "Error: API key not found. Please check your .env file"
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": location,
        "appid": API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        
        if 'main' not in weather_data:
            return f"Error: Unable to get weather data for {location}. Please check the location name."
        
        weather_info = {
            "temperature": weather_data["main"]["temp"],
            "feels_like": weather_data["main"]["feels_like"],
            "humidity": weather_data["main"]["humidity"],
            "description": weather_data["weather"][0]["description"],
            "wind_speed": weather_data["wind"]["speed"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Store weather data in a JSON file
        with open("weather_data.json", "w") as f:
            json.dump(weather_info, f, indent=4)
        
        return weather_info
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return "Error: Invalid API key. Please check your API key in the .env file"
        elif e.response.status_code == 404:
            return f"Error: Location '{location}' not found"
        else:
            return f"HTTP Error: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"Network Error: {str(e)}"
    except KeyError as e:
        return f"Data Error: Missing field {str(e)} in weather data"
    except Exception as e:
        return f"Error: {str(e)}"