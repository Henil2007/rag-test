"""
Module 2: Smart Financial Calculator & Scheme Router
-----------------------------------------------------
Pure deterministic logic. No LLM / RAG involved here on purpose:
loan numbers, interest rates, and EMI figures must be exact, not generated.
"""

from dataclasses import dataclass


# --- Scheme configuration (source of truth, matches PS document) ---
MICRO_FINANCE_SCHEME = {
    "name": "Micro Finance Scheme",
    "max_project_cost": 140_000,
    "loan_share": 0.90,
    "max_loan_amount": 125_000,
    "interest_rate_annual": 6.5,
    "tenure_years": 3,
    "moratorium_months": 3,
}

TERM_LOAN_SCHEME = {
    "name": "Term Loan Scheme",
    "max_project_cost": 5_000_000,
    "loan_share": 0.90,
    "max_loan_amount": 4_500_000,
    "interest_rate_annual": 8.0,
    "tenure_years": 7,
    "moratorium_months": 6,
}

MARGIN_MONEY_FRACTION = 0.10  # beneficiary contributes 10% of project cost


@dataclass
class FinancialPlan:
    margin_capital: float
    project_cost: float
    loan_amount: float
    scheme_name: str
    interest_rate_annual: float
    tenure_years: int
    moratorium_months: int
    quarterly_emi: float
    total_interest_payable: float
    total_repayment: float


def calculate_project_cost(margin_capital: float) -> float:
    """Project Cost = Margin Capital / 10%"""
    return round(margin_capital / MARGIN_MONEY_FRACTION, 2)


def select_scheme(project_cost: float) -> dict:
    """Logic A / Logic B routing exactly as specified in the PS."""
    if project_cost <= MICRO_FINANCE_SCHEME["max_project_cost"]:
        return MICRO_FINANCE_SCHEME
    elif project_cost <= TERM_LOAN_SCHEME["max_project_cost"]:
        return TERM_LOAN_SCHEME
    else:
        raise ValueError(
            f"Project cost Rs.{project_cost:,.0f} exceeds Rs.50,00,000 — "
            "outside both scheme ceilings. Not eligible under this PS's schemes."
        )


def calculate_loan_amount(project_cost: float, scheme: dict) -> float:
    raw_loan = project_cost * scheme["loan_share"]
    return round(min(raw_loan, scheme["max_loan_amount"]), 2)


def calculate_emi_schedule(loan_amount: float, scheme: dict) -> dict:
    """
    Quarterly EMI using standard amortization, applied AFTER the moratorium period.
    Simple/flat assumptions are avoided in favor of a proper amortizing loan formula.
    """
    annual_rate = scheme["interest_rate_annual"] / 100
    quarterly_rate = annual_rate / 4
    total_quarters = scheme["tenure_years"] * 4
    moratorium_quarters = round(scheme["moratorium_months"] / 3)
    repayment_quarters = total_quarters - moratorium_quarters

    if quarterly_rate == 0:
        quarterly_emi = loan_amount / repayment_quarters
    else:
        # standard amortization formula, per quarter
        quarterly_emi = (
            loan_amount
            * quarterly_rate
            * (1 + quarterly_rate) ** repayment_quarters
        ) / ((1 + quarterly_rate) ** repayment_quarters - 1)

    total_repayment = quarterly_emi * repayment_quarters
    total_interest = total_repayment - loan_amount

    return {
        "quarterly_emi": round(quarterly_emi, 2),
        "repayment_quarters": repayment_quarters,
        "moratorium_quarters": moratorium_quarters,
        "total_repayment": round(total_repayment, 2),
        "total_interest_payable": round(total_interest, 2),
    }


def build_financial_plan(margin_capital: float) -> FinancialPlan:
    if margin_capital <= 0:
        raise ValueError("Margin capital must be greater than 0.")

    project_cost = calculate_project_cost(margin_capital)
    scheme = select_scheme(project_cost)
    loan_amount = calculate_loan_amount(project_cost, scheme)
    emi_info = calculate_emi_schedule(loan_amount, scheme)

    return FinancialPlan(
        margin_capital=margin_capital,
        project_cost=project_cost,
        loan_amount=loan_amount,
        scheme_name=scheme["name"],
        interest_rate_annual=scheme["interest_rate_annual"],
        tenure_years=scheme["tenure_years"],
        moratorium_months=scheme["moratorium_months"],
        quarterly_emi=emi_info["quarterly_emi"],
        total_interest_payable=emi_info["total_interest_payable"],
        total_repayment=emi_info["total_repayment"],
    )


if __name__ == "__main__":
    plan = build_financial_plan(100_000)
    print(plan)
