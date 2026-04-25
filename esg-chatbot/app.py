import os
import gradio as gr
from groq import Groq
from rdflib import Graph
from pathlib import Path

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL_ID = "llama-3.3-70b-versatile"

g = Graph()
ONTOLOGY_PATH = Path(__file__).resolve().parent / "esgontology.owl"
g.parse(ONTOLOGY_PATH.as_posix(), format="xml")
print(f"Ontology loaded: {len(g)} triples")

def clean_uri(val):
    s = str(val)
    if "#" in s:
        return s.split("#")[-1].replace("_", " ")
    return s.split("/")[-1].replace("_", " ")

def generate_sparql(question):
    prompt = f"""You are a SPARQL expert for the ESGOnt ontology.
Use ONLY these prefixes:
PREFIX esg: <http://www.annasvijaya.com/ESGOnt/esgontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

ONTOLOGY STRUCTURE:
- esg:Domain has subclasses: esg:Environmental, esg:Social, esg:Governance
- esg:Category has subclasses: esg:GHG_Emissions, esg:Board_Diversity, esg:Energy, esg:Corruption, esg:Waste, esg:Water, esg:Biodiversity, esg:Labor_Practices, esg:Human_Rights

RULES:
- Use ONLY simple patterns: ?x rdfs:subClassOf esg:SomeClass
- Do NOT use FILTER NOT EXISTS
- Do NOT use nested subqueries
- Do NOT repeat the question in the output
- Output ONLY the SPARQL query, nothing else

Question: {question}
"""
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    lines = [l for l in raw.split("\n") if not l.strip().startswith("What") and not l.strip().startswith("Question")]
    return "\n".join(lines).strip()

def run_query(sparql):
    try:
        results = g.query(sparql)
        rows = []
        for row in results:
            clean = [clean_uri(val) for val in row]
            rows.append("• " + " → ".join(clean))
        return rows if rows else ["No results found"]
    except Exception as e:
        return [f"Query error: {e}"]

def chat(question):
    if not question.strip():
        return ""
    sparql = generate_sparql(question)
    results = run_query(sparql)
    results_text = "\n".join(results[:20])
    return f"**Generated SPARQL:**\n```sparql\n{sparql}\n```\n\n**Results:**\n{results_text}"

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body {
    margin: 0 !important;
    padding: 0 !important;
    background: #f0f4f8 !important;
    font-family: 'Inter', sans-serif !important;
    color: #1a1a1a !important;
}

.gradio-container {
    max-width: 100% !important;
    width: 100% !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    background: #f0f4f8 !important;
}

.main-wrap {
    max-width: 720px;
    margin: 0 auto;
    padding: 24px 16px;
}

#header {
    background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%);
    border-radius: 20px;
    padding: 20px 24px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(26,82,118,0.25);
}

#header h1 {
    color: white !important;
    font-size: clamp(1.4rem, 4vw, 2rem) !important;
    font-weight: 700 !important;
    margin: 0 0 8px 0 !important;
    line-height: 1.2 !important;
}

#header p {
    color: #aed6f1 !important;
    font-size: clamp(0.8rem, 2.5vw, 0.95rem) !important;
    margin: 0 !important;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: 16px;
    flex-wrap: wrap;
}

.badge {
    background: rgba(255,255,255,0.15);
    color: white !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    border: 1px solid rgba(255,255,255,0.25);
}

#examples-section {
    margin-bottom: 16px;
}

#examples-label {
    color: #5d6d7e !important;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 10px;
}

.example-btn {
    background: white !important;
    border: 1.5px solid #d6eaf8 !important;
    border-radius: 20px !important;
    color: #2e86c1 !important;
    font-size: 0.83rem !important;
    padding: 8px 16px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    white-space: normal !important;
    text-align: center !important;
}

.example-btn:hover {
    background: #eaf4fb !important;
    border-color: #2e86c1 !important;
}

#input-section {
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

#input-box label {
    color: #1a1a1a !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    margin-bottom: 8px !important;
}

#input-box textarea {
    border-radius: 12px !important;
    border: 2px solid #d6eaf8 !important;
    font-size: 0.95rem !important;
    padding: 12px !important;
    background: #f8fbff !important;
    color: #1a1a1a !important;
    transition: border-color 0.2s !important;
    width: 100% !important;
    resize: none !important;
}

#input-box textarea:focus {
    border-color: #2e86c1 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(46,134,193,0.12) !important;
}

#input-box textarea::placeholder {
    color: #aab7c4 !important;
}

#submit-btn {
    background: linear-gradient(135deg, #1a5276, #2e86c1) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 14px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.1s !important;
    margin-top: 12px !important;
}

#submit-btn:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

#output-box {
    background: white !important;
    border-radius: 16px !important;
    border: 1.5px solid #d6eaf8 !important;
    padding: 24px !important;
    min-height: 120px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    color: #1a1a1a !important;
}

#output-box * {
    color: #1a1a1a !important;
}

#output-box code, #output-box pre {
    color: #e8e8e8 !important;
    background: #1e2a35 !important;
    border-radius: 8px !important;
}

#output-box pre code {
    color: #e8e8e8 !important;
}

#output-box label {
    color: #5d6d7e !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

footer { display: none !important; }

@media (max-width: 600px) {
    .main-wrap { padding: 16px 12px; }
    #header { padding: 24px 16px; border-radius: 16px; }
    .example-btn { font-size: 0.78rem !important; padding: 6px 12px !important; }
    #input-section { padding: 16px; }
    #output-box { padding: 16px !important; }
}
"""

with gr.Blocks(css=custom_css, title="ESG Ontology Chatbot") as demo:
    with gr.Column(elem_classes="main-wrap"):

        with gr.Column(elem_id="header"):
            gr.HTML("""
                <h1>🌿 ESG Ontology Chatbot</h1>
                <p>Ask questions about ESG data in natural language — powered by Groq + ESGOnt</p>
                <div class="badge-row">
                    <span class="badge">🤖 Groq API</span>
                    <span class="badge">🔗 ESGOnt</span>
                    <span class="badge">⚡ SPARQL</span>
                    <span class="badge">🐍 Python</span>
                </div>
            """)

        with gr.Column(elem_id="examples-section"):
            gr.HTML('<div id="examples-label">💡 Try these examples:</div>')
            with gr.Row():
                ex1 = gr.Button("What are the ESG domains?", elem_classes="example-btn")
                ex2 = gr.Button("What are all ESG categories?", elem_classes="example-btn")
                ex3 = gr.Button("What is Board Diversity a subclass of?", elem_classes="example-btn")

        with gr.Column(elem_id="input-section"):
            question = gr.Textbox(
                label="Your Question",
                placeholder="e.g. What are the ESG domains?",
                lines=2,
                elem_id="input-box"
            )
            submit = gr.Button("Ask ✦", elem_id="submit-btn")

        output = gr.Markdown(
            label="Answer",
            elem_id="output-box"
        )

    submit.click(fn=chat, inputs=question, outputs=output)
    question.submit(fn=chat, inputs=question, outputs=output)
    ex1.click(fn=lambda: "What are the ESG domains?", outputs=question)
    ex2.click(fn=lambda: "What are all ESG categories?", outputs=question)
    ex3.click(fn=lambda: "What is Board Diversity a subclass of?", outputs=question)

demo.launch(share=True)
