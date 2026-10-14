/*
 atascadas.c — Búsqueda de gráficas Z2-acíclicas "homológicamente atascadas"
 (sin vértices ni aristas I_S-contraíbles) y herramientas auxiliares.

 Proyecto: Gráficas desmantelables (Espinoza, Frías-Armenta, Hernández, Dochtermann)
 Referencia: Dochtermann et al., Discrete Math. 346 (2023) 113516, Def. 1, 4, 5, Alg. 1-2.

 Convenciones (como en el artículo):
   - Vecindad abierta N(v); vecindad común N(u,v) = N(u) ∩ N(v).
   - La gráfica vacía NO está en I_S (Alg. 2 devuelve FALSE si n = 0).
   - "acíclica" = homología reducida Z2 del complejo de cliques nula en todas
     las dimensiones (incluye conexidad).

 Lema de reducción (usado por --modo atascadas):
   Sea n el menor número de vértices de una gráfica Z2-acíclica que no es I_S.
   Un contraejemplo con n vértices y mínimo número de aristas no posee ningún
   vértice v con N(v) ∈ I_S ni arista e con N(e) ∈ I_S; como esas vecindades
   tienen < n vértices, allí "I_S" ⇔ "Z2-acíclica". Luego basta buscar gráficas
   acíclicas con todas las vecindades abiertas no-acíclicas y todas las
   vecindades comunes no-acíclicas o vacías ("atascadas"). Todo contraejemplo
   con n vértices se obtiene de uno atascado agregando aristas I_S-contraíbles.

 Lema 2 (vértice de corte ⇒ 2-conexidad para n ≤ 18; justifica geng -C -d4 -D(n-2)):
   Sea G atascada y acíclica con vértice de corte u: G = A ∪_u B, A y B conexas,
   Δ(A) ∩ Δ(B) = {u} contráctil, luego H̃(G) = H̃(A) ⊕ H̃(B) y A, B son acíclicas.
   Para w ∈ A∖{u}: N_G(w) = N_A(w); para toda arista e de A: N_G(e) = N_A(e).
   Por tanto A (y B) es "casi atascada": acíclica, todo vértice ≠ u con vecindad
   no-acíclica y toda arista con vecindad común no-acíclica o vacía; además
   |A| ≥ 3 (si A = uw, N_G(w) = {u} sería acíclica). El modo --modo casi sobre
   geng -c n (n = 3..9) no encuentra ninguna pieza así:
     n=3 conexas=2 casi_atascadas=0
     n=4 conexas=6 casi_atascadas=0
     n=5 conexas=21 casi_atascadas=0
     n=6 conexas=112 casi_atascadas=0
     n=7 conexas=853 casi_atascadas=0
     n=8 conexas=11117 casi_atascadas=0
     n=9 conexas=261080 casi_atascadas=0
   Luego un contraejemplo atascado con vértice de corte tiene ≥ 10+10-1 = 19
   vértices y todo contraejemplo atascado con n ≤ 18 es 2-conexo. Consecuencias:
   (a) sin puentes; en una gráfica acíclica una arista sin triángulo es puente
       (un ciclo que la contenga no sería frontera), así que toda vecindad común
       N(u,v) es no vacía y por tanto no-acíclica (≥ 2 vértices, no cono);
   (b) para cada v, N(v) es no-acíclica y cada u ∈ N(v) tiene N_{N(v)}(u) = N(u,v)
       no-acíclica ⇒ |N(v)| ≥ 4 (grado mínimo ≥ 4);
   (c) sin vértice universal (haría cono toda otra vecindad) ⇒ grado máximo ≤ n-2.

 Modos:
   --modo atascadas : imprime (graph6) las gráficas acíclicas atascadas.
   --modo casi      : imprime "g6 u" para gráficas acíclicas con exactamente un
                      vértice u de vecindad acíclica y todas las aristas
                      atascadas (piezas para cuñas A ∪_u B).
   --modo tabla     : cuenta conexas, chi=1, acíclicas, I (I-contraíbles: I_S o con
                      certificado de <=3 pegados I4; las acíclicas sin certificado se
                      listan como INDECISAS), I_S, I_SV, 3-,2-,1-,0-,(-1)-Dis.
   --modo verificar : para cada g6 de entrada imprime un reporte detallado.
   --modo cerradura : todas las supergráficas obtenidas pegando aristas con
                      N(u,v) ∈ I_S (etiquetadas) y su estatus I_S.
   --modo traza     : sucesión explícita de borrados I_S (vértices/aristas) hasta K1.
   --modo 2dis_no_1dis : imprime las gráficas 2-desmantelables que no son 1-desmantelables.
   --modo icert [--prof d] : certificado de I-contraibilidad: busca pegados de
                      aristas I4 (<= d) que lleven a una gráfica I_S.
 Entrada: graph6 por stdin (p. ej. desde geng -c n). n <= 16.

 Compilar: gcc -O3 -march=native -std=c11 -o atascadas atascadas.c
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 16
typedef uint32_t msk;

static int n;                 /* vértices de la gráfica actual */
static msk FULL;

