import redis  # Redis library for connecting to a Redis server
import os 
from dotenv import load_dotenv  
import json  

# Load environment variables from a .env file
load_dotenv()

# Establish a connection to the Redis server
# Redis is an in-memory data store used here for caching purposes
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "localhost"),  # Host of the Redis server (default to localhost)
    port=6379,  # Default Redis port
    db=0,  # Default database index (Redis has multiple databases, 0 is the default one)
    decode_responses=True  # Automatically decode responses from Redis as strings
)

# Function to cache the result of a code analysis in Redis
def cache_result(chunk_id, result):
    """
    Caches the analysis result for a given code chunk.

    Args:
        chunk_id (str): The identifier for the code chunk.
        result (dict): The analysis result in JSON format (a dictionary).
    """
    # Store the result in Redis, with the key being "analysis:{chunk_id}" and the value being the JSON-encoded result
    redis_client.set(f"analysis:{chunk_id}", json.dumps(result))

# Function to retrieve the cached result from Redis
def get_cached_result(chunk_id):
    """
    Retrieves the cached analysis result for a given code chunk.

    Args:
        chunk_id (str): The identifier for the code chunk.

    Returns:
        dict or None: The cached analysis result (as a dictionary), or None if no cached result exists.
    """
    # Retrieve the cached result from Redis using the key "analysis:{chunk_id}"
    cached = redis_client.get(f"analysis:{chunk_id}")
    
    # If a result is found, parse the JSON and return it; otherwise, return None
    return json.loads(cached) if cached else None
