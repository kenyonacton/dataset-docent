import os
import pandas as pd
import numpy as np

CSV_PATH = os.path.join(os.path.dirname(__file__), "open_payments_sample.csv")

ALLOWED_COLUMNS = [
    "Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name",
    "Total_Amount_of_Payment_USDollars",
    "Recipient_Primary_Business_Street_Address_Line1",
    "Recipient_City",
    "Recipient_State"
]

def load_data() -> pd.DataFrame:
    """Helper to load data in a read-only manner."""
    return pd.read_csv(CSV_PATH)

def summary_stats(column: str) -> dict:
    """Enforces read-only, whitelist, and basic statistic constraints.
    
    Args:
        column: Column to compute stats for.
    """
    if column not in ALLOWED_COLUMNS:
        return {"error": f"Column '{column}' is not whitelisted. Allowed: {ALLOWED_COLUMNS}"}
    df = load_data()
    if not np.issubdtype(df[column].dtype, np.number):
        return {"error": f"Column '{column}' is not numeric. Summary stats only available for numeric columns."}
    stats = df[column].describe()
    return {
        "count": float(stats["count"]),
        "mean": float(stats["mean"]),
        "std": float(stats["std"]),
        "min": float(stats["min"]),
        "median": float(df[column].median()),
        "max": float(stats["max"])
    }

def top_values(column: str, n: int = 10) -> dict:
    """Enforces whitelist, read-only, and caps results at max 20 rows.
    
    Args:
        column: Column to analyze.
        n: Number of top values (maximum 20).
    """
    if column not in ALLOWED_COLUMNS:
        return {"error": f"Column '{column}' is not whitelisted. Allowed: {ALLOWED_COLUMNS}"}
    df = load_data()
    limit = min(n, 20)
    vc = df[column].value_counts().head(limit)
    return vc.to_dict()

def find_outliers(column: str) -> dict:
    """Enforces whitelist, read-only, and z-score outlier identification capped at 20 rows.
    
    Args:
        column: Numeric column to find outliers for.
    """
    if column not in ALLOWED_COLUMNS:
        return {"error": f"Column '{column}' is not whitelisted. Allowed: {ALLOWED_COLUMNS}"}
    df = load_data()
    if not np.issubdtype(df[column].dtype, np.number):
        return {"error": f"Column '{column}' is not numeric. Outliers only available for numeric columns."}
    mean = df[column].mean()
    std = df[column].std()
    if std == 0:
        return {"outliers": []}
    z_scores = (df[column] - mean) / std
    outliers_df = df[np.abs(z_scores) > 3].head(20)
    return {"outliers": outliers_df.to_dict(orient="records")}
