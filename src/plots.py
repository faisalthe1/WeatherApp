import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import io
import base64
from typing import Dict, Optional

class WeatherPlots:
    """Creates interactive visualizations for weather data"""
    
    def __init__(self):
        self.colors = {
            'tmax': '#FF6B6B',
            'tmin': '#4ECDC4', 
            'tmean': '#45B7D1',
            'precipitation': '#96CEB4',
            'anomaly_pos': '#FF8A80',
            'anomaly_neg': '#81C784',
            'background': '#F8F9FA'
        }
    
    def create_temperature_plot(self, df: pd.DataFrame, show_rolling: bool = True) -> go.Figure:
        """Create temperature ribbon plot with min/max band and mean line"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['tmax'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['tmin'],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(69, 183, 209, 0.2)',
            name='Temperature Range',
            hovertemplate='Date: %{x}<br>Min: %{y:.1f}°C<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['tmin'],
            mode='lines',
            line=dict(color=self.colors['tmin'], width=1.5),
            name='Min Temperature',
            hovertemplate='Date: %{x}<br>Min Temp: %{y:.1f}°C<extra></extra>'
        ))
         
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['tmax'],
            mode='lines',
            line=dict(color=self.colors['tmax'], width=1.5),
            name='Max Temperature',
            hovertemplate='Date: %{x}<br>Max Temp: %{y:.1f}°C<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['tmean'],
            mode='lines',
            line=dict(color=self.colors['tmean'], width=2),
            name='Mean Temperature',
            hovertemplate='Date: %{x}<br>Mean Temp: %{y:.1f}°C<extra></extra>'
        ))
        
        if show_rolling and 'tmean_7d' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['tmean_7d'],
                mode='lines',
                line=dict(color='#2C3E50', width=2, dash='dash'),
                name='7-day Rolling Avg',
                hovertemplate='Date: %{x}<br>7-day Avg: %{y:.1f}°C<extra></extra>'
            ))
        
        fig.update_layout(
            title='Temperature Analysis',
            xaxis_title='Date',
            yaxis_title='Temperature (°C)',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='white',
            height=500
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        return fig
    
    def create_precipitation_plot(self, df: pd.DataFrame, show_rolling: bool = True) -> go.Figure:
        """Create precipitation bar chart with optional rolling sum"""
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=df['precipitation'],
                name='Daily Precipitation',
                marker_color=self.colors['precipitation'],
                hovertemplate='Date: %{x}<br>Precipitation: %{y:.1f}mm<extra></extra>'
            ),
            secondary_y=False
        )
        
        if show_rolling and 'precip_7d' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['precip_7d'],
                    mode='lines',
                    line=dict(color='#E74C3C', width=2),
                    name='7-day Rolling Sum',
                    hovertemplate='Date: %{x}<br>7-day Sum: %{y:.1f}mm<extra></extra>'
                ),
                secondary_y=True
            )

        fig.update_layout(
            title='Precipitation Analysis',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='white',
            height=400
        )
        
        fig.update_yaxes(title_text="Daily Precipitation (mm)", secondary_y=False)
        if show_rolling and 'precip_7d' in df.columns:
            fig.update_yaxes(title_text="7-day Sum (mm)", secondary_y=True)
        
        fig.update_xaxes(title_text="Date")
        
        return fig
    
    def create_anomaly_plot(self, df: pd.DataFrame) -> go.Figure:
        """Create temperature anomaly plot"""
        if 'temp_anomaly' not in df.columns:
            fig = go.Figure()
            fig.add_annotation(text="No anomaly data available", 
                             xref="paper", yref="paper", x=0.5, y=0.5,
                             showarrow=False, font=dict(size=16))
            return fig
        
        fig = go.Figure()
        
        colors = ['#81C784' if x < 0 else '#FF8A80' for x in df['temp_anomaly']]
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['temp_anomaly'],
            marker_color=colors,
            name='Temperature Anomaly',
            hovertemplate='Date: %{x}<br>Anomaly: %{y:.1f}°C<extra></extra>'
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="black", 
                     annotation_text="Climatological Average")
        
        fig.update_layout(
            title='Temperature Anomalies (vs. Monthly Climate)',
            xaxis_title='Date',
            yaxis_title='Temperature Anomaly (°C)',
            hovermode='x',
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        return fig
    
    def create_combined_report(self, df: pd.DataFrame, city: Dict, 
                             options: Dict) -> bytes:
        """Create a combined PNG report with multiple charts"""
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=['Temperature Analysis', 'Precipitation', 'Wind Speed'],
            vertical_spacing=0.1,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": True}],
                   [{"secondary_y": False}]]
        )
        
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['tmax'], 
                      name='Max Temp', line=dict(color=self.colors['tmax'])),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['tmin'], 
                      name='Min Temp', line=dict(color=self.colors['tmin'])),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['tmean'], 
                      name='Mean Temp', line=dict(color=self.colors['tmean'])),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(x=df['date'], y=df['precipitation'], 
                  name='Precipitation', marker_color=self.colors['precipitation']),
            row=2, col=1
        )

        fig.add_trace(
            go.Scatter(x=df['date'], y=df['windspeed_max'], 
                      name='Max Wind Speed', line=dict(color='#9B59B6')),
            row=3, col=1
        )
        
        fig.update_layout(
            height=1200,
            title_text=f"Weather Report: {city['name']}, {city['country']}",
            title_x=0.5,
            showlegend=True,
            plot_bgcolor='white'
        )

        fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
        fig.update_yaxes(title_text="Precipitation (mm)", row=2, col=1)
        fig.update_yaxes(title_text="Wind Speed (km/h)", row=3, col=1)
        fig.update_xaxes(title_text="Date", row=3, col=1)
        
        img_bytes = fig.to_image(format="png", width=1200, height=1200, scale=2)
        return img_bytes
    
    def create_seasonal_summary(self, df: pd.DataFrame) -> go.Figure:
        """Create seasonal temperature and precipitation summary"""
        if 'season' not in df.columns:
            return go.Figure()
        
        seasonal_data = df.groupby('season').agg({
            'tmean': 'mean',
            'precipitation': 'sum',
            'tmax': 'max',
            'tmin': 'min'
        }).reset_index()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=['Average Temperature by Season', 'Total Precipitation by Season'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )

        fig.add_trace(
            go.Bar(
                x=seasonal_data['season'],
                y=seasonal_data['tmean'],
                name='Avg Temperature',
                marker_color=['#3498DB', '#2ECC71', '#E74C3C', '#F39C12']
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=seasonal_data['season'],
                y=seasonal_data['precipitation'],
                name='Total Precipitation',
                marker_color=['#9B59B6', '#1ABC9C', '#E67E22', '#34495E'],
                showlegend=False
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title='Seasonal Weather Summary',
            height=400,
            showlegend=False
        )
        
        fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
        fig.update_yaxes(title_text="Precipitation (mm)", row=1, col=2)
        
        return fig
    
    def create_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create correlation heatmap of weather variables"""
        numeric_cols = ['tmax', 'tmin', 'tmean', 'precipitation', 'windspeed_max', 'temp_range']
        if 'temp_anomaly' in df.columns:
            numeric_cols.append('temp_anomaly')
        corr_matrix = df[numeric_cols].corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Weather Variables Correlation Matrix',
            height=500,
            width=600
        )
        
        return fig
    
    def create_monthly_climate_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create monthly climatology chart"""
        if 'month' not in df.columns:
            return go.Figure()
        
        monthly_climate = df.groupby('month').agg({
            'tmean': 'mean',
            'tmax': 'mean',
            'tmin': 'mean',
            'precipitation': 'mean'
        }).reset_index()
    
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_climate['month_name'] = [month_names[m-1] for m in monthly_climate['month']]
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=monthly_climate['month_name'], y=monthly_climate['tmax'],
                      name='Avg Max Temp', line=dict(color=self.colors['tmax'], width=3)),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=monthly_climate['month_name'], y=monthly_climate['tmean'],
                      name='Avg Mean Temp', line=dict(color=self.colors['tmean'], width=3)),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=monthly_climate['month_name'], y=monthly_climate['tmin'],
                      name='Avg Min Temp', line=dict(color=self.colors['tmin'], width=3)),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(x=monthly_climate['month_name'], y=monthly_climate['precipitation'],
                  name='Avg Precipitation', marker_color=self.colors['precipitation'],
                  opacity=0.6),
            secondary_y=True
        )

        fig.update_layout(
            title='Monthly Climate Summary',
            hovermode='x unified',
            height=500
        )
        
        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
        fig.update_yaxes(title_text="Precipitation (mm)", secondary_y=True)
        fig.update_xaxes(title_text="Month")
        
        return fig