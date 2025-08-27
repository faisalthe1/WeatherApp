import requests
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional

class WeatherAPI:
    """Handles API interactions with Open-Meteo services"""
    
    def __init__(self):
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.historical_url = "https://archive-api.open-meteo.com/v1/era5"
    
    def search_cities(self, query: str, count: int = 10) -> List[Dict]:
        """Search for cities using the geocoding API"""
        try:
            params = {
                'name': query,
                'count': count,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data:
                return data['results']
            else:
                st.warning("No cities found matching your search.")
                return []
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error searching cities: {str(e)}")
            return []
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return []
    
    def get_historical_weather(self, latitude: float, longitude: float, 
                             start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Fetch historical weather data from Open-Meteo ERA5 API"""
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'start_date': start_date,
                'end_date': end_date,
                'daily': [
                    'temperature_2m_max',
                    'temperature_2m_min', 
                    'precipitation_sum',
                    'windspeed_10m_max'
                ],
                'timezone': 'auto'
            }
            
            response = requests.get(self.historical_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()

            if 'daily' in data:
                df = pd.DataFrame({
                    'date': pd.to_datetime(data['daily']['time']),
                    'tmax': data['daily']['temperature_2m_max'],
                    'tmin': data['daily']['temperature_2m_min'],
                    'precipitation': data['daily']['precipitation_sum'],
                    'windspeed_max': data['daily']['windspeed_10m_max']
                })
                
                df = df.fillna(0)
                
                return df
            else:
                st.error("Invalid response format from weather API")
                return None
                
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching weather data: {str(e)}")
            return None
        except KeyError as e:
            st.error(f"Missing expected data in API response: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error processing weather data: {str(e)}")
            return None
    
    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """Validate that the date range is reasonable"""
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            if start >= end:
                st.error("Start date must be before end date")
                return False
            
            min_date = pd.to_datetime('1940-01-01')
            if start < min_date:
                st.error(f"Historical data only available from {min_date.strftime('%Y-%m-%d')}")
                return False
            
            if (end - start).days > 3650:
                st.warning("Large date ranges may take longer to process")
            
            return True
            
        except Exception as e:
            st.error(f"Invalid date format: {str(e)}")
            return False