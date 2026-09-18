from __future__ import annotations

import sys
from pathlib import Path

from dash import Dash

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sec_dashboard.config import settings  # noqa: E402
from sec_dashboard.service import AnalysisService  # noqa: E402
from sec_dashboard.ui import layout, register_callbacks  # noqa: E402

app = Dash(__name__, title="SEC Financial Audit", assets_folder=str(ROOT / "assets"), suppress_callback_exceptions=True)
app.layout = layout(settings.default_cik)

try:
    service = AnalysisService(settings)
    register_callbacks(app, service)
except ValueError:
    class DeferredService:
        settings = settings

        def analyze(self, *_args, **_kwargs):
            settings.validate()

    register_callbacks(app, DeferredService())

server = app.server

if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, debug=settings.debug)

