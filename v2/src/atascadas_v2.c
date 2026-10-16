/*
 atascadas_v2.c — clasificador de gráficas, versión 2.1: la versión 2 (remediación de la ronda 1 de la auditoría
 externa, 15-16 oct 2026) más las correcciones de la ronda 2 (16 oct 2026: H-18 ampliado y H-25; ver abajo).

 Proyecto: Gráficas desmantelables (Espinoza, Frías-Armenta, Hernández-Amador, Hernández-Hernández).
 Referencia: Dochtermann, Espinoza, Frías-Armenta, Hernández, Discrete Math. 346 (2023) 113516 [DEFH].

 Los algoritmos son los de src/atascadas.c (v1); cambian la identidad de los estados memorizados, la validación
 de la entrada, los límites de capacidad, las etiquetas de diagnóstico, los códigos de salida y el formato.
 Correspondencia con los hallazgos del dictamen:
   H-01  is_rec memoriza con CLAVE COMPLETA (máscara m y filas A[i]&m); el hash sólo ubica la casilla.  Los conjuntos
         "vistos" de icert/icert_quiet/cerradura también usan clave completa.  Se informan consultas, aciertos y
         colisiones de hash (casos que v1 habría resuelto con la respuesta de otro estado).
   H-18  graph6 estricto: se consume el prefijo ">>graph6<<"; se exige orden 1..16, caracteres 63..126, longitud
         exacta 1+ceil(n(n-1)/12) y relleno nulo.  Todo registro inválido se cuenta y la salida es distinta de cero.
   H-19  MAXF = 2^14 >= C(16,8) = 12870 (K16 cabe); los contadores son de 64 bits sin signo por proceso.
   H-20  "atascada" (modo verificar) exige n >= 2, Z2-aciclicidad y ninguna vecindad (de vértice o de arista) en I_S,
         decidido con la búsqueda exacta; se informa por separado "sin_movimientos".
   H-21  una sentencia por línea; compila sin avisos con -Wall -Wextra -Wpedantic.
   H-06  definiciones (existenciales, como en DEFH Defs. 4-5):
           G ∈ I_SV  ⇔ G = K1, o existe v con N(v) ∈ I_SV y G - v ∈ I_SV;
           G ∈ I_S   ⇔ G = K1, o existe v con N(v) ∈ I_S y G - v ∈ I_S, o existe una arista uv con
                        N(u,v) = N(u) ∩ N(v) ∈ I_S y G - uv ∈ I_S;
         equivalentemente, I_S (I_SV) es la clase generada desde K1 por pegados de vértices y aristas (sólo vértices)
         cuya vecindad está en la clase.  La gráfica vacía no pertenece a ninguna de las clases.
         k-Dis (Def. 10): (-1)-Dis = conos; k >= 0: existe v con N(v) ∈ (k-1)-Dis y G - v ∈ k-Dis.

 "acíclica" = homología reducida con coeficientes en Z2 del complejo de cliques nula (incluye conexidad).

 Modos (--modo M; la entrada es graph6, un registro por línea, por stdin):
   tabla        cuenta conexas, chi=1, acíclicas, I (I_S o con certificado de <= --prof pegados I4), indecisas, I_S,
                I_SV, 3-,2-,1-,0-,(-1)-Dis.  Imprime en stdout "I_NO_IS g6" y "ACICLICA_NO_IS_INDECISA g6"
                (con --cert, además "CERT_I4 g6 {u,v} ..." con los pegados del certificado).  Exige entrada conexa.
   atascadas    imprime las gráficas acíclicas cuyas vecindades de vértice y de arista son todas no acíclicas
                (criterio de búsqueda del Lema de reducción; ver docs del artículo).
   casi         imprime "g6 u" para las acíclicas con exactamente un vértice u de vecindad acíclica y todas las
                aristas con vecindad común no acíclica.
   2dis_no_1dis imprime las gráficas 2-desmantelables que no son 1-desmantelables.
   verificar    reporte detallado por gráfica (diagnóstico).
   icert        certificado de I-contraibilidad por pegados I4 (BFS, profundidad <= --prof, por omisión 3).
                --prof acepta sólo dígitos decimales (v2.1); cualquier otro valor es error de uso (código 1).
   cerradura    supergráficas alcanzables pegando aristas con N(u,v) ∈ I_S (etiquetadas) y su estatus I_S.
   traza        sucesión explícita de borrados I_S hasta K1.
 En los modos de conteo (tabla, atascadas, casi, 2dis_no_1dis) todo renglón debe ser un graph6 válido (se admite
 un renglón que sea sólo la cabecera ">>graph6<<") y todas las gráficas deben tener el mismo orden.  En todos los
 modos cada renglón debe terminar en salto de línea y no puede contener bytes NUL (v2.1, hallazgo H-18): un último
 renglón sin salto de línea cuenta como inválido, porque puede ser un flujo truncado.  En los modos de
 diagnóstico se ignoran renglones vacíos y comentarios "#", y puede seguir texto tras el graph6 (separado por blanco).

 Resumen en stderr (un renglón).  Modo tabla:
   n=.. conexas=.. chi1=.. aciclicas=.. I=.. I_indecisas=.. I_S=.. I_SV=.. 3-Dis=.. 2-Dis=.. 1-Dis=.. 0-Dis=.. -1-Dis=..
   invalidos=.. errores=.. icert_truncados=.. memo_consultas=.. memo_aciertos=.. memo_colisiones_hash=.. version=v2.1
 (los 13 primeros campos son los de v1, en el mismo orden).
 Códigos de salida: 0 correcto; 1 uso; 2 capacidad interna excedida; 3 registros inválidos; 4 inconsistencia interna,
 invariante violado o error de lectura; 5 entrada no conexa (tabla) u órdenes mezclados (modos de conteo); 6 error de
 escritura en stdout o stderr (v2.1, hallazgo H-25).  El 6 tiene prioridad: si una salida no se escribió completa,
 la corrida no sirve aunque los conteos sean correctos.

 Compilar (portable, sin -march=native): gcc -O3 -std=c11 -Wall -Wextra -Wpedantic -Werror -o atascadas_v2 atascadas_v2.c
*/
#define _POSIX_C_SOURCE 200809L   /* getline */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/types.h>

