
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import requests
from .utils import load_company_metadata, load_sector_metadata, save_company_metadata, save_sector_metadata

COMPANY_CSV = os.path.join(os.path.dirname(__file__), "nepse_companies_metadata.csv")
SECTOR_CSV = os.path.join(os.path.dirname(__file__), "nepse_sectors_metadata.csv")

router = APIRouter()

API_URL = "https://sharehubnepal.com/live/api/v2/nepselive/live-nepse"

@router.get("/metadata/companies")
def get_companies():
    df = load_company_metadata(COMPANY_CSV)
    return df.to_dict(orient="records")

@router.get("/metadata/sectors")
def get_sectors():
    df = load_sector_metadata(SECTOR_CSV)
    return df["sector"].drop_duplicates().tolist()

@router.post("/metadata/update")
def update_metadata():
    """
    Fetch live NEPSE data and update company and sector metadata CSVs.
    """
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        if not data or not data.get('success'):
            raise HTTPException(status_code=502, detail="Invalid or unsuccessful API response")
        stocks = data.get('data', [])
        if not stocks:
            raise HTTPException(status_code=502, detail="No stock data available")
        df = pd.DataFrame(stocks)
        # Save company metadata
        company_data = df[[col for col in ['symbol', 'securityName', 'sector'] if col in df.columns]].copy()
        save_company_metadata(company_data, COMPANY_CSV)
        # Save sector metadata
        sector_data = df[['sector']].drop_duplicates().reset_index(drop=True)
        save_sector_metadata(sector_data, SECTOR_CSV)
        return {"message": "Metadata updated successfully.", "companies": len(company_data), "sectors": len(sector_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
