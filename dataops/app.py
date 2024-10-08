# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from functools import partial

from common import configure_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import ValidationError

from dataops.components.archive_preview import archive_preview_router
from dataops.components.exceptions import ServiceException
from dataops.components.exceptions import ServiceValidationError
from dataops.components.health import health_router
from dataops.components.resource_lock import resource_lock_router
from dataops.components.resource_operations import resource_ops_router
from dataops.components.task_dispatch import task_router
from dataops.components.task_stream import task_stream_router
from dataops.config import Settings
from dataops.config import get_settings
from dataops.dependencies import get_redis
from dataops.dependencies.db import get_db_engine


def create_app() -> FastAPI:
    """Initialize and configure the application."""

    settings = get_settings()

    app = FastAPI(
        title='Dataops Service',
        description='Dataops',
        docs_url='/v1/api-doc',
        version=settings.VERSION,
    )

    setup_logging(settings)
    setup_routers(app)
    setup_middlewares(app)
    setup_exception_handlers(app)
    setup_dependencies(app, settings)

    return app


def setup_logging(settings: Settings) -> None:
    """Configure the application logging."""

    configure_logging(settings.LOGGING_LEVEL, settings.LOGGING_FORMAT)


def setup_routers(app: FastAPI) -> None:
    """Configure the application routers."""

    app.include_router(health_router, prefix='/v1')
    app.include_router(task_router, prefix='/v1')
    app.include_router(task_stream_router, prefix='/v1')
    app.include_router(resource_ops_router, prefix='/v1')
    app.include_router(archive_preview_router, prefix='/v1')
    app.include_router(resource_lock_router, prefix='/v2')


def setup_dependencies(app: FastAPI, settings: Settings) -> None:
    """Perform dependencies setup/teardown at the application startup/shutdown events."""

    app.add_event_handler('startup', partial(startup_event, app, settings))


async def startup_event(app: FastAPI, settings: Settings) -> None:
    """Initialise dependencies at the application startup event."""
    await get_redis(settings)
    if settings.OPEN_TELEMETRY_ENABLED:
        await setup_tracing(app, settings)


def setup_middlewares(app: FastAPI) -> None:
    """Configure the application middlewares."""

    app.add_middleware(
        CORSMiddleware,
        allow_origins='*',
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure the application exception handlers."""

    app.add_exception_handler(ServiceException, service_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)


def service_exception_handler(request: Request, exception: ServiceException) -> JSONResponse:
    """Return the default response structure for service exceptions."""

    return JSONResponse(status_code=exception.status, content={'error': exception.dict()})


def global_exception_handler(request: Request, exception: Exception) -> JSONResponse:
    """Return the default response structure for all unhandled exceptions."""

    return JSONResponse(status_code=500, content={'error_msg': 'Internal Server Error'})


def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return service_exception_handler(request, ServiceValidationError(errors=exc.errors()))


async def setup_tracing(app: FastAPI, settings: Settings) -> None:
    """Instrument the application with OpenTelemetry tracing."""
    tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: settings.APP_NAME}))
    trace.set_tracer_provider(tracer_provider)

    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
    LoggingInstrumentor().instrument()

    db = await get_db_engine()
    SQLAlchemyInstrumentor().instrument(engine=db.sync_engine, service=settings.APP_NAME)

    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.OPEN_TELEMETRY_HOST, agent_port=settings.OPEN_TELEMETRY_PORT
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