#define VERSION "v2.1"
#define MAXN 16
typedef uint32_t msk;

static int n;      /* vértices de la gráfica actual */
static msk FULL;   /* máscara de todos sus vértices */

static inline int pc(msk x) { return __builtin_popcount(x); }
static inline int lowidx(msk x) { return __builtin_ctz(x); }

/* ---------------------------------------------------------------- graph6 */
/* Analiza el graph6 en s (sin fin de renglón).  Devuelve 0 y llena A, *nn si es válido; -1 si no. */
static int parse_g6(const char *s, msk *A, int *nn) {
  size_t L = strlen(s);
  if (L < 1) {
    return -1;
  }
  int c0 = (unsigned char)s[0];
  if (c0 < 63 || c0 > 126) {
    return -1;
  }
  int k = c0 - 63;
  if (k < 1 || k > MAXN) {
    return -1;
  }
  size_t nbits = (size_t)k * (size_t)(k - 1) / 2;
  if (L != 1 + (nbits + 5) / 6) {
    return -1;
  }
  for (size_t i = 1; i < L; i++) {
    int ch = (unsigned char)s[i];
    if (ch < 63 || ch > 126) {
      return -1;
    }
  }
  if (nbits % 6 != 0) {
    int last = (unsigned char)s[L - 1] - 63;
    int pad = 6 - (int)(nbits % 6);
    if (last & ((1 << pad) - 1)) {
      return -1;
    }
  }
  for (int i = 0; i < k; i++) {
    A[i] = 0;
  }
  size_t bit = 0;
  for (int j = 1; j < k; j++) {
    for (int i = 0; i < j; i++) {
      int val = (unsigned char)s[1 + bit / 6] - 63;
      if ((val >> (5 - (int)(bit % 6))) & 1) {
        A[i] |= 1u << j;
        A[j] |= 1u << i;
      }
      bit++;
    }
  }
  *nn = k;
  return 0;
}

static void print_g6(FILE *f, const msk *A, int nn) {
  char out[64];
  int c = 0;
  out[c++] = (char)(63 + nn);
  int val = 0;
  int nb = 0;
  for (int j = 1; j < nn; j++) {
    for (int i = 0; i < j; i++) {
      val = (val << 1) | (int)((A[i] >> j) & 1);
      nb++;
      if (nb == 6) {
        out[c++] = (char)(63 + val);
        val = 0;
        nb = 0;
      }
    }
  }
  if (nb > 0) {
    val <<= (6 - nb);
    out[c++] = (char)(63 + val);
  }
  out[c] = 0;
  fputs(out, f);
}

/* ------------------------------------------- subgráficas inducidas (máscara m, adyacencia A) */
static inline int is_cone(const msk *A, msk m) {
  msk t = m;
  while (t) {
    int w = lowidx(t);
    t &= t - 1;
    if ((A[w] & m) == (m ^ (1u << w))) {
      return 1;
    }
  }
  return 0;
}

static inline int connected(const msk *A, msk m) {
  if (!m) {
    return 0;
  }
  msk seen = 1u << lowidx(m);
  msk fr = seen;
  while (fr) {
    msk nx = 0;
    msk t = fr;
    while (t) {
      int v = lowidx(t);
      t &= t - 1;
      nx |= A[v] & m;
    }
    nx &= ~seen;
    seen |= nx;
    fr = nx;
  }
  return seen == m;
}

/* 0-desmantelamiento voraz (el orden no importa para 0-Dis).  1 si se llega a un vértice. */
static int dismantle0(const msk *A, msk m) {
  if (!m) {
    return 0;
  }
  int ch = 1;
  while (pc(m) > 1 && ch) {
    ch = 0;
    msk t = m;
    while (t) {
      int v = lowidx(t);
      t &= t - 1;
      msk link = A[v] & m;
      if (link && is_cone(A, link)) {
        m ^= 1u << v;
        ch = 1;
      }
    }
  }
  return pc(m) == 1;
}

/* característica de Euler del complejo de cliques inducido en cand */
static int chi(const msk *A, msk cand) {
  int s = 0;
  while (cand) {
    int v = lowidx(cand);
    cand &= cand - 1;
    s += 1 - chi(A, A[v] & cand);
  }
  return s;
}

/* ----------------------------------- homología Z2 completa del complejo de cliques inducido en m */
#define MAXF (1 << 14)               /* >= C(16,8) = 12870: cabe K16 */
#define MAXW (MAXF / 64 + 1)
static msk faces[MAXN + 1][MAXF];
static int nf[MAXN + 1];
static int32_t idxf[1 << MAXN];
static int maxdim;
static uint64_t cols[MAXF][MAXW];
static int pivot[MAXF];

static void enum_cliques(const msk *A, msk cur, msk cand) {
  int k = pc(cur);
  if (k > 0) {
    if (nf[k - 1] >= MAXF) {
      fprintf(stderr, "ERROR capacidad: overflow caras (dimension %d)\n", k - 1);
      exit(2);
    }
    faces[k - 1][nf[k - 1]++] = cur;
    if (k - 1 > maxdim) {
      maxdim = k - 1;
    }
  }
  while (cand) {
    int v = lowidx(cand);
    cand &= cand - 1;
    enum_cliques(A, cur | (1u << v), A[v] & cand);
  }
}

