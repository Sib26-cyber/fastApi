import time

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response

from app.routes import router

app = FastAPI(
    title="Products API",
    description="Product service with Prometheus monitoring and health checks.",
)

REQUEST_COUNT = Counter(
    "request_count",
    "Total API Requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "API request latency in seconds",
    ["method", "path"],
)
IN_PROGRESS = Gauge(
    "requests_in_progress",
    "Number of in-progress API requests",
    ["method", "path"],
)


@app.middleware("http")
async def count_requests(request: Request, call_next):
    method = request.method
    path = request.url.path
    start_time = time.perf_counter()
    status_code = 500

    IN_PROGRESS.labels(method=method, path=path).inc()
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration = time.perf_counter() - start_time
        REQUEST_COUNT.labels(method=method, path=path, status=str(status_code)).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
        IN_PROGRESS.labels(method=method, path=path).dec()


app.include_router(router)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def home():
    return {"message": "Products API is running"}