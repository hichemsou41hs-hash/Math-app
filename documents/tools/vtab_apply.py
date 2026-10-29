# Apply relative-position tables (vtab) to a .tex file from a list of anchored cases.
# modes: list (replace the itemize holding the anchor, plus a plain sign TAB just before),
#        sent (replace the anchor line), after (insert after the anchor line),
#        after_list (insert after the itemize holding the anchor), tab (replace the TAB holding the anchor)
exec(open('/home/user/Math-app/documents/tools/vtab.py').read())

def apply(path, cases):
    L = open(path).read().split('\n')
    edits = []
    for anc, occ, mode, a, *pre in cases:
        idx = [i for i, l in enumerate(L) if anc in l]
        assert len(idx) >= occ, (anc, len(idx))
        i = idx[occ - 1]
        xs, d, z, b, c, o, kw = a
        tab = ((pre[0] + '\n') if pre and pre[0] else '') + vtab(xs, d, z, b, c, o, **kw)
        tab = tab.split('\n')
        if mode == 'after':
            edits.append((i + 1, i, tab)); continue
        if mode == 'after_list':
            e = i
            while not L[e].startswith(r'\end{itemize}'): e += 1
            edits.append((e + 1, e, tab)); continue
        if mode == 'tab':
            s = i
            while L[s].strip() != r'\begin{TAB}': s -= 1
            e = i
            while L[e].strip() != r'\end{TAB}': e += 1
            edits.append((s, e, tab)); continue
        if mode == 'list':
            s = i
            while not L[s].startswith(r'\begin{itemize}'): s -= 1
            e = i
            while not L[e].startswith(r'\end{itemize}'): e += 1
        else:
            s = e = i
        j = s - 1
        while j >= 0 and not L[j].strip(): j -= 1
        if L[j].strip() == r'\end{TAB}':
            k = j
            while L[k].strip() != r'\begin{TAB}': k -= 1
            blk = L[k:j + 1]
            if sum(1 for x in blk if 'tkzTabLine' in x) == 1 and not any('tkzTabVar' in x for x in blk) and blk[1].count('/') <= 3:
                s = k
        edits.append((s, e, tab))
    edits.sort(key=lambda r: -r[0])
    for s, e, tab in edits:
        L[s:e + 1] = tab
    t = '\n'.join(L)
    if r'\newenvironment{FIG}' not in t:
        t = t.replace(r'\begin{document}', r'\newenvironment{FIG}{\par\begin{center}\begin{LTR}}{\end{LTR}\end{center}}' + '\n' + r'\begin{document}', 1)
    if 'pattern=' in t and 'patterns' not in t[:t.index(r'\begin{document}')]:
        t = t.replace(r'\begin{document}', r'\usetikzlibrary{patterns}' + '\n' + r'\begin{document}', 1)
    open(path, 'w').write(t)
    return len(edits)
