# import os
# from superlinked import framework as sl
# from pymongo import MongoClient
# import json

# # Connection details
# username = "amitabhdas1998"
# password = "GdhIC5wuD8pD6SdZ"
# MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.au2tbgb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# # MongoDB setup
# client = MongoClient(MONGO_URI)
# db = client.ecommerce_db
# collection = db.products

# # Clear existing data (optional)
# collection.drop()

# # Load and ingest sample data
# with open("data/processed/processed_sample.jsonl", "r") as f:
#     for line in f:
#         doc = json.loads(line)
#         collection.insert_one(doc)

# # Superlinked schema
# class Product(sl.Schema):
#     id: sl.IdField
#     type: sl.String
#     title: sl.String
#     description: sl.String
#     review_rating: sl.Float
#     price: sl.Float

# product = Product()

# # Index and query setup
# title_space = sl.TextSimilaritySpace(
#     text=product.title,
#     model="sentence-transformers/all-MiniLM-L6-v2"
# )
# description_space = sl.TextSimilaritySpace(
#     text=product.description,
#     model="sentence-transformers/all-MiniLM-L6-v2"
# )
# product_index = sl.Index([title_space, description_space])

# query = (
#     sl.Query(product_index)
#     .find(product)
#     .similar(title_space, "books")
#     .filter(product.price < 100)
#     .filter(product.rating > 4)
# )

# print("Setup complete. Database and index configured.")

from superlinked import framework as sl
from pymongo import MongoClient
import os
import pandas as pd
import urllib.parse

# Encode MongoDB credentials
# Connection details
username = "amitabhdas1998"
password = "GdhIC5wuD8pD6SdZ"
MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.au2tbgb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["ecommerce_db"]
collection = db.default

class ProductSchema(sl.Schema):
    id: sl.IdField
    type: sl.String
    title: sl.String
    description: sl.String
    review_rating: sl.Float
    price: sl.Float

product = ProductSchema()

title_space = sl.TextSimilaritySpace(text=product.title, model="sentence-transformers/all-MiniLM-L6-v2")
description_space = sl.TextSimilaritySpace(text=product.description, model="sentence-transformers/all-MiniLM-L6-v2")
review_space = sl.NumberSpace(number=product.review_rating, min_value=-1.0, max_value=5.0, mode=sl.Mode.MAXIMUM)
price_space = sl.NumberSpace(number=product.price, min_value=0.0, max_value=1000.0, mode=sl.Mode.MINIMUM)

product_index = sl.Index(spaces=[title_space, description_space, review_space, price_space])

def load_data_to_mongo(df):
    collection = db["default"]
    collection.drop()
    records = df.to_dict(orient="records")
    for record in records:
        record["id"] = record.pop("asin")
    collection.insert_many(records)

query = (
    sl.Query(product_index)
    .find(product)
    .similar(title_space.text, sl.Param("query_title", description="Text for title search"))
    .similar(description_space.text, sl.Param("query_description", description="Text for description search"))
    .filter(product.price <= sl.Param("query_price", description="Price to minimize"))
    .filter(product.review_rating >= sl.Param("query_review_rating", description="Rating to maximize"))
    .filter(product.type == sl.Param("filter_by_type", description="Filter by product type"))
    .with_natural_query(sl.Param("natural_query"), sl.OpenAIClientConfig(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo"))
    .select_all()
)


if __name__ == "__main__":
    df = pd.read_json("data/processed/processed_sample.jsonl", lines=True)
    load_data_to_mongo(df)
    print("Data indexed in MongoDB!")