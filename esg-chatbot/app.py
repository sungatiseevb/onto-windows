import os
import gradio as gr
from google import genai
from rdflib import Graph, URIRef

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
MODEL_ID = "gemini-3-flash-preview"

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
PREFIX esg: <http://www.annasvijaya.com/ESGOnt/esgontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

ONTOLOGY STRUCTURE:
- esg:Domain has subclasses: esg:Environmental, esg:Social, esg:Governance
- esg:Category has subclasses: esg:GHG_Emissions, esg:Board_Diversity, esg:Energy, esg:Corruption, esg:Waste, esg:Water, esg:Biodiversity, esg:Labor_Practices, esg:Human_Rights, etc.

Generate ONLY a valid SPARQL SELECT query. No explanation, no markdown, just the query.

Question: {question}
"""
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text.strip()

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
    sparql = generate_sparql(question)
    results = run_query(sparql)
    results_text = "\n".join(results[:20])
    return f"**SPARQL Query:**\n```sparql\n{sparql}\n```\n\n**Results:**\n{results_text}"

demo = gr.Interface(
    fn=chat,
    inputs=gr.Textbox(label="Ask about ESG data", placeholder="e.g. What are the ESG domains?"),
    outputs=gr.Markdown(label="Answer"),
    title="ESG Ontology Chatbot",
    description="Ask questions about ESG data in natural language. Powered by Gemini + ESGOnt.",
    examples=[
        ["What are the ESG domains?"],
        ["What are all ESG categories?"],
        ["What is Board Diversity a subclass of?"],
    ]
)

demo.launch(share=True)
