import pandas as pd
import json
import os

# Load raw dataset
def load_data(file_path="data/raw/sample.jsonl"):
    data = [json.loads(line) for line in open(file_path, 'r')]
    df = pd.DataFrame(data)
    return df[['asin', 'type', 'title', 'description', 'stars', 'ratings', 'price']]

# Parse and clean data
def parse_review_rating(stars):
    if pd.isna(stars):
        return -1.0
    try:
        return float(stars.split()[0].replace(',', '.'))
    except:
        return -1.0

def parse_review_count(ratings):
    if pd.isna(ratings):
        return 0
    try:
        return int(ratings.split()[0].replace(',', ''))
    except:
        return 0

def parse_price(price):
    if pd.isna(price) or not isinstance(price, str):
        return 0.0
    try:
        return float(price.replace('$', '').replace(',', ''))
    except:
        return 0.0

def preprocess_data(df):
    # Work with a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    df['review_rating'] = df['stars'].apply(parse_review_rating)
    df['review_count'] = df['ratings'].apply(parse_review_count)
    df['price'] = df['price'].apply(parse_price)
    
    # Remove outliers
    df = df[(df['price'] >= 0) & (df['price'] <= 1000)]
    
    # Fill NaNs using .loc
    df.loc[:, 'title'] = df['title'].fillna('')
    df.loc[:, 'description'] = df['description'].fillna('')
    
    return df[['asin', 'type', 'title', 'description', 'review_rating', 'review_count', 'price']]

# Save processed data
def save_processed_data(df, output_path="data/processed/processed_sample.jsonl"):
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_json(output_path, orient='records', lines=True)

if __name__ == "__main__":
    df = load_data()
    processed_df = preprocess_data(df)
    save_processed_data(processed_df)