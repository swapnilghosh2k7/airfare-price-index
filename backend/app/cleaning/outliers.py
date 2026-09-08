import numpy as np
import pandas as pd
from typing import List, Dict, Any

class OutlierDetector:
    @staticmethod
    def detect_mad_outliers(series: pd.Series, threshold: float = 3.0) -> pd.Series:
        """Detect outliers using Median Absolute Deviation (MAD)"""
        if len(series) < 3 or series.nunique() <= 1:
            return pd.Series(False, index=series.index)
            
        median = series.median()
        mad = (series - median).abs().median()
        
        if mad == 0 or np.isnan(mad):
            # Fallback to mean absolute deviation if MAD is zero
            mad = (series - median).abs().mean()
            if mad == 0:
                return pd.Series(False, index=series.index)
                
        # Modified z-score = 0.6745 * (x - median) / MAD
        modified_z = 0.6745 * (series - median).abs() / mad
        return modified_z > threshold

    @staticmethod
    def detect_iqr_outliers(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
        """Detect outliers using Interquartile Range (IQR)"""
        if len(series) < 4:
            return pd.Series(False, index=series.index)
            
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        
        if iqr == 0:
            return pd.Series(False, index=series.index)
            
        lower_bound = q1 - (multiplier * iqr)
        upper_bound = q3 + (multiplier * iqr)
        
        return (series < lower_bound) | (series > upper_bound)

    @classmethod
    def flag_outliers(
        cls,
        quotes_df: pd.DataFrame,
        method: str = "MAD",
        mad_threshold: float = 3.0,
        iqr_multiplier: float = 1.5
    ) -> pd.DataFrame:
        """Flag outliers grouped by route and lead_time_days"""
        df = quotes_df.copy()
        if "outlier_flag" not in df.columns:
            df["outlier_flag"] = False
            
        if df.empty or "total_fare" not in df.columns:
            return df

        # Create composite route group key
        if "route_code" not in df.columns:
            df["route_code"] = df["origin"] + "-" + df["destination"]

        for (route, lead_time), group in df.groupby(["route_code", "lead_time_days"]):
            fares = group["total_fare"]
            
            if method.upper() == "MAD":
                is_outlier = cls.detect_mad_outliers(fares, threshold=mad_threshold)
            elif method.upper() == "IQR":
                is_outlier = cls.detect_iqr_outliers(fares, multiplier=iqr_multiplier)
            else:
                # BOTH
                mad_out = cls.detect_mad_outliers(fares, threshold=mad_threshold)
                iqr_out = cls.detect_iqr_outliers(fares, multiplier=iqr_multiplier)
                is_outlier = mad_out | iqr_out
                
            df.loc[is_outlier[is_outlier].index, "outlier_flag"] = True

        return df
