"""Canonical metrics and ordered US-GAAP XBRL tag candidates.

Order expresses preference only. The normalizer still scores period, form,
filing date and amendments before choosing one fact per fiscal year.
"""

TAG_CANDIDATES: dict[str, tuple[str, ...]] = {
    "Revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ),
    "Cost of Revenue": (
        "CostOfRevenue",
        "CostOfGoodsAndServicesSold",
        "CostOfGoodsSold",
    ),
    "Gross Profit": ("GrossProfit",),
    "Operating Income": ("OperatingIncomeLoss",),
    "Net Income": ("NetIncomeLoss", "ProfitLoss"),
    "EPS Diluted": ("EarningsPerShareDiluted",),
    "Operating Cash Flow": ("NetCashProvidedByUsedInOperatingActivities",),
    "CapEx": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsForAdditionsToPropertyPlantAndEquipment",
    ),
    "Cash": (
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ),
    "Current Assets": ("AssetsCurrent",),
    "Current Liabilities": ("LiabilitiesCurrent",),
    "Debt Current": (
        "ShortTermBorrowings",
        "LongTermDebtCurrent",
        "ShortTermBorrowingsAndCurrentMaturitiesOfLongTermDebt",
    ),
    "Debt Noncurrent": ("LongTermDebtNoncurrent", "LongTermDebt"),
    "Assets": ("Assets",),
    "Liabilities": ("Liabilities",),
    "Shareholders' Equity": (
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ),
    "Dividends": ("PaymentsOfDividends", "PaymentsOfDividendsCommonStock"),
    "Share Repurchases": ("PaymentsForRepurchaseOfCommonStock",),
}

INSTANT_METRICS = {
    "Cash",
    "Current Assets",
    "Current Liabilities",
    "Debt Current",
    "Debt Noncurrent",
    "Assets",
    "Liabilities",
    "Shareholders' Equity",
}

EXPECTED_UNITS = {
    "EPS Diluted": {"USD/shares"},
    **{metric: {"USD"} for metric in TAG_CANDIDATES if metric != "EPS Diluted"},
}

