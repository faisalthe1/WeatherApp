import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import io
import base64
from src.api import WeatherAPI
from src.transform import WeatherTransformer
from src.plots import WeatherPlots


st.set_page_config(
    page_title="Weather Insights Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_weather_api():
    return WeatherAPI()

@st.cache_resource
def get_transformer():
    return WeatherTransformer()

@st.cache_resource
def get_plotter():
    return WeatherPlots()

def main():
    st.title("🌤️ Weather Insights Dashboard")
    st.markdown("Interactive weather analysis using Open-Meteo historical data")
    
    api = get_weather_api()
    transformer = get_transformer()
    plotter = get_plotter()
    
    with st.sidebar:
        st.header("🌍 Location & Settings")
        
        city_input = st.text_input("Enter city name:", placeholder="e.g., London, New York")
        search_btn = st.button("🔍 Search Cities", type="primary")
        
        if search_btn and city_input:
            with st.spinner("Searching cities..."):
                cities = api.search_cities(city_input)
                st.session_state['cities'] = cities
        
        selected_city = None
        if 'cities' in st.session_state and st.session_state['cities']:
            city_options = [f"{city['name']}, {city['country']}" for city in st.session_state['cities']]
            selected_idx = st.selectbox("Select city:", range(len(city_options)), 
                                      format_func=lambda x: city_options[x])
            selected_city = st.session_state['cities'][selected_idx]
        
        st.subheader("📅 Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date:", 
                                     value=date.today() - timedelta(days=365),
                                     max_value=date.today())
        with col2:
            end_date = st.date_input("End date:", 
                                   value=date.today(),
                                   max_value=date.today())
        
        st.subheader("📊 Analysis Options")
        show_rolling = st.toggle("7-day rolling average", value=True)
        show_anomaly = st.toggle("Temperature anomalies", value=False)
        monthly_view = st.toggle("Monthly aggregation", value=False)
   
        fetch_btn = st.button("📈 Fetch Weather Data", type="primary", 
                            disabled=not selected_city)
    
    if selected_city and fetch_btn:
        with st.spinner("Fetching weather data..."):
            weather_data = api.get_historical_weather(
                selected_city['latitude'], 
                selected_city['longitude'],
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if weather_data is not None:
                df = transformer.process_data(weather_data, show_rolling, show_anomaly, monthly_view)
                st.session_state['weather_df'] = df
                st.session_state['selected_city'] = selected_city
                st.session_state['analysis_options'] = {
                    'rolling': show_rolling,
                    'anomaly': show_anomaly,
                    'monthly': monthly_view
                }
    if 'weather_df' in st.session_state and 'selected_city' in st.session_state:
        df = st.session_state['weather_df']
        city = st.session_state['selected_city']
        options = st.session_state['analysis_options']
        
        st.info(f"**{city['name']}, {city['country']}** | "
               f"Coordinates: {city['latitude']:.2f}°N, {city['longitude']:.2f}°E | "
               f"Elevation: {city.get('elevation', 'N/A')}m")
        
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_temp = df['tmean'].mean()
            st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
        
        with col2:
            max_temp = df['tmax'].max()
            st.metric("Max Temperature", f"{max_temp:.1f}°C")
        
        with col3:
            total_precip = df['precipitation'].sum()
            st.metric("Total Precipitation", f"{total_precip:.1f}mm")
        
        with col4:
            max_wind = df['windspeed_max'].max()
            st.metric("Max Wind Speed", f"{max_wind:.1f}km/h")
        
        st.subheader("🌡️ Temperature Analysis")
        temp_fig = plotter.create_temperature_plot(df, options['rolling'])
        st.plotly_chart(temp_fig, use_container_width=True)
        st.subheader("🌧️ Precipitation Analysis")
        precip_fig = plotter.create_precipitation_plot(df, options['rolling'])
        st.plotly_chart(precip_fig, use_container_width=True)
        
        if options['anomaly'] and 'temp_anomaly' in df.columns:
            st.subheader("📈 Temperature Anomalies")
            anomaly_fig = plotter.create_anomaly_plot(df)
            st.plotly_chart(anomaly_fig, use_container_width=True)

        st.subheader("💾 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"weather_data_{city['name'].replace(' ', '_')}.csv",
                mime="text/csv"
            )
        
        with col2:
            if st.button("Generate PNG Report"):
                with st.spinner("Generating report..."):
                    png_data = plotter.create_combined_report(df, city, options)
                    st.download_button(
                        label="Download PNG Report",
                        data=png_data,
                        file_name=f"weather_report_{city['name'].replace(' ', '_')}.png",
                        mime="image/png"
                    )
        
        with st.expander("📋 View Raw Data"):
            st.dataframe(df, use_container_width=True)
    
    elif not selected_city:
        st.info("Please search and select a city to begin analysis")
    
    st.markdown("---")
    st.markdown("Data provided by [Open-Meteo](https://open-meteo.com/) | Built with Streamlit")

if __name__ == "__main__":
    main()