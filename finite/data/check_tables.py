#!/usr/bin/env python3
"""Read-only semantic checks of every column of the graph TSV tables.

Integral H1 uses integer Smith reduction. Closure homology is recomputed for
all represented graphs; classification is additionally tied to seed certificates.
No enumeration of a larger universe is claimed by this finite check.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'certificates'))
from finite_checks import *
from check_disc_hypotheses import GRAPHS
import csv,json,re,argparse,signal
sys.path.insert(0,str(ROOT))
from check_integrity import verify

def rows(name): return list(csv.DictReader((ROOT/name).open(),delimiter='\t'))
def main():
    seeds=rows('data/stuck_14_K4free.tsv'); seedmap={r['graph6']:r for r in seeds}
    assert len(seeds)==len(seedmap)==51
    hcounts={}; known_positive=set(GRAPHS[k] for k in ('G14a','G14b','G14c'))
    for r in seeds:
        A=decode(r['graph6']); assert len(A)==14 and not cliques(A,4)
        # Cheap recorded invariants first; the exact strong decision is costly.
        assert int(r['edges'])==len(cliques(A,2)) and int(r['triangles'])==len(cliques(A,3))
        assert not strong(A)
        assert int(r['automorphism_order'])==automorphisms(A)
        h=h1(A); assert h[0]==0 and h[1] in ((),(3,))
        assert r['H1_Z']==('trivial' if not h[1] else 'Z/3')
        hcounts[r['graph6']]=h
        assert all(not strong(induced(A,a)) for a in A)
        assert all(not strong(induced(A,A[u]&A[v])) for u,v in cliques(A,2))
        if r['I_certificate_edge']=='no':
            assert h[1]==(3,)
        else:
            m=re.fullmatch(r'yes \(\{(\d+),(\d+)\}\)',r['I_certificate_edge']); assert m
            u,v=map(int,m.groups()); assert r['graph6'] in known_positive and not A[u]>>v&1
            assert strong(induced(A,A[u]&A[v])) and strong(edge(A,u,v,True))
    mosaic=rows('figures/mosaic_index.tsv')
    assert mosaic==[{'panel':str(i),'graph6':r['graph6']} for i,r in enumerate(seeds,1)]
    strict=rows('data/strictly_2dis_12.tsv'); assert len(strict)==20
    for r in strict:
        A=decode(r['graph6']); assert len(A)==12
        values={'edges':len(cliques(A,2)),'triangles':len(cliques(A,3)),
         'K4_count':len(cliques(A,4)),'clique_number':max(k for k in range(1,13) if cliques(A,k)),
         'minimum_degree':min(a.bit_count() for a in A),'maximum_degree':max(a.bit_count() for a in A),
         'automorphism_order':automorphisms(A)}
        assert set(r)=={'graph6',*values}
        assert all(int(r[k])==v for k,v in values.items())
        assert kdis(A,2) and not kdis(A,1)
    closure=rows('data/acyclic_not_strong_14_closure.tsv'); assert len(closure)==2271
    for r in closure:
        assert set(r)=={'graph6','edges','K4_count','H1_torsion','I_contractible','seed_graph6','added_edges'}
        seed=r['seed_graph6']; assert seed in seedmap
        A=decode(r['graph6']); h=h1(A)
        assert h==hcounts[seed] and h[0]==0
        assert json.loads(r['H1_torsion'])==list(h[1])
        assert r['I_contractible']==('1' if seed in known_positive else '0')
        assert not strong(A)
    # Compare the original G14a closure list up to exact isomorphism. Labels can
    # differ because the deposited search used a different canonical labeller.
    c=json.loads((ROOT/'data/small_closure_certificates.json').read_text())['closures']['G14a']['states']
    old=rows('data/closure_G14a.tsv'); assert len(old)==len(c)==48
    remaining=list(c)
    for r in old:
        A=decode(r['graph6']); matches=[x for x in remaining if isomorphic(A,decode(x['graph6']))]
        assert len(matches)==1; x=matches[0]; remaining.remove(x)
        assert r['strong_I_contractible']==('yes' if x['strong'] else 'no')
        assert int(r['added_edges'])==len(x['added_edges'])
    assert not remaining
    print(json.dumps({'seed_rows':51,'strictly_2dis_rows':20,'closure_homology_rows':2271,
      'original_G14a_closure_rows':48,'mosaic_rows':51,'all_columns_checked':True,
      'unfolding_columns_checked_by':'check_unfoldings.py',
      'addition_paths_and_positive_subsets_checked_by':'check_small_closures.py'},indent=2))
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout',type=float,default=600.0,help='Maximum wall time in seconds (default: 600)')
    args=parser.parse_args()
    if args.timeout<=0: parser.error('--timeout must be positive')
    # Reject changed inputs before potentially expensive exact searches.
    verify(ROOT)
    def expired(signum,frame):
        raise TimeoutError('Semantic table check exceeded its wall-time limit; no result is certified')
    if hasattr(signal,'setitimer'):
        signal.signal(signal.SIGALRM,expired)
        signal.setitimer(signal.ITIMER_REAL,args.timeout)
    else:
        print('Warning: this platform needs an external timeout for the semantic check',file=sys.stderr)
    try:
        main()
    except TimeoutError as exc:
        parser.exit(124,str(exc)+'\n')
    finally:
        if hasattr(signal,'setitimer'): signal.setitimer(signal.ITIMER_REAL,0)

