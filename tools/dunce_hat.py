import itertools, networkx as nx
T = [(1,4,13),(1,13,12),(1,12,11),(1,11,4),(4,3,13),(3,13,14),(13,14,15),(13,15,12),(12,15,11),(11,15,10),(11,10,3),(4,11,3),
     (3,14,5),(14,5,15),(3,5,2),(2,5,1),(1,5,6),(5,6,15),(1,6,7),(6,7,15),(1,7,2),(2,7,3),(7,3,8),(7,8,15),(8,15,9),(15,9,10),
     (10,9,2),(3,10,2),(8,9,4),(3,8,4),(9,4,1),(9,2,1)]
G=nx.Graph()
for t in T:
    for a,b in itertools.combinations(t,2): G.add_edge(a,b)
print("V=",G.number_of_nodes(),"E=",G.number_of_edges(),"triangulos dados=",len(T))
tri=[c for c in nx.enumerate_all_cliques(G) if len(c)==3]; k4=[c for c in nx.enumerate_all_cliques(G) if len(c)==4]
print("triangulos del complejo de cliques=",len(tri),"K4=",len(k4))
# multiplicidad de aristas en triángulos
from collections import Counter
cnt=Counter()
for t in T:
    for a,b in itertools.combinations(t,2): cnt[frozenset((a,b))]+=1
print("aristas por #triangulos:",Counter(cnt.values()))
H=nx.relabel_nodes(G,{v:v-1 for v in G.nodes()})
g6=nx.to_graph6_bytes(H,header=False).decode().strip()
print(g6)
G2=G.copy(); G2.add_edge(5,7)
H2=nx.relabel_nodes(G2,{v:v-1 for v in G2.nodes()})
print(nx.to_graph6_bytes(H2,header=False).decode().strip())
open('dunce.g6','w').write(g6+"\n"+nx.to_graph6_bytes(H2,header=False).decode().strip()+"\n")
