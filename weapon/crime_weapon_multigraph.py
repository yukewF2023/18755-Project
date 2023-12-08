import pandas as pd
import networkx as nx

MG = nx.MultiGraph()

df = pd.read_csv('../la_crime_cleaned.csv')
# filter those with no description and unknown weapon
filtered_df = df[df['weapon_description'] != 'no description']
filtered_df = filtered_df[filtered_df['weapon_description'] != 'UNKNOWN WEAPON/OTHER WEAPON']

for index, row in filtered_df.iterrows():
    crime = row['crime_code_description']
    weapon = row['weapon_description']

    if not MG.has_node(crime):
        MG.add_node(crime, type='crime')
    if not MG.has_node(weapon):
        MG.add_node(weapon, type='weapon')

    MG.add_edge(crime, weapon)

print(f"Number of nodes: {MG.number_of_nodes()}")
print(f"Number of edges: {MG.number_of_edges()}")
#
nx.write_gml(MG, "crime_weapon_multigraph.gml")
MG = nx.read_gml("crime_weapon_multigraph.gml")

def project_bipartite_multigraph(G, nodes):
    # Create a new graph for the projection
    projection = nx.Graph()

    # Iterate over each pair of nodes
    for node1 in nodes:
        for node2 in nodes:
            if node1 != node2:
                # Count the number of shared neighbors between node1 and node2
                shared_neighbors = set(G.neighbors(node1)) & set(G.neighbors(node2))
                weight = len(shared_neighbors)

                # Add an edge in the projection if there is a shared neighbor
                if weight > 0:
                    projection.add_edge(node1, node2, weight=weight)

    return projection

# Projecting the multigraph
# Weapon-Weapon Projection
weapon_nodes = set(n for n, d in MG.nodes(data=True) if d['type'] == 'weapon')
weapon_projection = project_bipartite_multigraph(MG, weapon_nodes)
nx.write_gml(weapon_projection, "weapon_projection.gml")

weapon_projection = nx.read_gml("weapon_projection.gml")
print(f"Number of nodes: {weapon_projection.number_of_nodes()}")
# calculate the average degree of the weapon projection
total_degree = 0
for node in weapon_projection.nodes():
    total_degree += weapon_projection.degree(node)
print(f"Average degree of the weapon projection: {total_degree / weapon_projection.number_of_nodes()}")

# --------------------------------------------
# Calculating the weighted degree centrality
weighted_degrees = dict(weapon_projection.degree(weight='weight'))

# Optionally, sorting and printing the top nodes
sorted_weighted_degrees = sorted(weighted_degrees.items(), key=lambda x: x[1], reverse=True)
for weapon, degree in sorted_weighted_degrees[:5]:  # top 5 as an example
    print(f"Weapon: {weapon}, Weighted Degree: {degree}")

# --------------------------------------------
# Analyzing edge weights
edge_weights = [(u, v, d['weight']) for u, v, d in weapon_projection.edges(data=True)]

# Sorting and printing the top weighted edges
sorted_edge_weights = sorted(edge_weights, key=lambda x: x[2], reverse=True)
for u, v, weight in sorted_edge_weights[:5]:  # top 5 as an example
    print(f"Weapon Pair: ({u}, {v}), Weight: {weight}")

# --------------------------------------------
# Calculating the weighted clustering coefficient
weighted_clustering = nx.clustering(weapon_projection, weight='weight')

# Sorting and printing the top coefficients
sorted_clustering = sorted(weighted_clustering.items(), key=lambda x: x[1], reverse=True)
for weapon, clustering in sorted_clustering[:5]:  # top 5 as an example
    print(f"Weapon: {weapon}, Weighted Clustering Coefficient: {clustering}")

# --------------------------------------------
# Calculate degree centrality
degree_centrality = nx.degree_centrality(weapon_projection)
# Sort the weapons by their degree centrality
sorted_degree_centrality = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
# Optionally, print the top weapons by degree centrality
for weapon, centrality in sorted_degree_centrality[:5]:  # top 5 as an example
    print(f"Weapon: {weapon}, Degree Centrality: {centrality}")