#!/usr/bin/env python3
"""Check the selected table, residual homology and finite positive set.

This is a check of retained evidence and finite objects, not a census rerun.
The large-universe coverage assertions are inspected as records only.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'finite/certificates'))
sys.path.insert(0,str(ROOT/'tools'))
from finite_checks import decode, encode, edge, h1, cliques, components, isomorphic, tree, induced
from finite_isomorphism import pairwise_nonisomorphic, unique_inclusions
from check_disc_hypotheses import GRAPHS

def csvrows(path):
    with path.open() as stream:
        return list(csv.DictReader(line for line in stream if not line.startswith('#')))

def main():
    table=csvrows(ROOT/'data/cardinalities.csv')
    assert [int(r['n']) for r in table]==list(range(3,15))
    names=['connected','chi1','acyclic_F2','acyclic_Z','I','I_S','I_SV',
           '3_Dis','2_Dis','1_Dis','0_Dis','cones']
    byorder={int(r['n']):r for r in table}
    for n,r in byorder.items():
        assert set(r)=={'n','universe',*names}
        assert r['universe']==('connected_K4_free' if n==14 else 'connected')
        values={k:int(r[k]) for k in names}
        chain=[values[k] for k in names]
        assert all(a>=b for a,b in zip(chain,chain[1:]))
        assert values['acyclic_Z']==values['I']
    old=csvrows(ROOT/'data/table_cardinalities.csv')
    assert [int(r['n']) for r in old] == list(range(3,14))
    mapping={'connected':'connected','chi=1':'chi1','Z2-acyclic':'acyclic_F2',
             'I-contractible':'I','strong I-contractible (J_S)':'I_S','J_SV':'I_SV',
             '3-Dis':'3_Dis','2-Dis':'2_Dis','1-Dis':'1_Dis','0-Dis':'0_Dis','(-1)-Dis':'cones'}
    for row in old:
        current=byorder[int(row['n'])]
        assert all(int(row[a])==int(current[b]) for a,b in mapping.items())
    row14,=csvrows(ROOT/'data/table_row14_K4free.csv')
    map14={'Z2_acyclic':'acyclic_F2',**{x:x for x in names if x not in ['acyclic_F2','acyclic_Z']}}
    assert all(int(row14[a])==int(byorder[14][b]) for a,b in map14.items())
    countmap={'conexas':'connected','chi1':'chi1','aciclicas':'acyclic_F2',
              'I':'I','I_S':'I_S','I_SV':'I_SV','3-Dis':'3_Dis','2-Dis':'2_Dis',
              '1-Dis':'1_Dis','0-Dis':'0_Dis','-1-Dis':'cones'}
    raw_reference=csvrows(ROOT/'data/raw_classifier_reference.csv')
    assert [int(r['n']) for r in raw_reference]==list(range(3,15))
    rawmap={**mapping,'J_VS':'I_SV'}
    rawmap.pop('J_SV')
    for row in raw_reference:
        current=byorder[int(row['n'])]
        assert all(int(row[a])==int(current[b]) for a,b in rawmap.items())
        assert int(row['I-undecided'])==int(current['acyclic_F2'])-int(current['I'])
    aggregates={12:'F2_12',13:'F2_13',14:'F4'}
    aggregate_records={}
    for n,tag in aggregates.items():
        record=json.loads((ROOT/f'data/census/{tag}_aggregate.json').read_text())
        aggregate_records[n]=record
        assert record['ok'] and not record['problems']
        assert record['coverage']==record['mod'] and record['n']==n
        assert all(x['equal'] for x in record['comparison'].values())
        assert all(record['counts'][a]==int(byorder[n][b]) for a,b in countmap.items())
    residual_counts={}
    residual_graphs={}
    for n,tag,expected in [(13,'F2_13',3),(14,'F4',625)]:
        lines=(ROOT/f'data/census/{tag}_residual.g6').read_text().splitlines()
        records=[json.loads(line) for line in (ROOT/f'data/census/{tag}_adjudications.jsonl').read_text().splitlines()]
        assert len(lines)==len(set(lines))==len(records)==expected
        assert set(lines)=={r['g6'] for r in records}
        for record in records:
            assert record['PASS'] and record['nontrivial_integer_homology']
            A=decode(record['g6'])
            assert len(A)==n and components(A)==1 and not cliques(A,4)
            f=[len(cliques(A,k)) for k in (1,2,3)]
            assert f==record['integer_homology']['face_counts'] and f[0]-f[1]+f[2]==1
            assert h1(A)==(0,(3,))
            assert record['integer_homology']['reduced_homology']==[
                {'dimension':0,'free_rank':0,'torsion':[]},
                {'dimension':1,'free_rank':0,'torsion':[3]},
                {'dimension':2,'free_rank':0,'torsion':[]}]
        assert int(byorder[n]['acyclic_F2'])-int(byorder[n]['acyclic_Z'])==expected
        assert aggregate_records[n]['counts']['aciclicas']-aggregate_records[n]['counts']['I']==expected
        assert aggregate_records[n]['counts']['I_indecisas']==expected
        residual_counts[str(n)]=expected
        residual_graphs[n]=lines
    positives=(ROOT/'data/census/F4_positive.g6').read_text().splitlines()
    expected=list(csv.DictReader((ROOT/'finite/data/K4_free_I_not_strong_14.tsv').open(),delimiter='\t'))
    assert len(positives)==len(expected)==8
    remaining=list(expected)
    for graph in positives:
        A=decode(graph);matches=[r for r in remaining if isomorphic(A,decode(r['graph6']))]
        assert len(matches)==1;remaining.remove(matches[0])
    assert not remaining and int(byorder[14]['I'])-int(byorder[14]['I_S'])==8
    assert aggregate_records[14]['counts']['I']-aggregate_records[14]['counts']['I_S']==len(positives)

    # Link the independently generated seed and table universes exactly.
    residual14_distinct=pairwise_nonisomorphic(residual_graphs[14])
    seeds=list(csv.DictReader((ROOT/'finite/data/stuck_14_K4free.tsv').open(),delimiter='\t'))
    raw_seeds=(ROOT/'data/census/F3_stuck.g6').read_text().splitlines()
    assert len(raw_seeds)==len(seeds)==51
    seed_catalogue_matches=unique_inclusions(raw_seeds,[r['graph6'] for r in seeds])
    torsion_seeds=[r['graph6'] for r in seeds if r['H1_Z']=='Z/3']
    positive_seeds=[r['graph6'] for r in seeds if r['H1_Z']=='trivial']
    assert len(torsion_seeds)==48 and len(positive_seeds)==3
    assert set(positive_seeds)=={GRAPHS[name] for name in ('G14a','G14b','G14c')}
    torsion_seed_matches=unique_inclusions(torsion_seeds,residual_graphs[14])
    positive_seed_matches=unique_inclusions(positive_seeds,positives)
    G=decode(GRAPHS['G13']);variants=[encode(G)]
    for u,v in ((4,7),(5,6)):
        assert not G[u]>>v&1 and G[u]&G[v]==1<<12
        G=edge(G,u,v,True);variants.append(encode(G))
    assert all(not cliques(decode(g),4) for g in variants)
    variants13_matches=unique_inclusions(residual_graphs[13],variants)
    # Independent finite cross-check of the seed census within the 633 exceptions.
    # It supplements the seed enumeration; it does not replace its coverage proof.
    stuck_in_exceptional_set=[]
    stuck_positive=[]
    for graph in residual_graphs[14]+positives:
        A=decode(graph)
        assert len(A)==14 and components(A)==1 and not cliques(A,4)
        if graph in positives:
            assert h1(A)==(0,()) and len(A)-len(cliques(A,2))+len(cliques(A,3))==1
        if any(tree(induced(A,row)) for row in A):
            continue
        if any((A[u]&A[v]).bit_count()==1 for u,v in cliques(A,2)):
            continue
        stuck_in_exceptional_set.append(graph)
        if graph in positives:
            stuck_positive.append(graph)
    assert len(stuck_in_exceptional_set)==51 and len(stuck_positive)==3
    stuck_exception_matches=unique_inclusions(stuck_in_exceptional_set,raw_seeds)
    stuck_positive_matches=unique_inclusions(stuck_positive,positive_seeds)
    sources=['data/census/F3_stuck.g6','finite/data/stuck_14_K4free.tsv',
             'data/census/F2_13_residual.g6','data/census/F4_residual.g6',
             'data/census/F4_positive.g6','data/census/F4_aggregate.json',
             'finite/certificates/check_disc_hypotheses.py','tools/finite_isomorphism.py']
    print(json.dumps({'PASS':True,'table_counts_checked':144,'rows':12,
        'residual_H1_recomputed':residual_counts,'positive_set_isomorphism_checks':8,
        'order14_residual_nonisomorphism':residual14_distinct,
        'seed_catalogue_matches':len(seed_catalogue_matches),
        'torsion_seeds_in_625_residuals':torsion_seed_matches,
        'contractible_seeds_in_eight_positives':positive_seed_matches,
        'order13_residuals_match_constructed_variants':variants13_matches,
        'order13_constructed_variants_K4_counts':[len(cliques(decode(g),4)) for g in variants],
        'stuck_members_of_633_exceptional_graphs_match_51_seeds':len(stuck_exception_matches),
        'stuck_positive_members_match_three_contractible_seeds':stuck_positive_matches,
        'residual_count_matches_raw_acyclic_minus_certified_I':True,
        'cross_check_source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
        'integral_column':'derived from finite adjudication and recorded exhaustive partition',
        'coverage_evidence':'retained aggregate records; receipts not reprocessed',
        'full_census_rerun':False},indent=2))

if not __debug__: raise RuntimeError('Run without -O: assertions are required.')
if __name__=='__main__':main()
