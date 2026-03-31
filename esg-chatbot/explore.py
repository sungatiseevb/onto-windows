from rdflib import Graph, RDF, RDFS, OWL

g = Graph()
g.parse("esgontology.owl", format="xml")

print(f"Триплов: {len(g)}")
print()

print("=== КЛАССЫ ===")
classes = list(g.subjects(RDF.type, OWL.Class))
for c in classes[:30]:
    label = g.value(c, RDFS.label)
    name = str(c).split('#')[-1].split('/')[-1]
    print(f"  {name} {f'({label})' if label else ''}")

print()
print("=== СВЯЗИ ===")
props = list(g.subjects(RDF.type, OWL.ObjectProperty))
for p in props[:20]:
    name = str(p).split('#')[-1].split('/')[-1]
    print(f"  {name}")
