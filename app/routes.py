from fastapi import APIRouter, HTTPException, Query
from app.models import Product

from app.database import collection
import requests


router = APIRouter()


# /getSingleProduct
@router.get("/getSingleProduct/{product_id}")
def get_single_product(product_id: str):
    product = collection.find_one({"ProductID": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# /getAll
@router.get("/getAll")
def get_all():
    products = list(collection.find({}, {"_id": 0}))
    return products


# /addNew
@router.post("/addNew")
def add_new(product: Product):
    existing = collection.find_one({"ProductID": product.ProductID})
    if existing:
        raise HTTPException(status_code=400, detail="Product with this ID already exists")

    collection.insert_one(product.model_dump())
    return {"message": "Product added successfully"}


# /deleteOne
@router.delete("/deleteOne/{product_id}")
def delete_one(product_id: str):
    result = collection.delete_one({"ProductID": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


# /startsWith
@router.get("/startsWith/{letter}")
def starts_with(letter: str):
    if len(letter) != 1:
        raise HTTPException(status_code=400, detail="Please provide a single letter")

    products = list(
        collection.find(
            {"Name": {"$regex": f"^{letter}", "$options": "i"}},
            {"_id": 0}
        )
    )
    return products


# /paginate
@router.get("/paginate")
def paginate(
    start_id: int = Query(...),
    end_id: int = Query(...),
    page: int = Query(1)
):
    page_size = 10
    skip = (page - 1) * page_size

    products = list(
        collection.find(
            {"ProductID": {"$gte": str(start_id), "$lte": str(end_id)}},
            {"_id": 0}
        )
        .sort("ProductID", 1)
        .skip(skip)
        .limit(page_size)
    )
    return products
# /health api endpoint to check if the service is running or not and return a simple status message. This can be used for monitoring and health checks.
@router.get("/health")
def health():
    return {"status": "ok"}


# /convert
@router.get("/convert/{product_id}")
def convert_price(product_id: str):
    product = collection.find_one({"ProductID": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    usd_price = float(product["UnitPrice"])

    response = requests.get(
        "https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR",
        timeout=10
    )
    response.raise_for_status()
    data = response.json()

    eur_rate = data["rates"]["EUR"]
    eur_price = round(usd_price * eur_rate, 2)

    return {
        "ProductID": product["ProductID"],
        "Name": product["Name"],
        "UnitPriceUSD": usd_price,
        "ExchangeRateUSDtoEUR": eur_rate,
        "UnitPriceEUR": eur_price
    }
    
   
    