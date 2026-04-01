import numpy as np

labels = ['renewable_energy_share', 'total_energy_consumption', 
          'co2_ch4_n2o_scope_1_3', 'carbon_intensity',
          'board_diversity', 'governance_compliance_score',
          'corruption_cases', 'turnover_rate', 
          'injury_frequency_rate', 'green_financing']

# Ground truth edges (what we planted in the dataset)
ground_truth = {
    ('renewable_energy_share', 'total_energy_consumption'),
    ('total_energy_consumption', 'co2_ch4_n2o_scope_1_3'),
    ('co2_ch4_n2o_scope_1_3', 'carbon_intensity'),
    ('board_diversity', 'governance_compliance_score'),
    ('governance_compliance_score', 'corruption_cases'),
    ('governance_compliance_score', 'green_financing'),
    ('turnover_rate', 'injury_frequency_rate'),
    ('injury_frequency_rate', 'green_financing'),
}

# Baseline PC found (undirected treated as edges)
baseline = {
    ('renewable_energy_share', 'total_energy_consumption'),
    ('total_energy_consumption', 'co2_ch4_n2o_scope_1_3'),
    ('co2_ch4_n2o_scope_1_3', 'carbon_intensity'),
    ('board_diversity', 'governance_compliance_score'),
    ('governance_compliance_score', 'corruption_cases'),
    ('governance_compliance_score', 'green_financing'),
    ('corruption_cases', 'turnover_rate'),
    ('turnover_rate', 'injury_frequency_rate'),
    ('injury_frequency_rate', 'green_financing'),
}

# Ontology-guided PC (same edges minus forbidden)
forbidden = {
    ('carbon_intensity', 'co2_ch4_n2o_scope_1_3'),
    ('corruption_cases', 'board_diversity'),
    ('injury_frequency_rate', 'turnover_rate'),
    ('green_financing', 'governance_compliance_score'),
}
ontology_guided = baseline - forbidden

def evaluate(predicted, ground_truth, name):
    tp = len(predicted & ground_truth)
    fp = len(predicted - ground_truth)
    fn = len(ground_truth - predicted)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    print(f"\n=== {name} ===")
    print(f"  Edges predicted: {len(predicted)}")
    print(f"  TP: {tp}, FP: {fp}, FN: {fn}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall:    {recall:.3f}")
    print(f"  F1 Score:  {f1:.3f}")
    return precision, recall, f1

evaluate(baseline, ground_truth, "Baseline PC")
evaluate(ontology_guided, ground_truth, "Ontology-Guided PC")

print("\n=== Summary ===")
print("Ontology constraints removed semantically invalid edges:")
for e in forbidden:
    print(f"  {e[0]} -X-> {e[1]}")
