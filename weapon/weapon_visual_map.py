import folium
import pandas as pd

df = pd.read_csv('../la_crime_cleaned.csv')

weapons = ["KNIFE WITH BLADE 6INCHES OR LESS", "HAND GUN", "OTHER KNIFE"]
filtered_df = df[df['weapon_description'].isin(weapons)]

crime_counts = filtered_df.groupby(['area_name', 'weapon_description']).agg({
    'ID': 'count',
    'longitude': 'mean',
    'latitude': 'mean'
}).reset_index()
print(crime_counts.head())

m = folium.Map(location=[34.0522, -118.2437], zoom_start=11)

# Define a color for each weapon type
colors = {
    "KNIFE WITH BLADE 6INCHES OR LESS": "green",
    "HAND GUN": "blue",
    "OTHER KNIFE": "red"
}

for _, row in crime_counts.iterrows():
    radius = row['ID'] * 1.5

    color = colors[row['weapon_description']]

    folium.Circle(
        location=[row['longitude'], row['latitude']],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=(f"area_name: {row['area_name']}<br>"
               f"weapon: {row['weapon_description']}<br>"
               f"count: {row['ID']}")
    ).add_to(m)

map_filename = 'LA_Crime_Map_Weapon.html'
m.save(map_filename)
print(f"Map has been saved as {map_filename}")