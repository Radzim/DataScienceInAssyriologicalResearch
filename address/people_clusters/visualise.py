import csv
import pickle

import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

def load_pickle(filename):
    with open('pickles/' + filename + '.pickle', 'rb') as handle:
        return pickle.load(handle)

# s2 = load_pickle('2')
# print(s2)
# with open('file.txt', 'w') as file:
#     for i, row in s2.iterrows():
#         tablets = row.numbers
#         if '[' not in ''.join(i):
#             for tablet1 in tablets:
#                 for tablet2 in tablets:
#                     if tablet1 != tablet2:
#                         G.add_edge(tablet1, tablet2, weight=1)
#                         file.write(tablet1.replace(' ', '_')+';'+tablet2.replace(' ', '_')+'\n')

s2 = load_pickle('2')
print(s2)
with open('file.txt', 'w') as file:
    for i, row in s2.iterrows():
        tablets = row.numbers
        if '[' not in ''.join(i):
            name1, name2 = i
            name1, name2 = str(name1.encode("utf-8")), str(name2.encode("utf-8"))
            G.add_edge(name1, name2, weight=row['count'])
            for _ in range(row['count']):
                file.write(name1.replace(' ', '_')+';'+name2.replace(' ', '_')+'\n')

# Driver code
elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
# esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]

pos = nx.spring_layout(G, seed=1)  # positions for all nodes - seed for reproducibility

# nodes
nx.draw_networkx_nodes(G, pos, node_size=50)

# edges
nx.draw_networkx_edges(G, pos, edgelist=elarge, width=2)
# nx.draw_networkx_edges(
#     G, pos, edgelist=esmall, width=1, alpha=0.5, edge_color="b", style="dashed"
# )

# node labels
nx.draw_networkx_labels(G, pos, font_size=5, font_family="sans-serif")
# edge weight labels
edge_labels = nx.get_edge_attributes(G, "weight")
# nx.draw_networkx_edge_labels(G, pos, edge_labels)

ax = plt.gca()
ax.margins(0.08)
plt.axis("off")
plt.tight_layout()
plt.show()