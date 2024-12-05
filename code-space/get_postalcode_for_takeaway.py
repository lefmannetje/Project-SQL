import pandas as pd
from opencage.geocoder import OpenCageGeocode
import os

# Your OpenCage API key (sign up at https://opencagedata.com/ for a free key)
API_KEY = 'd5a3fc36ce1f4f9b9631c01cef16aebf'
geocoder = OpenCageGeocode(API_KEY)

# Load the CSV
file_path = "databases\\takeaway_postalcode-distinct.csv"  # Replace with your file path

# Check if the file exists
if os.path.exists(file_path):
    print(f"File found at: {file_path}")
else:
    print(f"File not found at: {file_path}")
    
data = pd.read_csv(file_path, sep=';', encoding='ISO-8859-1')
print(data.head())  # Verify the structure

# Function to get postal code based on city
def get_postal_code(city):
    try:
        results = geocoder.geocode(city)
        if results:
            # Extract postal code from the response
            for component in results[0]['components']:
                if 'postcode' in results[0]['components']:
                    return results[0]['components']['postcode']
    except Exception as e:
        print(f"Error for city {city}: {e}")
    return None

# Apply function to the city column
data['postal_code'] = data['city'].apply(get_postal_code)

# Save updated data to a new CSV
data.to_csv("updated_with_postal_codes.csv", sep=';', index=False)
print("Updated CSV saved as 'updated_with_postal_codes.csv'")
