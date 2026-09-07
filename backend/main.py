from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import csv
import logging
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Internal Service Imports
# These represent the modular "Science" of the application
from backend.services.normalizer import detect_bank, normalize_dataframe
from backend.services.categorizer import categorize_transactions
from backend.services.analyzer import generate_report

# --- LOGGING CONFIGURATION ---
# Essential for production-ready Linux software
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- PYDANTIC SCHEMAS (DATA CONTRACTS) ---
# These ensure the "Science" of data integrity between Backend and Frontend.
class FinancialKPIs(BaseModel):
    income: float
    expense: float
    net_cashflow: float
    savings_rate: float

class FinancialReport(BaseModel):
    kpis: FinancialKPIs
    health_metrics: Dict[str, float]
    insights: Dict[str, Any]

class AnalysisResponse(BaseModel):
    detected_bank: str
    rows: int
    columns: List[str]
    report: Optional[FinancialReport]
    data: List[Dict[str, Any]]

app = FastAPI(title="AI Finance Analyzer API")

@app.post("/upload/", response_model=AnalysisResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Main entry point for the analysis pipeline.
    Orchestrates the flow from raw CSV to categorized financial insights.
    """
    logger.info(f"Received upload request for file: {file.filename}")

    try:
        # 1. READ CSV (With Encoding Resilience)
        # Science: Handling messy real-world data formats
        try:
            logger.info("Attempting to parse CSV with UTF-8")
            df = pd.read_csv(
                file.file,
                sep=None,
                engine="python",
                encoding="utf-8",
                quoting=csv.QUOTE_NONE,
                on_bad_lines="skip"
            )
        except UnicodeDecodeError:
            logger.warning("UTF-8 parsing failed. Retrying with Latin-1 fallback.")
            file.file.seek(0)
            df = pd.read_csv(
                file.file,
                sep=None,
                engine="python",
                encoding="latin1",
                quoting=csv.QUOTE_NONE,
                on_bad_lines="skip"
            )

        # 2. PIPELINE EXECUTION
        # Step A: Detect which bank statement this is
        bank = detect_bank(df)
        logger.info(f"Bank format identified: {bank}")

        # Step B: Standardize columns and cleanup descriptions
        df = normalize_dataframe(df, bank)

        # Step C: Categorize transactions using Hybrid Rule/AI logic
        df = categorize_transactions(df)

        # Step D: Generate mathematical analytics report
        report = generate_report(df)

        logger.info("Processing pipeline completed successfully")

        # 3. RETURN STRUCTURED DATA
        # Pydantic will automatically validate this dictionary against AnalysisResponse
        return {
            "detected_bank": bank,
            "rows": len(df),
            "columns": list(df.columns),
            "report": report,
            "data": df.to_dict(orient="records")
        }

    except ValueError as ve:
        # Handle specific validation errors (e.g. Unsupported Bank)
        logger.error(f"Validation Error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        # Handle unexpected system errors
        # exc_info=True adds the traceback to the logs for debugging
        logger.error(f"Critical System Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during file processing"
        )