static inline int pc(msk x){ return __builtin_popcount(x); }
static inline int lowidx(msk x){ return __builtin_ctz(x); }

/* ---------- graph6 ---------- */
static int parse_g6(const char *s, msk *A){
  int k = s[0]-63; if(k<1||k>MAXN) return -1;
  n=k; for(int i=0;i<n;i++) A[i]=0;
  int c=1; int val=0; int nb=0;
  for(int j=1;j<n;j++) for(int i=0;i<j;i++){
    if(nb==0){ val=s[c++]-63; if(val<0) return -1; nb=6; }
    nb--; if((val>>nb)&1){ A[i]|=1u<<j; A[j]|=1u<<i; }
  }
  FULL=(1u<<n)-1;
  return 0;
}
static void print_g6(FILE*f, const msk *A, int nn){
  char out[64]; int c=0; out[c++]=63+nn;
  int val=0, nb=0;
  for(int j=1;j<nn;j++) for(int i=0;i<j;i++){
    val=(val<<1)|((A[i]>>j)&1); nb++;
    if(nb==6){ out[c++]=63+val; val=0; nb=0; }
  }
  if(nb>0){ val<<=(6-nb); out[c++]=63+val; }
  out[c]=0; fputs(out,f);
}

/* ---------- utilidades sobre subgráficas inducidas (máscara m, adyacencia A) ---------- */
static inline int is_cone(const msk *A, msk m){
  msk t=m; while(t){ int w=lowidx(t); t&=t-1; if((A[w]&m)==(m^(1u<<w))) return 1; } return 0;
}
static inline int connected(const msk *A, msk m){
  if(!m) return 0; msk seen=1u<<lowidx(m), fr=seen;
  while(fr){ msk nx=0; msk t=fr; while(t){int v=lowidx(t); t&=t-1; nx|=A[v]&m;} nx&=~seen; seen|=nx; fr=nx; }
  return seen==m;
}
/* desmantelamiento 0 greedy (el orden no importa para 0-Dis). 1 si llega a un vértice */
static int dismantle0(const msk *A, msk m){
  if(!m) return 0;
  int ch=1;
  while(pc(m)>1 && ch){ ch=0; msk t=m;
    while(t){ int v=lowidx(t); t&=t-1; msk link=A[v]&m; if(link && is_cone(A,link)){ m^=1u<<v; ch=1; } }
  }
  return pc(m)==1;
}
/* característica de Euler del complejo de cliques inducido en cand: sum (-1)^{|s|-1} */
static int chi(const msk *A, msk cand){ int s=0; while(cand){ int v=lowidx(cand); cand&=cand-1; s+=1-chi(A,A[v]&cand);} return s; }

