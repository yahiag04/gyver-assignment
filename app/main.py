from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import Settings, get_settings
from app.controllers.health import router as health_router
from app.controllers.ads import router as ads_router
from app.controllers.job_offers import router as job_offers_router
from app.db.session import Base, create_database


VIEW_DIR = Path(__file__).resolve().parent / "views"


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    upload_dir = Path(app_settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    engine, session_factory = create_database(app_settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        from app import models  # noqa: F401 — register model metadata before table creation

        Base.metadata.create_all(bind=app.state.engine)
        yield
        app.state.engine.dispose()

    app = FastAPI(title="Gyver Annunci", lifespan=lifespan)
    app.state.settings = app_settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.mount("/static", StaticFiles(directory=VIEW_DIR / "static"), name="static")
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

    templates = Jinja2Templates(directory=str(VIEW_DIR / "templates"))

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"max_upload_mb": app.state.settings.max_upload_mb},
        )

    app.include_router(health_router, prefix="/api")
    app.include_router(job_offers_router, prefix="/api")
    app.include_router(ads_router, prefix="/api")
    return app


app = create_app()
