import pandas as pd
from typing import List, Dict, Any
from datetime import date
from pathlib import Path
from collectors.base_provider import FareProvider

class DatasetFareProvider(FareProvider):
    def __init__(self, csv_filepath: str = "data/sample/fare_quotes.csv"):
        self.csv_filepath = Path(csv_filepath)

    @property
    def provider_id(self) -> str:
        return "dataset_provider"

    @property
    def provider_name(self) -> str:
        return "Reference Dataset CSV Provider"

    async def search_fares(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        lead_time_days: int = 1
    ) -> List[Dict[str, Any]]:
        if not self.csv_filepath.exists():
            return []

        df = pd.read_csv(self.csv_filepath)
        sub = df[
            (df["origin"] == origin.upper()) &
            (df["destination"] == destination.upper()) &
            (df["departure_date"] == departure_date.isoformat())
        ]
        return sub.to_dict(orient="records")
