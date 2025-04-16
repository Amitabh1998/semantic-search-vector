import os
import pandas as pd

file_path = "data/processed/processed_sample.jsonl"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

with open(file_path, "r") as f:
    first_line = f.readline()
    if not first_line.strip():
        raise ValueError(f"File {file_path} is empty or has no valid JSON lines.")

df = pd.read_json(file_path, lines=True)
print(df.head())