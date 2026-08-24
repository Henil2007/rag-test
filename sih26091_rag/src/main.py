"""
End-to-end pipeline for SIH26091:
  Input: village, margin capital, business category
  Output: Module 2 financial plan (deterministic) + Module 1 feasibility report (RAG)
"""

from financial_calculator import build_financial_plan
from local_data import find_village, get_competitor_density
from rag_engine import build_retriever, generate_feasibility_report


def run(village_name: str, margin_capital: float, sector: str):
    print("=" * 70)
    print(f"INPUT -> Village: {village_name} | Margin Capital: Rs.{margin_capital:,.0f} | Sector: {sector}")
    print("=" * 70)

    # ---- Module 2: Smart Financial Calculator & Scheme Router ----
    plan = build_financial_plan(margin_capital)
    print("\n--- MODULE 2: FINANCIAL PLAN ---")
    print(f"Project Cost:        Rs.{plan.project_cost:,.2f}")
    print(f"Scheme Selected:     {plan.scheme_name}")
    print(f"Loan Amount:         Rs.{plan.loan_amount:,.2f}")
    print(f"Interest Rate:       {plan.interest_rate_annual}% p.a.")
    print(f"Tenure:              {plan.tenure_years} years (moratorium: {plan.moratorium_months} months)")
    print(f"Quarterly EMI:       Rs.{plan.quarterly_emi:,.2f}")
    print(f"Total Interest:      Rs.{plan.total_interest_payable:,.2f}")
    print(f"Total Repayment:     Rs.{plan.total_repayment:,.2f}")

    # ---- Module 1: Hyper-Local Feasibility Report (RAG) ----
    village_row = find_village(village_name)
    if village_row is None:
        print(f"\n[WARN] Village '{village_name}' not found in dummy dataset. "
              f"Using generic context only (no structured local stats).")
        village_row = {}

    competitor_density = get_competitor_density(village_row, sector) if village_row else None

    retriever = build_retriever()
    query = f"{sector} sector local market opportunity threats SWOT pricing"
    retrieved = retriever.retrieve(query, top_k=4)

    report = generate_feasibility_report(village_row, competitor_density, sector, retrieved)

    print("\n--- MODULE 1: HYPER-LOCAL FEASIBILITY REPORT ---")
    print(report)


if __name__ == "__main__":
    # Example run — change these to test different inputs
    run(village_name="sundarpur", margin_capital=100_000, sector="textiles")
