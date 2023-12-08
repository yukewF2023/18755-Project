import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Reading crime data from a CSV file
data_all = pd.read_csv("../la_crime_cleaned.csv")

def temporal_motifs(data_all):
    """
    This function identifies temporal crime motifs from the provided dataset.
    It sorts the data by occurrence dates, and then counts transitions between
    different types of crimes from one day to the next.

    Args:
        data_all (DataFrame): The crime dataset.

    Returns:
        DataFrame, DataFrame: DataFrames of transitions and nodes.
    """
    sorted_df = data_all.sort_values(by=['date_occured'])
    transitions = []
    unique_dates = sorted_df['date_occured'].unique()
    
    for i in range(len(unique_dates) - 1):
        curr_date = unique_dates[i]
        next_date = unique_dates[i + 1]
        
        curr_day_df = sorted_df[sorted_df['date_occured'] == curr_date]
        next_day_df = sorted_df[sorted_df['date_occured'] == next_date]

        # For each crime on the current day, count how many times it is followed by each crime on the next day
        for curr_crime in curr_day_df['crime_code_description'].unique():
            curr_crime_count = curr_day_df[curr_day_df['crime_code_description'] == curr_crime].shape[0]
            for next_crime in next_day_df['crime_code_description'].unique():
                next_crime_count = next_day_df[next_day_df['crime_code_description'] == next_crime].shape[0]
                transitions.append((curr_crime, next_crime, min(curr_crime_count, next_crime_count)))
    
    transitions_df = pd.DataFrame(transitions, columns=['Source', 'Target', 'weight'])

    transitions_sum_df = transitions_df.groupby(['Source', 'Target']).sum().reset_index()

    transitions_sum_df.to_csv('temporal_crime_pattern_edges.csv', index=False)

    nodes = pd.DataFrame(list(set(transitions_sum_df['Source']).union(set(transitions_sum_df['Target']))), columns=['id'])
    nodes.to_csv('temporal_crime_pattern_nodes.csv', index=False)
    
    return transitions_sum_df, nodes

transitions_sum_df, nodes = temporal_motifs(data_all)

def get_statistics(csv, percentage):
    """
    This function calculates various statistics for the network graph created from
    crime data and saves relevant plots.

    Args:
        csv (str): Path to the CSV file containing edge data.
        percentage (float): The percentage of data used for analysis.

    Returns:
        Graph: The network graph.
    """
    
    edges = pd.read_csv(csv)
    
    G1 = nx.from_pandas_edgelist(edges, source='Source', target='Target', edge_attr='weight', create_using=nx.DiGraph())
    G1.remove_edges_from(nx.selfloop_edges(G1))
        
    degrees = [d for n, d in G1.degree()]
    plt.hist(degrees, bins=100)
    plt.xlabel("Degree")
    plt.ylabel("Count")
    plt.title("Degree Distribution")
    plt.savefig(f"temporal_degree_distribution_{percentage}.png")
    
    print("Number of nodes: ", G1.number_of_nodes())
    print("Number of edges: ", G1.number_of_edges())
    print("Average degree: ", np.mean(degrees))
    print("Average in-degree: ", np.mean([d for n, d in G1.in_degree()]))
    print("Average out-degree: ", np.mean([d for n, d in G1.out_degree()]))
    print("Average clustering coefficient: ", nx.average_clustering(G1))
    print("Global clustering coefficient: ", nx.transitivity(G1))
    print("Average shortest path length: ", nx.average_shortest_path_length(G1))
    print("Diameter: ", nx.diameter(G1))
    
    print("Vertex connectivity: ", nx.node_connectivity(G1))
    print("Edge connectivity: ", nx.edge_connectivity(G1))
    
    k_core = nx.k_core(G1)
    print("Largest edge-connectivity with k-core approach: ", nx.edge_connectivity(k_core))
    print("Number of nodes in the largest k-core: ", k_core.number_of_nodes())
    print("Vertex connectivity of the largest k-core: ", nx.node_connectivity(k_core))
    
    degree_sequence = sorted([d for n, d in G1.degree()], reverse=True)  # degree sequence
    degreeCount = dict()
    for d in degree_sequence:
        if d not in degreeCount:
            degreeCount[d] = 1
        else:
            degreeCount[d] += 1
    degree, count = zip(*degreeCount.items())
    total_nodes = G1.number_of_nodes()
    probabilities = [c/total_nodes for c in count]
    plt.plot(degree, probabilities, 'bo')
    plt.xlabel('Degree k')
    plt.ylabel('Count of Degree = k')
    plt.title(f'Degree Distribution {percentage*100}% of Data')
    plt.savefig(f'Degree_Distribution_{percentage}.png')
    plt.close()
    return G1

G1 = get_statistics('temporal_crime_pattern_edges.csv', 1)

