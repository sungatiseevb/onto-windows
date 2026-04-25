import pandas as pd
import numpy as np
from causallearn.search.ConstraintBased.PC import pc
import matplotlib.pyplot as plt
import networkx as nx

df = pd.read_csv('esg_dataset_causal.csv')
data = df.values.astype(float)
labels = list(df.columns)

print("=== Baseline PC (no ontology constraints) ===")
cg = pc(data, alpha=0.5, indep_test='fisherz')

print("Causal edges found:")
for i in range(len(labels)):
    for j in range(len(labels)):
        if cg.G.graph[i][j] == -1 and cg.G.graph[j][i] == 1:
            print(f"  {labels[i]} -> {labels[j]}")
        elif cg.G.graph[i][j] == -1 and cg.G.graph[j][i] == -1 and i < j:
            print(f"  {labels[i]} -- {labels[j]} (undirected)")

print("\n=== Ontology-Guided PC (with forbidden edges) ===")
# Forbidden edges from ESGOnt domain logic:
# carbon_intensity cannot CAUSE co2 (it's derived FROM co2)
# corruption cannot CAUSE board_diversity (governance causes ethics, not reverse)
# green_financing cannot CAUSE governance_score (governance enables financing)

n = len(labels)
forbidden = np.zeros((n, n), dtype=int)

def forbid(a, b):
    i, j = labels.index(a), labels.index(b)
    forbidden[i][j] = 1

forbid('carbon_intensity', 'co2_ch4_n2o_scope_1_3')
forbid('corruption_cases', 'board_diversity')
forbid('green_financing', 'governance_compliance_score')
forbid('injury_frequency_rate', 'turnover_rate')

cg2 = pc(data, alpha=0.5, indep_test='fisherz', background_knowledge=None)

# Apply forbidden edges manually by removing them
print("Causal edges (ontology-constrained):")
for i in range(len(labels)):
    for j in range(len(labels)):
        if cg.G.graph[i][j] == -1 and cg.G.graph[j][i] == 1:
            if not forbidden[i][j]:
                print(f"  {labels[i]} -> {labels[j]}")
        elif cg.G.graph[i][j] == -1 and cg.G.graph[j][i] == -1 and i < j:
            if not forbidden[i][j]:
                print(f"  {labels[i]} -- {labels[j]} (undirected)")

print("\nForbidden edges (removed by ontology):")
for i in range(n):
    for j in range(n):
        if forbidden[i][j]:
            print(f"  {labels[i]} -X-> {labels[j]}")

# Build a simple visualization and save as causal_graph.png
directed_edges = []
undirected_edges = []
for i in range(len(labels)):
    for j in range(len(labels)):
        if cg.G.graph[i][j] == -1 and cg.G.graph[j][i] == 1 and not forbidden[i][j]:
            directed_edges.append((labels[i], labels[j]))
        elif cg.G.graph[i][j] == -1 and cg.G.graph[j][i] == -1 and i < j and not forbidden[i][j]:
            undirected_edges.append((labels[i], labels[j]))

forbidden_edges = []
for i in range(n):
    for j in range(n):
        if forbidden[i][j]:
            forbidden_edges.append((labels[i], labels[j]))

dg = nx.DiGraph()
ug = nx.Graph()
dg.add_nodes_from(labels)
ug.add_nodes_from(labels)
dg.add_edges_from(directed_edges)
ug.add_edges_from(undirected_edges)

pos = nx.spring_layout(dg.to_undirected(), seed=42, k=0.9)
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_title("ESG Causal Graph: baseline + ontology constraints", fontsize=12)

nx.draw_networkx_nodes(dg, pos, node_color="#eaf4fb", edgecolors="#2e86c1", node_size=2200, ax=ax)
nx.draw_networkx_labels(dg, pos, font_size=8, font_family="sans-serif", ax=ax)

# Undirected edges (baseline skeleton)
nx.draw_networkx_edges(ug, pos, edge_color="#4f81bd", width=1.8, style="solid", ax=ax)
# Directed edges (kept after filtering)
nx.draw_networkx_edges(
    dg,
    pos,
    edgelist=directed_edges,
    edge_color="#2ca02c",
    width=2.2,
    arrows=True,
    arrowstyle="-|>",
    arrowsize=16,
    ax=ax,
)
# Forbidden directions as dashed red arrows
nx.draw_networkx_edges(
    dg,
    pos,
    edgelist=forbidden_edges,
    edge_color="#d62728",
    width=1.6,
    style="dashed",
    arrows=True,
    arrowstyle="-|>",
    arrowsize=14,
    alpha=0.8,
    ax=ax,
)

ax.axis("off")
plt.tight_layout()
plt.savefig("causal_graph.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("\nSaved graph image: causal_graph.png")
