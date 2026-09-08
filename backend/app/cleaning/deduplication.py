import hashlib
from typing import List, Dict, Any, Set

class Deduplicator:
    @staticmethod
    def generate_fingerprint(quote: Dict[str, Any]) -> str:
        origin = str(quote.get("origin", "")).upper()
        destination = str(quote.get("destination", "")).upper()
        dep_date = str(quote.get("departure_date", ""))
        carrier = str(quote.get("carrier", "")).strip()
        flight_num = str(quote.get("flight_number", "")).strip()
        fare_class = str(quote.get("fare_class", "Economy")).strip()
        source = str(quote.get("source", "")).strip()
        obs_time = str(quote.get("observation_timestamp", ""))
        
        payload = f"{origin}|{destination}|{dep_date}|{carrier}|{flight_num}|{fare_class}|{source}|{obs_time}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def flag_duplicates(cls, quotes: List[Dict[str, Any]], existing_hashes: Set[str] = None) -> List[Dict[str, Any]]:
        seen_hashes = set(existing_hashes) if existing_hashes else set()
        processed = []
        
        for q in quotes:
            item = q.copy()
            fp = q.get("raw_hash") or cls.generate_fingerprint(q)
            item["raw_hash"] = fp
            
            if fp in seen_hashes:
                item["duplicate_flag"] = True
            else:
                item["duplicate_flag"] = False
                seen_hashes.add(fp)
                
            processed.append(item)
            
        return processed