/* rango sobre Z2 de la matriz frontera d_k : C_k -> C_{k-1}, k >= 1 */
static int rank_boundary(int k) {
  int rows = nf[k - 1];
  int ncol = nf[k];
  if (!rows || !ncol) {
    return 0;
  }
  int W = (rows + 63) / 64;
  for (int i = 0; i < rows; i++) {
    idxf[faces[k - 1][i]] = i;
    pivot[i] = -1;
  }
  int r = 0;
  for (int c = 0; c < ncol; c++) {
    uint64_t *col = cols[c];
    memset(col, 0, (size_t)W * 8);
    msk f = faces[k][c];
    msk t = f;
    while (t) {
      int v = lowidx(t);
      t &= t - 1;
      int i = idxf[f ^ (1u << v)];
      col[i >> 6] ^= 1ull << (i & 63);
    }
    for (;;) {
      int low = -1;
      for (int w = W - 1; w >= 0; w--) {
        if (col[w]) {
          low = w * 64 + 63 - __builtin_clzll(col[w]);
          break;
        }
      }
      if (low < 0) {
        break;
      }
      if (pivot[low] < 0) {
        pivot[low] = c;
        r++;
        break;
      }
      const uint64_t *p = cols[pivot[low]];
      for (int w = 0; w < W; w++) {
        col[w] ^= p[w];
      }
    }
  }
  return r;
}

static int betti[MAXN + 2];

/* 1 si la homología reducida Z2 del complejo de cliques de m es nula; llena betti[] */
static int acyclic_full(const msk *A, msk m) {
  for (int k = 0; k < MAXN + 2; k++) {
    betti[k] = 0;
  }
  if (!m) {
    betti[0] = -1;
    return 0;
  }
  for (int k = 0; k <= MAXN; k++) {
    nf[k] = 0;
  }
  maxdim = 0;
  enum_cliques(A, 0, m);
  int rk[MAXN + 2];
  for (int k = 0; k < MAXN + 2; k++) {
    rk[k] = 0;
  }
  for (int k = 1; k <= maxdim; k++) {
    rk[k] = rank_boundary(k);
  }
  int ok = 1;
  betti[0] = nf[0] - rk[1];
  if (betti[0] != 1) {
    ok = 0;
  }
  for (int k = 1; k <= maxdim; k++) {
    betti[k] = nf[k] - rk[k] - rk[k + 1];
    if (betti[k] != 0) {
      ok = 0;
    }
  }
  return ok;
}

/* aciclicidad con filtros baratos primero (mismo resultado que acyclic_full) */
static int acyclic(const msk *A, msk m) {
  if (!m) {
    return 0;
  }
  if (pc(m) == 1) {
    return 1;
  }
  if (!connected(A, m)) {
    return 0;
  }
  if (dismantle0(A, m)) {
    return 1;
  }
  if (chi(A, m) != 1) {
    return 0;
  }
  return acyclic_full(A, m);
}

/* ------------------------------------------- I_SV exacto: programación dinámica sobre subconjuntos */
static uint8_t memo_isv[1 << MAXN];   /* 0 desconocido, 1 sí, 2 no; índice = subconjunto (exacto) */

static int isv(const msk *A, msk m) {
  if (!m) {
    return 0;
  }
  if (pc(m) == 1) {
    return 1;
  }
  uint8_t *st = &memo_isv[m];
  if (*st) {
    return *st == 1;
  }
  int res = 0;
  msk t = m;
  while (t && !res) {
    int v = lowidx(t);
    t &= t - 1;
    msk link = A[v] & m;
    if (link && isv(A, link) && isv(A, m ^ (1u << v))) {
      res = 1;
    }
  }
  *st = res ? 1 : 2;
  return res;
}

static int isv_graph(const msk *A) {
  memset(memo_isv, 0, (size_t)1 << n);
  return isv(A, FULL);
}

/* ------------------------------------------------ clave completa de un estado (H-01) */
/* Un estado de la búsqueda I_S es la gráfica inducida en m con la adyacencia actual A (que puede tener aristas
   borradas).  Dos estados son el mismo subproblema si y sólo si sus claves son iguales byte a byte. */
typedef struct {
  uint16_t m;
  uint16_t r[MAXN];
} gkey;

static void make_key(const msk *A, msk m, gkey *k) {
  memset(k, 0, sizeof *k);
  k->m = (uint16_t)m;
  for (int i = 0; i < n; i++) {
    if (m >> i & 1) {
      k->r[i] = (uint16_t)(A[i] & m);
    }
  }
}

static uint64_t hash_key(const gkey *k) {
  const unsigned char *p = (const unsigned char *)k;
  uint64_t h = 1469598103934665603ull;
  for (size_t i = 0; i < sizeof *k; i++) {
    h ^= p[i];
    h *= 1099511628211ull;
  }
  h ^= h >> 30;
  h *= 0xbf58476d1ce4e5b9ull;
  h ^= h >> 27;
  h *= 0x94d049bb133111ebull;
  h ^= h >> 31;
#ifdef HASH_WEAK_BITS
  /* sólo para pruebas: trunca el hash para forzar colisiones; el resultado debe ser idéntico (clave completa) */
  h &= ((uint64_t)1 << HASH_WEAK_BITS) - 1;
#endif
  return h | 1;   /* 0 marca casilla vacía */
}

