import json
import pandas as pd
import os

# Paths to input files
jsonl_file = os.path.join(os.path.dirname(__file__), 'postal-codes-belgium.jsonl')
csv_file = "takeaway-distinct-cities.csv"

# Load JSONL data into a list
jsonl_data = []
with open(jsonl_file, "r", encoding="utf-8") as file:
    for line in file:
        jsonl_data.append(json.loads(line))

# Convert JSONL data to a DataFrame
jsonl_df = pd.DataFrame(jsonl_data)

# Load the CSV with city names
city_data = pd.read_csv(csv_file)

# Function to find postal code based on city
def find_postal_code(city_name):
    match = jsonl_df[jsonl_df['municipality_name_dutch'] == city_name]
    if not match.empty:
        return match.iloc[0]['post_code']  # Return the first match's postal code
    return None  # If no match, return None

# Apply the function to the city column
city_data['postal_code'] = city_data['city'].apply(find_postal_code)
# Convert postal_code to integer
city_data['postal_code'] = city_data['postal_code'].astype('Int64')  # Int64 handles NaN values if present


# Save the updated data to a new CSV
city_data.to_csv("updated_with_postal_codes.csv", index=False, encoding="utf-8")
print("Updated CSV saved as 'updated_with_postal_codes.csv'")