/* ---------- homología Z2 completa del complejo de cliques inducido en m ---------- */
#define MAXF (1<<13)
static msk faces[MAXN+1][MAXF]; static int nf[MAXN+1];
static int32_t idx[1<<MAXN];
static int maxdim;
static void enum_cliques(const msk *A, msk cur, msk cand){
  int k=pc(cur); if(k>0){ if(nf[k-1]>=MAXF){fprintf(stderr,"overflow caras\n"); exit(2);} faces[k-1][nf[k-1]++]=cur; if(k-1>maxdim) maxdim=k-1; }
  while(cand){ int v=lowidx(cand); cand&=cand-1; enum_cliques(A, cur|(1u<<v), A[v]&cand); }
}
#define MAXW (MAXF/64+1)
static uint64_t cols[MAXF][MAXW]; static int pivot[MAXF];
/* rango sobre Z2 de la matriz frontera d_k : C_k -> C_{k-1}, k>=1 */
static int rank_boundary(int k){
  int rows=nf[k-1], ncol=nf[k]; if(!rows||!ncol) return 0;
  int W=(rows+63)/64;
  for(int i=0;i<rows;i++) idx[faces[k-1][i]]=i;
  for(int i=0;i<rows;i++) pivot[i]=-1;
  int r=0;
  for(int c=0;c<ncol;c++){
    uint64_t *col=cols[c]; memset(col,0,(size_t)W*8);
    msk f=faces[k][c]; msk t=f; while(t){ int v=lowidx(t); t&=t-1; int i=idx[f^(1u<<v)]; col[i>>6]^=1ull<<(i&63); }
    for(;;){ int low=-1; for(int w=W-1;w>=0;w--) if(col[w]){ low=w*64+63-__builtin_clzll(col[w]); break; }
      if(low<0) break; if(pivot[low]<0){ pivot[low]=c; r++; break; }
      uint64_t *p=cols[pivot[low]]; for(int w=0;w<W;w++) col[w]^=p[w]; }
  }
  return r;
}
static int betti[MAXN+2];
/* 1 si la homología reducida Z2 del complejo de cliques de m es nula; llena betti[] */
static int acyclic_full(const msk *A, msk m){
  for(int k=0;k<MAXN+2;k++) betti[k]=0;
  if(!m){ betti[0]=-1; return 0; }
  for(int k=0;k<=MAXN;k++) nf[k]=0; maxdim=0; enum_cliques(A,0,m);
  int rk[MAXN+2]; for(int k=0;k<MAXN+2;k++) rk[k]=0;
  for(int k=1;k<=maxdim;k++) rk[k]=rank_boundary(k);
  int ok=1;
  betti[0]=nf[0]-rk[1]; if(betti[0]!=1) ok=0;
  for(int k=1;k<=maxdim;k++){ betti[k]=nf[k]-rk[k]-rk[k+1]; if(betti[k]!=0) ok=0; }
  return ok;
}
/* decide aciclicidad con filtros baratos primero */
static int acyclic(const msk *A, msk m){
  if(!m) return 0; if(pc(m)==1) return 1; if(!connected(A,m)) return 0;
  if(dismantle0(A,m)) return 1;
  if(chi(A,m)!=1) return 0;
  return acyclic_full(A,m);
}

/* ---------- I_SV exacto por programación dinámica sobre subconjuntos ---------- */
static uint8_t memo_isv[1<<MAXN]; /* 0 desconocido, 1 sí, 2 no */
static int isv(const msk *A, msk m){
  if(!m) return 0; if(pc(m)==1) return 1;
  uint8_t *st=&memo_isv[m]; if(*st) return *st==1;
  int res=0; msk t=m;
  while(t && !res){ int v=lowidx(t); t&=t-1; msk link=A[v]&m; if(link && isv(A,link) && isv(A,m^(1u<<v))) res=1; }
  *st=res?1:2; return res;
}
static int isv_graph(const msk *A){ memset(memo_isv,0,(size_t)1<<n); return isv(A,FULL); }

