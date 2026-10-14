#!/usr/bin/env python3
"""Generate the LaTeX tables of the paper from the data files in ../data (run from paper/)."""
import csv, os
os.makedirs('tables', exist_ok=True)

def num(x):
    return r'\num{%s}' % x if x not in ('', None) else '--'

# Table: extended cardinalities
rows = [r for r in csv.reader(l for l in open('../data/table_cardinalities.csv') if not l.startswith('#'))]
hdr, rows = rows[0], rows[1:]
cols = ['n','connected','chi=1','Z2-acyclic','I-contractible','strong I-contractible (J_S)','J_VS','3-Dis','2-Dis','1-Dis','0-Dis','(-1)-Dis']
idx = [hdr.index(c) for c in cols]
with open('tables/table_cardinalities.tex','w') as f:
    f.write(r'''\begin{tabular}{@{}rrrrrrrrrrrr@{}}
\toprule
$n$ & connected & $\chi=1$ & $\Ztwo$-acyclic & $\I$ & $\IS$ & $\IVS$ & $3$-Dis & $2$-Dis & $1$-Dis & $0$-Dis & $(-1)$-Dis \\
\midrule
''')
    for r in rows:
        vals = [r[i] for i in idx]
        f.write(' & '.join([vals[0]] + [num(v) for v in vals[1:]]) + r' \\' + '\n')
    f.write(r'''14$^{\dagger}$ & & \multicolumn{10}{l}{\emph{computation in progress}; stuck $\Ztwo$-acyclic $\setminus\IS=51$, $\I\setminus\IS\ge 29$ (Theorem~\ref{thm:B})} \\
\bottomrule
\end{tabular}
''')

# Table: the 51 stuck graphs
rows = [l.rstrip('\n').split('\t') for l in open('../data/stuck_14_K4free.tsv') if not l.startswith('#')]
ESC = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '_': r'\_', '^': r'\^{}',
       '&': r'\&', '#': r'\#', '%': r'\%', '$': r'\$'}
def tex_g6(s):
    return r'\texttt{' + ''.join(ESC.get(c, c) for c in s) + '}'
struct = {r['g6']: r for r in csv.DictReader(open('../data/structure_84_graphs.csv'))}
def pattern(g6):
    r = struct.get(g6)
    if not r or r['superficie'] != 'disco' or not r['k_ciclo']: 
        return (r['superficie'].split(' (')[0] if r else '') .replace('anillo','annulus').replace('desconexo','not a disc')
    rot = int(r['numero_rotacion']); k = r['k_ciclo']
    pat = r'$a^{3}$' if abs(rot) == 3 else r'$a\,a\,a^{-1}$'
    sp = r' (+spur)' if r['espolones'].strip() else ''
    return f'{k} / {pat}{sp}'
with open('tables/stuck51.tex','w') as f:
    f.write(r'''\begin{longtable}{@{}llrrlcrl@{}}
\caption{The $51$ stuck $\Ztwo$-acyclic $K_4$-free graphs on $14$ vertices. $m$ = edges, $t$ = triangles; $H_1=H_1(\cl(G);\ZZ)$; ``$\I$'' gives the $\mathrm{I}_4$ edge certifying I-contractibility; $k$ = length of the cycle carrying the boundary identification and ``pattern'' its orientation word ($a^3$ or $a\,a\,a^{-1}$), when the unfolding is a disc.}\label{tab:stuck51}\\
\toprule
\# & \texttt{graph6} & $m$ & $t$ & $H_1$ & $\I$ & $|\mathrm{Aut}|$ & $k$ / pattern \\
\midrule
\endfirsthead
\toprule
\# & \texttt{graph6} & $m$ & $t$ & $H_1$ & $\I$ & $|\mathrm{Aut}|$ & $k$ / pattern \\
\midrule
\endhead
\bottomrule
\endfoot
''')
    for i, r in enumerate(rows, 1):
        g6, m, t, h1, icon, aut, nd, nb, word = r[:9]
        h1t = r'$0$' if h1 == 'trivial' else r'$\ZZ/3$'
        ic = r'yes' if icon.startswith('yes') else 'no'
        if icon.startswith('yes'):
            ic = icon.replace('yes ', '').replace('{', r'$\{').replace('}', r'\}$')
        # pattern from boundary word: compute cycle length and pattern if word non-empty
        pat = pattern(g6)
        f.write(f'{i} & {tex_g6(g6)} & {m} & {t} & {h1t} & {ic} & {aut} & {pat} \\\\\n')
    f.write(r'\end{longtable}' + '\n')
rows = [l.rstrip('\n').split('\t') for l in open('../data/strictly_2dis_12.tsv') if not l.startswith('#')]
with open('tables/strictly2dis12.tex','w') as f:
    f.write(r'''\begin{tabular}{@{}rlrrrrrr@{}}
\toprule
\# & \texttt{graph6} & $m$ & $t$ & $K_4$ & $\omega$ & $\delta,\Delta$ & $|\mathrm{Aut}|$ \\
\midrule
''')
    for i, r in enumerate(rows, 1):
        g6, m_, t, k4, om, dmin, dmax, aut = r
        f.write(f'{i} & {tex_g6(g6)} & {m_} & {t} & {k4} & {om} & {dmin},\\,{dmax} & {aut} \\\\\n')
    f.write(r'\bottomrule' + '\n' + r'\end{tabular}' + '\n')
print('tables written')
