from dotenv import load_dotenv
load_dotenv()

import os
from google import genai
from rdflib import Graph

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
MODEL_ID = "gemini-3-flash-preview"

g = Graph()
g.parse("/workspaces/onto/esg-chatbot/esgontology.owl", format="xml")
print(f"Ontology loaded: {len(g)} triples")

def generate_sparql(question: str) -> str:
    prompt = f"""You are a SPARQL expert for the ESGOnt ontology.
PREFIX esg: <http://www.annasvijaya.com/ESGOnt/esgontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

ONTOLOGY STRUCTURE (very important):
- esg:Domain has subclasses: esg:Environmental, esg:Social, esg:Governance
- esg:Category has subclasses: esg:GHG_Emissions, esg:Board_Diversity, esg:Energy, esg:Corruption, esg:Waste, esg:Water, esg:Biodiversity, esg:Labor_Practices, esg:Human_Rights, etc.
- esg:Category and esg:Domain are separate hierarchies
- To find all ESG categories: SELECT ?c WHERE {{ ?c rdfs:subClassOf esg:Category }}
- To find all ESG domains: SELECT ?d WHERE {{ ?d rdfs:subClassOf esg:Domain }}
- To find all classes: SELECT ?c WHERE {{ ?c a owl:Class }}

Generate ONLY a valid SPARQL SELECT query. No explanation, no markdown, just the query.

Question: {question}
"""
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text.strip()

def run_query(sparql: str):
    try:
        results = g.query(sparql)
        rows = [str(row) for row in results]
        return rows if rows else ["No results found"]
    except Exception as e:
        return [f"Query error: {e}"]

def ask(question: str):
    print(f"\nQuestion: {question}")
    sparql = generate_sparql(question)
    print(f"\nGenerated SPARQL:\n{sparql}")
    results = run_query(sparql)
    print(f"\nResults:")
    for r in results[:15]:
        print(r)

if __name__ == "__main__":
    print("\n--- ESG Chatbot Ready ---")
    print("Type your question (or 'quit' to exit)\n")
    while True:
        q = input("You: ")
        if q.lower() == "quit":
            break
        ask(q)
