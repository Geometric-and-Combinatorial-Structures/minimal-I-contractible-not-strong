"""Check all boundary components by gluing triangle corners.

The input is the supplied TSV graph6 column; no geometric description is assumed.
Uses only Python's standard library and performs no writes. Run python3 check_unfoldings.py.
"""
from pathlib import Path
from itertools import combinations
from collections import defaultdict, Counter
import argparse, csv, json

OUT=Path(__file__).resolve().parent

def graph6(s):
    n=ord(s[0])-63;assert 0<=n<=62
    bits=[(ord(c)-63>>i)&1 for c in s[1:] for i in range(5,-1,-1)]
    return n,{(i,j) for bit,(i,j) in zip(bits,((i,j) for j in range(1,n) for i in range(j))) if bit}

class UF:
    def __init__(self):self.p={}
    def find(self,x):
        self.p.setdefault(x,x)
        if self.p[x]!=x:self.p[x]=self.find(self.p[x])
        return self.p[x]
    def join(self,x,y):
        x,y=self.find(x),self.find(y)
        if x!=y:self.p[max(x,y)]=min(x,y)

def components(adj):
    todo=set(adj);out=[]
    while todo:
        seen={min(todo)};stack=list(seen)
        while stack:
            v=stack.pop()
            for w in adj[v]:
                if w not in seen:seen.add(w);stack.append(w)
        todo-=seen;out.append(seen)
    return out

def reconstruct(s):
    n,edges=graph6(s)
    triangles=[t for t in combinations(range(n),3) if all(e in edges for e in combinations(t,2))]
    incidence=defaultdict(list)
    for k,t in enumerate(triangles):
        for e in combinations(t,2):incidence[e].append(k)
    corners=UF();triangle_adj={k:set() for k in range(len(triangles))}
    for k,t in enumerate(triangles):
        for v in t:corners.find((k,v))
    for e,ts in incidence.items():
        if len(ts)==2:
            a,b=ts;triangle_adj[a].add(b);triangle_adj[b].add(a)
            for v in e:corners.join((a,v),(b,v))
    records=[]
    for ts in components(triangle_adj):
        verts={corners.find((k,v)) for k in ts for v in triangles[k]}
        local_edges={};links={v:defaultdict(list) for v in verts};boundary={v:[] for v in verts}
        for k in ts:
            tri=triangles[k];eids={}
            for e in combinations(tri,2):
                eid=(min(incidence[e]),e) if len(incidence[e])==2 else (k,e)
                ends=tuple(corners.find((k,v)) for v in e)
                local_edges[eid]=ends;eids[e]=eid
            for v in tri:
                ids=[eid for e,eid in eids.items() if v in e]
                a,b=ids;link=links[corners.find((k,v))];link[a].append(b);link[b].append(a)
        for eid,(a,b) in local_edges.items():
            if len(incidence[eid[1]])!=2:
                boundary[a].append((b,eid));boundary[b].append((a,eid))
        boundary={v:es for v,es in boundary.items() if es}
        assert all(len(es)==2 for es in boundary.values())
        linkchecks=[]
        for v,link in links.items():
            degs=sorted(map(len,link.values()));connected=len(components(link))==1
            good=connected and (degs.count(1)==2 and all(d in (1,2) for d in degs) if v in boundary else all(d==2 for d in degs))
            assert good,(v,degs,connected)
            linkchecks.append({'corner_class':v,'image_vertex':v[1],'boundary':v in boundary,'link':'path' if v in boundary else 'cycle'})
        todo={eid for es in boundary.values() for _,eid in es};words=[]
        while todo:
            eid=min(todo);start=local_edges[eid][0];v=start;used=None;word=[]
            while True:
                word.append(v[1]);choices=[(w,e) for w,e in boundary[v] if e!=used and e in todo]
                w,e=min(choices,key=lambda z:z[1]);todo.remove(e);used=e;v=w
                if v==start:break
            words.append(word)
        words.sort(key=lambda w:(len(w),w))
        V,E,F=len(verts),len(local_edges),len(ts);chi=V-E+F
        kind='disc' if chi==1 and len(words)==1 else 'annulus' if chi==0 and len(words)==2 else 'other surface'
        records.append({'type':kind,'vertices':V,'edges':E,'triangles':F,'euler_characteristic':chi,'boundary_lengths':[len(w) for w in words],'boundary_words':words,'vertex_links':linkchecks})
    records.sort(key=lambda r:(r['type'],r['triangles']))
    return records

def canonical(records):
    records=json.loads(json.dumps(records))
    for row in records:
        for comp in row['components']:
            comp['vertex_links'].sort(key=lambda x:x['corner_class'])
    return records

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path,default=OUT/'unfolding_components.json')
    args=parser.parse_args()
    rows=list(csv.DictReader((OUT/'stuck_14_K4free.tsv').open(),delimiter='\t'))
    counts=Counter();computed=[]
    for i,row in enumerate(rows,1):
        comps=reconstruct(row['graph6'])
        kind=' + '.join(sorted(c['type'] for c in comps))
        words=sorted([w for c in comps for w in c['boundary_words']],key=lambda w:(len(w),w))
        assert kind==row['unfolding'],i
        assert sum(c['vertices'] for c in comps)==int(row['unfolded_vertices']),i
        assert sum(map(len,words))==int(row['boundary_edges']),i
        assert '+'.join(str(len(w)) for w in words)==row['boundary_component_lengths'],i
        assert words==json.loads(row['boundary_words']),i
        counts[kind]+=1
        computed.append({'row':i,'graph6':row['graph6'],'components':comps})
    assert len(rows)==51
    assert counts=={'disc':48,'annulus':2,'annulus + disc':1}
    try: supplied=json.loads(args.certificate.read_text())
    except (OSError,ValueError) as error: parser.exit(1,'Certificate cannot be read: '+str(error)+'\n')
    if canonical(supplied)!=canonical(computed): parser.exit(1,'Certificate differs from the reconstructed components.\n')
    print(json.dumps({'rows_checked':len(rows),'component_types':dict(counts),'all_vertex_links_valid':True,'all_boundary_components_match':True,'deposited_JSON_matches':True},indent=2))
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
if __name__=='__main__': main()
