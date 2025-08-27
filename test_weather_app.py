import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api import WeatherAPI
from src.transform import WeatherTransformer
from src.plots import WeatherPlots


class TestWeatherTransformer:
    """Test cases for WeatherTransformer class"""
    
    def setup_method(self):
        """Setup test data and transformer"""
        self.transformer = WeatherTransformer()
        
        # Create sample weather data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.sample_data = pd.DataFrame({
            'date': dates,
            'tmax': np.random.normal(20, 10, len(dates)),
            'tmin': np.random.normal(10, 8, len(dates)),
            'precipitation': np.random.exponential(2, len(dates)),
            'windspeed_max': np.random.gamma(2, 5, len(dates))
        })
        # Ensure tmax > tmin
        self.sample_data['tmin'] = np.minimum(
            self.sample_data['tmin'], 
            self.sample_data['tmax'] - 1
        )
    
    def test_add_basic_features(self):
        """Test basic feature engineering"""
        result = self.transformer.add_basic_features(self.sample_data)
        
        # Check new columns exist
        expected_cols = ['tmean', 'temp_range', 'year', 'month', 'day_of_year', 'season']
        for col in expected_cols:
            assert col in result.columns, f"Column {col} not found"
        
        # Check tmean calculation
        expected_tmean = (result['tmax'] + result['tmin']) / 2
        pd.testing.assert_series_equal(result['tmean'], expected_tmean, check_names=False)
        
        # Check temp_range calculation
        expected_range = result['tmax'] - result['tmin']
        pd.testing.assert_series_equal(result['temp_range'], expected_range, check_names=False)
        
        # Check season mapping
        assert result['season'].nunique() == 4, "Should have 4 seasons"
        assert all(season in ['Winter', 'Spring', 'Summer', 'Fall'] 
                  for season in result['season'].unique())
    
    def test_add_rolling_averages(self):
        """Test rolling average calculations"""
        # Add basic features first
        df_with_features = self.transformer.add_basic_features(self.sample_data)
        result = self.transformer.add_rolling_averages(df_with_features)
        
        # Check rolling columns exist
        rolling_cols = ['tmean_7d', 'tmax_7d', 'tmin_7d', 'precip_7d']
        for col in rolling_cols:
            assert col in result.columns, f"Rolling column {col} not found"
        
        # Check that rolling averages have some NaN values (due to window)
        assert result['tmean_7d'].isna().sum() > 0, "Rolling average should have NaN values"
    
    def test_add_temperature_anomalies(self):
        """Test temperature anomaly calculations"""
        # Add basic features first
        df_with_features = self.transformer.add_basic_features(self.sample_data)
        result = self.transformer.add_temperature_anomalies(df_with_features)
        
        # Check anomaly columns exist
        anomaly_cols = ['temp_anomaly', 'monthly_climate', 'anomaly_category']
        for col in anomaly_cols:
            assert col in result.columns, f"Anomaly column {col} not found"
        
        # Check that anomalies sum to approximately zero (deviations from mean)
        assert abs(result['temp_anomaly'].sum()) < 1, "Anomalies should sum to near zero"
    
    def test_monthly_aggregation(self):
        """Test monthly data aggregation"""
        # Add basic features first
        df_with_features = self.transformer.add_basic_features(self.sample_data)
        result = self.transformer.aggregate_monthly(df_with_features)
        
        # Should have 12 months for full year
        assert len(result) == 12, "Should have 12 monthly records"
        
        # Check that aggregation preserved essential columns
        essential_cols = ['date', 'tmax', 'tmin', 'tmean', 'precipitation']
        for col in essential_cols:
            assert col in result.columns, f"Essential column {col} missing after aggregation"
    
    def test_calculate_statistics(self):
        """Test summary statistics calculation"""
        df_with_features = self.transformer.add_basic_features(self.sample_data)
        stats = self.transformer.calculate_statistics(df_with_features)
        
        # Check structure
        assert isinstance(stats, dict), "Statistics should be a dictionary"
        assert 'temperature' in stats, "Temperature stats missing"
        assert 'precipitation' in stats, "Precipitation stats missing"
        assert 'wind' in stats, "Wind stats missing"
        
        # Check specific values
        assert stats['count'] == len(self.sample_data), "Count mismatch"
        assert isinstance(stats['temperature']['mean_avg'], (int, float)), "Mean temp should be numeric"


