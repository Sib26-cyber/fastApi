from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from starlette.requests import Request
from starlette.responses import Response
from app.routes import router

app = FastAPI(title="Products API")

REQUEST_COUNT = Counter("request_count", "Total API Requests")

@app.middleware("http")
async def count_requests(request: Request, call_next):
    REQUEST_COUNT.inc()
    response = await call_next(request)
    return response

app.include_router(router)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.get("/")
def home():
    return {"message": "Products API is running"}