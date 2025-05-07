from pymongo import MongoClient
import os

# Use the service name 'mongo' as the host when running inside Docker
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")

client = MongoClient(MONGO_URI)
db = client["code_analysis"]

codebase_files = db["codebase_files"]
chunks = db["chunks"]
analysis_results = db["analysis_results"]
