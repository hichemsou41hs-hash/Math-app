# Convert tkz-tab tables that hold a «الوضع النسبي» row into the teacher's TikZ model (vtab).
# Usage: python3 tkz_to_vtab.py FILE.tex   (prints a report; points not found are written x=a)
import re, sys
exec(open(__file__.replace('tkz_to_vtab.py', 'vtab.py')).read())

def split_top(s):
    out, d, cur = [], 0, ''
    for ch in s:
        if ch in '{': d += 1
        if ch in '}': d -= 1
        if ch == ',' and d == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return out

def braces(s, i):
    """return content of the {...} group starting at s[i]=='{' and the index after it"""
    d = 0
    for j in range(i, len(s)):
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[i + 1:j], j + 1

def clean(c):
    c = re.sub(r'\\(text|hbox|mbox)\{', '{', c)
    c = re.sub(r'\\(scriptsize|footnotesize|small)\s*', '', c)
    c = c.replace(r'\ar{', '{')
    while True:
        n = re.sub(r'\{([^{}]*)\}', r'\1', c)
        if n == c: break
        c = n
    return c.strip()

def name_of(t):
    t = t.strip().strip('.')
    m = re.search(r'\$([^$]*)\$', t)
    if 'محور الفواصل' in t or "xx'" in t: return "(xx')"
    if m:
        v = m.group(1).strip()
        return v if v.startswith('(') else '(' + v + ')'
    return t

def norm(x):
    return re.sub(r'\s|\\[td]frac', lambda m: '' if m.group(0).isspace() else r'\frac', x)

import sympy as sp
def tex2py(s):
    s = s.replace(r'\left', '').replace(r'\right', '').replace(r'\dfrac', r'\frac').replace(r'\tfrac', r'\frac')
    for _ in range(4):
        s = re.sub(r'\\frac\{([^{}]*)\}\{([^{}]*)\}', r'((\1)/(\2))', s)
        s = re.sub(r'\\frac(\w)(\w)', r'((\1)/(\2))', s)
        s = re.sub(r'\\sqrt\{([^{}]*)\}', r'sqrt(\1)', s)
        s = re.sub(r'e\^\{([^{}]*)\}', r'exp(\1)', s)
    s = re.sub(r'e\^(-?\w)', r'exp(\1)', s)
    s = re.sub(r'\\ln\s*\(?([a-z0-9]+)\)?', r'log(\1)', s)
    s = s.replace('^', '**').replace('{', '(').replace('}', ')')
    s = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', s)
    return sp.sympify(s, locals={'e': sp.E, 'x': sp.Symbol('x')})
def line_of(diff):
    d = diff.replace(' ', '')
    m = re.fullmatch(r'f\(x\)-\((.*)\)', d) or re.fullmatch(r'f\(x\)-([^()]*)', d)
    if m: return m.group(1)
    if d == 'f(x)+x': return '-x'
    return None
def point_tex(x0, expr):
    try:
        X = tex2py(x0); y = sp.nsimplify(sp.simplify(tex2py(expr).subs(sp.Symbol('x'), X)))
        return '(%s;%s)' % (x0, sp.latex(y).replace(r'\left(', '(').replace(r'\right)', ')'))
    except Exception:
        return None
def convert(path):
    t = open(path).read()
    L = t.split('\n')
    out, i, rep = [], 0, []
    while i < len(L):
        if L[i].strip() != r'\begin{TAB}':
            out.append(L[i]); i += 1; continue
        j = i
        while L[j].strip() != r'\end{TAB}': j += 1
        blk = L[i:j + 1]
        txt = '\n'.join(blk)
        if 'الوضع' not in txt or not ('فوق' in txt or 'تحت' in txt):
            out.extend(blk); i = j + 1; continue
        init = next(l for l in blk if r'\tkzTabInit' in l)
        k = init.index('{', init.index(']') if ']' in init else 0)
        rows, k2 = braces(init, k)
        xs, _ = braces(init, k2)
        rows = split_top(rows); xs = [x.strip().strip('$') for x in split_top(xs)]
        labels = [r.rsplit('/', 1)[0].strip() for r in rows]
        pos_r = next(n for n, l in enumerate(labels) if 'الوضع' in l)
        lines = [l for l in blk if r'\tkzTabLine' in l or r'\tkzTabVar' in l]
        cells = [split_top(braces(l, l.index('{'))[0]) for l in lines]
        if len(lines) < pos_r:
            print('skip (rows/lines mismatch) at', i + 1); out.extend(blk); i = j + 1; continue
        diff = labels[pos_r - 1].strip('$ ')
        sign = [c.strip() for c in cells[pos_r - 2]]
        posc = [clean(c) for c in cells[pos_r - 1]]
        n = len(xs)
        between, curve, other = [], None, None
        for m in range(n - 1):
            c = posc[2 * m + 1] if 2 * m + 1 < len(posc) else ''
            w = 'فوق' if 'فوق' in c else ('تحت' if 'تحت' in c else '')
            if w:
                a, b = c.split(w, 1)
                if '$' in a: curve = name_of(a)
                if b.strip(): other = name_of(b)
            between.append(w)
        curve = curve or '(C_f)'; other = other or '(\\Delta)'
        zeros, bars = {}, []
        ctx = '\n'.join(L[max(0, i - 8):i] + L[j + 1:j + 6])
        for m in range(n):
            c = sign[2 * m] if 2 * m < len(sign) else ''
            if c == 'd' or c.startswith('d'):
                bars.append(m)
            elif c == 'z' or c == 't' and False:
                x0 = xs[m]
                pm = re.search(r'\(\s*' + re.escape(norm(x0)) + r'\s*;\s*([^()$]+?)\)', norm(ctx))
                pt = '(%s;%s)' % (x0, pm.group(1).replace(r'\right', '').strip()) if pm else None
                if not pt and other in ("(xx')", "(x'x)"):
                    pt = '(%s;0)' % x0
                if not pt and line_of(diff):
                    pt = point_tex(x0, line_of(diff))
                pt = pt or 'x=%s' % x0
                l_ = sign[2 * m - 1] if m > 0 else ''
                r_ = sign[2 * m + 1] if 2 * m + 1 < len(sign) else ''
                tch = l_ and r_ and l_ == r_
                zeros[m] = (pt, 'يمس') if tch else pt
        tab = vtab(xs, diff, zeros, between, curve, other, bars=tuple(bars))
        extra = [r for n_, r in enumerate(rows) if n_ not in (0, pos_r - 1, pos_r)]
        if extra:   # keep the factor rows: drop only the difference and position rows
            keep = [l for l in blk if l not in (lines[pos_r - 1], lines[pos_r - 2])]
            keep = [l if r'\tkzTabInit' not in l else l.replace(rows[pos_r], '').replace(',' + rows[pos_r - 1].strip(), '').replace(rows[pos_r - 1].strip() + ',', '') for l in keep]
            keep = [re.sub(r',\s*\}', '}', l) if r'\tkzTabInit' in l else l for l in keep]
            out.extend(keep)
        out.extend(tab.split('\n'))
        rep.append((i + 1, xs, diff, zeros, between, curve, other, bars, bool(extra)))
        i = j + 1
    t = '\n'.join(out)
    if r'\newenvironment{FIG}' not in t:
        t = t.replace(r'\begin{document}', r'\newenvironment{FIG}{\par\begin{center}\begin{LTR}}{\end{LTR}\end{center}}' + '\n' + r'\begin{document}', 1)
    open(path, 'w').write(t)
    return rep

if __name__ == '__main__':
    for r in convert(sys.argv[1]):
        print(r)
