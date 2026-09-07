import sys
import os
import io
import requests
import numpy as np
import pandas as pd
import streamlit as st
from fpdf import FPDF

# --- PATH ENFORCEMENT ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.settings import API_BASE_URL
from backend.config.category_rules import TRANSACTION_CATEGORIES, CATEGORY_GROUPS

# --- PAGE ARCHITECTURE ---
st.set_page_config(
    page_title="FinSight Executive | Financial Intelligence Suite",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CLEAN, THEME-ADAPTIVE STYLING ---
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
    
    /* Sleek Cards that adapt to dark & light modes */
    .metric-card {
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
    }
    .metric-card-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #888888;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-card-value {
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .metric-card-sub {
        font-size: 0.8rem;
        margin-top: 4px;
        color: #888888;
    }
    
    /* Plain English Alert Callouts */
    .plain-alert-danger {
        background-color: rgba(255, 75, 75, 0.08);
        border-left: 5px solid #ff4b4b;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .plain-alert-success {
        background-color: rgba(0, 204, 126, 0.08);
        border-left: 5px solid #00cc7e;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .plain-alert-info {
        background-color: rgba(59, 130, 246, 0.08);
        border-left: 5px solid #3b82f6;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Chart Explanation Box */
    .chart-note {
        background: rgba(128, 128, 128, 0.06);
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.88rem;
        color: #888888;
        margin-top: 8px;
        margin-bottom: 24px;
        border-left: 3px solid #6c757d;
    }
</style>
""", unsafe_allow_html=True)


# --- EXECUTIVE PDF GENERATOR (Error-Free Byte Output) ---
def generate_executive_pdf(df, kpi_summary, macro_groups, bank_name):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 12, "FINANCIAL HEALTH & AUDIT REPORT", ln=True, align="L")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(108, 117, 125)
    pdf.cell(0, 6, f"BANK: {bank_name.upper()} | AUDIT DATE: {pd.Timestamp.now().strftime('%Y-%m-%d')}", ln=True, align="L")
    pdf.line(10, 28, 200, 28)
    pdf.ln(8)

    # 1. Financial Overview
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 8, "1. Executive Summary", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(47, 10, f"Total Income: Rs. {kpi_summary['income']:,.0f}", border=1)
    pdf.cell(47, 10, f"Total Spending: Rs. {kpi_summary['expense']:,.0f}", border=1)
    pdf.cell(47, 10, f"Net Saved: Rs. {kpi_summary['net']:,.0f}", border=1)
    pdf.cell(49, 10, f"Savings Rate: {kpi_summary['savings']:.1f}%", border=1, ln=True)
    pdf.ln(6)

    # 2. 50/30/20 Breakdown
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Where Your Money Went (Budget Allocation)", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(80, 7, "Category Group", border=1)
    pdf.cell(50, 7, "Amount Spent", border=1)
    pdf.cell(60, 7, "% of Total Spending", border=1, ln=True)

    pdf.set_font("Helvetica", "", 9)
    for group, val in macro_groups.items():
        pct = (val / kpi_summary['expense'] * 100) if kpi_summary['expense'] > 0 else 0
        pdf.cell(80, 7, f" {group}", border=1)
        pdf.cell(50, 7, f" Rs. {val:,.0f}", border=1)
        pdf.cell(60, 7, f" {pct:.1f}%", border=1, ln=True)
    pdf.ln(6)

    # 3. Top Spending Vendors
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Top Places You Spent Money", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(90, 7, "Recipient / Store", border=1)
    pdf.cell(50, 7, "Category", border=1)
    pdf.cell(50, 7, "Amount (Rs.)", border=1, ln=True)

    top_merchants = (
        df[df["Amount"] < 0]
        .groupby(["Clean_Description", "Category"])["Amount"]
        .sum()
        .abs()
        .reset_index()
        .sort_values(by="Amount", ascending=False)
        .head(8)
    )

    pdf.set_font("Helvetica", "", 8)
    for _, row in top_merchants.iterrows():
        desc_str = str(row["Clean_Description"])[:45]
        pdf.cell(90, 6, f" {desc_str}", border=1)
        pdf.cell(50, 6, f" {str(row['Category'])}", border=1)
        pdf.cell(50, 6, f" {row['Amount']:,.0f}", border=1, ln=True)

    return bytes(pdf.output())


# --- APPLICATION HEADER & INGESTION ---
st.title("⚖️ FinSight Executive")
st.caption("Complete Financial Audit • AI Category & Entity Detection • Private & In-Memory")

# Main Page Dropzone (No sidebar)
if "raw_payload" not in st.session_state:
    st.markdown("### 📥 Step 1: Upload Your Bank Statement")
    uploaded_file = st.file_uploader(
        "Upload your bank statement (CSV format). Axis Bank, Bank of India, or generic statements are supported.",
        type=["csv"]
    )
    if uploaded_file:
        with st.spinner("Analyzing bank statement with AI pipeline..."):
            try:
                response = requests.post(f"{API_BASE_URL}/upload/", files={"file": uploaded_file})
                if response.status_code == 200:
                    st.session_state.raw_payload = response.json()
                    st.rerun()
                else:
                    st.error(f"Upload rejected: {response.text}")
            except Exception as e:
                st.error(f"Could not reach backend server: {e}")
        st.stop()
    else:
        st.info("Upload a bank statement CSV above to generate your report.")
        st.stop()
else:
    col_hdr, col_reset = st.columns([5, 1])
    with col_reset:
        if st.button("🔄 Ingest New File", use_container_width=True):
            del st.session_state["raw_payload"]
            st.rerun()

res_data = st.session_state.raw_payload

# Clean Data & Setup Dates
df = pd.DataFrame(res_data["data"])
df["Date"] = pd.to_datetime(df["Date"])
df["DayName"] = df["Date"].dt.day_name()
df["IsWeekend"] = df["Date"].dt.dayofweek.isin([5, 6])
if "Remarks" not in df.columns:
    df["Remarks"] = ""


# --- SECTION 1: INTERACTIVE TABLE DIRECTLY ON SCREEN ---
st.markdown("---")
st.subheader("📝 1. Your Transactions (Review & Edit)")
st.caption("AI automatically categorized these. If any category is incorrect, double-click it to change it. Your edits will update all metrics below instantly.")

edited_df = st.data_editor(
    df,
    column_config={
        "Category": st.column_config.SelectboxColumn(
            "Category",
            options=TRANSACTION_CATEGORIES,
            width="medium",
            help="Select the right category if the AI made a mistake"
        ),
        "Remarks": st.column_config.TextColumn(
            "Smart Remarks (AI Detected)",
            width="large"
        ),
        "Amount": st.column_config.NumberColumn("Amount (₹)", format="₹ %.2f"),
        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
        "Clean_Description": st.column_config.TextColumn("Recipient / Description")
    },
    disabled=["Date", "Description", "Clean_Description", "Amount", "DayName", "IsWeekend"],
    use_container_width=True,
    key="master_ledger"
)

# Dynamic Quantitative Calculations
total_inflow = edited_df[edited_df["Amount"] > 0]["Amount"].sum()
expense_mask = edited_df["Amount"] < 0
expenses_df = edited_df[expense_mask].copy()
total_outflow = abs(expenses_df["Amount"].sum())
net_cashflow = total_inflow - total_outflow
savings_margin = (net_cashflow / total_inflow * 100) if total_inflow > 0 else 0.0

# Time Variables
min_date = edited_df["Date"].min()
max_date = edited_df["Date"].max()
active_days = max((max_date - min_date).days + 1, 1)
burn_rate_daily = total_outflow / active_days

# Budget Pillars (50/30/20)
macro_alloc = {}
for g_name, cat_list in CATEGORY_GROUPS.items():
    macro_alloc[g_name] = abs(expenses_df[expenses_df["Category"].isin(cat_list)]["Amount"].sum())

needs_spent = macro_alloc.get("Essential", 0)
wants_spent = macro_alloc.get("Lifestyle", 0)
invest_spent = macro_alloc.get("Investment", 0)
leakage_spent = macro_alloc.get("Leakage", 0)

needs_ratio = (needs_spent / total_outflow * 100) if total_outflow > 0 else 0
wants_ratio = (wants_spent / total_outflow * 100) if total_outflow > 0 else 0
invest_ratio = (invest_spent / total_outflow * 100) if total_outflow > 0 else 0
leakage_ratio = (leakage_spent / total_outflow * 100) if total_outflow > 0 else 0

weekend_spend = abs(expenses_df[expenses_df["IsWeekend"]]["Amount"].sum())
weekday_spend = abs(expenses_df[~expenses_df["IsWeekend"]]["Amount"].sum())

# Anomaly Threshold: Purchases far above typical (mean + 2 std deviations)
mean_expense = abs(expenses_df["Amount"]).mean() if not expenses_df.empty else 0
std_expense = abs(expenses_df["Amount"]).std() if not expenses_df.empty else 0
anomaly_threshold = mean_expense + (2 * std_expense) if std_expense > 0 else mean_expense * 3
outliers = expenses_df[abs(expenses_df["Amount"]) > anomaly_threshold]


# --- SECTION 2: EXECUTIVE KPIS & HEALTH SCORE EXPLAINED ---
st.markdown("---")
st.subheader("🏛️ 2. Cash Flow & Financial Health Score")

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Total Money In</div>
        <div class="metric-card-value" style="color: #00cc7e;">₹ {total_inflow:,.0f}</div>
        <div class="metric-card-sub">{len(edited_df[edited_df['Amount'] > 0])} deposits / salary</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Total Money Out</div>
        <div class="metric-card-value" style="color: #ff4b4b;">₹ {total_outflow:,.0f}</div>
        <div class="metric-card-sub">{len(expenses_df)} total purchases</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    flow_color = "#00cc7e" if net_cashflow >= 0 else "#ff4b4b"
    flow_label = "Saved This Period" if net_cashflow >= 0 else "Overspent (In Deficit)"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Net Balance</div>
        <div class="metric-card-value" style="color: {flow_color};">₹ {net_cashflow:,.0f}</div>
        <div class="metric-card-sub">{flow_label}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Daily Spending Rate</div>
        <div class="metric-card-value" style="color: #3b82f6;">₹ {burn_rate_daily:,.0f}</div>
        <div class="metric-card-sub">Average per day across {active_days} days</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    # Health Score Calculation (Transparent algorithm)
    score = 100
    if savings_margin < 20: score -= 25
    if wants_ratio > 35: score -= 25
    if leakage_ratio > 4: score -= 25
    if invest_ratio < 10: score -= 15
    score = max(score, 10)
    score_color = "#00cc7e" if score >= 75 else "#f59e0b" if score >= 50 else "#ff4b4b"
    grade = "Excellent" if score >= 80 else "Fair" if score >= 50 else "Needs Attention"

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Financial Health Score</div>
        <div class="metric-card-value" style="color: {score_color};">{score} / 100</div>
        <div class="metric-card-sub">Rating: <strong>{grade}</strong></div>
    </div>
    """, unsafe_allow_html=True)

# Transparent Breakdown of Financial Health Score
with st.expander("ℹ️ What is the Financial Health Score and how is it calculated?", expanded=False):
    st.markdown("""
    The **Financial Health Score** rates your financial habits from **0 to 100** based on 4 golden rules of personal finance:
    1. **Saving at least 20% of your income:** If you save less than 20%, your score drops by 25 points.
    2. **Keeping lifestyle/wants under 35%:** If shopping, dining, and travel exceed 35% of your spending, you lose 25 points.
    3. **Eliminating cash leakage:** If bank charges and ATM withdrawals exceed 4% of total spending, you lose 25 points.
    4. **Investing for the future:** If investments are below 10% of spending, you lose 15 points.
    
    *A score above 75 means you have healthy cash habits and disciplined capital retention.*
    """)


# --- SECTION 3: PLAIN-ENGLISH RISK & ANOMALY WATCHLIST ---
st.markdown("---")
st.subheader("🔍 3. Alerts & Spending Warnings (Plain English)")

# Alert 1: Unusually Big Expenses
if not outliers.empty:
    largest_item = outliers.sort_values("Amount").iloc[0]
    st.markdown(f"""
    <div class="plain-alert-danger">
        <strong>⚠️ Unusually Large Purchases Detected:</strong><br>
        You had <strong>{len(outliers)} purchases</strong> that were significantly larger than your typical day-to-day spending (higher than ₹ {anomaly_threshold:,.0f}).<br>
        Your single largest payment was <strong>₹ {abs(largest_item['Amount']):,.0f}</strong> on {largest_item['Date'].strftime('%d %b %Y')} to <strong>{largest_item['Clean_Description']}</strong>.<br>
        <em>Action: Confirm this was a planned expense and not an incorrect or unauthorized charge.</em>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="plain-alert-success"><strong>✅ Consistent Spending:</strong> You had no sudden, massive spending spikes. All transactions were within your normal spending range.</div>', unsafe_allow_html=True)

# Alert 2: Cash Leakage & Bank Fees
if leakage_ratio > 4.0:
    st.markdown(f"""
    <div class="plain-alert-danger">
        <strong>💸 Money Leaks (ATM Withdrawals & Bank Charges):</strong><br>
        You spent <strong>₹ {leakage_spent:,.0f} ({leakage_ratio:.1f}% of all spending)</strong> on cash withdrawals or bank fees.<br>
        Cash is dangerous for budgeting because it is untracked once withdrawn, and bank maintenance fees are pure money lost.<br>
        <em>Action: Use digital payments (UPI/Cards) instead of ATM cash so every rupee is tracked, and check your bank's fee schedule.</em>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="plain-alert-success"><strong>✅ Low Money Leaks:</strong> Less than 4% of your spending went to ATM cash or fees. Your money is well-tracked digitally.</div>', unsafe_allow_html=True)

# Alert 3: Deficit or Surplus Warning
if net_cashflow < 0:
    st.markdown(f"""
    <div class="plain-alert-danger">
        <strong>🚨 Overspending Alert (Negative Cash Flow):</strong><br>
        You spent <strong>₹ {abs(net_cashflow):,.0f} more than you earned</strong> during this statement period.<br>
        This means you dipped into existing savings or ran up credit debt to cover expenses.<br>
        <em>Action: Cut down on non-essential categories (like shopping and dining) until you return to a positive monthly surplus.</em>
    </div>
    """, unsafe_allow_html=True)
elif savings_margin >= 25:
    st.markdown(f"""
    <div class="plain-alert-success">
        <strong>🎉 Strong Savings Habit:</strong><br>
        You saved <strong>{savings_margin:.1f}% (₹ {net_cashflow:,.0f})</strong> of your income this month. Saving more than 20% puts you in the top tier of financial discipline. Consider putting this surplus into mutual funds or high-interest savings.
    </div>
    """, unsafe_allow_html=True)


# --- SECTION 4: 50/30/20 BUDGET BENCHMARK ---
st.markdown("---")
st.subheader("📊 4. The 50 / 30 / 20 Budget Check")
st.caption("A standard personal finance rule recommends spending 50% on Needs, 30% on Wants, and putting 20% toward Savings/Investments.")

b1, b2, b3, b4 = st.columns(4)
with b1:
    st.metric("1. Needs (Essentials)", f"₹ {needs_spent:,.0f}", f"{needs_ratio:.1f}% (Target: ≤ 50%)", delta_color="inverse" if needs_ratio > 50 else "normal")
    st.caption("Groceries, Rent, Utilities, Transport, Medical")
with b2:
    st.metric("2. Wants (Lifestyle)", f"₹ {wants_spent:,.0f}", f"{wants_ratio:.1f}% (Target: ≤ 30%)", delta_color="inverse" if wants_ratio > 30 else "normal")
    st.caption("Dining out, Shopping, Movies, Travel")
with b3:
    st.metric("3. Investments", f"₹ {invest_spent:,.0f}", f"{invest_ratio:.1f}% (Target: ≥ 20%)", delta_color="normal" if invest_ratio >= 20 else "inverse")
    st.caption("SIPs, Mutual Funds, Stocks, Savings")
with b4:
    st.metric("4. Cash & Fees (Friction)", f"₹ {leakage_spent:,.0f}", f"{leakage_ratio:.1f}% (Target: ≤ 4%)", delta_color="inverse" if leakage_ratio > 4 else "normal")
    st.caption("ATM cash, Bank charges, Taxes")


# --- SECTION 5: FULL-WIDTH STACKED GRAPHS WITH READING NOTES ---
st.markdown("---")
st.subheader("📈 5. Detailed Visual Trends")

# Graph 1: Account Balance Trajectory
st.markdown("#### Graph A: Cumulative Net Cash Trajectory")
chronological_df = edited_df.sort_values("Date").copy()
chronological_df["Cumulative_Cashflow"] = chronological_df["Amount"].cumsum()
daily_cum = chronological_df.groupby(chronological_df["Date"].dt.date)["Cumulative_Cashflow"].last()

st.area_chart(daily_cum, color="#3b82f6", use_container_width=True)
st.markdown("""
<div class="chart-note">
    <strong>💡 How to read this graph:</strong> This line shows whether your bank account was growing or shrinking over time.<br>
    • <strong>A rising blue area</strong> indicates money coming in (salary/deposits) and out-pacing expenses.<br>
    • <strong>A dropping blue area</strong> shows periods where money is rapidly exiting your account.<br>
    • If the curve ends above zero, you finished the period with money saved. If it dips below zero, you spent more than you earned.
</div>
""", unsafe_allow_html=True)

# Graph 2: Daily Spending Spikes
st.markdown("#### Graph B: Daily Spending Velocity")
daily_expense = expenses_df.groupby(expenses_df["Date"].dt.date)["Amount"].sum().abs()
st.line_chart(daily_expense, color="#ff4b4b", use_container_width=True)

peak_day = daily_expense.idxmax() if not daily_expense.empty else "N/A"
peak_amount = daily_expense.max() if not daily_expense.empty else 0

st.markdown(f"""
<div class="chart-note">
    <strong>💡 How to read this graph:</strong> Each red point represents the total amount spent on that specific calendar day.<br>
    • <strong>Tall spikes</strong> indicate days with heavy spending. Your highest spending day was <strong>{peak_day}</strong> where you spent <strong>₹ {peak_amount:,.0f}</strong>.<br>
    • A healthy financial graph shows low, steady daily spending with minimal tall spikes.
</div>
""", unsafe_allow_html=True)

# Graph 3: Weekday vs Weekend Spending
st.markdown("#### Graph C: Weekday vs. Weekend Spending")
weekday_summary = pd.DataFrame({
    "Day Category": ["Monday to Friday (Workdays)", "Saturday & Sunday (Weekend)"],
    "Total Spent (₹)": [weekday_spend, weekend_spend]
}).set_index("Day Category")

st.bar_chart(weekday_summary, color="#ff7f0e", use_container_width=True)

weekend_pct = (weekend_spend / total_outflow * 100) if total_outflow > 0 else 0
st.markdown(f"""
<div class="chart-note">
    <strong>💡 How to read this graph:</strong> This compares workweek spending against weekend spending.<br>
    • You spent <strong>{weekend_pct:.1f}% (₹ {weekend_spend:,.0f})</strong> of your money on Saturdays and Sundays alone.<br>
    • Weekends only make up ~28% of the calendar days. If your weekend spending exceeds 35-40% of total spend, you are heavily leaking money on weekend leisure activities.
</div>
""", unsafe_allow_html=True)

# Graph 4: Top Merchants
st.markdown("#### Graph D: Top Places You Spent Money (Top Vendors)")
top_counterparties = (
    expenses_df.groupby("Clean_Description")["Amount"]
    .sum()
    .abs()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(top_counterparties, color="#ff4b4b", use_container_width=True)
st.markdown("""
<div class="chart-note">
    <strong>💡 How to read this graph:</strong> The 80/20 Pareto rule in finance shows that 80% of spending usually goes to just a handful of recurring merchants. Focus on reducing your top 3 merchants on this list to quickly improve monthly savings.
</div>
""", unsafe_allow_html=True)


# --- SECTION 6: CLEAN EXPORTS ---
st.markdown("---")
st.subheader("💾 6. Export Your Report")
st.write("Save your audited financial data and reports locally:")

c_btn_excel, c_btn_pdf = st.columns(2)

# Excel Export
with c_btn_excel:
    excel_stream = io.BytesIO()
    with pd.ExcelWriter(excel_stream, engine='xlsxwriter') as writer:
        export_clean_df = edited_df.drop(columns=["IsWeekend", "DayName"], errors="ignore")
        export_clean_df.to_excel(writer, sheet_name="Cleaned_Ledger", index=False)

        macro_df = pd.DataFrame([
            {"Budget Pillar": k, "Amount Spent": v, "Share": f"{(v/total_outflow*100):.1f}%"}
            for k, v in macro_alloc.items()
        ])
        macro_df.to_excel(writer, sheet_name="Budget_Pillars", index=False)

        top_counterparties.reset_index().rename(columns={"Amount": "Total Spent"}).to_excel(writer, sheet_name="Top_Merchants", index=False)

    st.download_button(
        label="📊 Download Excel Spreadsheet (.xlsx)",
        data=excel_stream.getvalue(),
        file_name=f"Finance_Model_{res_data['detected_bank']}.xlsx",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )

# PDF Export
with c_btn_pdf:
    kpi_report_payload = {
        "income": total_inflow,
        "expense": total_outflow,
        "net": net_cashflow,
        "savings": savings_margin
    }
    pdf_bytes = generate_executive_pdf(
        edited_df,
        kpi_report_payload,
        macro_alloc,
        res_data['detected_bank']
    )
    
    st.download_button(
        label="📄 Download PDF Summary Statement (.pdf)",
        data=pdf_bytes,
        file_name=f"Financial_Summary_{res_data['detected_bank']}.pdf",
        mime="application/pdf",
        use_container_width=True
    )