/* ------------------------------------------- I_S exacto (borrado de vértices y aristas) con memo */
#define HBITS 22
#define HSIZE ((uint64_t)1 << HBITS)
static uint64_t *htab = NULL;
static gkey *hkey = NULL;
static uint8_t *hval = NULL;
static uint64_t hcount = 0;
static unsigned long long memo_q = 0, memo_hit = 0, memo_coll = 0, memo_resets = 0;

static int memo_get(uint64_t h, const gkey *k) {
  memo_q++;
  uint64_t p = h & (HSIZE - 1);
  while (htab[p]) {
    if (htab[p] == h) {
      if (memcmp(&hkey[p], k, sizeof *k) == 0) {
        memo_hit++;
        return hval[p];
      }
      memo_coll++;
    }
    p = (p + 1) & (HSIZE - 1);
  }
  return 0;
}

static void memo_put(uint64_t h, const gkey *k, int v) {
  if (hcount > HSIZE * 3 / 4) {
    memset(htab, 0, sizeof(uint64_t) * HSIZE);
    hcount = 0;
    memo_resets++;
  }
  uint64_t p = h & (HSIZE - 1);
  while (htab[p] && !(htab[p] == h && memcmp(&hkey[p], k, sizeof *k) == 0)) {
    p = (p + 1) & (HSIZE - 1);
  }
  if (!htab[p]) {
    hcount++;
  }
  htab[p] = h;
  hkey[p] = *k;
  hval[p] = (uint8_t)v;
}

static long long is_nodes = 0;

/* ¿la gráfica (A restringida a m) está en I_S?  A puede tener aristas borradas; se restaura al salir. */
static int is_rec(msk *A, msk m) {
  if (!m) {
    return 0;
  }
  if (pc(m) == 1) {
    return 1;
  }
  if (!connected(A, m)) {
    return 0;
  }
  if (dismantle0(A, m)) {
    return 1;                       /* 0-Dis ⊂ I_SV ⊂ I_S */
  }
  gkey key;
  make_key(A, m, &key);
  uint64_t h = hash_key(&key);
  int g = memo_get(h, &key);
  if (g) {
    return g == 1;
  }
  is_nodes++;
  int res = 0;
  msk t = m;
  while (t && !res) {               /* vértices I_S-borrables */
    int v = lowidx(t);
    t &= t - 1;
    msk link = A[v] & m;
    if (link && is_rec(A, link) && is_rec(A, m ^ (1u << v))) {
      res = 1;
    }
  }
  for (int u = 0; u < n && !res; u++) {   /* aristas I_S-borrables */
    if (!(m >> u & 1)) {
      continue;
    }
    for (int v = u + 1; v < n && !res; v++) {
      if (!(m >> v & 1) || !(A[u] >> v & 1)) {
        continue;
      }
      msk cn = A[u] & A[v] & m;
      if (cn && is_rec(A, cn)) {
        A[u] ^= 1u << v;
        A[v] ^= 1u << u;
        if (is_rec(A, m)) {
          res = 1;
        }
        A[u] ^= 1u << v;
        A[v] ^= 1u << u;
      }
    }
  }
  memo_put(h, &key, res ? 1 : 2);
  return res;
}

static int is_set(const msk *A, msk m) {
  msk B[MAXN];
  memcpy(B, A, sizeof(msk) * (size_t)n);
  return is_rec(B, m);
}

static int is_graph(const msk *A) {
  return is_set(A, FULL);
}

/* ---------------------------------------------------- filtros de atascamiento (criterio de búsqueda) */
static int count_acyclic_links(const msk *A, int tope, msk *which) {
  int c = 0;
  *which = 0;
  for (int v = 0; v < n; v++) {
    if (acyclic(A, A[v])) {
      c++;
      *which |= 1u << v;
      if (c > tope) {
        return c;
      }
    }
  }
  return c;
}

static int edges_stuck(const msk *A) {
  for (int u = 0; u < n; u++) {
    for (int v = u + 1; v < n; v++) {
      if (A[u] >> v & 1) {
        msk cn = A[u] & A[v];
        if (cn && acyclic(A, cn)) {
          return 0;
        }
      }
    }
  }
  return 1;
}

/* ------------------------------ certificado de I-contraibilidad por pegados I4 (BFS por niveles) ------
   Busca una sucesión de pegados de aristas uv con N(u,v) ∈ I_S ⊂ I (transformación I4) que lleve a una gráfica en
   I_S.  Como I4 y los borrados I_S son transformaciones contráctiles de Ivashchenko, esto certifica G ∈ I.        */
#define QMAX 200000
#define SBITS 20
#define SSIZE ((uint32_t)1 << SBITS)
static msk qg[QMAX][MAXN];
static int qpar[QMAX];
static int qedge[QMAX];
static int qdepth[QMAX];
static uint64_t seen_h[SSIZE];
static gkey seen_k[SSIZE];
static uint32_t seen_used[QMAX + 2];
static int nused = 0;

static void seen_clear(void) {
  for (int i = 0; i < nused; i++) {
    seen_h[seen_used[i]] = 0;
  }
  nused = 0;
}

/* 1 si la gráfica C (completa) ya estaba en el conjunto; si no, la inserta y devuelve 0 */
static int seen_test_insert(const msk *C) {
  gkey k;
  make_key(C, FULL, &k);
  uint64_t h = hash_key(&k);
  uint32_t p = (uint32_t)(h & (SSIZE - 1));
  while (seen_h[p]) {
    if (seen_h[p] == h && memcmp(&seen_k[p], &k, sizeof k) == 0) {
      return 1;
    }
    p = (p + 1) & (SSIZE - 1);
  }
  seen_h[p] = h;
  seen_k[p] = k;
  seen_used[nused++] = p;
  return 0;
}

static unsigned long long icert_trunc = 0;

