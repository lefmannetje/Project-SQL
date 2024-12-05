import json
import pandas as pd

# Paths to input files
jsonl_file = "postal-codes-belgium.jsonl"
csv_file = "deliveroo_postalcode-distinct.csv"

# Load JSONL data
jsonl_data = []
with open(jsonl_file, "r", encoding="utf-8") as file:
    for line in file:
        jsonl_data.append(json.loads(line))

# Load CSV file
csv_data = pd.read_csv(csv_file)

# Convert JSONL to a DataFrame
jsonl_df = pd.DataFrame(jsonl_data)

# Create a new DataFrame to store the results
results = []

# Match and create rows
for _, row in csv_data.iterrows():
    postal_code = row['postal_code']
    
    # Find matching entry in the JSONL data
    match = jsonl_df[jsonl_df['post_code'] == postal_code]
    
    if not match.empty:
        match = match.iloc[0]  # Get the first match
        sub_municipality = match['sub_municipality_name_dutch']
        municipality = match['municipality_name_dutch']
        
        # Choose sub_municipality if available, otherwise use municipality
        name = sub_municipality if sub_municipality else municipality
        
        # Add the matched row
        results.append({
            'postal_code': postal_code,
            'name': name
        })

# Convert results to a DataFrame
results_df = pd.DataFrame(results)

# Save to a new CSV
results_df.to_csv("output.csv", index=False, encoding="utf-8")
print("Output saved to 'output.csv'")
