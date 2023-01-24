''' This file contains the definitions of reference tenants, which are currently implemented for FINALES2. If you do not find a tenant suitable for your application, please
create a new one and create a pull request in our repository to add it to the list of available tenants. '''

from ontopy import get_ontology
from emmopy import get_emmo

from dlite.triplestore import (
    en, Literal, Triplestore,
    EMMO, OWL, RDF, RDFS, SKOS, XSD,
)
import rdflib

#Load local copy of BattINFO
battinfo = get_ontology(r'C:\Users\MonikaVogler\Documents\BIG-MAP\FINALES2\BattINFO\battinfo.ttl').load()

# # Load ontology from the web
# battinfo = get_ontology('https://raw.githubusercontent.com/BIG-MAP/BattINFO/master/battinfo.ttl').load()

emmo = get_emmo()

triplestore = Triplestore("rdflib")
triplestore.parse(r'C:\Users\MonikaVogler\Documents\BIG-MAP\FINALES2\BattINFO\battery.ttl')

graph = rdflib.Graph()
graph.parse(r'C:\Users\MonikaVogler\Documents\BIG-MAP\FINALES2\BattINFO\battery.ttl')
print(len(graph))

graph.serialize(format='turtle')

for p in graph.predicates():
    print(p)

prop = rdflib.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf')
for predicate in graph.predicate_objects(rdflib.term.URIRef('https://big-map.github.io/BattINFO/ontology/BattINFO#EMMO_17b3beaa_6f91_4f73_8a9a_d960eb542b7e')):
    print(predicate)
print('--------------------------------------')

for predicate in graph.subject_objects(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel')):
    print(predicate)
    print(predicate[0].isprintable())
print('--------------------------------------')

# print(BI)
g = rdflib.Graph()
g.parse(r'C:\Users\MonikaVogler\Documents\BIG-MAP\FINALES2\BattINFO\battinfo.ttl')
print(len(g))

for s, p, o in g:
    print(s,'\t', p, '\t', o, '\n')

print(g.serialize(format="turtle"))
predicate = rdflib.URIRef("http://purl.org/dc/terms/creator")
for p in g.objects(predicate=predicate):
    print(p)


# TG = rdflib.Graph(triplestore)
# print(TG.serialize(format='turtle'))

batteryGraph = rdflib.Graph(triplestore)
SO = triplestore.subject_objects(predicate="Battery")

type(g)

battinfo.ElectrolyteSolution



'''-----------------------------------------------'''
from dlite.triplestore import Triplestore

HASPART = "http://emmo.info/emmo#EMMO_17e27c22_37e1_468c_9dd7_95e137f73e7f"
property = "https://big-map.github.io/BattINFO/ontology/BattINFO#EMMO_b7fdab58_6e91_4c84_b097_b06eff86a124"

ts = Triplestore("rdflib") 
ts.parse('Desktop/Ontology.ttl')
print(len(list(ts.subjects())))

x = ts.predicate_objects(subject=property)
print(list(x))



# battinfo = get_ontology('https://raw.githubusercontent.com/BIG-MAP/FAIRBatteryData/main/examples/ontologies/battinfo-merged.ttl').load() # -> use Triplestore from DLite


'''
Find IRI:
1) open Protege
2) open BattINFO
3) search option
4) enter desired thing
5) right click "copy IRI" or at the top
'''



def iri_to_preflabel(ts:Triplestore, iri:str)-> str:
    """
    Queries the triplestore for the IRI supplied, and retrievies its prefLabel if it exists.

    ts: Triplestore
        Triplestore object.
    iri: str
        IRI of the enetity.

    Eibar Flores, 2022, SINTEF Industry
    """
   
    prefLabel = list(ts.objects(subject=iri, predicate=SKOS.prefLabel))

    if len(prefLabel) == 1:
        return prefLabel[0].value

    else:
        warnings.warn(f"""The supplied IRI {iri} has {len(list(prefLabel))} prefLabels: {list(prefLabel)}""")
        return ""



from dlite.triplestore import Triplestore

HASPART = "http://emmo.info/emmo#EMMO_17e27c22_37e1_468c_9dd7_95e137f73e7f"
battery_electrode = "http://emmo.info/emmo#EMMO_17e27c22_37e1_44335_54337f73"

ts = Triplestore("rdflib") 
ts.parse(path_to_battinfo)

my_list = ts.subjects(predicate =HASPART, object = battery_electrode)

print(my_list)
> ["http://emmo.info/emmo#EMMO_17e27c22_37e1_44335_54337f73", "http://emmo.info/emmo#EMMO_17e27c22_37e1_44335_54337f73", "http://emmo.info/emmo#EMMO_17e27c22_37e1_44335_54337f73"]

for iri in my_list:
    labels = []
    label = get_label(iri)
    labels.append(label)

print(labels)
> ["PrismaticCell", "CoinCell", "CylindricalCell"]