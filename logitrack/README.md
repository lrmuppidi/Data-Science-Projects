# LogiTrack: Supply Chain & Logistics Performance Analytics

Pipeline: raw CSVs -> clean (Pandas) -> SQLite database -> features -> EDA -> 5 statistical tests -> Streamlit dashboard -> business insights.

## Project structure
```
logitrack/
├── data/
│   ├── raw/        
│   └── cleaned/    
├── notebooks/
│   ├── 01_data_cleaning.ipynb          
│   ├── 02_feature_engineering.ipynb    
│   ├── 03_eda.ipynb                    
│   └── 04_statistical_analysis.ipynb   
├── sql/
│   ├── schema.sql                      
│   └── analysis_queries.sql            
├── dashboard/
│   └── app.py                          
├── src/
│   ├── data_cleaning.py                
│   ├── feature_engineering.py          
│   └── utils.py                        
├── README.md
└── requirements.txt
```
Created automatically when you run the project: `logitrack.db` (database) and `reports/` (charts, outlier CSV).

## Setup (Windows, VS Code)
1. Install Python from python.org (tick **Add python.exe to PATH**), then restart VS Code.
2. Open this folder in VS Code. Put the 7 CSV files in `data/raw/` (names like `logitrack_drivers_expanded.csv`).
3. Install the VS Code extensions **Python** and **Jupyter** (Microsoft).
4. In the terminal:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## How to run
**Option A: notebooks (recommended for explaining step by step).** Open each notebook in `notebooks/`, click *Select Kernel* (top right) and choose the `.venv`, then *Run All*. Run them in order 01, 02, 03, 04.

**Option B: scripts.** From the project folder:
```
python src/data_cleaning.py
python src/feature_engineering.py
```
(EDA and statistics are in notebooks 03 and 04.)

**Dashboard** (after notebook 01 and 02, or the two scripts):
```
streamlit run dashboard/app.py
```

## KPI rules
- Success rate = Delivered / all deliveries except In-Transit.
- `delay_hours` is NULL for Cancelled and In-Transit deliveries, so averages ignore them.
- Experience levels: Junior 0-2, Mid 3-5, Senior 6-10, Expert 10+ years. Weight and distance categories are quartiles.

## Business insights (Step 11)
Write each finding as **Observation -> Interpretation -> Business Impact** using your own results. Example:
- Observation: delayed deliveries have a lower average rating (query Q7).
- Interpretation: delivery experience affects satisfaction.
- Business impact: prioritise on-time delivery for customer retention.

Where to look: success rate (Q1), worst routes (Q2), seasonality (Q5, EDA), experience vs performance (Q9, Test 4), vehicles (Q6), warehouses (Q4), outliers (Test 5).

## GitHub
`.gitignore` excludes `data/`, `*.db` and `.env`, so datasets and credentials are not uploaded.
