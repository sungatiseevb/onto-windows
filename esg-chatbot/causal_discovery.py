import pandas as pd
import numpy as np
from causallearn.search.ConstraintBased.PC import pc

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
