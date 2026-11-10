#!/usr/bin/env python3
"""Recompute all local links, G13 successors, and four finite reduction traces.

All certificate fields are compared or tested; no file is written. Python stdlib.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import csv,json
from itertools import combinations
sys.path.insert(0, str(Path(__file__).resolve().parent))
from finite_checks import *
from check_disc_hypotheses import GRAPHS
ROOT=Path(__file__).resolve().parents[1]

def local_graph(A,vs): return induced(A,sum(1<<v for v in vs))
def present_edges(A,vs): return [[u,v] for u,v in combinations(sorted(vs),2) if A[u]>>v&1]

def check_links():
    records=[]
    for name,s in GRAPHS.items():
        A=decode(s); links=[]
        for u in range(len(A)):
            L=induced(A,A[u]); assert not cliques(L,3)
            links.append([u,len(L),len(cliques(L,2)),len(cliques(L,2))-len(L)+components(L)])
        records.append({'name':name,'g6':s,'links':links,'edge_link_sizes':sorted({(A[u]&A[v]).bit_count() for u,v in cliques(A,2)})})
    assert records==json.loads((ROOT/'certificates/link_checks.json').read_text())
    return sum(len(r['links']) for r in records)

def check_g13():
    A=decode(GRAPHS['G13']); paths=[[],[[4,7]],[[4,7],[5,6]]]; result=[]
    for path in paths:
        B=A
        for u,v in path: B=edge(B,u,v,True)
        allowed=[[u,v,vertices(B[u]&B[v])] for u,v in combinations(range(len(B)),2)
                 if not B[u]>>v&1 and strong(induced(B,B[u]&B[v]))]
        result.append({'added':path,'IS_admissible':allowed})
    assert isomorphic(edge(A,4,7,True),edge(A,5,6,True))
    assert result==json.loads((ROOT/'certificates/G13_successors.json').read_text())
    return len(result)

def check_traces():
    records=json.loads((ROOT/'certificates/certificate_replay.json').read_text()); expected=[]
    seeds=[GRAPHS[k] for k in ('G14a','G14b','G14c','D15')]
    edges=[[0,1],[0,3],[2,3],[9,12]]; figure_names=['S1','S2','S3',None]
    assert len(records)==4
    for r,seed,added,fig in zip(records,seeds,edges,figure_names):
        assert set(r)=={'g6','added_edge','steps','last_vertex'} and r['g6']==seed and r['added_edge']==added
        A=decode(seed); u,v=added; assert not A[u]>>v&1
        assert strong(induced(A,A[u]&A[v])) and not strong(A)
        A=edge(A,u,v,True); active=set(range(len(A)))
        for i,s in enumerate(r['steps'],1):
            assert set(s)=={'step','kind','element','link_vertices','link_edges','link_certificate','tree'} and s['step']==i
            if s['kind']=='vertex':
                u=s['element']; assert u in active; vs=sorted(set(vertices(A[u]))&active)
            else:
                assert s['kind']=='edge'; u,v=s['element']; assert u in active and v in active and A[u]>>v&1
                vs=sorted(set(vertices(A[u]&A[v]))&active)
            L=local_graph(A,vs)
            assert s['link_vertices']==vs and s['link_edges']==present_edges(A,vs)
            assert s['tree'] is tree(L) and strong(L)
            local=set(vs)
            for op in s['link_certificate']:
                assert len(op)==2 and op[0]=='v' and op[1] in local
                z=op[1]; N=sorted(set(vertices(A[z]))&local)
                assert strong(local_graph(A,N)); local.remove(z)
            assert len(local)==1
            if fig:
                expected.append({'figure':fig,'step':str(i),'operation':s['kind'],
                    'vertices':','.join(map(str,[s['element']] if s['kind']=='vertex' else s['element'])),
                    'current_neighbourhood':','.join(map(str,vs)),
                    'criterion':'K1' if len(L)==1 else 'cone' if cone(L) else '0-Dis' if kdis(L,0) else 'strong'})
            if s['kind']=='vertex': active.remove(s['element'])
            else: A=edge(A,*s['element'],False)
        assert active=={r['last_vertex']}
    rows=list(csv.DictReader((ROOT/'figures/trace_steps.tsv').open(),delimiter='\t'))
    assert rows==expected
    return [len(r['steps']) for r in records]

def main():
    print(json.dumps({'vertex_links':check_links(),'G13_successor_states':check_g13(),
      'trace_steps':check_traces(),'all_fields_checked':True},indent=2))
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
if __name__=='__main__': main()
