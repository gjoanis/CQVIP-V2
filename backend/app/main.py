import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    administration,
    auth,
    clients,
    dashboard,
    documents,
    knowledge_library,
    notifications,
    project_dashboard,
    project_workspace,
    projects,
    reports,
    requirements,
    risk_register,
    settings as settings_routes,
    systems,
    traceability,
    users,
    validation_activities,
)
from app.config import get_settings
from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.database import init_db

settings = get_settings()
logger = logging.getLogger("cqvip")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_all() only creates tables that don't exist yet -- safe to run
    # every startup regardless of environment, since schema changes in this
    # app go through non-destructive ALTER TABLE rather than Alembic revisions.
    init_db()
    yield


app = FastAPI(title="CQVIP", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def catch_unhandled_exceptions(request: Request, call_next):
    # A handler registered via @app.exception_handler(Exception) gets promoted by
    # Starlette to the outermost ServerErrorMiddleware, which sits OUTSIDE
    # CORSMiddleware -- so its response never gets CORS headers and the browser
    # reports an opaque network failure instead of a readable error.
    #
    # Starlette's add_middleware() *prepends* to the middleware list, so the
    # middleware added LAST ends up OUTERMOST. Registering this middleware
    # before CORSMiddleware is added below means CORSMiddleware ends up
    # wrapping this one -- i.e. this stays INSIDE CORS -- so a response built
    # here still passes back out through CORS's header-adding logic. Catches
    # anything NotFoundError/ValidationError/PermissionDeniedError (handled
    # below, via the inner ExceptionMiddleware) didn't already catch.
    try:
        return await call_next(request)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        detail = str(exc) if settings.is_development else "Internal server error"
        return JSONResponse(status_code=500, content={"detail": detail})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.exception_handler(NotFoundError)
def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(PermissionDeniedError)
def handle_permission_denied(request: Request, exc: PermissionDeniedError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(clients.router)
app.include_router(projects.router)
app.include_router(project_dashboard.router)
app.include_router(project_workspace.router)
app.include_router(systems.router)
app.include_router(documents.router)
app.include_router(requirements.router)
app.include_router(risk_register.router)
app.include_router(traceability.router)
app.include_router(validation_activities.router)
app.include_router(reports.router)
app.include_router(knowledge_library.router)
app.include_router(administration.router)
app.include_router(users.router)
app.include_router(notifications.router)
app.include_router(settings_routes.router)
