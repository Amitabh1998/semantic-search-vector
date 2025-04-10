from fastapi import FastAPI
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float
from llama_index.core import SQLDatabase
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.llms.openai import OpenAI
import pandas as pd
import os

engine = create_engine("sqlite:///:memory:")
metadata = MetaData()
product_table = Table(
    "products",
    metadata,
    Column("asin", String, primary_key=True),
    Column("type", String),
    Column("title", String),
    Column("description", String),
    Column("review_rating", Float),
    Column("price", Float),
)
metadata.create_all(engine)

df = pd.read_json("data/processed/processed_sample.jsonl", lines=True)
df.to_sql("products", engine, if_exists="replace", index=False)

llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
sql_database = SQLDatabase(engine, include_tables=["products"])
nl_sql_retriever = NLSQLRetriever(sql_database, tables=["products"], return_raw=False)

app = FastAPI()

@app.post("/search")
async def search(query_data: dict):
    natural_query = query_data.get("natural_query")
    limit = query_data.get("limit", 3)
    results = nl_sql_retriever.retrieve(natural_query)[:limit]
    return [{"title": r.title, "price": r.price, "rating": r.review_rating} for r in results]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)