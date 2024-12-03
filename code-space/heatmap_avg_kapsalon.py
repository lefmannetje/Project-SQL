import pandas as pd
import folium
from folium.plugins import HeatMap
from matplotlib import colormaps
from matplotlib.colors import to_hex

# Load the data
file_path = "kapsalon_prices.csv"  # Replace with your actual file path
data = pd.read_csv(file_path, sep=';')  # Use ';' as separator

# Ensure latitude and longitude are floats
data['latitude'] = data['latitude'].astype(float)
data['longitude'] = data['longitude'].astype(float)
data['avg_kapsalon'] = data['avg_kapsalon'].astype(float)

# Normalize avg_kapsalon to a 0-1 scale
min_price = data['avg_kapsalon'].min()
max_price = data['avg_kapsalon'].max()
data['color'] = data['avg_kapsalon'].apply(lambda x: (x - min_price) / (max_price - min_price))
data['radius'] = data['avg_kapsalon'].apply(lambda x: (max_price - x) / (max_price - min_price) * 15 + 5)

# Create a base map centered on Belgium
m = folium.Map(location=[50.8503, 4.3517], zoom_start=8)  # Centered on Belgium

# Create a colormap from green (low) to red (high)
cmap = colormaps['RdYlGn'].reversed()

# Add each restaurant as a circle marker
for index, row in data.iterrows():
    # Map normalized value to a color
    color = to_hex(cmap(row['color']))  # Convert RGBA to HEX
    
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=row['radius'],
        color=None,
        fill=True,
        fill_opacity=0.7,
        fill_color=color,
        popup=f"{row['restaurant_name']} - €{row['avg_kapsalon']}"
    ).add_to(m)

# Save the map
m.save("kapsalon_heatmap.html")
print("Heatmap saved as 'kapsalon_heatmap.html'")