/* Devuelve el índice en la cola del estado I_S hallado (>= 0), -1 si no hay certificado con <= maxd pegados,
   -2 si la cola se llenó (indecisión por capacidad). */
static int icert_search(const msk *A, int maxd) {
  int head = 0;
  int tail = 1;
  memcpy(qg[0], A, sizeof(msk) * (size_t)n);
  qpar[0] = -1;
  qedge[0] = -1;
  qdepth[0] = 0;
  seen_clear();
  seen_test_insert(A);
  while (head < tail) {
    int cur = head++;
    const msk *B = qg[cur];
    if (is_graph(B)) {
      seen_clear();
      return cur;
    }
    if (qdepth[cur] >= maxd) {
      continue;
    }
    for (int u = 0; u < n; u++) {
      for (int v = u + 1; v < n; v++) {
        if (B[u] >> v & 1) {
          continue;
        }
        msk cn = B[u] & B[v];
        if (!cn || !is_set(B, cn)) {
          continue;                  /* se exige N(u,v) ∈ I_S */
        }
        msk C[MAXN];
        memcpy(C, B, sizeof(msk) * (size_t)n);
        C[u] |= 1u << v;
        C[v] |= 1u << u;
        if (seen_test_insert(C)) {
          continue;
        }
        if (tail >= QMAX) {
          seen_clear();
          return -2;
        }
        memcpy(qg[tail], C, sizeof(msk) * (size_t)n);
        qpar[tail] = cur;
        qedge[tail] = (u << 8) | v;
        qdepth[tail] = qdepth[cur] + 1;
        tail++;
      }
    }
  }
  seen_clear();
  return -1;
}

static void print_cert_path(FILE *f, int cur) {
  int path[64];
  int k = 0;
  for (int x = cur; x > 0; x = qpar[x]) {
    path[k++] = qedge[x];
  }
  for (int i = k - 1; i >= 0; i--) {
    fprintf(f, " {%d,%d}", path[i] >> 8, path[i] & 255);
  }
}

static void icert_report(const msk *A, int maxd) {
  int r = icert_search(A, maxd);
  if (r >= 0) {
    printf("I-CONTRAIBLE: en I_S tras %d pegado(s) de arista I4:", qdepth[r]);
    print_cert_path(stdout, r);
    printf("\n  gráfica final (g6): ");
    print_g6(stdout, qg[r], n);
    printf("\n");
  } else if (r == -2) {
    printf("INDECISO: cola llena (QMAX=%d) antes de agotar <= %d pegados\n", QMAX, maxd);
  } else {
    printf("NO se halló certificado con <= %d pegados de arista\n", maxd);
  }
}

/* ------------------------------ cerradura por pegados de aristas I4 con N(u,v) ∈ I_S (etiquetada) ------ */
static int cerradura(const msk *A) {
  int head = 0;
  int tail = 1;
  memcpy(qg[0], A, sizeof(msk) * (size_t)n);
  qdepth[0] = 0;
  seen_clear();
  seen_test_insert(A);
  int truncada = 0;
  while (head < tail) {
    int cur = head++;
    const msk *B = qg[cur];
    int isS = is_graph(B);
    printf("%s ", isS ? "I_S" : "NO_I_S");
    print_g6(stdout, B, n);
    printf(" aristas_agregadas=%d\n", qdepth[cur]);
    if (isS) {
      continue;      /* las supergráficas de una I_S por pegados I4 son I_S */
    }
    for (int u = 0; u < n && !truncada; u++) {
      for (int v = u + 1; v < n && !truncada; v++) {
        if (B[u] >> v & 1) {
          continue;
        }
        msk cn = B[u] & B[v];
        if (!cn || !is_set(B, cn)) {
          continue;
        }
        msk C[MAXN];
        memcpy(C, B, sizeof(msk) * (size_t)n);
        C[u] |= 1u << v;
        C[v] |= 1u << u;
        if (seen_test_insert(C)) {
          continue;
        }
        if (tail >= QMAX) {
          truncada = 1;
          break;
        }
        memcpy(qg[tail], C, sizeof(msk) * (size_t)n);
        qdepth[tail] = qdepth[cur] + 1;
        tail++;
      }
    }
  }
  seen_clear();
  if (truncada) {
    printf("CERRADURA_TRUNCADA: cola llena (QMAX=%d)\n", QMAX);
  }
  return truncada;
}

/* ------------------------------------------------ traza: sucesión explícita de borrados I_S hasta K1 */
static const char *cert_vecindad(const msk *A, msk m) {
  if (pc(m) == 1) {
    return "K1";
  }
  if (is_cone(A, m)) {
    return "cono (0-Dis)";
  }
  if (dismantle0(A, m)) {
    return "0-Dis";
  }
  return "I_S (por recursion)";
}

static void print_set(msk m) {
  printf("{");
  int first = 1;
  for (int v = 0; v < n; v++) {
    if (m >> v & 1) {
      printf(first ? "%d" : ",%d", v);
      first = 0;
    }
  }
  printf("}");
}

