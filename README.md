#  Weather Insights Dashboard

An interactive weather analysis dashboard built with Streamlit that provides comprehensive historical weather data visualization and analysis using the Open-Meteo API.

##  Features

### 🌍 Location Search
- **City Search**: Search for any city worldwide using Open-Meteo's geocoding API
- **Multiple Results**: Handle multiple cities with the same name
- **Coordinates Display**: Show latitude, longitude, and elevation information

###  Data Analysis
- **Historical Weather Data**: Access to ERA5 reanalysis data from 1940 onwards
- **Temperature Analysis**: Min/max temperature bands with mean temperature trends
- **Precipitation Tracking**: Daily precipitation with rolling averages
- **Wind Speed Analysis**: Maximum daily wind speed visualization

###  Advanced Features
- **Rolling Averages**: 7-day smoothed trends for temperature and precipitation
- **Temperature Anomalies**: Deviation from monthly climatological averages
- **Monthly Aggregation**: Option to view data at monthly resolution
- **Seasonal Analysis**: Automatic season categorization and analysis
- **Extreme Event Detection**: Identify temperature and precipitation extremes

### Interactive Visualizations
- **Temperature Ribbon Plot**: Min/max bands with mean temperature line
- **Precipitation Charts**: Bar charts with optional rolling sums
- **Anomaly Visualization**: Color-coded temperature departures from normal
- **Correlation Analysis**: Heatmap showing relationships between variables
- **Monthly Climate Charts**: Long-term monthly averages

###  Export Options
- **CSV Export**: Download processed data for further analysis
- **PNG Reports**: Generate comprehensive visual reports
- **Data Table View**: Interactive table with all calculated variables

## Quick Start

### Installation

1. **Clone or create the project structure**:
```bash
mkdir weather-insights
cd weather-insights
```

2. **Create the directory structure**:
```
weather-insights/
├── app.py
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    ├── api.py
    ├── transform.py
    └── plots.py
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Initialize git (optional)**:
```bash
git init
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Search for a City
1. Enter a city name in the sidebar
2. Click "🔍 Search Cities"
3. Select your desired city from the dropdown

### Step 2: Configure Analysis
- **Date Range**: Select start and end dates (up to present day)
- **Analysis Options**:
  - Toggle 7-day rolling averages
  - Enable temperature anomaly calculation
  - Switch to monthly aggregation view

### Step 3: Fetch and Analyze
1. Click "📈 Fetch Weather Data"
2. View the interactive charts and key metrics
3. Explore different visualizations

### Step 4: Export Results
- Download CSV data for external analysis
- Generate PNG reports for presentations
- View raw data in the expandable table

## 🛠️ Technical Architecture

### API Integration (`src/api.py`)
- **Geocoding API**: City search and coordinate resolution
- **ERA5 Historical API**: Weather data retrieval
- **Error Handling**: Robust error management and user feedback
- **Data Validation**: Input validation and reasonable limits

### Data Processing (`src/transform.py`)
- **Feature Engineering**: Calculate derived variables (mean temp, anomalies, etc.)
- **Rolling Statistics**: Smoothed trends and moving averages
- **Anomaly Detection**: Temperature departures from climatological normals
- **Temporal Aggregation**: Daily to monthly data resampling

### Visualization (`src/plots.py`)
- **Interactive Charts**: Plotly-based responsive visualizations
- **Multi-axis Plots**: Combined temperature and precipitation displays
- **Color Schemes**: Consistent and intuitive color coding
- **Export Graphics**: PNG generation for reports

### Main Application (`app.py`)
- **Streamlit Interface**: Responsive web application
- **Session Management**: Persistent data across user interactions
- **Caching**: Optimized performance with Streamlit caching
- **User Experience**: Intuitive workflow and feedback

## 📊 Data Sources

### Open-Meteo APIs
- **Geocoding API**: `https://geocoding-api.open-meteo.com/v1/search`
- **ERA5 Historical API**: `https://archive-api.open-meteo.com/v1/era5`

### Available Variables
- **Temperature**: Daily maximum, minimum, and calculated mean
- **Precipitation**: Daily precipitation sum
- **Wind**: Daily maximum wind speed at 10m
- **Derived Variables**: Temperature range, anomalies, rolling averages

## 🔧 Configuration Options

### Analysis Parameters
- **Rolling Window**: Default 7-day window (configurable)
- **Anomaly Baseline**: Monthly climatological averages
- **Date Range**: Limited to ERA5 availability (1940-present)
- **Extreme Thresholds**: Configurable percentiles and standard deviations

### Visualization Settings
- **Color Palette**: Customizable color schemes
- **Chart Dimensions**: Responsive sizing
- **Export Quality**: High-resolution PNG output
- **Interactive Features**: Hover tooltips, zoom, pan

## 🧪 Testing & Validation

### Test Cases
- **Normal Operation**: Standard city search and data retrieval
- **Edge Cases**: Invalid cities, extreme date ranges
- **Error Handling**: Network failures, API limits
- **Data Quality**: Missing values, outlier detection

### Validation Methods
- **Schema Validation**: Ensure correct data structure
- **Mathematical Accuracy**: Verify calculations and transformations
- **Visual Inspection**: Chart accuracy and formatting

## 🌐 Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy with automatic updates

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

##  Contributing

### Code Structure
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maintain comprehensive docstrings
- Write unit tests for core functions

### Feature Additions
- Extend analysis capabilities in `transform.py`
- Add new visualizations in `plots.py`
- Enhance API integration in `api.py`
- Improve UI/UX in `app.py`

## 🔍 Troubleshooting

### Common Issues

**City Not Found**
- Check spelling and try variations
- Some small cities may not be in the database
- Try nearby larger cities

**Data Loading Errors**
- Check internet connection
- Verify date range is reasonable
- ERA5 data starts from 1940

**Performance Issues**
- Reduce date range for faster loading
- Use monthly aggregation for large datasets
- Clear browser cache if needed

**Export Problems**
- Ensure sufficient disk space
- Check browser download permissions
- Try different export formats

##  Example Analyses

### Climate Analysis
- Compare seasonal temperature patterns
- Identify long-term warming trends
- Analyze precipitation variability

### Extreme Weather
- Detect heat waves and cold spells
- Identify heavy precipitation events
- Track wind speed extremes

### Comparative Studies
- Compare different cities
- Analyze urban heat islands
- Study elevation effects

## Future Enhancements

### Planned Features
- **Multi-city Comparison**: Side-by-side analysis
- **Climate Indices**: Calculate standard climate metrics
- **Forecast Integration**: Add weather prediction capabilities
- **Statistical Tests**: Trend analysis and significance testing

### Advanced Analytics
- **Machine Learning**: Predictive modeling
- **Spatial Analysis**: Regional climate patterns
- **Time Series**: Advanced temporal analysis
- **Custom Metrics**: User-defined calculations

## 📄 License

This project is open source. Weather data provided by Open-Meteo under their terms of service.



---

**Built with using Streamlit, Plotly, and Open-Meteo API**