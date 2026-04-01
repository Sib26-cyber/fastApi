from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Products API")

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Products API is running"}