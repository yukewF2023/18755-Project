# %%
import pandas as pd
import networkx as nx

# %%
data = pd.read_csv('../la_crime_cleaned.csv')

# Filter out invalid 'victim_sex' values
valid_sexes = {'Male', 'Female'}
la_crime_sample = data[data['victim_sex'].isin(valid_sexes)]
la_crime_sample = la_crime_sample[la_crime_sample['victim_age'] <= 100]

# Categorize 'victim_age' into different age groups
def categorize_age(age):
    if age <= 12:
        return 'Child'
    elif age <= 17:
        return 'Teenager'
    elif age <= 29:
        return 'Young Adult'
    elif age <= 59:
        return 'Adult'
    else:
        return 'Senior'

la_crime_sample['age_group'] = la_crime_sample['victim_age'].apply(categorize_age)
G = nx.Graph()

# Add nodes and edges
for index, row in la_crime_sample.iterrows():
    age_group_node = f"Age Group {row['age_group']}"
    area_node = f"Area {row['area_name']}"
    G.add_node(age_group_node, type='age_group')
    G.add_node(area_node, type='area')
    G.add_edge(age_group_node, area_node, weight=G.get_edge_data(age_group_node, area_node, default={'weight': 0})['weight'] + 1)

nx.write_gexf(G, 'la_crime_network_age_groups.gexf')


# %%
# Degree Centrality
degree_centrality = nx.degree_centrality(G)
sorted_degree_centrality = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
for node, centrality in sorted_degree_centrality[:5]:
    print(f"Node: {node}, Degree Centrality: {centrality}")


# %%
# Edge Weights
edge_weights = [(u, v, d['weight']) for u, v, d in G.edges(data=True)]
sorted_edge_weights = sorted(edge_weights, key=lambda x: x[2], reverse=True)
for u, v, weight in sorted_edge_weights[:5]:
    print(f"Edge: ({u}, {v}), Weight: {weight}")

# %%
# Sort the areas for each age group with highest edge weights (crime counts)
age_groups = ['Child', 'Teenager', 'Young Adult', 'Adult', 'Senior']
crime_by_area_for_age_group = {age_group: {} for age_group in age_groups}
areas = [node for node, attr in G.nodes(data=True) if attr['type'] == 'area']

for area in areas:
    for age_node in G.neighbors(area):
        age_group = age_node.split()[-1]
        if age_group in age_groups:
            crime_count = G[area][age_node]['weight']
            if area in crime_by_area_for_age_group[age_group]:
                crime_by_area_for_age_group[age_group][area] += crime_count
            else:
                crime_by_area_for_age_group[age_group][area] = crime_count

sorted_areas_by_age_group = {}
for age_group in age_groups:
    sorted_areas = sorted(crime_by_area_for_age_group[age_group].items(), key=lambda x: x[1], reverse=True)
    sorted_areas_by_age_group[age_group] = sorted_areas

sorted_areas_by_age_group


# %%
# Visualize it with folium
import folium

data =  la_crime_sample

crime_counts = data.groupby('area_name').agg({
    'ID': 'count',
    'longitude': 'first', 
    'latitude': 'first',
    'age_group': lambda x: x.mode()[0],
    'victim_sex': lambda x: x.mode()[0]
})
crime_counts = crime_counts.sort_values('ID', ascending=False).head(20)

m = folium.Map(location=[34.0522, -118.2437], zoom_start=10)  # Coordinates for Los Angeles

# Draw circles for each area (colored by most common victim sex)
for index, row in crime_counts.iterrows():
    circle_color = 'red' if row['victim_sex'] == 'Female' else 'blue'
    folium.Circle(
        location=[row['longitude'], row['latitude']],
        radius=row['ID'] * 0.02, 
        color=circle_color,
        fill=True,
        fill_color=circle_color,
        fill_opacity=0.5,
        popup=f"Area: {index}<br>Most common age group: {row['age_group']}<br>Most common gender: {row['victim_sex']}<br>Incidents: {row['ID']}"
    ).add_to(m)

m.save('LA_Crime_Map.html')
m


# %%
age_group_area_counts = data.groupby(['age_group', 'area_name']).agg({
    'ID': 'count',
    'longitude': 'first', 
    'latitude': 'first'
}).reset_index()

top_3_per_age_group = age_group_area_counts.groupby('age_group').apply(lambda x: x.nlargest(3, 'ID')).reset_index(drop=True)

age_group_colors = {
    'Child': 'green',
    'Teenager': 'blue',
    'Young Adult': 'orange',
    'Adult': 'red',
    'Senior': 'purple'
}

def get_color(age_group):
    return age_group_colors.get(age_group, 'black')

m = folium.Map(location=[34.0522, -118.2437], zoom_start=10)

# Draw circles for each area (colored by age groups)
for _, row in top_3_per_age_group.iterrows():
    folium.Circle(
        location=[row['longitude'], row['latitude']],
        radius=row['ID'] * 0.08,
        color=get_color(row['age_group']),
        fill=True,
        fill_color=get_color(row['age_group']),
        fill_opacity=0.5,
        popup=f"Area: {row['area_name']}<br>Age Group: {row['age_group']}<br>Incidents: {row['ID']}"
    ).add_to(m)

m.save('LA_Crime_Top_3_Areas_Per_Age_Group_Map.html')
m




