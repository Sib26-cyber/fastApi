import os
from pathlib import Path

from pymongo import MongoClient

try:
	from dotenv import load_dotenv
except ImportError:
	load_dotenv = None

# Load the repository .env file regardless of the current working directory.
if load_dotenv is not None:
	load_dotenv(Path(__file__).resolve().parent.parent / ".env")

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
	raise RuntimeError("MONGO_URI is not set")

client = MongoClient(mongo_uri)
db = client["products_db"]
collection = db["products"]