static int traza(msk *A, msk m, int paso) {
  if (pc(m) == 1) {
    printf("  => queda el vertice ");
    print_set(m);
    printf(" = K1.\n");
    return 1;
  }
  if (!connected(A, m)) {
    return 0;
  }
  msk t = m;
  while (t) {
    int v = lowidx(t);
    t &= t - 1;
    msk link = A[v] & m;
    if (link && is_rec(A, link)) {
      msk m2 = m ^ (1u << v);
      if (is_rec(A, m2)) {
        printf("  %2d. borrar vertice %d: N(%d) = ", paso, v, v);
        print_set(link);
        printf("  [%s]\n", cert_vecindad(A, link));
        return traza(A, m2, paso + 1);
      }
    }
  }
  for (int u = 0; u < n; u++) {
    if (!(m >> u & 1)) {
      continue;
    }
    for (int v = u + 1; v < n; v++) {
      if (!(m >> v & 1) || !(A[u] >> v & 1)) {
        continue;
      }
      msk cn = A[u] & A[v] & m;
      if (cn && is_rec(A, cn)) {
        A[u] ^= 1u << v;
        A[v] ^= 1u << u;
        if (is_rec(A, m)) {
          printf("  %2d. borrar arista {%d,%d}: N(%d,%d) = ", paso, u, v, u, v);
          print_set(cn);
          printf("  [%s]\n", cert_vecindad(A, cn));
          return traza(A, m, paso + 1);
        }
        A[u] ^= 1u << v;
        A[v] ^= 1u << u;
      }
    }
  }
  return 0;
}

/* ---------------------------------------------- k-desmantelabilidad exacta (Def. 10) */
static uint8_t *memo_kdis[4];   /* k = 1..3; índice = subconjunto (exacto) */

static int kdis(const msk *A, msk m, int k) {
  if (!m) {
    return 0;
  }
  if (pc(m) == 1) {
    return 1;
  }
  if (k < 0) {
    return is_cone(A, m);
  }
  if (k == 0) {
    return dismantle0(A, m);
  }
  uint8_t *st = &memo_kdis[k][m];
  if (*st) {
    return *st == 1;
  }
  int res = 0;
  msk t = m;
  while (t && !res) {
    int v = lowidx(t);
    t &= t - 1;
    msk link = A[v] & m;
    if (link && kdis(A, link, k - 1) && kdis(A, m ^ (1u << v), k)) {
      res = 1;
    }
  }
  *st = res ? 1 : 2;
  return res;
}

static int kdis_graph(const msk *A, int k) {
  for (int j = 1; j <= k; j++) {
    memset(memo_kdis[j], 0, (size_t)1 << n);
  }
  return kdis(A, FULL, k);
}

/* ------------------------------------------------------------------ verificar (diagnóstico) */
static void verificar(const msk *A, const char *g6, int maxd) {
  (void)maxd;
  int m_edges = 0;
  for (int v = 0; v < n; v++) {
    m_edges += pc(A[v]);
  }
  m_edges /= 2;
  printf("== %s  n=%d aristas=%d\n", g6, n, m_edges);
  int ac = acyclic_full(A, FULL);
  printf("chi=%d conexa=%d aciclica=%d betti=", chi(A, FULL), connected(A, FULL), ac);
  for (int k = 0; k <= maxdim; k++) {
    printf("%d ", betti[k]);
  }
  printf("\n");
  int nv_ac = 0;
  int nv_is = 0;
  for (int v = 0; v < n; v++) {
    msk l = A[v];
    int a = acyclic(A, l);
    int s = l ? is_set(A, l) : 0;
    nv_ac += a;
    nv_is += s;
    printf("  N(%d) = {", v);
    for (int u = 0; u < n; u++) {
      if (l >> u & 1) {
        printf("%d ", u);
      }
    }
    printf("} |N|=%d conexa=%d cono=%d aciclica=%d I_S=%d%s\n", pc(l), connected(A, l), is_cone(A, l), a, s,
           s ? "  <-- vertice I_S-borrable" : "");
  }
  int ne_ac = 0;
  int ne_is = 0;
  for (int u = 0; u < n; u++) {
    for (int v = u + 1; v < n; v++) {
      if (!(A[u] >> v & 1)) {
        continue;
      }
      msk cn = A[u] & A[v];
      int a = cn ? acyclic(A, cn) : 0;
      int s = cn ? is_set(A, cn) : 0;
      ne_ac += a;
      ne_is += s;
      printf("  N(%d,%d) = {", u, v);
      for (int x = 0; x < n; x++) {
        if (cn >> x & 1) {
          printf("%d ", x);
        }
      }
      printf("} vacia=%d aciclica=%d I_S=%d%s\n", cn == 0, a, s, s ? "  <-- arista I_S-borrable" : "");
    }
  }
  int sin_mov = (nv_is == 0 && ne_is == 0);
  int atascada = (n >= 2 && ac && sin_mov);
  printf("vertices con vecindad aciclica: %d (en I_S: %d); aristas con vecindad comun aciclica: %d (en I_S: %d)\n",
         nv_ac, nv_is, ne_ac, ne_is);
  printf("0-Dis=%d  I_SV=%d  I_S=%d  sin_movimientos=%d  atascada=%d\n", dismantle0(A, FULL), isv_graph(A),
         is_graph(A), sin_mov, atascada);
}

/* ----------------------------------------------------------------------------- main */
static int is_counting_mode(const char *modo) {
  return !strcmp(modo, "tabla") || !strcmp(modo, "atascadas") || !strcmp(modo, "casi") ||
         !strcmp(modo, "2dis_no_1dis");
}

static void usage(void) {
  fprintf(stderr, "uso: atascadas_v2 [--modo tabla|atascadas|casi|2dis_no_1dis|verificar|icert|cerradura|traza]"
                  " [--prof d] [--cert] [--version]  < graph6\n");
}

