
"""
Weather Insights Dashboard

A comprehensive weather analysis tool built with Streamlit that provides:
- Interactive weather data visualization
- Historical climate analysis
- Temperature anomaly detection
- Data export capabilities

Modules:
- api: Weather API integration and data fetching
- transform: Data processing and feature engineering
- plots: Interactive visualization generation
"""

__version__ = "1.0.0"
__author__ = "Weather Insights Team"
__email__ = "contact@weatherinsights.com"

from .api import WeatherAPI
from .transform import WeatherTransformer
from .plots import WeatherPlots

__all__ = ["WeatherAPI", "WeatherTransformer", "WeatherPlots"]