from __future__ import annotations

import pandas as pd
import plotly.express as px
from dash import Input, Output, State, callback, dash_table, dcc, html

from .metrics import trend_summary
from .models import AnalysisBundle

COLORS = {"bg": "#07111f", "panel": "#101d2f", "text": "#edf4ff", "muted": "#9bb0ca", "accent": "#42d3a5", "danger": "#ff667a"}

SECTIONS = {
    "Overview": ["Revenue", "Operating Income", "Net Income", "Free Cash Flow"],
    "Income Statement": ["Revenue", "Gross Profit", "Operating Income", "Net Income", "EPS Diluted"],
    "Balance Sheet": ["Cash", "Debt", "Assets", "Liabilities", "Shareholders' Equity", "Current Assets", "Current Liabilities"],
    "Cash Flow": ["Operating Cash Flow", "CapEx", "Free Cash Flow"],
    "Margins & Returns": ["Operating Margin", "Net Margin", "FCF Margin", "ROA", "ROE", "Current Ratio", "Cash Conversion"],
    "Growth": ["Revenue Growth"],
    "Capital Allocation": ["CapEx", "CapEx / Revenue", "Dividends", "Share Repurchases", "Debt"],
}


def layout(default_cik: str) -> html.Div:
    return html.Div([
        dcc.Store(id="analysis-store"),
        html.Header([html.Div([html.P("SEC EDGAR · 10-K intelligence", className="eyebrow"), html.H1("Financial statement audit dashboard"), html.P("Traceable facts, explicit calculations, reviewable flags.", className="subtitle")]), html.Div([dcc.Input(id="identifier", value=default_cik, placeholder="Ticker or CIK"), dcc.Dropdown(id="years", options=[3, 5, 10, 15], value=10, clearable=False), html.Button("Analyze", id="analyze", n_clicks=0)])], className="hero"),
        html.Div(id="status", className="status"),
        dcc.Tabs(id="tabs", value="Overview", children=[dcc.Tab(label=name, value=name) for name in [*SECTIONS, "Audit / Data Quality", "SEC Filings"]]),
        dcc.Loading(html.Main(id="content"), type="circle"),
    ], className="shell")


def _all_rows(bundle: AnalysisBundle) -> pd.DataFrame:
    facts = [{"kind": "FACT", "metric": x.metric, "fiscal_year": x.fiscal_year, "value": x.value, "unit": x.unit, "xbrl_tag": x.xbrl_tag, "accession_number": x.accession_number, "filed": str(x.filed)} for x in bundle.facts]
    calculated = [{"kind": "CALCULATED", "metric": x.metric, "fiscal_year": x.fiscal_year, "value": x.value, "unit": x.unit, "xbrl_tag": None, "accession_number": None, "filed": None, "reason_na": x.reason_na} for x in bundle.calculated]
    return pd.DataFrame(facts + calculated)


def _format_value(value: float | None, unit: str) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if unit == "USD":
        return f"${value / 1e9:,.2f}B"
    if unit == "%":
        return f"{value:,.2f}%"
    return f"{value:,.2f} {unit}"


def register_callbacks(app, service) -> None:
    @callback(Output("analysis-store", "data"), Output("status", "children"), Input("analyze", "n_clicks"), State("identifier", "value"), State("years", "value"), prevent_initial_call=False)
    def analyze(_, identifier, years):
        try:
            bundle = service.analyze(identifier or service.settings.default_cik, int(years or 10))
            return bundle.model_dump(mode="json"), f"{bundle.entity} · CIK {bundle.cik} · {len(bundle.facts)} selected SEC facts · {len(bundle.flags)} flags"
        except Exception as exc:
            return None, f"Analysis unavailable: {exc}"

    @callback(Output("content", "children"), Input("tabs", "value"), Input("analysis-store", "data"))
    def render(tab, data):
        if not data:
            return html.Div("Configure SEC_USER_AGENT, then click Analyze.", className="empty")
        bundle = AnalysisBundle.model_validate(data)
        if tab == "Audit / Data Quality":
            rows = [f.model_dump(mode="json") for f in bundle.flags]
            return html.Section([html.H2(tab), html.P("Flags are review prompts, not automatic corrections."), dash_table.DataTable(data=rows, columns=[{"name": c, "id": c} for c in ["severity", "code", "fiscal_year", "metric", "message"]], page_size=20, sort_action="native", filter_action="native", style_table={"overflowX": "auto"})], className="panel")
        if tab == "SEC Filings":
            rows = [f.model_dump(mode="json") for f in bundle.filings]
            return html.Section([html.H2(tab), dash_table.DataTable(data=rows, columns=[{"name": c, "id": c, "presentation": "markdown" if c == "filing_url" else "input"} for c in ["form", "filing_date", "report_date", "accession_number", "is_amended", "filing_url"]], markdown_options={"link_target": "_blank"}, page_size=20, sort_action="native", style_table={"overflowX": "auto"})], className="panel")

        df = _all_rows(bundle)
        metrics = SECTIONS[tab]
        view = df[df.metric.isin(metrics)].copy()
        latest_year = int(view.fiscal_year.max()) if not view.empty else None
        cards = []
        for metric in metrics[:4]:
            item = view[(view.metric == metric) & (view.fiscal_year == latest_year)]
            cards.append(html.Div([html.Span(metric), html.Strong(_format_value(item.iloc[0].value, item.iloc[0].unit) if not item.empty else "N/A")], className="kpi"))
        fig = px.line(view.dropna(subset=["value"]), x="fiscal_year", y="value", color="metric", markers=True, template="plotly_dark")
        fig.update_layout(paper_bgcolor=COLORS["panel"], plot_bgcolor=COLORS["panel"], legend_title_text="", xaxis_title="Fiscal year", yaxis_title="Reported / calculated value", hovermode="x unified")
        table = view.copy()
        table["display_value"] = table.apply(lambda r: _format_value(r.value, r.unit), axis=1)
        columns = ["kind", "metric", "fiscal_year", "display_value", "unit", "xbrl_tag", "accession_number", "filed"]
        children = [html.Div(cards, className="kpis"), html.Div(dcc.Graph(figure=fig), className="panel"), html.Div([html.H3("Underlying values and provenance"), dash_table.DataTable(data=table[columns].to_dict("records"), columns=[{"name": c.replace("_", " ").title(), "id": c} for c in columns], page_size=20, sort_action="native", filter_action="native", style_table={"overflowX": "auto"})], className="panel")]
        if tab == "Growth":
            trends = pd.DataFrame(trend_summary(bundle.facts, bundle.calculated))
            children.append(html.Div([html.H3("3 / 5 / 10-year trend summary"), dash_table.DataTable(data=trends.to_dict("records"), columns=[{"name": c, "id": c} for c in trends.columns], page_size=20, sort_action="native", style_table={"overflowX": "auto"})], className="panel"))
        return html.Section(children)

