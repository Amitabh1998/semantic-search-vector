from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float
from llama_index.core import SQLDatabase
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.llms.openai import OpenAI
import pandas as pd
import os
import re
import logging
from openai import OpenAI as OpenAIClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import openai  # Add this import if not already present

from openai import OpenAI as OpenAIClient  # Avoid conflict with LlamaIndex's OpenAI class

def validate_openai_key(api_key):
    try:
        if not api_key:
            return False, "OPENAI_API_KEY is not set"
        if not api_key.isascii():
            return False, "API key contains non-ASCII characters"
        if not re.match(r"^sk-[a-zA-Z0-9_-]+$", api_key):
            return False, "API key format invalid (expected sk- followed by alphanumeric characters)"

        # Create a client instance using the new SDK style
        client = OpenAIClient(api_key=api_key)

        # Minimal call to validate API key
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )

        logger.info("API key validated successfully")
        return True, "API key is valid"

    except Exception as e:
        logger.error(f"API key validation failed: {e}")
        return False, f"API key validation failed: {str(e)}"


# Initialize FastAPI
app = FastAPI()

# Set up SQLite database
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

# Load data
try:
    df = pd.read_json("data/processed/processed_sample.jsonl", lines=True)
    logger.info(f"Loaded data:\n{df.head()}")
    df.to_sql("products", engine, if_exists="replace", index=False)
except Exception as e:
    logger.error(f"Failed to load data: {e}")
    raise

# Validate and initialize OpenAI
api_key = os.getenv("OPENAI_API_KEY")
is_valid, message = validate_openai_key(api_key)
if not is_valid:
    logger.error(message)
    raise ValueError(message)

try:
    llm = OpenAI(
        temperature=0.1,
        model="gpt-3.5-turbo",
        api_key=api_key
    )
    sql_database = SQLDatabase(engine, include_tables=["products"])
    nl_sql_retriever = NLSQLRetriever(
        sql_database,
        tables=["products"],
        return_raw=False
    )
    logger.info("OpenAI and LlamaIndex initialized successfully")
except Exception as e:
    logger.error(f"Initialization error: {e}")
    raise

# Define request model
# class QueryRequest(BaseModel):
#     natural_query: str = ""
#     limit: int = 3

@app.post("/search")
async def search(query_data: dict):
    try:
        natural_query = query_data.get("natural_query")
        limit = query_data.get("limit", 3)
        logger.info(f"Received query: {natural_query}, limit: {limit}")

        # Validate inputs
        if limit < 1:
            raise HTTPException(status_code=400, detail="Limit must be positive")

        # Handle empty query
        if not natural_query.strip():
            logger.info("Empty query, returning top rows")
            with engine.connect() as conn:
                query = f"SELECT * FROM products LIMIT {limit}"
                df_result = pd.read_sql(query, conn)
            results = df_result[["title", "price", "review_rating"]].rename(
                columns={"review_rating": "rating"}
            ).to_dict(orient="records")
        else:
            # Retrieve using LlamaIndex
            nodes = nl_sql_retriever.retrieve(natural_query)
            results = []
            for node in nodes[:limit]:
                metadata = node.node.metadata
                results.append({
                    "title": metadata.get("title", ""),
                    "price": float(metadata.get("price", 0.0)),
                    "rating": float(metadata.get("review_rating", 0.0))
                })
            logger.info(f"Retrieved {len(results)} results")

        return results
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)