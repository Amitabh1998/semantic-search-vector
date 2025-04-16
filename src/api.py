from superlinked import framework as sl
import os
import urllib.parse

username = urllib.parse.quote_plus("amitabhdas1998")
password = urllib.parse.quote_plus("GdhIC5wuD8pD6SdZ")  # New password
HOST = "cluster0.au2tbgb.mongodb.net"  # New cluster
DB_NAME = "ecommerce_db"
CLUSTER_NAME = "Cluster0"
PROJECT_ID = "67f7e2390bed5f7a93d04c9f"
ADMIN_API_USER = "ogaqxsef"
ADMIN_API_PASSWORD = "03dade6b-67fd-4276-9566-ba958df180ef"

from superlinked_setup import product, product_index, query

source = sl.RestSource(product)
rest_query = sl.RestQuery(sl.RestDescriptor("search"), query)
executor = sl.RestExecutor(
    sources=[source],
    indices=[product_index],
    queries=[rest_query],
    vector_database=sl.MongoDBVectorDatabase(
        HOST,
        DB_NAME,
        CLUSTER_NAME,
        project_id=PROJECT_ID,
        admin_api_user=ADMIN_API_USER,
        admin_api_password=ADMIN_API_PASSWORD,
        username=username,
        password=password
    )
)

print("Executor methods:", dir(executor))
sl.SuperlinkedRegistry.register(executor)

if __name__ == "__main__":
    print("Starting Superlinked server...")
    executor.run()