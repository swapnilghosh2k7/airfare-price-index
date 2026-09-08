from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date

class FareProvider(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider string identifier"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human readable provider name"""
        pass

    @abstractmethod
    async def search_fares(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        lead_time_days: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Searches airfare quotes for given route and departure date.
        Returns list of standardized fare quote dictionaries.
        """
        pass
