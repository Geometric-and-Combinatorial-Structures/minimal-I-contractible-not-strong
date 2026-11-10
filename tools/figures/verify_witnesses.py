#!/usr/bin/env python3
"""Independent local checks of the finite data printed in the new manuscript.

Requires networkx and sympy. Computes homology through a spanning-tree cycle
basis, replays reductions on full graph states, and checks the disc attachment
order. This is not a repetition of any census.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import copy
import hashlib
import json
import re

import networkx as nx
import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ
from make_witness_figures import ROOT, DATA, unfold

REPORT = ROOT / 'build' / 'verification' / 'witnesses'


def edgeset(g):
    return {tuple(sorted(e)) for e in g.edges()}


def homology(g):
    assert nx.is_connected(g)
    cliques = list(nx.enumerate_all_cliques(g))
    assert max(map(len, cliques)) <= 3
    tris = [tuple(sorted(t)) for t in cliques if len(t) == 3]
    tree = nx.minimum_spanning_tree(g)
    chord_edges = sorted(edgeset(g) - edgeset(tree))
    index = {e: i for i, e in enumerate(chord_edges)}
    boundary = sp.zeros(len(chord_edges), len(tris))
    for j, (a, b, c) in enumerate(tris):
        for e, sign in [((a, b), 1), ((a, c), -1), ((b, c), 1)]:
            if e in index:
                boundary[index[e], j] = sign
    smith = smith_normal_form(boundary, domain=ZZ)
    diagonal = [abs(int(smith[i, i])) for i in range(min(smith.shape)) if smith[i, i]]
    rank = len(diagonal)
    return {'reduced_H0_rank': 0, 'H1_free_rank': len(chord_edges)-rank,
            'H1_torsion': [x for x in diagonal if x > 1],
            'H2_rank': len(tris)-rank, 'higher_groups': 'zero (no higher simplices)',
            'face_vector': [len(g), g.number_of_edges(), len(tris)]}


def replay(g, reduction):
    h = g.copy()
    e = tuple(reduction['added_edge'])
    assert not h.has_edge(*e)
    n = set(h[e[0]]) & set(h[e[1]])
    assert n and nx.is_tree(h.subgraph(n))
    h.add_edge(*e)
    observations = []
    for number, s in enumerate(reduction['steps'], 1):
        assert number == s['step']
        if s['kind'] == 'edge':
            a, b = s['element']; assert h.has_edge(a, b)
            n = set(h[a]) & set(h[b])
        else:
            a = s['element']; assert a in h
            n = set(h[a])
        link = h.subgraph(n)
        assert sorted(n) == s['link_vertices']
        assert edgeset(link) == set(map(tuple, s['link_edges']))
        assert n and nx.is_tree(link)
        observations.append({'step': number, 'vertices': len(link), 'edges': link.number_of_edges(), 'tree': True})
        if s['kind'] == 'edge': h.remove_edge(*s['element'])
        else: h.remove_node(s['element'])
    assert list(h) == [13] and h.number_of_edges() == 0
    return observations


def disk_checks(data):
    g = data['graphs']['G13']; label, tris, counts = unfold(g['n'], g['edges'])
    order = [1,2,4,3,5,6,8,7,10,9,11,12,14,13,16,15,17,18,20,19,22,21,23,24,25,26,27,28]
    assert sorted(order) == list(range(1, 29))
    current_vertices = set(tris[0]); current_edges = Counter(tuple(sorted(e)) for e in combinations(tris[0],2))
    gluing_lengths = []
    for j in order[1:]:
        tri = tris[j-1]; es = [tuple(sorted(e)) for e in combinations(tri,2)]
        shared = [e for e in es if e in current_edges]
        assert len(shared) in (1,2)
        assert all(current_edges[e] == 1 for e in shared)
        assert set(tri) & current_vertices == set(v for e in shared for v in e)
        gluing_lengths.append(len(shared)); current_vertices.update(tri); current_edges.update(es)
    assert current_edges == counts
    boundary = nx.Graph([e for e, n in counts.items() if n == 1])
    assert nx.is_connected(boundary) and all(d==2 for _,d in boundary.degree())
    start = max(boundary, key=lambda v:data['positions']['G13_disc'][str(v)][1])
    cycle, prev = [start], None
    while True:
        nxt = min(set(boundary[cycle[-1]]) - {prev})
        if nxt == start: break
        prev = cycle[-1];cycle.append(nxt)
    if [label[v] for v in cycle[:4]] != [10,9,11,8]:cycle=[cycle[0]]+cycle[:0:-1]
    word=[label[v] for v in cycle];assert word==[10,9,11,8]*3
    original = nx.Graph(g['edges']); original.add_nodes_from(range(g['n']))
    original_triangles = {tuple(sorted(t)) for t in nx.enumerate_all_cliques(original) if len(t)==3}
    images=[tuple(sorted(label[v] for v in tri)) for tri in tris]
    assert len(images)==len(set(images)) and set(images)==original_triangles
    interior=set(label)-set(boundary)
    all_labels=Counter(label.values())
    assert all(all_labels[label[v]]==1 for v in interior)
    image_edges=Counter(tuple(sorted(label[v] for v in e)) for e in counts)
    assert all(image_edges[tuple(sorted(label[v] for v in e))]==1 for e,n in counts.items() if n==2)
    assert set(image_edges)==edgeset(original)
    # Every vertex link is a path (boundary) or cycle (interior).
    for v in label:
        link=nx.Graph([tuple(x for x in tri if x!=v) for tri in tris if v in tri])
        assert nx.is_connected(link)
        degrees=sorted(d for _,d in link.degree())
        if v in boundary: assert degrees==[1,1]+[2]*(len(link)-2)
        else: assert all(d==2 for d in degrees)
    return {'face_vector':[len(label),len(counts),len(tris)],'boundary_word':word,
            'attachment_order':order,'glued_boundary_edges_at_each_step':gluing_lengths,
            'disk_proved_by_attachments':True,'interior_injective':True,
            'quotient_matches_all_cliques':True}


def main():
    data=json.loads(DATA.read_text()); graphs={}
    results={'scope':'local finite witnesses; no census or remote computation',
             'input_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(), 'graphs':{},'reductions':{},'mutation_tests':{}}
    expected_betti={'G13':[1]*8+[2]*4+[1],
                    'Ga':[1,1,1,1,1,2,1,1,1,2,2,1,2,2],
                    'Gb':[1,1,1,1,1,2,1,2,2,2,1,1,1,3],
                    'Gc':[2,1,1,1,1,1,1,2,1,2,2,2,1,2]}
    for name,item in data['graphs'].items():
        g=nx.Graph();g.add_nodes_from(range(item['n']));g.add_edges_from(item['edges'])
        assert edgeset(g)==edgeset(nx.from_graph6_bytes(item['original_graph6'].encode()))
        graphs[name]=g
        h=homology(g)
        assert h['H1_torsion']==([3] if name=='G13' else [])
        assert h['H1_free_rank']==h['H2_rank']==0
        betti=[]
        for v in g:
            link=g.subgraph(g[v]);assert nx.is_connected(link)
            assert all(len(c)<3 for c in nx.enumerate_all_cliques(link))
            betti.append(link.number_of_edges()-len(link)+1)
        assert betti==expected_betti[name]
        edge_sizes=sorted({len(set(g[a])&set(g[b])) for a,b in g.edges})
        assert min(edge_sizes)>=2
        results['graphs'][name]={**h,'vertex_link_betti1':betti,'edge_link_sizes':edge_sizes}
    variants=[];g=graphs['G13'].copy()
    for a,b in [(4,7),(5,6)]:
        assert set(g[a])&set(g[b])=={12};g.add_edge(a,b)
        h=homology(g);assert h['H1_torsion']==[3] and h['H1_free_rank']==h['H2_rank']==0
        variants.append(h)
    results['G13_variants']=variants
    for name,red in zip(['Ga','Gb','Gc'],data['reductions']):
        results['reductions'][name]=replay(graphs[name],red)
    results['G13_disk']=disk_checks(data)
    # Reject an incomplete reduction rather than accepting its proper prefix.
    short=copy.deepcopy(data['reductions'][0]);short['steps'].pop()
    try:replay(graphs['Ga'],short)
    except AssertionError:results['mutation_tests']['truncated_reduction']='rejected'
    else:raise AssertionError('truncated reduction accepted')
    wrong=copy.deepcopy(data['reductions'][0]);wrong['steps'][0]['link_vertices']=[1,10]
    try:replay(graphs['Ga'],wrong)
    except AssertionError:results['mutation_tests']['altered_neighbourhood']='rejected'
    else:raise AssertionError('wrong local neighbourhood accepted')
    panel=(ROOT/'paper/figures/G13_graph.tex').read_text()
    emitted=[tuple(map(int,m)) for m in re.findall(r'\\draw\[[^\n]+\] \(v(\d+)\) -- \(v(\d+)\);',panel)]
    assert set(emitted)==edgeset(graphs['G13']) and len(emitted)==len(set(emitted))
    assert set(emitted[:-1])!=edgeset(graphs['G13'])
    results['mutation_tests']['missing_emitted_edge']='rejected by edge-set equality'
    results['status']='PASS'
    REPORT.mkdir(parents=True,exist_ok=True)
    (REPORT/'finite_verification.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'status':'PASS','graphs':results['graphs'],'mutation_tests':results['mutation_tests']},indent=2))


if __name__=='__main__':main()