/* ---------- I_S exacto (borrado de vértices y aristas) con backtracking y memo ---------- */
#define HBITS 22
static uint64_t *htab=NULL; static uint8_t *hval=NULL; static long hcount=0;
static uint64_t hash_graph(const msk *A, msk m){
  uint64_t h=1469598103934665603ull ^ m;
  for(int i=0;i<n;i++) if(m>>i&1){ h^=((uint64_t)(A[i]&m)<<8)+i; h*=1099511628211ull; h^=h>>29; }
  return h|1;
}
static int memo_get(uint64_t h){ uint64_t p=h&((1u<<HBITS)-1); while(htab[p]){ if(htab[p]==h) return hval[p]; p=(p+1)&((1u<<HBITS)-1);} return 0; }
static void memo_put(uint64_t h,int v){ if(hcount>(1L<<HBITS)*3/4){ memset(htab,0,sizeof(uint64_t)<<HBITS); hcount=0; }
  uint64_t p=h&((1u<<HBITS)-1); while(htab[p]&&htab[p]!=h) p=(p+1)&((1u<<HBITS)-1); if(!htab[p]) hcount++; htab[p]=h; hval[p]=v; }
static long is_nodes;
static int is_rec(msk *A, msk m){
  /* ¿la gráfica (A restringida a m) está en I_S? A puede tener aristas borradas. */
  if(!m) return 0; if(pc(m)==1) return 1;
  if(!connected(A,m)) return 0;
  if(dismantle0(A,m)) return 1;         /* 0-Dis ⊂ I_SV ⊂ I_S */
  uint64_t h=hash_graph(A,m); int g=memo_get(h); if(g) return g==1;
  is_nodes++;
  int res=0;
  /* vértices I_S-contraíbles */
  msk t=m;
  while(t && !res){ int v=lowidx(t); t&=t-1; msk link=A[v]&m;
    if(link && is_rec(A,link)){ if(is_rec(A,m^(1u<<v))) res=1; } }
  /* aristas I_S-contraíbles */
  if(!res){ for(int u=0;u<n && !res;u++) if(m>>u&1) for(int v=u+1;v<n && !res;v++) if((m>>v&1) && (A[u]>>v&1)){
      msk cn=A[u]&A[v]&m;
      if(cn && is_rec(A,cn)){
        A[u]^=1u<<v; A[v]^=1u<<u;           /* borrar arista */
        if(is_rec(A,m)) res=1;
        A[u]^=1u<<v; A[v]^=1u<<u;           /* restaurar */
      } } }
  memo_put(h,res?1:2); return res;
}
static int is_graph(const msk *A){ msk B[MAXN]; memcpy(B,A,sizeof(msk)*n); return is_rec(B,FULL); }

/* ---------- filtro de atascamiento ---------- */
static int count_acyclic_links(const msk *A, int tope, msk *which){
  int c=0; *which=0;
  for(int v=0;v<n;v++){ if(acyclic(A,A[v])){ c++; *which|=1u<<v; if(c>tope) return c; } }
  return c;
}
static int edges_stuck(const msk *A){
  for(int u=0;u<n;u++) for(int v=u+1;v<n;v++) if(A[u]>>v&1){ msk cn=A[u]&A[v]; if(cn && acyclic(A,cn)) return 0; }
  return 1;
}


/* ---------- certificado de I-contraibilidad por "anti-colapso" ----------
   Busca (BFS, profundidad <= maxd) una sucesión de pegados de aristas I4
   (N(u,v) ∈ I_S ⊂ I) que lleve a una gráfica en I_S. Como I4 y los borrados
   I_S (I1, I3) son transformaciones de Ivashchenko, esto certifica G ∈ I.   */
