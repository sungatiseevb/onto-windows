# Ontology-Guided Hybrid Causal Discovery in ESG Data
### LLM-Based Development of Query Interface

Bachelor Thesis — Constructor University Bremen  
**Author:** Merey Yessengaliyeva  
**Supervisor:** Prof. Dr. Hendro Wicaksono  

---

## Overview

This project presents an ontology-guided hybrid causal discovery system for ESG
(Environmental, Social, and Governance) data, combined with a natural language
query interface powered by Google Gemini.

**Two main components:**
1. **LLM-based Query Interface** — users ask questions in plain English, automatically translated into SPARQL queries against the ESGOnt ontology
2. **Hybrid Causal Discovery Pipeline** — PC algorithm guided by ESGOnt ontological constraints to produce semantically valid causal graphs

---

## Project Structure
```
esg-chatbot/
├── app.py                    # Gradio web application (main prototype)
├── causal_discovery.py       # PC algorithm with ESGOnt constraints
├── evaluation.py             # Precision, recall, F1 evaluation
├── query_interface.py        # CLI version of the query interface
├── esgontology.owl           # ESGOnt ontology (604 triples)
├── esg_dataset_causal.csv    # Synthetic ESG dataset (3,000 observations)
└── causal_graph.png          # Causal graph visualization
```

---

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.12 | Core language |
| rdflib | 7.6.0 | OWL ontology loading and SPARQL execution |
| google-generativeai | 0.8.6 | Gemini API for NL to SPARQL translation |
| causal-learn | latest | PC algorithm for causal discovery |
| gradio | latest | Web interface |
| networkx | latest | Causal graph visualization |
| pandas | latest | Data processing |
| numpy | latest | Numerical computations |

---

## Setup and Installation

### 1. Clone the repository
```bash
git clone https://github.com/sungatiseevb/onto.git
cd onto
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set API keys
For CLI (`query_interface.py`) you need Gemini:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

For Gradio web app (`app.py`) you need Groq:
```bash
export GROQ_API_KEY="your-api-key-here"
```

> **Windows PowerShell**
> ```powershell
> $env:GOOGLE_API_KEY="your-api-key-here"
> $env:GROQ_API_KEY="your-api-key-here"
> ```

> **Tip (Linux/macOS):** To avoid setting this every session, add it to your `~/.bashrc`:
> ```bash
> echo 'export GOOGLE_API_KEY="your-api-key-here"' >> ~/.bashrc
> echo 'export GROQ_API_KEY="your-api-key-here"' >> ~/.bashrc
> source ~/.bashrc
> ```

---

## Running the App

### Option 1: Gradio Web Interface (recommended)
```bash
cd esg-chatbot
python app.py
```
Then open `http://localhost:7860` in your browser.

You can ask questions like:
- *"What are the ESG domains?"*
- *"What are all ESG categories?"*
- *"What is Board Diversity a subclass of?"*

### Option 2: Command Line Interface
```bash
cd esg-chatbot
python query_interface.py
```

### Option 3: Run Causal Discovery
```bash
cd esg-chatbot
python causal_discovery.py
```
This generates the causal graph and saves it as `causal_graph.png`.

### Option 4: Run Evaluation
```bash
cd esg-chatbot
python evaluation.py
```
This prints precision, recall, and F1 scores for both models.

---

## Results

### Causal Discovery

| Model | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Baseline PC | 0.889 | 1.000 | 0.941 |
| Ontology-Guided PC | 0.889 | 1.000 | 0.941 |

4 forbidden edges from ESGOnt successfully blocked semantically invalid causal directions:
- `carbon_intensity` ↛ `co2_emissions`
- `corruption_cases` ↛ `board_diversity`
- `injury_frequency_rate` ↛ `turnover_rate`
- `green_financing` ↛ `governance_compliance_score`

### Query Interface
All test queries produced correct SPARQL and accurate results.

---

## Ontology

ESGOnt — OWL-based ontology with 604 RDF triples, organized into three domains:

- 🌱 **Environmental** — GHG Emissions, Energy, Water, Waste, Biodiversity
- 👥 **Social** — Labor Practices, Health & Safety, Human Rights, Community
- 🏛️ **Governance** — Board Diversity, Corruption, Transparency, Shareholder Rights

Ontology prefix: `http://www.annasvijaya.com/ESGOnt/esgontology#`

---

## Dataset

Synthetic ESG dataset with 3,000 company observations and 10 variables:

| Variable | Domain | Description |
|----------|--------|-------------|
| renewable_energy_share | Environmental | % energy from renewable sources |
| total_energy_consumption | Environmental | Total energy in GJ |
| co2_ch4_n2o_scope_1_3 | Environmental | GHG emissions in tCO2e |
| carbon_intensity | Environmental | GHG normalized by revenue |
| turnover_rate | Social | Annual employee turnover % |
| injury_frequency_rate | Social | Injuries per 100 workers |
| board_diversity | Governance | % diverse board members |
| governance_compliance_score | Governance | Compliance rating 0-100 |
| corruption_cases | Governance | Reported corruption incidents |
| green_financing | Governance | Green financing volume (USD M) |

---

## Note on API Key

Never commit your API key to GitHub. The `.env` file is listed in `.gitignore`.  
Always set your key via `export` in the terminal or in `~/.bashrc`.