# Plot the network graph using spring layout and export to gexf
pos = nx.spring_layout(G1, k=0.15, iterations=20)
plt.figure(figsize=(20, 20))
nx.draw_networkx_nodes(G1, pos, node_size=20, alpha=0.6, node_color="blue")
nx.draw_networkx_edges(G1, pos, alpha=0.1, width=0.5)
plt.title("Temporal Crime Pattern Network")
plt.axis("off")
plt.savefig(f'Temporal_Network.png')
nx.write_gexf(G1, "Temporal_Network.gexf") 

# Remove self loops
edges = pd.read_csv("temporal_crime_pattern_edges.csv")
G1 = nx.from_pandas_edgelist(edges, source='Source', target='Target', edge_attr='weight', create_using=nx.DiGraph())
G1.remove_edges_from(nx.selfloop_edges(G1))
    
# Plot the degree distribution
degrees = [d for n, d in G1.degree()]
plt.hist(degrees, bins=100)
plt.xlabel('Degree k')
plt.ylabel('Count of Degree = k')
plt.title("Degree Distribution of Temporal Network")
plt.savefig(f"temporal_degree_distribution.png")

# top 10 nodes with highest betweenness centrality
sorted_edges = sorted(G1.edges(data=True), key=lambda x: x[2].get('weight', 1), reverse=True)
top_10_connections = sorted_edges[:10]
top_transitions = []
for connection in top_10_connections:
    source = connection[0]
    target = connection[1]
    weight = connection[2]['weight']
    top_transitions.append((source, target))
    print(f"The connection from {source} to {target} has a weight of {weight}.")

data_all['date_occured'] = pd.to_datetime(data_all['date_occured'])

# Filter the data for the 'Burglary From Vehicle' events
burglary_df = data_all[data_all['crime_code_description'] == 'Burglary From Vehicle']
next_day = burglary_df['date_occured'] + pd.Timedelta(days=1)
# Filter the data for 'Battery - Simple Assault' events that occurred the day after a 'Burglary From Vehicle'
battery_df = data_all[(data_all['crime_code_description'] == 'Battery - Simple Assault') & 
                (data_all['date_occured'].isin(next_day))]
# Group by area and count occurrences for both crime types
burglary_by_area = burglary_df.groupby('area_name').size().reset_index(name='burglary_counts')
battery_by_area = battery_df.groupby('area_name').size().reset_index(name='battery_counts')
# Merge the two dataframes on area_name
area_counts = pd.merge(burglary_by_area, battery_by_area, on='area_name', how='outer').fillna(0)

# Plot the counts for both crime types by area
area_counts.plot(x='area_name', y=['burglary_counts', 'battery_counts'], kind='bar', figsize=(7, 5))
plt.title('Crime Counts by Area', fontsize=16)
plt.xlabel('Area Name', fontsize=14)
plt.ylabel('Counts', fontsize=14)
plt.xticks(rotation=90, fontsize=12)  # Rotate the x-labels by 90 degrees
plt.legend(['Burglary From Vehicle', 'Battery - Simple Assault'], fontsize=12)
plt.tight_layout()
plt.savefig('crime_counts_by_area.png', dpi=300)

# Plot the counts of 'Burglary From Vehicle' by hour of the day
burglary_by_hour = burglary_df.groupby('hour').size().reset_index(name='counts')
battery_by_hour = battery_df.groupby('hour').size().reset_index(name='counts')
plt.figure(figsize=(7, 5))  # Adjust the figure size as per your requirement
plt.plot(burglary_by_hour['hour'], burglary_by_hour['counts'], label='Burglary From Vehicle')
plt.plot(battery_by_hour['hour'], battery_by_hour['counts'], label='Battery - Simple Assault')
plt.title('Crime Counts by Hour of the Day', fontsize=16)  # Increase the font size of the title
plt.xlabel('Hour', fontsize=14)  # Increase the font size of the x-axis label
plt.ylabel('Counts', fontsize=14)  # Increase the font size of the y-axis label
# increase the font size of the tick labels
plt.yticks(fontsize=12)
plt.xticks(fontsize=12)
plt.xticks(range(0, 24))
plt.legend(fontsize=12)  # Increase the font size of the legend
plt.grid(True)
plt.tight_layout()  # Adjust the spacing between the plot elements
plt.savefig('crime_counts_by_hour.png', dpi=1000)  # Increase the dpi for higher resolution

# Get the degrees of all nodes in the graph
degrees = dict(G1.degree())
# Find the maximum degree in the graph
max_degree = max(degrees.values())
# Filter the nodes with the maximum degree
highest_degree_nodes = [node for node, degree in degrees.items() if degree == max_degree]
# Create a subgraph with the highest degree nodes
subgraph = G1.subgraph(highest_degree_nodes)
# save as gexf
nx.write_gexf(subgraph, "temporal_subgraph.gexf")
