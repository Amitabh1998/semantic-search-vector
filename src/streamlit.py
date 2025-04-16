import streamlit as st
import requests

# Define API endpoints
SUPERLINKED_API = "http://localhost:8080/search"
TEXT_TO_SQL_API = "http://localhost:8081/search"

# Streamlit UI setup
st.title("E-commerce Search Comparison")
st.write("Compare Superlinked Semantic Search vs. Text-to-SQL Search")

# Input fields
query = st.text_input(
    "Enter your search query",
    "books with a price lower than 100 and a rating bigger than 4"
)
limit = st.number_input("Number of results", min_value=1, value=3)

# Search button
if st.button("Search"):
    # Superlinked API request
    try:
        superlinked_response = requests.post(
            SUPERLINKED_API,
            json={"natural_query": query, "limit": limit}
        )
        superlinked_response.raise_for_status()
        superlinked_results = superlinked_response.json()
    except requests.RequestException as e:
        superlinked_results = []
        st.error(f"Superlinked API error: {e}")

    # Text-to-SQL API request
    try:
        sql_response = requests.post(
            TEXT_TO_SQL_API,
            json={"natural_query": query, "limit": limit}
        )
        sql_response.raise_for_status()
        sql_results = sql_response.json()
    except requests.RequestException as e:
        sql_results = []
        st.error(f"Text-to-SQL API error: {e}")

    # Display results in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Superlinked Results")
        if superlinked_results:
            for result in superlinked_results:
                st.write(f"**{result['title']}** - Price: ${result['price']} - Rating: {result['rating']}")
        else:
            st.write("No results or API unavailable.")
    
    with col2:
        st.subheader("Text-to-SQL Results")
        if sql_results:
            for result in sql_results:
                st.write(f"**{result['title']}** - Price: ${result['price']} - Rating: {result['rating']}")
        else:
            st.write("No results or API unavailable.")