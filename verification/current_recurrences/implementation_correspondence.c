
#define main classifier_main
#include "../../v2/src/atascadas_v2.c"
#undef main
int main(void) {
  htab = calloc((size_t)HSIZE, sizeof(uint64_t));
  hkey = calloc((size_t)HSIZE, sizeof(gkey));
  hval = calloc((size_t)HSIZE, 1);
  for (int j = 0; j < 4; ++j) memo_kdis[j] = calloc((size_t)1 << MAXN, 1);
  if (!htab || !hkey || !hval) return 2;
  for (int j = 0; j < 4; ++j) if (!memo_kdis[j]) return 2;
  for (n = 0; n <= 5; ++n) {
    FULL = (1u << n) - 1;
    unsigned limit = 1u << (n * (n - 1) / 2);
    for (unsigned code = 0; code < limit; ++code) {
      msk A[MAXN] = {0};
      int bit = 0;
      for (int v = 1; v < n; ++v) for (int u = 0; u < v; ++u, ++bit) {
        if ((code >> bit) & 1) { A[u] |= 1u << v; A[v] |= 1u << u; }
      }
      memset(memo_isv, 0, sizeof(memo_isv));
      for (int j = 0; j < 4; ++j) memset(memo_kdis[j], 0, (size_t)1 << MAXN);
      for (msk active = 0; active <= FULL; ++active) {
        unsigned vfirst = 0, efirst = 0;
        for (int v = 0; v < n; ++v) if ((active >> v) & 1) {
          if (is_set(A, A[v] & active) && is_set(A, active ^ (1u << v))) vfirst |= 1u << v;
        }
        bit = 0;
        for (int v = 1; v < n; ++v) for (int u = 0; u < v; ++u, ++bit) {
          if (!((active >> u) & 1) || !((active >> v) & 1) || !((A[u] >> v) & 1)) continue;
          if (is_set(A, A[u] & A[v] & active)) {
            msk B[MAXN]; memcpy(B, A, sizeof(B));
            B[u] ^= 1u << v; B[v] ^= 1u << u;
            if (is_set(B, active)) efirst |= 1u << bit;
          }
        }
        printf("%d %u %u %d %d %d %d %d %d %d %d %d %d %d %u %u\n",
          n, code, active, is_set(A, active), isv(A, active),
          is_cone(A, active), kdis(A, active, 0), kdis(A, active, 1),
          kdis(A, active, 2), kdis(A, active, 3), acyclic_full(A, active), acyclic(A, active),
          chi(A, active), connected(A, active), vfirst, efirst);
      }
    }
  }
  return finish_streams(0);
}
