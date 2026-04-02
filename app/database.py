import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

# Load the repository .env file regardless of the current working directory.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
	raise RuntimeError("MONGO_URI is not set")

client = MongoClient(mongo_uri)
db = client["products_db"]
collection = db["products"]