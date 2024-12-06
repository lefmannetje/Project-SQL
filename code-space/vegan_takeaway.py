# Takeaway compare percentage vegan to other
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct paths relative to the current script
takeaway_db = os.path.join(current_dir, "../databases/takeaway.db")

# Connect to Takeaway database
conn = sqlite3.connect(takeaway_db)

# SQL Query
takeaway_percentage_vegan = """
WITH item_counts AS (
    SELECT 
        SUM(CASE WHEN c.name LIKE '%Veg%' OR c.name LIKE '%veg%' THEN 1 ELSE 0 END) AS vegan_count,
        SUM(CASE WHEN c.name NOT LIKE '%Veg%' OR c.name NOT LIKE '%veg%' THEN 1 ELSE 0 END) AS non_vegan_count
    FROM menuItems AS mi
    INNER JOIN categories AS c ON mi.id = c.item_id
    INNER JOIN restaurants AS r ON mi.primarySlug = r.primarySlug
    WHERE mi.price > 0
)
SELECT 
    vegan_count,
    non_vegan_count,
    ROUND((vegan_count * 100.0) / (vegan_count + non_vegan_count), 2) AS vegan_percentage
FROM item_counts;
"""

top10_vegan_cities_max = """
SELECT 
    r.city AS city,
    COUNT(mi.id) AS vegan_dish_count
FROM menuItems AS mi
INNER JOIN restaurants AS r ON mi.primarySlug = r.primarySlug
INNER JOIN categories AS c ON mi.id = c.item_id
WHERE c.name LIKE '%Veg%' OR c.name LIKE '%veg%'
  AND mi.price > 0
GROUP BY r.city
ORDER BY vegan_dish_count DESC
LIMIT 10;
"""

top10_vegan_cities_min = """
SELECT 
    r.city AS city,
    COUNT(mi.id) AS vegan_dish_count
FROM menuItems AS mi
INNER JOIN restaurants AS r ON mi.primarySlug = r.primarySlug
INNER JOIN categories AS c ON mi.id = c.item_id
WHERE c.name LIKE '%Veg%' OR c.name LIKE '%veg%'
  AND mi.price > 0
GROUP BY r.city
ORDER BY vegan_dish_count ASC
LIMIT 10;
"""

# Execute query and fetch results
percentage_result = pd.read_sql_query(takeaway_percentage_vegan, conn)
best_vegan_dishes_by_city = pd.read_sql_query(top10_vegan_cities_max, conn)
worst_vegan_dishes_by_city = pd.read_sql_query(top10_vegan_cities_min, conn)

# Close connection
conn.close()

# Pie chart for percentage vegan vs non-vegan
labels_percentage = ['Vegan', 'Non-Vegan']
sizes_percentage = [
    percentage_result['vegan_count'].iloc[0],
    percentage_result['non_vegan_count'].iloc[0]
]

# Pie chart for top vegan cities
labels_max = best_vegan_dishes_by_city['city']
sizes_max = best_vegan_dishes_by_city['vegan_dish_count']

# Pie chart for bottom vegan cities
labels_min = worst_vegan_dishes_by_city['city']
sizes_min = worst_vegan_dishes_by_city['vegan_dish_count']

# Total vegan dishes
total_vegan_dishes = percentage_result['vegan_count'].iloc[0]

# Plot all pie charts
fig, axs = plt.subplots(1, 3, figsize=(20, 8))

# Pie chart 1: Vegan vs Non-Vegan
total_dishes = sum(sizes_percentage)
axs[0].pie(
    sizes_percentage,
    labels=labels_percentage,
    autopct=lambda p: f'{p:.1f}% ({int(p * total_dishes / 100)})',
    colors=['green', 'red'],
    startangle=140
)
axs[0].set_title(f"Percentage of Vegan vs Non-Vegan Dishes (Total: {total_dishes})")

# Pie chart 2: Top Vegan Cities
total_vegan_top = sum(sizes_max)
axs[1].pie(
    sizes_max,
    labels=labels_max,
    autopct=lambda p: f'{int(p * total_vegan_top / 100)}',
    startangle=140
)
axs[1].set_title(f"Top 10 Cities with Most Vegan Dishes (Total: {total_vegan_dishes})")

# Pie chart 3: Bottom Vegan Cities
total_vegan_bottom = sum(sizes_min)
axs[2].pie(
    sizes_min,
    labels=labels_min,
    autopct=lambda p: f'{int(p * total_vegan_bottom / 100)}',
    startangle=140
)
axs[2].set_title(f"Top 10 Cities with Least Vegan Dishes (Total: {total_vegan_dishes})")

# Save and Show
plt.tight_layout()
plt.savefig("assets/takeaway_vegan_piecharts.png")
plt.show()