int main(int argc, char **argv) {
  const char *modo = "atascadas";
  int maxd = 3;
  int want_cert = 0;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--modo") && i + 1 < argc) {
      modo = argv[++i];
    } else if (!strcmp(argv[i], "--prof") && i + 1 < argc) {
      const char *arg = argv[++i];
      char *end = NULL;
      long d = strtol(arg, &end, 10);
      if (!*arg || strspn(arg, "0123456789") != strlen(arg) || !end || *end || d < 0 || d > 60) {
        usage();
        return 1;
      }
      maxd = (int)d;
    } else if (!strcmp(argv[i], "--cert")) {
      want_cert = 1;
    } else if (!strcmp(argv[i], "--version")) {
      printf("atascadas %s MAXN=%d MAXF=%d HBITS=%d QMAX=%d\n", VERSION, MAXN, MAXF, HBITS, QMAX);
      return (fflush(stdout) != 0 || ferror(stdout)) ? 6 : 0;
    } else {
      usage();
      return 1;
    }
  }
  int M_AT = !strcmp(modo, "atascadas");
  int M_CASI = !strcmp(modo, "casi");
  int M_TAB = !strcmp(modo, "tabla");
  int M_VER = !strcmp(modo, "verificar");
  int M_IC = !strcmp(modo, "icert");
  int M_CE = !strcmp(modo, "cerradura");
  int M_TR = !strcmp(modo, "traza");
  int M_D21 = !strcmp(modo, "2dis_no_1dis");
  if (!(M_AT || M_CASI || M_TAB || M_VER || M_IC || M_CE || M_TR || M_D21)) {
    fprintf(stderr, "modo desconocido: %s\n", modo);
    usage();
    return 1;
  }
  int counting = is_counting_mode(modo);
  htab = calloc((size_t)HSIZE, sizeof(uint64_t));
  hkey = calloc((size_t)HSIZE, sizeof(gkey));
  hval = calloc((size_t)HSIZE, 1);
  for (int j = 0; j < 4; j++) {
    memo_kdis[j] = calloc((size_t)1 << MAXN, 1);
  }
  if (!htab || !hkey || !hval || !memo_kdis[0] || !memo_kdis[1] || !memo_kdis[2] || !memo_kdis[3]) {
    fprintf(stderr, "ERROR capacidad: sin memoria\n");
    return 2;
  }

  char line[4096];
  msk A[MAXN];
  unsigned long long total = 0, invalid = 0, errors = 0, disconnected = 0, mixed = 0;
  unsigned long long pasa_cono = 0, pasa_chi = 0, pasa_links = 0, pasa_aristas = 0, encontradas = 0;
  unsigned long long c_acyc = 0, c_is = 0, c_isv = 0, c_d0 = 0, c_chi1 = 0, c_dm1 = 0, c_d1 = 0, c_d2 = 0, c_d3 = 0;
  unsigned long long c_I = 0, c_Iind = 0, out_inois = 0, out_ind = 0;
  int n_first = 0;
  int have_first = 0;

  char *buf = NULL;
  size_t cap = 0;
  ssize_t got;
  while ((got = getline(&buf, &cap, stdin)) != -1) {
    size_t L = (size_t)got;
    if (L >= sizeof line) {          /* renglón más largo que el búfer: inválido */
      invalid++;
      fprintf(stderr, "g6 inválido (renglón demasiado largo)\n");
      continue;
    }
    if (memchr(buf, '\0', L)) {      /* un NUL ocultaría el resto del renglón (H-18) */
      invalid++;
      fprintf(stderr, "g6 inválido (byte NUL en el renglón)\n");
      continue;
    }
    if (buf[L - 1] != '\n') {        /* último renglón sin salto de línea: posible truncamiento (H-18) */
      invalid++;
      fprintf(stderr, "g6 inválido (último renglón sin salto de línea)\n");
      continue;
    }
    memcpy(line, buf, L + 1);
    while (L && (line[L - 1] == '\n' || line[L - 1] == '\r')) {
      line[--L] = 0;
    }
    char *s = line;
    if (!strncmp(s, ">>graph6<<", 10)) {
      s += 10;
      if (!*s) {
        continue;                    /* renglón que es sólo cabecera */
      }
    }
    if (!counting && (*s == 0 || *s == '#')) {
      continue;
    }
    char *rest = s + strcspn(s, " \t");
    if (*rest) {
      if (counting) {
        invalid++;
        fprintf(stderr, "g6 inválido (texto adicional): %s\n", line);
        continue;
      }
      *rest = 0;
    }
    int nn = 0;
    if (parse_g6(s, A, &nn)) {
      invalid++;
      fprintf(stderr, "g6 inválido: %s\n", line);
      continue;
    }
    n = nn;
    FULL = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
    if (counting) {
      if (!have_first) {
        n_first = n;
        have_first = 1;
      } else if (n != n_first) {
        mixed++;
        fprintf(stderr, "orden distinto (%d != %d): %s\n", n, n_first, s);
        continue;
      }
    }
    if (M_TAB && !connected(A, FULL)) {
      disconnected++;
      fprintf(stderr, "entrada no conexa: %s\n", s);
      continue;
    }
    total++;

    if (M_AT) {
      int ok = 1;
      for (int v = 0; v < n; v++) {
        if (pc(A[v]) < 2 || is_cone(A, A[v])) {
          ok = 0;
          break;
        }
      }
      if (!ok) {
        continue;
      }
      pasa_cono++;
      if (chi(A, FULL) != 1) {
        continue;
      }
      pasa_chi++;
      msk w;
      if (count_acyclic_links(A, 0, &w) > 0) {
        continue;
      }
      pasa_links++;
      if (!edges_stuck(A)) {
        continue;
      }
      pasa_aristas++;
      if (!acyclic_full(A, FULL)) {
        continue;
      }
      encontradas++;
      printf("%s\n", s);
      fflush(stdout);
    } else if (M_CASI) {
      if (chi(A, FULL) != 1) {
        continue;
      }
      pasa_chi++;
      msk w;
      int c = count_acyclic_links(A, 1, &w);
      if (c != 1) {
        continue;
      }
      pasa_links++;
      if (!edges_stuck(A)) {
        continue;
      }
      pasa_aristas++;
      if (!acyclic_full(A, FULL)) {
        continue;
      }
      encontradas++;
      printf("%s %d\n", s, lowidx(w));
      fflush(stdout);
    } else if (M_TAB) {
      int ch = (chi(A, FULL) == 1);
      c_chi1 += ch;
      int ac = ch && acyclic_full(A, FULL);
      c_acyc += ac;
      int d0 = dismantle0(A, FULL);
      c_d0 += d0;
      int sv = d0 || (ac && isv_graph(A));
      c_isv += sv;
      int si = sv || (ac && is_graph(A));
      c_is += si;
      int dm1 = is_cone(A, FULL);
      c_dm1 += dm1;
      int d1 = d0 || (sv && kdis_graph(A, 1));
      c_d1 += d1;
      int d2 = d1 || (sv && kdis_graph(A, 2));
      c_d2 += d2;
      int d3 = d2 || (sv && kdis_graph(A, 3));
      c_d3 += d3;
      if (ac && !si) {
        int r = icert_search(A, maxd);
        if (r >= 0) {
          c_I++;
          out_inois++;
          printf("I_NO_IS %s\n", s);
          if (want_cert) {
            printf("CERT_I4 %s", s);
            print_cert_path(stdout, r);
            printf("\n");
          }
        } else {
          if (r == -2) {
            icert_trunc++;
          }
          c_Iind++;
          out_ind++;
          printf("ACICLICA_NO_IS_INDECISA %s\n", s);
        }
      } else if (si) {
        c_I++;
      }
      if (si && !ac) {
        errors++;
        printf("ERROR IS_NO_ACICLICA %s\n", s);
      }
    } else if (M_D21) {
      if (dismantle0(A, FULL)) {
        continue;                                    /* 0-Dis ⊂ 1-Dis */
      }
      if (chi(A, FULL) != 1 || !acyclic_full(A, FULL)) {
        continue;                                    /* k-Dis ⊂ I_S ⇒ acíclica */
      }
      if (!isv_graph(A)) {
        continue;                                    /* k-Dis ⊂ I_SV */
      }
      if (kdis_graph(A, 1)) {
        continue;
      }
      if (kdis_graph(A, 2)) {
        encontradas++;
        printf("2DIS_NO_1DIS %s\n", s);
        fflush(stdout);
      }
    } else if (M_IC) {
      printf("== %s\n", s);
      icert_report(A, maxd);
    } else if (M_CE) {
      printf("== cerradura de %s\n", s);
      if (cerradura(A)) {
        errors++;
      }
    } else if (M_TR) {
      printf("== traza I_S de %s\n", s);
      msk B[MAXN];
      memcpy(B, A, sizeof(msk) * (size_t)n);
      if (!traza(B, FULL, 1)) {
        printf("  NO es I_S\n");
      }
    } else if (M_VER) {
      verificar(A, s, maxd);
    }
  }
  if (ferror(stdin)) {
    fprintf(stderr, "ERROR de lectura en stdin\n");
    errors++;
  }
  int nprint = counting ? n_first : n;
  if (M_TAB) {
    /* invariantes de la tabla (se cumplen por construcción; se comprueban para detectar regresiones) */
    int bad = !(c_dm1 <= c_d0 && c_d0 <= c_d1 && c_d1 <= c_d2 && c_d2 <= c_d3 && c_d3 <= c_isv && c_isv <= c_is &&
                c_is <= c_I && c_I <= c_acyc && c_acyc <= c_chi1 && c_chi1 <= total && c_acyc == c_I + c_Iind &&
                c_I - c_is == out_inois && c_Iind == out_ind);
    if (bad) {
      errors++;
      fprintf(stderr, "ERROR invariante de la tabla violado\n");
    }
    fprintf(stderr,
            "n=%d conexas=%llu chi1=%llu aciclicas=%llu I=%llu I_indecisas=%llu I_S=%llu I_SV=%llu 3-Dis=%llu "
            "2-Dis=%llu 1-Dis=%llu 0-Dis=%llu -1-Dis=%llu invalidos=%llu errores=%llu icert_truncados=%llu "
            "memo_consultas=%llu memo_aciertos=%llu memo_colisiones_hash=%llu version=%s\n",
            nprint, total, c_chi1, c_acyc, c_I, c_Iind, c_is, c_isv, c_d3, c_d2, c_d1, c_d0, c_dm1, invalid,
            errors + disconnected + mixed, icert_trunc, memo_q, memo_hit, memo_coll, VERSION);
  } else {
    fprintf(stderr,
            "n=%d total=%llu pasa_cono=%llu pasa_chi=%llu pasa_vecindades=%llu pasa_aristas=%llu encontradas=%llu "
            "invalidos=%llu errores=%llu memo_consultas=%llu memo_aciertos=%llu memo_colisiones_hash=%llu "
            "version=%s\n",
            nprint, total, pasa_cono, pasa_chi, pasa_links, pasa_aristas, encontradas, invalid,
            errors + mixed, memo_q, memo_hit, memo_coll, VERSION);
  }
  free(buf);
  int werr = (fflush(stdout) != 0) | (ferror(stdout) != 0);
  werr |= (fflush(stderr) != 0) | (ferror(stderr) != 0);
  if (werr) {
    fprintf(stderr, "ERROR de escritura en stdout o stderr\n");
    return 6;
  }
  if (invalid) {
    return 3;
  }
  if (errors) {
    return 4;
  }
  if (disconnected || mixed) {
    return 5;
  }
  return 0;
}
