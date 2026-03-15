from __future__ import annotations

from fastapi import FastAPI

from api.routes_accounts import router as accounts_router
from api.routes_analysis import router as analysis_router
from api.routes_reports import router as reports_router


app = FastAPI(title="EdgeTracker-Pro API", version="0.1.0")
app.include_router(accounts_router)
app.include_router(analysis_router)
app.include_router(reports_router)

