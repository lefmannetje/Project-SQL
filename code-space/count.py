import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct paths relative to the current script
takeaway_db = os.path.join(current_dir, "../databases/takeaway.db")
deliveroo_db = os.path.join(current_dir, "../databases/deliveroo.db")
ubereats_db = os.path.join(current_dir, "../databases/ubereats.db")

# Connect to the Deliveroo database and attach others
conn = sqlite3.connect(deliveroo_db)
conn.execute(f"ATTACH DATABASE '{ubereats_db}' AS ubereats_db;")
conn.execute(f"ATTACH DATABASE '{takeaway_db}' AS takeaway_db;")

# Query the combined data
query1 = """
SELECT platform, COUNT(*) AS total_restaurants
FROM (
    SELECT 'Deliveroo' AS platform, name, city
    FROM restaurants
    UNION ALL
    SELECT 'UberEats' AS platform, name, city
    FROM ubereats_db.restaurants
    UNION ALL
    SELECT 'Takeaway' AS platform, name, city
    FROM takeaway_db.restaurants
)
GROUP BY platform;
"""

# query to find the cities where restaurant names occur in all three databases and count how many such restaurants exist for each city
query2 = """
SELECT d.city, COUNT(d.name) AS common_restaurant_count
FROM restaurants AS d
INNER JOIN ubereats_db.restaurants AS u 
    ON d.name = u.name AND d.city = u.city
INNER JOIN takeaway_db.restaurants AS t 
    ON d.name = t.name AND d.city = t.city
GROUP BY d.city
ORDER BY common_restaurant_count DESC;
"""

# Count Restaurants > 100 by City Per Platform
query3="""
SELECT 'Deliveroo' AS platform, city, COUNT(*) AS total_restaurants
FROM restaurants
GROUP BY city
HAVING COUNT(*) > 99
UNION ALL
SELECT 'UberEats' AS platform, city, COUNT(*) AS total_restaurants
FROM ubereats_db.restaurants
GROUP BY city
HAVING COUNT(*) > 99
UNION ALL
SELECT 'Takeaway' AS platform, city, COUNT(*) AS total_restaurants
FROM takeaway_db.restaurants
GROUP BY city
HAVING COUNT(*) > 99
ORDER BY total_restaurants DESC, city;
"""

query4_deliveroo="""
-- Deliveroo-exclusive restaurants
SELECT d.name AS restaurant_name, 'Deliveroo' AS platform
FROM restaurants AS d
WHERE NOT EXISTS (
    SELECT 1
    FROM ubereats_db.restaurants AS u
    WHERE u.name = d.name
)
AND NOT EXISTS (
    SELECT 1
    FROM takeaway_db.restaurants AS t
    WHERE t.name = d.name
);

"""

query4_ubereats="""
-- Uber Eats-exclusive restaurants
SELECT u.name AS restaurant_name, 'Ubereats' AS platform
FROM ubereats_db.restaurants AS u
WHERE NOT EXISTS (
    SELECT 1
    FROM restaurants AS d
    WHERE d.name = u.name
)
AND NOT EXISTS (
    SELECT 1
    FROM takeaway_db.restaurants AS t
    WHERE t.name = u.name
);
"""

query4_takeaway="""
-- TakeAway-exclusive restaurants
SELECT t.name AS restaurant_name, 'Takeaway' AS platform
FROM takeaway_db.restaurants AS t
WHERE NOT EXISTS (
    SELECT 1
    FROM restaurants AS d
    WHERE d.name = t.name
)
AND NOT EXISTS (
    SELECT 1
    FROM ubereats_db.restaurants AS u
    WHERE u.name = t.name
);
"""

# 1 Execute the query and load into pandas
restaurants_count = pd.read_sql_query(query1, conn)

# 2 Load the data into a Pandas DataFrame
restaurants_overlapping_3times = pd.read_sql_query(query2, conn)

# 3 Restaurants by City Per Platform
restaurants_by_city_per_platform = pd.read_sql_query(query3, conn)

# 4 Restaurants Exclusive to a Single Platform:
restaurant_excl_deliveroo = pd.read_sql_query(query4_deliveroo, conn)

restaurant_excl_ubereats =  pd.read_sql_query(query4_ubereats, conn)

restaurant_excl_takeaway =  pd.read_sql_query(query4_takeaway, conn)

# Close the connection
conn.close()

print("Restaurants on all 3 Platforms:")
print(restaurants_overlapping_3times)