class TestWeatherAPI:
    """Test cases for WeatherAPI class"""
    
    def setup_method(self):
        """Setup API instance"""
        self.api = WeatherAPI()
    
    def test_api_urls(self):
        """Test that API URLs are properly set"""
        assert self.api.geocoding_url == "https://geocoding-api.open-meteo.com/v1/search"
        assert self.api.historical_url == "https://archive-api.open-meteo.com/v1/era5"
    
    def test_validate_date_range(self):
        """Test date range validation"""
        # Valid date range
        assert self.api.validate_date_range('2023-01-01', '2023-12-31') == True
        
        # Invalid date range (start after end)
        assert self.api.validate_date_range('2023-12-31', '2023-01-01') == False
        
        # Date too early
        assert self.api.validate_date_range('1900-01-01', '2023-01-01') == False
    
    @patch('src.api.requests.get')
    def test_search_cities_success(self, mock_get):
        """Test successful city search"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'name': 'London', 'country': 'United Kingdom', 
                 'latitude': 51.5074, 'longitude': -0.1278}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.api.search_cities('London')
        
        assert len(result) == 1
        assert result[0]['name'] == 'London'
        assert result[0]['country'] == 'United Kingdom'
    
    @patch('src.api.requests.get')
    def test_search_cities_no_results(self, mock_get):
        """Test city search with no results"""
        # Mock response with no results
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.api.search_cities('NonexistentCity')
        
        assert result == []


class TestWeatherPlots:
    """Test cases for WeatherPlots class"""
    
    def setup_method(self):
        """Setup test data and plotter"""
        self.plotter = WeatherPlots()
        
        # Create sample processed data
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        self.sample_data = pd.DataFrame({
            'date': dates,
            'tmax': np.random.normal(20, 5, 100),
            'tmin': np.random.normal(10, 5, 100),
            'tmean': np.random.normal(15, 5, 100),
            'precipitation': np.random.exponential(2, 100),
            'windspeed_max': np.random.gamma(2, 5, 100),
            'temp_range': np.random.normal(10, 2, 100),
            'month': [d.month for d in dates],
            'season': ['Winter'] * 25 + ['Spring'] * 25 + ['Summer'] * 25 + ['Fall'] * 25
        })
    
    def test_color_palette(self):
        """Test that color palette is properly defined"""
        assert hasattr(self.plotter, 'colors')
        assert 'tmax' in self.plotter.colors
        assert 'tmin' in self.plotter.colors
        assert 'tmean' in self.plotter.colors
    
    def test_create_temperature_plot(self):
        """Test temperature plot creation"""
        fig = self.plotter.create_temperature_plot(self.sample_data)
        
        # Check that figure is created
        assert fig is not None
        assert len(fig.data) > 0  # Should have traces
        
        # Check for expected traces
        trace_names = [trace.name for trace in fig.data if trace.name]
        expected_traces = ['Temperature Range', 'Min Temperature', 'Max Temperature', 'Mean Temperature']
        
        for expected in expected_traces:
            assert expected in trace_names, f"Missing trace: {expected}"
    
    def test_create_precipitation_plot(self):
        """Test precipitation plot creation"""
        fig = self.plotter.create_precipitation_plot(self.sample_data)
        
        # Check that figure is created
        assert fig is not None
        assert len(fig.data) > 0
        
        # Should have at least precipitation bars
        trace_names = [trace.name for trace in fig.data if trace.name]
        assert 'Daily Precipitation' in trace_names
    
    def test_create_anomaly_plot_no_data(self):
        """Test anomaly plot with no anomaly data"""
        # Remove anomaly columns
        data_no_anomaly = self.sample_data.copy()
        
        fig = self.plotter.create_anomaly_plot(data_no_anomaly)
        
        # Should return a figure with annotation about missing data
        assert fig is not None