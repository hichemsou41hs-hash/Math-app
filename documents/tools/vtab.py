# Relative-position table in TikZ (teacher's model): label column left, dotted line at each zero,
# a bell-shaped cell under each zero holding the intersection.
def vtab(xs, diff, zeros, between, curve, other, W=15.5):
    """xs: x labels; diff: label of the difference row; zeros: {index: point text} for the zeros;
    between: list of 'فوق'/'تحت' per interval; curve/other: e.g. '(C_f)', "(xx')"."""
    L, h1, h2, h3 = 2.6, 0.9, 0.9, 2.8
    n = len(xs); w = 1.5; m = 0.7
    # interval widths: room for the text (2 cm) plus the half-bells at its ends
    ws = [2.4 + (w if i in zeros else 0) + (w if i + 1 in zeros else 0) for i in range(n - 1)]
    lm = m + (w if 0 in zeros else 0); rm = m + (w if n - 1 in zeros else 0)
    k = (W - L - lm - rm) / sum(ws)
    X = [L + lm]
    for a in ws:
        X.append(X[-1] + a * k)
    yt, y1, y2, yb = 0, -h1, -h1 - h2, -h1 - h2 - h3
    s = [r'\begin{tikzpicture}[font=\normalsize]']
    s.append(r'\fill[gray!12] (0,%g) rectangle (%g,%g);' % (yt, L, y1))
    s.append(r'\fill[green!18] (%g,%g) rectangle (%g,%g);' % (L, yt, W, y1))
    s.append(r'\fill[orange!45] (0,%g) rectangle (%g,%g);' % (y1, L, yb))
    s.append(r'\fill[cyan!22] (%g,%g) rectangle (%g,%g);' % (L, y1, W, yb))
    s.append(r'\draw[thick] (0,%g) rectangle (%g,%g); \draw (0,%g)--(%g,%g) (0,%g)--(%g,%g) (%g,%g)--(%g,%g);'
             % (yt, W, yb, y1, W, y1, y2, W, y2, L, yt, L, yb))
    s.append(r'\node at (%g,%g){$x$};' % (L / 2, y1 / 2))
    s.append(r'\node at (%g,%g){$%s$};' % (L / 2, (y1 + y2) / 2, diff))
    s.append(r'\node[align=center,font=\bfseries] at (%g,%g){\ar{الوضع}\\ \ar{النسبي}};' % (L / 2, (y2 + yb) / 2))
    for i, x in enumerate(xs):
        s.append(r'\node at (%g,%g){$%s$};' % (X[i], y1 / 2, x))
    for i, pos in enumerate(between):
        xm = (X[i] + (w if i in zeros else 0) + X[i + 1] - (w if i + 1 in zeros else 0)) / 2
        sg = '+' if pos == 'فوق' else '-'
        s.append(r'\node at (%g,%g){$%s$};' % (xm, (y1 + y2) / 2, sg))
        s.append(r'\node[align=center,font=\small] at (%g,%g){$%s$\\ \ar{%s}\\ $%s$};' % (xm, (y2 + yb) / 2, curve, pos, other))
    for i, pt in zeros.items():
        x = X[i]
        s.append(r'\node at (%g,%g){$0$};' % (x, (y1 + y2) / 2))
        ym = (y1 + y2) / 2
        s.append(r'\draw[densely dotted] (%g,%g)--(%g,%g) (%g,%g)--(%g,%g);' % (x, y1, x, ym + 0.22, x, ym - 0.22, x, y2))
        s.append(r'\draw (%g,%g) .. controls (%g,%g) and (%g,%g) .. (%g,%g) .. controls (%g,%g) and (%g,%g) .. (%g,%g);'
                 % (x - w, yb, x - 0.95 * w, yb + 0.55 * h3, x - 0.3 * w, y2 - 0.12 * h3, x, y2,
                    x + 0.3 * w, y2 - 0.12 * h3, x + 0.95 * w, yb + 0.55 * h3, x + w, yb))
        s.append(r'\node[align=center,font=\footnotesize,inner sep=0pt] at (%g,%g){\ar{$%s$ يقطع}\\ $%s$\\ \ar{في النقطة}\\ $%s$};'
                 % (x, yb + 0.95, curve, other, pt))
    s.append(r'\end{tikzpicture}')
    return r'\begin{FIG}' + '\n' + '\n'.join(s) + '\n' + r'\end{FIG}'