#define QMAX 200000
static msk qg[QMAX][MAXN]; static int qpar[QMAX]; static int qedge[QMAX]; static int qdepth[QMAX];
static int icert(const msk *A, int maxd){
  int head=0, tail=0; memcpy(qg[0],A,sizeof(msk)*n); qpar[0]=-1; qedge[0]=-1; qdepth[0]=0; tail=1;
  uint64_t *seen=calloc(1<<20,sizeof(uint64_t)); long nseen=0;
  while(head<tail){
    int cur=head++; msk *B=qg[cur];
    if(is_graph(B)){
      printf("I-CONTRAIBLE: en I_S tras %d pegado(s) de arista I4:", qdepth[cur]);
      int path[64], k=0; for(int x=cur; x>0; x=qpar[x]) path[k++]=qedge[x];
      for(int i=k-1;i>=0;i--) printf(" {%d,%d}", path[i]>>8, path[i]&255); printf("\n");
      printf("  gráfica final (g6): "); print_g6(stdout,B,n); printf("\n");
      free(seen); return 1; }
    if(qdepth[cur]>=maxd) continue;
    for(int u=0;u<n;u++) for(int v=u+1;v<n;v++) if(!(B[u]>>v&1)){
      msk cn=B[u]&B[v]; if(!cn) continue;
      msk C[MAXN]; memcpy(C,B,sizeof(msk)*n);
      if(!is_rec(C,cn)) continue;             /* N(u,v) ∈ I_S */
      memcpy(C,B,sizeof(msk)*n); C[u]|=1u<<v; C[v]|=1u<<u;
      uint64_t h=hash_graph(C,FULL); uint64_t p=h&((1u<<20)-1); int dup=0;
      while(seen[p]){ if(seen[p]==h){dup=1;break;} p=(p+1)&((1u<<20)-1); }
      if(dup) continue; seen[p]=h; nseen++;
      if(tail>=QMAX){ fprintf(stderr,"cola llena\n"); free(seen); return 0; }
      memcpy(qg[tail],C,sizeof(msk)*n); qpar[tail]=cur; qedge[tail]=(u<<8)|v; qdepth[tail]=qdepth[cur]+1; tail++;
    }
  }
  printf("NO se halló certificado con <= %d pegados de arista (explorados %d estados)\n", maxd, tail);
  free(seen); return 0;
}

static int icert_quiet(const msk *A, int maxd){
  int head=0, tail=0; memcpy(qg[0],A,sizeof(msk)*n); qdepth[0]=0; tail=1;
  uint64_t *seen=calloc(1<<20,sizeof(uint64_t));
  while(head<tail){
    int cur=head++; msk *B=qg[cur];
    if(is_graph(B)){ free(seen); return 1; }
    if(qdepth[cur]>=maxd) continue;
    for(int u=0;u<n;u++) for(int v=u+1;v<n;v++) if(!(B[u]>>v&1)){
      msk cn=B[u]&B[v]; if(!cn) continue;
      msk C[MAXN]; memcpy(C,B,sizeof(msk)*n);
      if(!is_rec(C,cn)) continue;
      memcpy(C,B,sizeof(msk)*n); C[u]|=1u<<v; C[v]|=1u<<u;
      uint64_t h=hash_graph(C,FULL); uint64_t p=h&((1u<<20)-1); int dup=0;
      while(seen[p]){ if(seen[p]==h){dup=1;break;} p=(p+1)&((1u<<20)-1); }
      if(dup) continue; seen[p]=h;
      if(tail>=QMAX){ free(seen); return 0; }
      memcpy(qg[tail],C,sizeof(msk)*n); qdepth[tail]=qdepth[cur]+1; tail++;
    }
  }
  free(seen); return 0;
}

/* ---------- cerradura por pegados de aristas I4 con N(u,v) ∈ I_S ----------
   Imprime todas las gráficas (etiquetadas; deduplicar por isomorfismo aparte)
   alcanzables desde G agregando aristas I_S-contraíbles, con su estatus I_S.
   Por el Lema de reducción, toda gráfica Z2-acíclica no-I_S con n vértices se
   obtiene así desde alguna atascada.                                           */
