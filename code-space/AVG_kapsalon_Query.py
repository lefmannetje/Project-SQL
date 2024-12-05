import sqlite3
import pandas as pd

# Paths to your databases
deliveroo_db_path = "C:\\repos\Project-SQL\\databases\\deliveroo.db"
ubereats_db_path = "C:\\repos\Project-SQL\\databases\\ubereats.db"
takeaway_db_path = "C:\\repos\Project-SQL\\databases\\takeaway.db"

# Connect to the Deliveroo database
conn = sqlite3.connect(deliveroo_db_path)

# Attach the other databases
conn.execute(f"ATTACH DATABASE '{ubereats_db_path}' AS ubereats_db;")
conn.execute(f"ATTACH DATABASE '{takeaway_db_path}' AS takeaway_db;")

# Check attached databases
cursor = conn.cursor()  # Initialize the cursor
cursor.execute("PRAGMA database_list;")
print("Attached Databases:")
for row in cursor.fetchall():
    print(row)

# Query to execute
query = """
SELECT 
    'Deliveroo' AS company,    
    'Kapsalon' AS menu_item_name,
    r.name AS restaurant_name,
    r.latitude AS latitude,
    r.longitude AS longitude,
    ROUND(AVG(m.price), 2) AS avg_kapsalon
FROM menu_items AS m
INNER JOIN restaurants AS r ON m.restaurant_id = r.id
WHERE m.name LIKE '%kapsalon%' AND m.price <> 0 AND m.price > 0
GROUP BY r.id, r.name, r.latitude, r.longitude, r.address, r.postal_code

UNION ALL

SELECT 
    'Uber Eats' AS company,    
    'Kapsalon' AS menu_item_name,
    r.title AS restaurant_name,
    r.location__latitude AS latitude,
    r.location__longitude AS longitude,
    ROUND(AVG(m.price), 2) AS avg_kapsalon
FROM ubereats_db.menu_items AS m
INNER JOIN ubereats_db.restaurants AS r ON m.restaurant_id = r.id
WHERE m.name LIKE '%kapsalon%' AND m.price <> 0 AND m.price > 0
GROUP BY r.id, r.title, r.location__latitude, r.location__longitude, r.location__street_address, r.location__postal_code

UNION ALL

SELECT 
    'Takeaway' AS company,    
    'Kapsalon' AS menu_item_name,
    r.name AS restaurant_name,
    r.latitude AS latitude,
    r.longitude AS longitude,
    ROUND(AVG(m.price), 2) AS avg_kapsalon
FROM takeaway_db.menuItems AS m
INNER JOIN takeaway_db.restaurants AS r ON m.primarySlug = r.primarySlug
WHERE m.name LIKE '%kapsalon%' AND m.price <> 0
GROUP BY r.primarySlug, r.name, r.latitude, r.longitude, r.address, r.city
ORDER BY avg_kapsalon;
"""

# Execute the query
cursor = conn.cursor()
cursor.execute(query)

# Fetch results
columns = [description[0] for description in cursor.description]
results = cursor.fetchall()

# Convert to Pandas DataFrame for better readability
df = pd.DataFrame(results, columns=columns)

# Close the connection
conn.close()

# Output the results
print(df)

# Optionally save to CSV
df.to_csv("kapsalon_prices.csv", index=False, sep=';')
df.to_excel("kapsalon_prices.xlsx", index=False)