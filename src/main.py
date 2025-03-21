from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from httpx import AsyncClient
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.middleware.sessions import SessionMiddleware

from src.api.v1.auth import auth_router
from src.api.v1.me import me_router
from src.api.v1.oauth import oauth_router
from src.api.v1.permission import perm_router
from src.api.v1.roles import roles_router
from src.core import http_client
from src.core.config import settings
from src.core.exception_handlers import exception_handlers
from src.db import postgres, redis


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis.redis = Redis(host=settings.redis.redis_host, port=settings.redis.redis_port)
    postgres.engine = create_async_engine(settings.db.db_url, echo=False)
    postgres.async_session_maker = async_sessionmaker(bind=postgres.engine, expire_on_commit=False, class_=AsyncSession)
    http_client.http_client = AsyncClient()

    yield

    await http_client.http_client.close()
    await redis.redis.close()


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(JaegerExporter(agent_host_name=settings.jaeger.host, agent_port=settings.jaeger.port))
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


configure_tracer()
app = FastAPI(
    title=settings.service.project_name,
    docs_url="/api/openapi/",
    openapi_url="/api/openapi.json/",
    default_response_class=ORJSONResponse,
    exception_handlers=exception_handlers,
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=settings.oauth.secret_key)


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if request_id is None:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    return response


FastAPIInstrumentor.instrument_app(app=app)


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(me_router, prefix="/api/v1/me", tags=["me"])
app.include_router(roles_router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(perm_router, prefix="/api/v1/permissions", tags=["permissions"])
app.include_router(oauth_router, prefix="/api/v1/oauth", tags=["oauth"])

if __name__ == "__main__":
    app()