static void cerradura(const msk *A){
  int head=0, tail=0; memcpy(qg[0],A,sizeof(msk)*n); qdepth[0]=0; tail=1;
  uint64_t *seen=calloc(1<<20,sizeof(uint64_t));
  { uint64_t h=hash_graph(A,FULL); seen[h&((1u<<20)-1)]=h; }
  while(head<tail){
    int cur=head++; msk *B=qg[cur]; int isS=is_graph(B);
    printf("%s ", isS?"I_S":"NO_I_S"); print_g6(stdout,B,n); printf(" aristas_agregadas=%d\n", qdepth[cur]);
    if(isS) continue;   /* las supergráficas de una I_S por pegados I4 son I_S */
    for(int u=0;u<n;u++) for(int v=u+1;v<n;v++) if(!(B[u]>>v&1)){
      msk cn=B[u]&B[v]; if(!cn) continue;
      msk C[MAXN]; memcpy(C,B,sizeof(msk)*n);
      if(!is_rec(C,cn)) continue;
      memcpy(C,B,sizeof(msk)*n); C[u]|=1u<<v; C[v]|=1u<<u;
      uint64_t h=hash_graph(C,FULL); uint64_t p=h&((1u<<20)-1); int dup=0;
      while(seen[p]){ if(seen[p]==h){dup=1;break;} p=(p+1)&((1u<<20)-1); }
      if(dup) continue; seen[p]=h;
      if(tail>=QMAX){ fprintf(stderr,"cola llena\n"); free(seen); return; }
      memcpy(qg[tail],C,sizeof(msk)*n); qdepth[tail]=qdepth[cur]+1; tail++;
    }
  }
  free(seen);
}

/* ---------- traza: sucesión explícita de borrados I_S hasta K1 ----------
   Repite la búsqueda de is_rec pero registrando el camino exitoso. Para cada
   paso imprime la vecindad relevante y un certificado corto de que está en
   I_S: "cono" (vértice universal ⇒ 0-Dis ⊂ I_S), "0-Dis" (desmantelable
   greedy) o "I_S (recursivo)".                                               */
static const char* cert_vecindad(const msk *A, msk m){
  if(pc(m)==1) return "K1";
  if(is_cone(A,m)) return "cono (0-Dis)";
  if(dismantle0(A,m)) return "0-Dis";
  return "I_S (por recursion)";
}
static void print_set(msk m){ printf("{"); int first=1; for(int v=0;v<n;v++) if(m>>v&1){ printf(first?"%d":",%d",v); first=0;} printf("}"); }
static int traza(msk *A, msk m, int paso){
  if(pc(m)==1){ printf("  => queda el vertice "); print_set(m); printf(" = K1.\n"); return 1; }
  if(!connected(A,m)) return 0;
  /* primero vértices */
  msk t=m;
  while(t){ int v=lowidx(t); t&=t-1; msk link=A[v]&m;
    if(link && is_rec(A,link)){
      msk m2=m^(1u<<v);
      if(is_rec(A,m2)){
        printf("  %2d. borrar vertice %d: N(%d) = ",paso,v,v); print_set(link); printf("  [%s]\n",cert_vecindad(A,link));
        return traza(A,m2,paso+1); } } }
  for(int u=0;u<n;u++) if(m>>u&1) for(int v=u+1;v<n;v++) if((m>>v&1)&&(A[u]>>v&1)){
    msk cn=A[u]&A[v]&m;
    if(cn && is_rec(A,cn)){
      A[u]^=1u<<v; A[v]^=1u<<u;
      if(is_rec(A,m)){
        printf("  %2d. borrar arista {%d,%d}: N(%d,%d) = ",paso,u,v,u,v); print_set(cn); printf("  [%s]\n",cert_vecindad(A,cn));
        return traza(A,m,paso+1); }
      A[u]^=1u<<v; A[v]^=1u<<u; } }
  return 0;
}

/* ---------- k-desmantelabilidad exacta (Def. 10) ----------
   kdis(A,m,k): 1 si la subgráfica inducida en m es k-desmantelable.
   k = -1: cono. k >= 0: existe v con N(v) (k-1)-desmantelable y m-v k-desmantelable.
   Para k = 0 el orden no importa (greedy); para k >= 1 se usa DP sobre subconjuntos
   con memo por (k, m) — memo_kdis[k][m] en {0,1,2}.                                  */
static uint8_t *memo_kdis[4];  /* k = 0..3 */
static int kdis(const msk *A, msk m, int k){
  if(!m) return 0; if(pc(m)==1) return 1;
  if(k<0) return is_cone(A,m);
  if(k==0) return dismantle0(A,m);
  uint8_t *st=&memo_kdis[k][m]; if(*st) return *st==1;
  int res=0; msk t=m;
  while(t && !res){ int v=lowidx(t); t&=t-1; msk link=A[v]&m;
    if(link && kdis(A,link,k-1) && kdis(A,m^(1u<<v),k)) res=1; }
  *st=res?1:2; return res;
}
static int kdis_graph(const msk *A, int k){ if(k>=1) for(int j=1;j<=k;j++) memset(memo_kdis[j],0,(size_t)1<<n); return kdis(A,FULL,k); }

