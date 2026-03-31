import pandas as pd
import numpy as np

np.random.seed(42)
n = 100

df = pd.DataFrame({
    "company_id": [f"C{i:03d}" for i in range(n)],
    "ghg_emissions":      np.random.normal(500, 100, n),
    "energy_consumption": np.random.normal(1000, 200, n),
    "board_diversity":    np.random.uniform(0, 1, n),
    "corruption_index":   np.random.uniform(0, 1, n),
    "revenue":            np.random.normal(5000, 1000, n),
    "stock_return":       np.random.normal(0.08, 0.15, n),
})

# Добавляем causal структуру
df["stock_return"] += -0.0002 * df["ghg_emissions"] + 0.05 * df["board_diversity"]
df["revenue"]      += -0.3 * df["ghg_emissions"] + 200 * df["board_diversity"]

df.to_csv("esg_dataset.csv", index=False)
print("Dataset создан: esg_dataset.csv")
print(df.describe().round(2))
