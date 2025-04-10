from superlinked import framework as sl
from fastapi import FastAPI
import uvicorn
import os
import urllib.parse

username = urllib.parse.quote_plus("amitabhdas1998")
password = urllib.parse.quote_plus("Harekrishna@123")
MONGO_URI = os.getenv("MONGO_URI", f"mongodb+srv://{username}:{password}@cluster0.luwj61d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
PROJECT_ID = "67f1800dafdd5446211e7e2e"
ADMIN_API_USER = "your_public_key"
ADMIN_API_PASSWORD = "your_private_key"

from superlinked_setup import product, product_index, query

app = FastAPI()

source = sl.RestSource(product)
rest_query = sl.RestQuery(sl.RestDescriptor("search"), query)
executor = sl.RestExecutor(
    sources=[source],
    indices=[product_index],
    queries=[rest_query],
    vector_database=sl.MongoDBVectorDatabase(
        MONGO_URI,
        "ecommerce_db",
        "products",
        project_id=PROJECT_ID,
        admin_api_user=ADMIN_API_USER,
        admin_api_password=ADMIN_API_PASSWORD
    )
)

sl.SuperlinkedRegistry.register(executor)

@app.post("/search")
async def search(query_data: dict):
    natural_query = query_data.get("natural_query")
    limit = query_data.get("limit", 3)
    # Try 'run' instead of 'execute_query'
    results = executor.run(
        rest_query,
        params={"natural_query": natural_query, "limit": limit}
    )
    return [{"title": r.title, "price": r.price, "rating": r.review_rating} for r in results]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)