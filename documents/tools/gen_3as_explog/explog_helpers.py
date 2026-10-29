# helpers for the 3AS exp / ln lesson plans (tables sized to the «سير الحصة» column)
exec(open('/home/user/Math-app/documents/tools/vtab.py').read())
CW = 12.5   # usable width of the plan column (cm)

def VP(*a, **k):
    """relative-position table (teacher's model) inside a plan cell"""
    s = vtab(*a, W=CW, **k)
    s = s.replace(r'\begin{FIG}' + '\n', '').replace('\n' + r'\end{FIG}', '')
    return r'\par\smallskip\begin{LTR}\centering ' + s + r'\end{LTR}\par '

def VAR(xs, fname, dname, signs, vals, levels, W=CW):
    """variation table: signs has 2n-1 cells (even = at a point: '', '0' or '||'), vals/levels per point"""
    L, h1, h2, h3 = 2.4, 0.85, 0.85, 2.1
    n = len(xs)
    X = [L + 0.9 + i * (W - L - 1.8) / (n - 1) for i in range(n)]
    y1, y2, yb = -h1, -h1 - h2, -h1 - h2 - h3
    s = [r'\begin{tikzpicture}[font=\normalsize]']
    s.append(r'\fill[gray!12] (0,0) rectangle (%g,%g); \fill[green!18] (%g,0) rectangle (%g,%g);' % (L, y1, L, W, y1))
    s.append(r'\fill[orange!45] (0,%g) rectangle (%g,%g); \fill[cyan!15] (%g,%g) rectangle (%g,%g);' % (y1, L, yb, L, y1, W, yb))
    s.append(r'\draw[thick] (0,0) rectangle (%g,%g); \draw (0,%g)--(%g,%g) (0,%g)--(%g,%g) (%g,0)--(%g,%g);'
             % (W, yb, y1, W, y1, y2, W, y2, L, L, yb))
    s.append(r'\node at (%g,%g){$x$}; \node at (%g,%g){$%s$}; \node at (%g,%g){$%s$};'
             % (L / 2, y1 / 2, L / 2, (y1 + y2) / 2, dname, L / 2, (y2 + yb) / 2, fname))
    for i, x in enumerate(xs):
        s.append(r'\node at (%g,%g){$%s$};' % (X[i], y1 / 2, x))
    for j, c in enumerate(signs):
        if not c:
            continue
        xm = X[j // 2] if j % 2 == 0 else (X[j // 2] + X[j // 2 + 1]) / 2
        if c == '||':
            s.append(r'\draw[double,thick] (%g,%g)--(%g,%g);' % (xm, y1, xm, yb))
        else:
            s.append(r'\node at (%g,%g){$%s$};' % (xm, (y1 + y2) / 2, c))
    ys = {'h': y2 - 0.4, 'l': yb + 0.4, 'm': (y2 + yb) / 2}
    for i, (v, lv) in enumerate(zip(vals, levels)):
        dx = 0
        s.append(r'\node[inner sep=2pt] (v%d) at (%g,%g){$%s$};' % (i, X[i] + dx, ys[lv], v))
    for i in range(n - 1):
        if signs[2 * i + 2] == '||' and False:
            pass
        s.append(r'\draw[->,cDef,thick,shorten <=3pt,shorten >=3pt] (v%d)--(v%d);' % (i, i + 1))
    s.append(r'\end{tikzpicture}')
    return r'\par\smallskip\begin{LTR}\centering ' + '\n'.join(s) + r'\end{LTR}\par '

def GR(body, xr, yr, x=1, y=1, xt=None, yt=None):
    """graph on graph paper: body = tikz commands; xr, yr ranges"""
    (a, b), (c, d) = xr, yr
    xt = xt or [t for t in range(int(a) + 1, int(b)) if t]
    yt = yt or [t for t in range(int(c) + 1, int(d)) if t]
    s = r'\begin{tikzpicture}[x=%gcm,y=%gcm,font=\footnotesize]' % (x, y)
    s += r'\draw[gray!25,step=0.5] (%g,%g) grid (%g,%g);' % (a, c, b, d)
    s += r'\draw[->,thick] (%g,0)--(%g,0) node[right]{$x$}; \draw[->,thick] (0,%g)--(0,%g) node[above]{$y$};' % (a, b, c, d)
    s += ''.join(r'\draw (%g,0.08)--(%g,-0.08) node[below]{$%g$};' % (t, t, t) for t in xt)
    s += ''.join(r'\draw (0.08,%g)--(-0.08,%g) node[left]{$%g$};' % (t, t, t) for t in yt)
    s += r'\node[below left] at (0,0){$O$};' + body + r'\end{tikzpicture}'
    return r'\par\smallskip\begin{LTR}\centering ' + s + r'\end{LTR}\par '
