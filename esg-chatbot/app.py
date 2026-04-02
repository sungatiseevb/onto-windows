import os
import gradio as gr
from groq import Groq
from rdflib import Graph

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL_ID = "llama-3.3-70b-versatile"

g = Graph()
g.parse("/workspaces/onto/esg-chatbot/esgontology.owl", format="xml")
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

body, .gradio-container {
    font-family: 'Inter', sans-serif !important;
    background-color: #f0f4f8 !important;
}

.gradio-container {
    max-width: 860px !important;
    margin: 0 auto !important;
}

#header {
    background: linear-gradient(135deg, #1a5276, #2e86c1);
    border-radius: 16px;
    padding: 32px;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(26,82,118,0.3);
}

#header h1 {
    color: white !important;
    font-size: 1.8rem !important;
    font-weight: 600 !important;
    margin: 0 0 8px 0 !important;
}

#header p {
    color: #aed6f1 !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 14px;
    flex-wrap: wrap;
}

.badge {
    background: rgba(255,255,255,0.15);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    border: 1px solid rgba(255,255,255,0.25);
}

#input-box textarea {
    border-radius: 12px !important;
    border: 2px solid #d6eaf8 !important;
    font-size: 0.95rem !important;
    padding: 12px !important;
    background: white !important;
    color: #1a1a1a !important;
    transition: border-color 0.2s;
}

#input-box textarea:focus {
    border-color: #2e86c1 !important;
    box-shadow: 0 0 0 3px rgba(46,134,193,0.15) !important;
}

#submit-btn {
    background: linear-gradient(135deg, #1a5276, #2e86c1) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 12px 28px !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
}

#submit-btn:hover {
    opacity: 0.88 !important;
}

#output-box {
    background: white !important;
    color: #1a1a1a !important;
    border-radius: 12px !important;
    border: 1px solid #d6eaf8 !important;
    padding: 20px !important;
    min-height: 160px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}

#examples-label {
    color: #5d6d7e;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 8px;
}

.example-btn {
    background: white !important;
    color: #1a1a1a !important;
    border: 1px solid #d6eaf8 !important;
    border-radius: 20px !important;
    color: #2e86c1 !important;
    font-size: 0.83rem !important;
    padding: 6px 14px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
}

.example-btn:hover {
    background: #d6eaf8 !important;
}

footer { display: none !important; }

* { color: #1a1a1a; }
label { color: #1a1a1a !important; }
.prose * { color: #1a1a1a !important; }
"""

with gr.Blocks(css=custom_css, title="ESG Ontology Chatbot") as demo:

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

    with gr.Column():
        gr.HTML('<div id="examples-label">💡 Try these examples:</div>')
        with gr.Row():
            ex1 = gr.Button("What are the ESG domains?", elem_classes="example-btn")
            ex2 = gr.Button("What are all ESG categories?", elem_classes="example-btn")
            ex3 = gr.Button("What is Board Diversity a subclass of?", elem_classes="example-btn")

    with gr.Column():
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
