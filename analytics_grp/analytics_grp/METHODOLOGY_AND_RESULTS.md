# Methodology and Results Guide

This file supports your report writing and viva by mapping each implementation step to expected outputs.

## Methodology
1. **Data Collection**
   - Accident data generated and exported to CSV (`data/raw/accidents_ireland.csv`)
   - Weather data pulled from Open-Meteo API as JSON and stored in MongoDB
   - County-by-day traffic exposure panel saved to CSV (`data/raw/county_traffic_exposure_daily.csv`)

2. **Data Storage**
   - Raw JSON in MongoDB (`raw_weather`)
   - Structured tables in PostgreSQL after cleaning and integration

3. **Data Processing**
   - Missing values imputed using median/mean strategies where appropriate
   - Date and time standardized using pandas datetime parsing
   - Integration by `date` and `county`
   - Derived variables for risk profiling (`accident_severity_index`, `weather_impact_score`)

4. **Analysis**
   - EDA by county, hour, day-of-week
   - Daily accident time-series
   - Weather/accident correlation
   - Location hotspot analysis
   - Optional linear regression model for severity index prediction

5. **Visualization and Dashboard**
   - Static charts: matplotlib/seaborn
   - Interactive map and dashboard: plotly + streamlit

## Output Checklist
- Processed integrated data: `data/processed/integrated_accident_weather.csv`
- EDA tables: `data/processed/eda_by_county.csv`, `data/processed/eda_by_hour.csv`
- Correlation matrix: `data/processed/correlation_matrix.csv`
- Findings summary: `data/processed/key_findings.json`
- Figures: `outputs/figures/*.png`
- Model outputs: `outputs/models/*.csv`, `outputs/models/*.json`

## Suggested Report Findings (Populate after running)
- Peak accident periods (commuting rush windows)
- Counties with highest absolute accident burden
- Severity increase during heavy rainfall/wind conditions
- Prioritized recommendations for enforcement, signage, and targeted interventions

