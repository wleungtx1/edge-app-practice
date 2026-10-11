"""Application factory. Run locally with: uvicorn app.main:app --reload"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import __version__
from app.config import get_settings
from app.routes import providers

TEMPLATES = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version=__version__)
    application.include_router(providers.router)

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @application.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return TEMPLATES.TemplateResponse(
            request, "index.html", {"app_name": settings.app_name, "version": __version__}
        )

    return application


app = create_app()
