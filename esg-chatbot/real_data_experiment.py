from pathlib import Path

import numpy as np
import pandas as pd
from causallearn.search.ConstraintBased.PC import pc


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data" / "processed" / "df_asst_bnk_ecb_clean.csv"
OUT_DIR = ROOT / "outputs" / "real_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_edges(graph_matrix: np.ndarray, labels: list[str]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    directed: list[tuple[str, str]] = []
    undirected: list[tuple[str, str]] = []
    n = len(labels)
    for i in range(n):
        for j in range(n):
            if graph_matrix[i][j] == -1 and graph_matrix[j][i] == 1:
                directed.append((labels[i], labels[j]))
            elif graph_matrix[i][j] == -1 and graph_matrix[j][i] == -1 and i < j:
                undirected.append((labels[i], labels[j]))
    return directed, undirected


def semantic_validity(
    directed_edges: list[tuple[str, str]], forbidden: set[tuple[str, str]]
) -> tuple[int, float, list[tuple[str, str]]]:
    if not directed_edges:
        return 0, 1.0, []
    violations = [e for e in directed_edges if e in forbidden]
    score = 1.0 - (len(violations) / len(directed_edges))
    return len(violations), score, violations


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)
    labels = list(df.columns)
    data = df.values.astype(float)

    print("=== Real Data Experiment (ECB ESG) ===")
    print(f"Input file: {INPUT_CSV}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {labels}")

    # Baseline model
    print("\n=== Baseline PC ===")
    baseline = pc(data, alpha=0.05, indep_test="fisherz")
    b_dir, b_undir = extract_edges(baseline.G.graph, labels)
    print(f"Directed edges: {len(b_dir)}")
    print(f"Undirected edges: {len(b_undir)}")

    # Lightweight ontology/domain-inspired constraints for semantic validity
    forbidden = {
        ("reporting_quality_score", "scope1_emissions"),
        ("reporting_quality_score", "scope2_emissions"),
        ("reporting_quality_score", "scope3_emissions"),
        ("board_esg_oversight_score", "scope1_emissions"),
        ("board_esg_oversight_score", "scope2_emissions"),
        ("board_esg_oversight_score", "scope3_emissions"),
        ("community_investment", "scope1_emissions"),
        ("community_investment", "scope2_emissions"),
        ("community_investment", "scope3_emissions"),
    }

    b_viol_n, b_semantic_score, b_violations = semantic_validity(b_dir, forbidden)

    # Ontology-guided view by removing forbidden directed edges from baseline output
    og_dir = [e for e in b_dir if e not in forbidden]
    og_undir = b_undir.copy()
    og_viol_n, og_semantic_score, og_violations = semantic_validity(og_dir, forbidden)

    print("\n=== Ontology-Guided (post-filtered forbidden directions) ===")
    print(f"Directed edges: {len(og_dir)}")
    print(f"Undirected edges: {len(og_undir)}")

    print("\n=== Semantic Validity ===")
    print(f"Baseline violations: {b_viol_n}")
    print(f"Baseline semantic validity score: {b_semantic_score:.3f}")
    print(f"Ontology-guided violations: {og_viol_n}")
    print(f"Ontology-guided semantic validity score: {og_semantic_score:.3f}")

    # Save edge lists
    pd.DataFrame(b_dir, columns=["source", "target"]).to_csv(OUT_DIR / "baseline_directed_edges.csv", index=False)
    pd.DataFrame(b_undir, columns=["node_a", "node_b"]).to_csv(OUT_DIR / "baseline_undirected_edges.csv", index=False)
    pd.DataFrame(og_dir, columns=["source", "target"]).to_csv(OUT_DIR / "ontology_guided_directed_edges.csv", index=False)
    pd.DataFrame(og_undir, columns=["node_a", "node_b"]).to_csv(OUT_DIR / "ontology_guided_undirected_edges.csv", index=False)
    pd.DataFrame(sorted(forbidden), columns=["source", "target"]).to_csv(OUT_DIR / "forbidden_directed_edges.csv", index=False)
    pd.DataFrame(b_violations, columns=["source", "target"]).to_csv(OUT_DIR / "baseline_semantic_violations.csv", index=False)
    pd.DataFrame(og_violations, columns=["source", "target"]).to_csv(OUT_DIR / "ontology_guided_semantic_violations.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "model": "baseline",
                "directed_edges": len(b_dir),
                "undirected_edges": len(b_undir),
                "semantic_violations": b_viol_n,
                "semantic_validity_score": round(b_semantic_score, 3),
            },
            {
                "model": "ontology_guided",
                "directed_edges": len(og_dir),
                "undirected_edges": len(og_undir),
                "semantic_violations": og_viol_n,
                "semantic_validity_score": round(og_semantic_score, 3),
            },
        ]
    )
    summary_path = OUT_DIR / "summary_metrics.csv"
    summary.to_csv(summary_path, index=False)

    print(f"\nSaved results to: {OUT_DIR}")
    print(f"Summary file: {summary_path}")


if __name__ == "__main__":
    main()
