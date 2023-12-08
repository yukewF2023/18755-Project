import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


df = pd.read_csv('la_crime_cleaned.csv')
filtered_df = df[df['weapon_description'] != 'no description']
filtered_df = filtered_df[filtered_df['weapon_description'] != 'UNKNOWN WEAPON/OTHER WEAPON']

G = nx.Graph()

for index, row in filtered_df.iterrows():
    crime = row['crime_code_description']
    weapon = row['weapon_description']

    if not G.has_node(crime):
        G.add_node(crime, type='crime')
    if not G.has_node(weapon):
        G.add_node(weapon, type='weapon')

    if G.has_edge(crime, weapon):
        G[crime][weapon]['weight'] += 1
    else:
        G.add_edge(crime, weapon, weight=1)

nx.write_gml(G, "crime_weapon.gml")
G = nx.read_gml("crime_weapon.gml")

clustering = nx.bipartite.clustering(G)

print(f"Number of nodes: {G.number_of_nodes()}")
print(f"Number of edges: {G.number_of_edges()}")
print(f"Number of crime types: {len([n for n, d in G.nodes(data=True) if d['type'] == 'crime'])}")
print(f"Number of weapon types: {len([n for n, d in G.nodes(data=True) if d['type'] == 'weapon'])}")

crime_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'crime']
crime_projection = nx.bipartite.projected_graph(G, crime_nodes, multigraph=True)

weapon_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'weapon']
weapon_projection = nx.bipartite.projected_graph(G, weapon_nodes, multigraph=True)

nx.write_gml(crime_projection, "crime_projection.gml")
nx.write_gml(weapon_projection, "weapon_projection.gml")
