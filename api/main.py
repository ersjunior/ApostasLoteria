from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import get_settings
from api.exceptions import register_exception_handlers
from api.limiter import limiter
from api.logging_config import configure_logging
from api.routes import combinations, dataset, forecast, health, lotteries, verify

configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Loterias Analyzer API",
    description=(
        "API REST multi-loteria para verificação, combinações inéditas e dataset (SQLite). "
        "Rotas canônicas em `/lotteries/{lottery_key}/...`; "
        "`/verify/`, `/combinations/`, `/forecast/` e `/dataset/` são aliases da Mega-Sena."
    ),
    version="0.2.0",
)
app.state.limiter = limiter

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.effective_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH"}:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_body_bytes:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": f"Payload excede o limite de {settings.max_body_bytes} bytes.",
                    "code": "PAYLOAD_TOO_LARGE",
                },
            )
    return await call_next(request)


app.include_router(health.router)
app.include_router(lotteries.router)

# Canônico: /lotteries/{lottery_key}/...
app.include_router(verify.router, prefix="/lotteries")
app.include_router(combinations.router, prefix="/lotteries")
app.include_router(forecast.router, prefix="/lotteries")
app.include_router(dataset.router, prefix="/lotteries")

# Aliases legados (= megasena)
app.include_router(verify.legacy_router, prefix="/verify")
app.include_router(combinations.legacy_router, prefix="/combinations")
app.include_router(forecast.legacy_router, prefix="/forecast")
app.include_router(dataset.legacy_router, prefix="/dataset")

logger.info(
    "API iniciada (env=%s, cors_origins=%s, log_level=%s)",
    settings.environment,
    settings.effective_cors_origins or "[]",
    settings.log_level,
)
