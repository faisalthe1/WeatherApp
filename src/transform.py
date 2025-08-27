import pandas as pd
import numpy as np

class WeatherTransformer:
    """Handles data transformation and feature engineering for weather data"""
    
    def __init__(self):
        pass
    
    def process_data(self, df: pd.DataFrame, add_rolling: bool = True, 
                    add_anomalies: bool = False, monthly_agg: bool = False) -> pd.DataFrame:
        """Main processing pipeline for weather data"""
        processed_df = df.copy()
        processed_df['date'] = pd.to_datetime(processed_df['date'])
        processed_df = self.add_basic_features(processed_df)
        if add_rolling:
            processed_df = self.add_rolling_averages(processed_df)
        if add_anomalies:
            processed_df = self.add_temperature_anomalies(processed_df)
        if monthly_agg:
            processed_df = self.aggregate_monthly(processed_df)
        
        return processed_df
    
    def add_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic derived features"""
        df_copy = df.copy()
        df_copy['tmean'] = (df_copy['tmax'] + df_copy['tmin']) / 2
        df_copy['temp_range'] = df_copy['tmax'] - df_copy['tmin']
        df_copy['year'] = df_copy['date'].dt.year
        df_copy['month'] = df_copy['date'].dt.month
        df_copy['day_of_year'] = df_copy['date'].dt.dayofyear
        df_copy['season'] = df_copy['month'].apply(self._get_season)
        
        return df_copy
    
    def add_rolling_averages(self, df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
        """Add rolling averages for smoothing trends"""
        df_copy = df.copy()
        df_copy['tmean_7d'] = df_copy['tmean'].rolling(window=window, center=True).mean()
        df_copy['tmax_7d'] = df_copy['tmax'].rolling(window=window, center=True).mean()
        df_copy['tmin_7d'] = df_copy['tmin'].rolling(window=window, center=True).mean()
        df_copy['precip_7d'] = df_copy['precipitation'].rolling(window=window, center=True).sum()
        
        return df_copy
    
    def add_temperature_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate temperature anomalies relative to monthly climatology"""
        df_copy = df.copy()
        monthly_climate = df_copy.groupby('month')['tmean'].transform('mean')
        df_copy['temp_anomaly'] = df_copy['tmean'] - monthly_climate
        df_copy['monthly_climate'] = monthly_climate
        df_copy['anomaly_category'] = pd.cut(
            df_copy['temp_anomaly'], 
            bins=[-np.inf, -2, -1, 1, 2, np.inf],
            labels=['Very Cold', 'Cold', 'Normal', 'Warm', 'Very Warm']
        )
        
        return df_copy
    
    def aggregate_monthly(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate data to monthly resolution"""
        df_copy = df.copy()
        df_copy['year_month'] = df_copy['date'].dt.to_period('M')
        agg_rules = {
            'tmax': 'mean',
            'tmin': 'mean', 
            'tmean': 'mean',
            'precipitation': 'sum',
            'windspeed_max': 'mean',
            'temp_range': 'mean'
        }
        
        if 'tmean_7d' in df_copy.columns:
            agg_rules.update({
                'tmean_7d': 'mean',
                'tmax_7d': 'mean',
                'tmin_7d': 'mean',
                'precip_7d': 'sum'
            })
        
        if 'temp_anomaly' in df_copy.columns:
            agg_rules['temp_anomaly'] = 'mean'
        
        monthly_df = df_copy.groupby('year_month').agg(agg_rules).reset_index()
        monthly_df['date'] = monthly_df['year_month'].dt.to_timestamp()
        monthly_df = monthly_df.drop('year_month', axis=1)
        monthly_df['year'] = monthly_df['date'].dt.year
        monthly_df['month'] = monthly_df['date'].dt.month
        
        return monthly_df
    
    def detect_extreme_events(self, df: pd.DataFrame, 
                            temp_threshold: float = 2.0, 
                            precip_threshold: float = 95) -> pd.DataFrame:
        """Detect extreme weather events"""
        df_copy = df.copy()
        
        if 'temp_anomaly' in df_copy.columns:
            df_copy['extreme_heat'] = df_copy['temp_anomaly'] > temp_threshold
            df_copy['extreme_cold'] = df_copy['temp_anomaly'] < -temp_threshold
        else:
            temp_95th = df_copy['tmean'].quantile(0.95)
            temp_5th = df_copy['tmean'].quantile(0.05)
            df_copy['extreme_heat'] = df_copy['tmean'] > temp_95th
            df_copy['extreme_cold'] = df_copy['tmean'] < temp_5th
        
        precip_threshold_value = df_copy['precipitation'].quantile(precip_threshold / 100)
        df_copy['extreme_precip'] = df_copy['precipitation'] > precip_threshold_value
        
        return df_copy
    
    def calculate_statistics(self, df: pd.DataFrame) -> dict:
        """Calculate summary statistics"""
        stats = {
            'count': len(df),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d'),
                'end': df['date'].max().strftime('%Y-%m-%d')
            },
            'temperature': {
                'mean_avg': df['tmean'].mean(),
                'mean_max': df['tmax'].mean(),
                'mean_min': df['tmin'].mean(),
                'absolute_max': df['tmax'].max(),
                'absolute_min': df['tmin'].min()
            },
            'precipitation': {
                'total': df['precipitation'].sum(),
                'mean_daily': df['precipitation'].mean(),
                'max_daily': df['precipitation'].max(),
                'days_with_rain': (df['precipitation'] > 0).sum()
            },
            'wind': {
                'mean_max': df['windspeed_max'].mean(),
                'absolute_max': df['windspeed_max'].max()
            }
        }
        
        return stats
    
    @staticmethod
    def _get_season(month: int) -> str:
        """Convert month number to season name"""
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'