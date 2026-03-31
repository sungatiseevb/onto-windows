import os
from groq import Groq
from rdflib import Graph

g = Graph()
g.parse("esgontology.owl", format="xml")
print(f"Онтология загружена: {len(g)} триплов\n")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ONTOLOGY_CONTEXT = """You are a SPARQL query generator for the ESGOnt ontology.
Namespace: http://www.annasvijaya.com/ESGOnt/esgontologi#
Prefix: PREFIX esg: <http://www.annasvijaya.com/ESGOnt/esgontologi#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

Classes: Board_Diversity, GHG_Emissions, Energy, Corruption, Category, Domain, SDG, CausalRelationship, Organization
Properties: contributesTo, hasCategory, hasCause, consumesEnergy, generatesWaste, belongsToCategory

Rules:
- Generate ONLY a valid SPARQL SELECT query
- Always include PREFIX declarations
- No explanation, no markdown, no code blocks
- Just the raw SPARQL query"""

def ask(question):
    print(f"Вопрос: {question}")
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": ONTOLOGY_CONTEXT},
            {"role": "user", "content": f"Generate SPARQL query for: {question}"}
        ],
        temperature=0
    )
    
    sparql = response.choices[0].message.content.strip()
    print(f"SPARQL:\n{sparql}\n")
    
    try:
        results = list(g.query(sparql))
        print(f"Результатов: {len(results)}")
        for row in results[:10]:
            vals = [str(v).split('#')[-1].split('/')[-1] for v in row if v]
            print(f"  {' | '.join(vals)}")
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    print()

ask("What classes are related to environmental impact?")
ask("What properties does Board_Diversity have?")
ask("What SDGs are linked to GHG emissions?")