int main(int argc, char **argv){
  const char *modo="atascadas"; 
  for(int i=1;i<argc;i++){ if(!strcmp(argv[i],"--modo")&&i+1<argc) modo=argv[++i]; }
  int M_AT=!strcmp(modo,"atascadas"), M_CASI=!strcmp(modo,"casi"), M_TAB=!strcmp(modo,"tabla"), M_VER=!strcmp(modo,"verificar"), M_IC=!strcmp(modo,"icert"), M_CE=!strcmp(modo,"cerradura"), M_TR=!strcmp(modo,"traza"), M_D21=!strcmp(modo,"2dis_no_1dis");
  int maxd=3; for(int i=1;i<argc;i++){ if(!strcmp(argv[i],"--prof")&&i+1<argc) maxd=atoi(argv[++i]); }
  if(!(M_AT||M_CASI||M_TAB||M_VER||M_IC||M_CE||M_TR||M_D21)){ fprintf(stderr,"modo desconocido\n"); return 1; }
  htab=calloc((size_t)1<<HBITS,sizeof(uint64_t)); hval=calloc((size_t)1<<HBITS,1);
  char line[4096]; msk A[MAXN];
  long long total=0, pasa_cono=0, pasa_chi=0, pasa_links=0, pasa_aristas=0, encontradas=0;
  long long c_acyc=0, c_is=0, c_isv=0, c_d0=0, c_chi1=0, c_dm1=0, c_d1=0, c_d2=0, c_d3=0, c_I=0, c_Iind=0;
  for(int j=0;j<4;j++) memo_kdis[j]=calloc((size_t)1<<MAXN,1);
  while(fgets(line,sizeof line,stdin)){
    if(line[0]=='>'||line[0]=='\n') continue;
    size_t L=strlen(line); while(L&&(line[L-1]=='\n'||line[L-1]=='\r'||line[L-1]==' ')) line[--L]=0;
    if(parse_g6(line,A)) { fprintf(stderr,"g6 inválido: %s\n",line); continue; }
    total++;
    if(M_AT){
      int ok=1;
      for(int v=0;v<n;v++){ if(pc(A[v])<2 || is_cone(A,A[v])){ ok=0; break; } }
      if(!ok) continue; pasa_cono++;
      if(chi(A,FULL)!=1) continue; pasa_chi++;
      msk w; if(count_acyclic_links(A,0,&w)>0) continue; pasa_links++;
      if(!edges_stuck(A)) continue; pasa_aristas++;
      if(!acyclic_full(A,FULL)) continue;
      encontradas++; printf("%s\n",line); fflush(stdout);
    } else if(M_CASI){
      if(chi(A,FULL)!=1) continue; pasa_chi++;
      msk w; int c=count_acyclic_links(A,1,&w); if(c!=1) continue; pasa_links++;
      if(!edges_stuck(A)) continue; pasa_aristas++;
      if(!acyclic_full(A,FULL)) continue;
      encontradas++; printf("%s %d\n",line,lowidx(w)); fflush(stdout);
    } else if(M_TAB){
      int ch=(chi(A,FULL)==1); if(ch) c_chi1++;
      int ac= ch && acyclic_full(A,FULL); if(ac) c_acyc++;
      int d0= dismantle0(A,FULL); if(d0) c_d0++;
      int sv= d0 || (ac && isv_graph(A)); if(sv) c_isv++;
      int si= sv || (ac && is_graph(A)); if(si) c_is++;
      int dm1 = is_cone(A,FULL); if(dm1) c_dm1++;
      int d1 = d0 || (sv && kdis_graph(A,1)); if(d1) c_d1++;
      int d2 = d1 || (sv && kdis_graph(A,2)); if(d2) c_d2++;
      int d3 = d2 || (sv && kdis_graph(A,3)); if(d3) c_d3++;
      if(ac && !si){ int ok=icert_quiet(A,3); if(ok){ c_I++; printf("I_NO_IS %s\n",line);} else { c_Iind++; printf("ACICLICA_NO_IS_INDECISA %s\n",line);} }
      else if(si) c_I++;
      if(si && !ac){ printf("ERROR IS_NO_ACICLICA %s\n",line); }
    } else if(M_D21){
      /* imprime las gráficas 2-desmantelables que NO son 1-desmantelables (cascada barata primero) */
      if(dismantle0(A,FULL)) continue;              /* 0-Dis ⊂ 1-Dis */
      if(chi(A,FULL)!=1 || !acyclic_full(A,FULL)) continue;   /* k-Dis ⊂ I_S ⇒ acíclica */
      if(!isv_graph(A)) continue;                   /* k-Dis ⊂ I_SV */
      if(kdis_graph(A,1)) continue;
      if(kdis_graph(A,2)){ encontradas++; printf("2DIS_NO_1DIS %s\n",line); fflush(stdout); }
    } else if(M_IC){
      printf("== %s\n",line); icert(A,maxd);
    } else if(M_CE){
      printf("== cerradura de %s\n",line); cerradura(A);
    } else if(M_TR){
      printf("== traza I_S de %s\n",line); msk B[MAXN]; memcpy(B,A,sizeof(msk)*n); if(!traza(B,FULL,1)) printf("  NO es I_S\n");
    } else if(M_VER){
      int m_edges=0; for(int v=0;v<n;v++) m_edges+=pc(A[v]); m_edges/=2;
      printf("== %s  n=%d aristas=%d\n",line,n,m_edges);
      int ac=acyclic_full(A,FULL);
      printf("chi=%d conexa=%d aciclica=%d betti=",chi(A,FULL),connected(A,FULL),ac);
      for(int k=0;k<=maxdim;k++) printf("%d ",betti[k]); printf("\n");
      for(int v=0;v<n;v++){ msk l=A[v]; int a=acyclic(A,l); printf("  N(%d) = {",v); for(int u=0;u<n;u++) if(l>>u&1) printf("%d ",u); printf("} |N|=%d conexa=%d cono=%d aciclica=%d\n",pc(l),connected(A,l),is_cone(A,l),a); }
      int nst=0; for(int u=0;u<n;u++) for(int v=u+1;v<n;v++) if(A[u]>>v&1){ msk cn=A[u]&A[v]; int a=cn?acyclic(A,cn):0; if(a) nst++; printf("  N(%d,%d) = {",u,v); for(int x=0;x<n;x++) if(cn>>x&1) printf("%d ",x); printf("} vacia=%d aciclica=%d%s\n",cn==0,a,a?"  <-- arista I_S-contraible":""); }
      msk w; int cl=count_acyclic_links(A,MAXN,&w);
      printf("vertices con vecindad aciclica: %d; aristas con vecindad comun aciclica: %d\n",cl,nst);
      printf("0-Dis=%d  I_SV=%d  I_S=%d  (atascada=%d)\n",dismantle0(A,FULL),isv_graph(A),is_graph(A),(cl==0&&nst==0));
    }
  }
  if(M_TAB) fprintf(stderr,"n=%d conexas=%lld chi1=%lld aciclicas=%lld I=%lld I_indecisas=%lld I_S=%lld I_SV=%lld 3-Dis=%lld 2-Dis=%lld 1-Dis=%lld 0-Dis=%lld -1-Dis=%lld\n",n,total,c_chi1,c_acyc,c_I,c_Iind,c_is,c_isv,c_d3,c_d2,c_d1,c_d0,c_dm1);
  else fprintf(stderr,"n=%d total=%lld pasa_cono=%lld pasa_chi=%lld pasa_vecindades=%lld pasa_aristas=%lld encontradas=%lld\n",n,total,pasa_cono,pasa_chi,pasa_links,pasa_aristas,encontradas);
  return 0;
}