""" print out results
# Print the results
print(restaurants_count)

print("Restaurants on all 3 Platforms:")
print(restaurants_overlapping_3times)

print("Restaurants by City Per Platform:")
print(restaurants_by_city_per_platform)

exclusive_count_deliveroo = len(restaurant_excl_deliveroo)
exclusive_count_ubereats = len(restaurant_excl_ubereats)
exclusive_count_takeaway = len(restaurant_excl_takeaway)

print(f"Number of exclusive Deliveroo restaurants: {exclusive_count_deliveroo}")
print(f"Number of exclusive Ubereats restaurants: {exclusive_count_ubereats}")
print(f"Number of exclusive Takeaway restaurants: {exclusive_count_takeaway}")
 """

# Extract total restaurants dynamically
platforms = restaurants_count['platform'].tolist()
total_restaurants = restaurants_count['total_restaurants'].tolist()

# Extract exclusive restaurants dynamically
exclusive_restaurants = [
    len(restaurant_excl_deliveroo),
    len(restaurant_excl_takeaway),
    len(restaurant_excl_ubereats)
]

# Calculate shared restaurants dynamically
shared_restaurants = [t - e for t, e in zip(total_restaurants, exclusive_restaurants)]

# Bar Chart Design
fig, ax = plt.subplots(figsize=(8, 6))

bar_width = 0.5
x = range(len(platforms))

# Plot shared restaurants (bottom of bars)
ax.bar(x, shared_restaurants, bar_width, label='Shared Restaurants', color='skyblue')

# Plot exclusive restaurants (top of bars)
ax.bar(x, exclusive_restaurants, bar_width, bottom=shared_restaurants, label='Exclusive Restaurants', color='orange')

# Add labels to bars
for i in range(len(platforms)):
    ax.text(i, total_restaurants[i] + 50, f"{total_restaurants[i]}/{exclusive_restaurants[i]}", 
            ha='center', va='bottom', fontsize=10)

# Add titles and labels
ax.set_title("Total Restaurants with Exclusive Counts", fontsize=14)
ax.set_xlabel("Platform", fontsize=12)
ax.set_ylabel("Number of Restaurants", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(platforms)
ax.legend()

# Display the chart
plt.tight_layout()
plt.show()


# Extract data
platforms = restaurants_by_city_per_platform['platform']
cities = restaurants_by_city_per_platform['city']
total_restaurants = restaurants_by_city_per_platform['total_restaurants']

# Pivot data to structure it for grouped bars
pivot_data = restaurants_by_city_per_platform.pivot(index='city', columns='platform', values='total_restaurants').fillna(0)

# Define the platforms and colors
platform_order = ['UberEats', 'Deliveroo', 'Takeaway']  # Ensure consistent order
colors = {'UberEats': 'green', 'Deliveroo': 'lightblue', 'Takeaway': 'orange'}

# Create the bar chart
fig, ax = plt.subplots(figsize=(12, 8))
bar_width = 0.25
x_positions = np.arange(len(pivot_data.index))  # Initial positions for cities

# Loop through cities and dynamically place bars
for city_idx, city in enumerate(pivot_data.index):
    # Dynamically select platforms with non-zero data
    platforms_present = [platform for platform in platform_order if pivot_data.loc[city, platform] > 0]
    num_platforms = len(platforms_present)
    
    # Dynamically position bars for the current city
    for i, platform in enumerate(platforms_present):
        ax.bar(
            x_positions[city_idx] + (i - num_platforms / 2) * bar_width,  # Center the bars for the city
            pivot_data.loc[city, platform],  # Height of the bar
            bar_width,
            label=platform if city_idx == 0 else None,  # Add label only once for the legend
            color=colors[platform]
        )

# Add dotted horizontal lines every 100 units
ax.yaxis.grid(True, which='major', linestyle='--', linewidth=0.5, color='gray')
ax.set_yticks(range(0, int(pivot_data.max().max()) + 100, 100))  # Set ticks at intervals of 100

# Add labels and legend
ax.set_title("Number of Restaurants by Platform and City > 100", fontsize=14)
ax.set_xlabel("Cities", fontsize=12)
ax.set_ylabel("Number of Restaurants", fontsize=12)
ax.set_xticks(x_positions)
ax.set_xticklabels(pivot_data.index, rotation=45, ha='right')
ax.legend()

# Display the chart
plt.tight_layout()
plt.show()

# Extract data
cities = restaurants_overlapping_3times['city']
common_counts = restaurants_overlapping_3times['common_restaurant_count']

# Create a horizontal bar chart
fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(cities, common_counts, color='skyblue')

# Add labels and title
ax.set_xlabel("Number of Overlapping Restaurants", fontsize=12)
ax.set_ylabel("City", fontsize=12)
ax.set_title("Overlapping Restaurants Across 3 Platforms by City", fontsize=14)

# Add values next to the bars
for i in range(len(common_counts)):
    ax.text(common_counts[i] + 0.5, i, str(common_counts[i]), va='center', fontsize=10)

# Display the chart
plt.tight_layout()
plt.show()

