import pandas as pd
import logging
from backend.config.category_rules import CATEGORY_GROUPS

logger = logging.getLogger(__name__)

def generate_report(df: pd.DataFrame) -> dict:
    if df.empty:
        logger.warning("Empty data provided to analyzer.")
        return {
            "kpis": {"income": 0.0, "expense": 0.0, "net_cashflow": 0.0, "savings_rate": 0.0},
            "health_metrics": {g: 0.0 for g in CATEGORY_GROUPS.keys()},
            "insights": {"top_category": "N/A", "avg_daily_spend": 0.0, "total_transactions": 0}
        }

    try:
        income = df[df["Amount"] > 0]["Amount"].sum()
        expense_df = df[df["Amount"] < 0]
        expense = abs(expense_df["Amount"].sum())
        
        health_metrics = {}
        for group, cats in CATEGORY_GROUPS.items():
            health_metrics[group] = float(abs(expense_df[expense_df["Category"].isin(cats)]["Amount"].sum()))

        category_spend = expense_df.groupby("Category")["Amount"].sum().abs()
        top_cat = category_spend.idxmax() if not category_spend.empty else "N/A"
        
        # Ensure Date is datetime for .dt accessor
        df["Date"] = pd.to_datetime(df["Date"])
        avg_daily = expense_df.groupby(df["Date"].dt.date)["Amount"].sum().abs().mean()

        return {
            "kpis": {
                "income": float(income),
                "expense": float(expense),
                "net_cashflow": float(income - expense),
                "savings_rate": round(float(((income - expense) / income * 100)), 2) if income > 0 else 0.0
            },
            "health_metrics": health_metrics,
            "insights": {
                "top_category": top_cat,
                "avg_daily_spend": float(avg_daily) if not pd.isna(avg_daily) else 0.0,
                "total_transactions": len(df)
            }
        }
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        return {}