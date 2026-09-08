PROJECT: Real-time Airfare Price Index (APIx)



RAW SCRAPED DATA — columns (CSV):

route, airline, scrape\_date, travel\_date, advance\_days, base\_fare, tax, total\_fare



ROUTE FORMAT: "DEL-BOM" (3-letter airport codes, hyphen separated)

DATE FORMAT: "YYYY-MM-DD"

FARE FORMAT: plain numbers, no ₹ symbol, no commas (e.g. 4500 not ₹4,500)



FILE PATHS:

\- Raw scraped data: data/raw\_fares.csv

\- Cleaned data: data/clean\_fares.csv

\- Database: data/fares.db (SQLite), table name: fares

\- Index output: data/index\_values.csv with columns: date, index\_value



API BASE: FastAPI, running locally on http://localhost:8000

\- GET /fares?route=DEL-BOM  → returns list of fare records as JSON

\- GET /index                → returns index\_value over time as JSON



TECH STACK: Python 3.11, pandas, SQLite, Playwright, FastAPI, Streamlit



