# Traffic Accident Risk Analysis and Prediction (Ireland)

End-to-end academic + production-style analytics project that integrates CSV, API JSON, MongoDB, PostgreSQL, ETL, EDA, predictive modeling, and a Streamlit dashboard.

## 1) Project Objectives
- Analyse road traffic accident patterns in Ireland
- Identify high-risk locations, time windows, and contributing factors
- Quantify weather-condition impact on accident severity/risk
- Produce actionable recommendations for road safety interventions

## 2) Datasets
This project uses 3 linked datasets:

1. **Accident dataset (CSV, 5000+ records)**  
   - File: `data/raw/accidents_ireland.csv`  
   - Generated programmatically with realistic accident structure and temporal/location variation.

2. **Weather dataset (API JSON)**  
   - Source: [Open-Meteo Archive API](https://archive-api.open-meteo.com)  
   - Stored as raw JSON in MongoDB (`raw_weather` collection), then flattened for analysis.

3. **Traffic exposure dataset (CSV, 1,000+ rows)**  
   - File: `data/raw/county_traffic_exposure_daily.csv`  
   - County-by-day panel with population baseline and synthetic traffic exposure features (`vehicle_km_millions`, `congestion_index`, etc.), joinable on **county + date**.

Integration key is **county + date**.

## 3) Database Architecture
- **MongoDB**: stores raw weather JSON documents (semi-structured).
- **PostgreSQL**: stores cleaned/structured data:
  - `accidents_clean`
  - `weather_daily`
  - `county_traffic_exposure_daily`
  - `accident_risk_integrated`

## 4) ETL Pipeline
Implemented in Python (`main_etl.py`):

- **Extract**  
  - Generate/load accident CSV  
  - Create additional county stats CSV  
  - Fetch weather JSON from API per county

- **Transform**  
  - Missing value treatment  
  - Date/time normalization  
  - County/date joins across all sources  
  - Feature engineering:
    - `accident_severity_index`
    - `weather_impact_score`
    - `rain_flag`, `wind_flag`
    - `is_rush_hour`, `is_weekend`

- **Load**  
  - Raw weather JSON -> MongoDB  
  - Processed structured tables -> PostgreSQL  
  - Output integrated CSV -> `data/processed/`

## 5) Analysis and Visualization
Implemented in `run_analysis.py` and `src/visualization.py`:

- EDA (county/hour/day summaries)
- Time-series trend analysis
- Weather-accident correlation matrix
- Hotspot analysis (county and geospatial patterns)
- Optional predictive model (Linear Regression) for severity index

Saved outputs:
- `outputs/figures/` (time series, severity bar chart, correlation heatmap)
- `outputs/models/` (model coefficients and metrics)
- `data/processed/` (EDA tables, findings JSON)

## 6) Streamlit Dashboard
Interactive dashboard in `dashboard.py` includes:
- Date/county/weather filtering
- KPI cards
- Time-series plots
- Severity chart
- Geospatial hotspot map
- Correlation matrix

## 7) Setup and Run
### Prerequisites
- Python 3.10+
- Docker Desktop (recommended for DB setup)

### Installation
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### Start databases
```bash
docker compose up -d
```

### Run ETL
```bash
python main_etl.py
```

### Run analysis artifacts
```bash
python run_analysis.py
```

### Launch dashboard
```bash
streamlit run dashboard.py
```

## 8) Modular Code Structure
- `src/ingestion.py` -> extraction/API retrieval and raw dataset creation
- `src/preprocessing.py` -> cleaning, standardization, merging, features
- `src/db.py` -> MongoDB/PostgreSQL read/write and index optimization
- `src/analysis.py` -> EDA/time-series/correlation/hotspot analytics
- `src/visualization.py` -> static and map visualizations
- `src/modeling.py` -> predictive linear regression model

## 9) Academic Integrity and Originality
- Project code and generated dataset logic are original
- No copied Kaggle project implementation
- API ingestion, ETL flow, and data model are custom-built for this assignment brief

