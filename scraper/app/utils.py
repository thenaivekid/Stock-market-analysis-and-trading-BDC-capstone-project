# Utility functions for NEPSE data and metadata
import pandas as pd
import os

def load_company_metadata(csv_path):
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=["symbol", "securityName", "sector"])
    return pd.read_csv(csv_path)

def load_sector_metadata(csv_path):
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=["sector"])
    return pd.read_csv(csv_path)

def save_company_metadata(df, csv_path):
    df.to_csv(csv_path, index=False)

def save_sector_metadata(df, csv_path):
    df.to_csv(csv_path, index=False)
