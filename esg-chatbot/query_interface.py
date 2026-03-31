import os
from rdflib import Graph, RDF, RDFS, OWL

g = Graph()
g.parse("esgontology.owl", format="xml")
print(f"Онтология загружена: {len(g)} триплов\n")

# Заготовленные SPARQL запросы (имитируем что LLM генерирует)
PREDEFINED = {
    "what classes exist": """
        SELECT ?class ?label WHERE {
            ?class rdf:type owl:Class .
            OPTIONAL { ?class rdfs:label ?label }
        } LIMIT 20
    """,
    "what properties does board diversity have": """
        SELECT ?prop ?val WHERE {
            ?s rdfs:label "Board_Diversity" .
            ?s ?prop ?val .
        } LIMIT 10
    """,
    "what is related to environment": """
        SELECT ?class WHERE {
            ?class rdf:type owl:Class .
            FILTER(CONTAINS(STR(?class), "Emission") || 
                   CONTAINS(STR(?class), "Energy") ||
                   CONTAINS(STR(?class), "Water") ||
                   CONTAINS(STR(?class), "Waste"))
        }
    """,
}

def ask(question):
    q = question.lower().strip()
    print(f"Вопрос: {question}")
    
    # Находим подходящий запрос
    sparql = None
    for key, query in PREDEFINED.items():
        if any(word in q for word in key.split()):
            sparql = query
            break
    
    if not sparql:
        print("Ответ: Вопрос не распознан. Попробуй: 'what classes exist', 'what is related to environment'\n")
        return

    try:
        results = list(g.query(sparql))
        print(f"Результатов: {len(results)}")
        for row in results[:10]:
            vals = [str(v).split('#')[-1].split('/')[-1] for v in row if v]
            print(f"  {' | '.join(vals)}")
    except Exception as e:
        print(f"Ошибка: {e}")
    print()

# Тесты
ask("What classes exist in the ontology?")
ask("What is related to environment?")
ask("What properties does board diversity have?")
