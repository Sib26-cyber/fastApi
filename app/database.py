from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:sibeil123@cluster0.p3ovyvo.mongodb.net/?appName=Cluster0")
db = client["products_db"]
collection = db["products"]