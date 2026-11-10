/* Separate local filter: K4-free stuck candidates.
   For a K4-free graph, N(v) is triangle-free, so N(v) in I_S iff N(v) is a tree;
   N(u,v) is an independent set, so it lies in I_S iff it has exactly one vertex.
   Reads graph6 lines (n<=31), writes survivors of: no tree neighbourhood,
   no edge in exactly one triangle, Euler characteristic 1. Counters on stderr. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
static int popc(uint32_t x){return __builtin_popcount(x);}
static int connected_on(uint32_t S, const uint32_t *adj){
  if(!S) return 0; uint32_t seen = S & (-S), frontier = seen;
  while(frontier){ uint32_t nxt=0; uint32_t f=frontier;
    while(f){ int i=__builtin_ctz(f); f&=f-1; nxt |= adj[i] & S; }
    nxt &= ~seen; seen |= nxt; frontier = nxt; }
  return seen == S;
}
int main(void){
  char line[256]; uint32_t adj[32];
  unsigned long long total=0, c_vert=0, c_edge=0, c_euler=0;
  while(fgets(line,sizeof line,stdin)){
    int n = line[0]-63; if(n<1||n>31) continue; total++;
    memset(adj,0,sizeof adj);
    int bit=0, k=1; int val = line[k]-63, pos=5;
    for(int j=1;j<n;j++) for(int i=0;i<j;i++){
      if(pos<0){ k++; val=line[k]-63; pos=5; }
      if((val>>pos)&1){ adj[i]|=1u<<j; adj[j]|=1u<<i; }
      pos--; bit++;
    }
    int E=0, T3=0, reject=0;
    for(int v=0; v<n && !reject; v++){
      uint32_t N = adj[v]; int d = popc(N), t=0;
      uint32_t f=N; while(f){int i=__builtin_ctz(f); f&=f-1; t += popc(adj[i]&N);} t/=2;
      T3 += t; E += d;
      if(t == d-1 && connected_on(N, adj)) reject=1; /* tree neighbourhood: admissible vertex */
    }
    if(reject) continue; c_vert++;
    for(int u=0; u<n && !reject; u++){ uint32_t f = adj[u] & ~((2u<<u)-1);
      while(f){int v=__builtin_ctz(f); f&=f-1; if(popc(adj[u]&adj[v])==1){reject=1;break;}}}
    if(reject) continue; c_edge++;
    E/=2; int T=T3/3;
    if(n - E + T != 1) continue; c_euler++;
    fputs(line, stdout);
  }
  fprintf(stderr,"total=%llu after_vertex=%llu after_edge=%llu after_euler=%llu\n", total,c_vert,c_edge,c_euler);
  return 0;
}
