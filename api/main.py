from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from auth import router as auth_router
from auth.dependencies import DEFAULT_AUTH_SECRET
from api.routes_accounts import router as accounts_router
from api.routes_analysis import router as analysis_router
from api.routes_reports import router as reports_router
from database.db import DEFAULT_DATABASE_NAME, connect_db, initialize_db


def create_app(
    database_path: str | Path | None = None,
    auth_secret: str = DEFAULT_AUTH_SECRET,
) -> FastAPI:
    app = FastAPI(title="EdgeTracker-Pro API", version="0.1.0")
    app.state.database_path = Path(database_path or (Path("data") / DEFAULT_DATABASE_NAME))
    app.state.auth_secret = auth_secret

    connection = connect_db(app.state.database_path)
    initialize_db(connection)
    connection.close()

    app.include_router(accounts_router)
    app.include_router(analysis_router)
    app.include_router(reports_router)
    app.include_router(auth_router)
    return app


app = create_app()
