# Re-draw every relative-position table made by vtab() in the given .tex files with the current vtab
# (reads the parameters back from the TikZ code). Usage: python3 vtab_rerender.py FILE.tex ...
import re, sys
exec(open(__file__.replace('vtab_rerender.py', 'vtab.py')).read())

PIC = re.compile(r'\\begin\{tikzpicture\}\[font=\\normalsize\]\n.*?\\end\{tikzpicture\}', re.S)

def parse(s):
    W = float(re.search(r'\\fill\[green!18\] \(([\d.]+),0\) rectangle \(([\d.]+),', s).group(2))
    top = re.findall(r'\\node at \(([\d.]+),-0\.45\)\{\$(.*?)\$\};\n', s)
    xs_pos = [(float(a), b) for a, b in top][1:]          # first one is the «x» label
    diff = re.search(r'\\node(?:\[font=\\[a-z]+\])? at \([\d.]+,-1\.35\)\{\$(.*?)\$\};', s).group(1)
    iv = re.findall(r'\\node\[align=center,font=\\(?:small|footnotesize)\] at \(([\d.]+),[-\d.]+\)\{\$(.*?)\$\\\\ \\ar\{(.*?)\}\\\\ \$(.*?)\$\};', s)
    between = [p for _, _, p, _ in sorted(iv, key=lambda r: float(r[0]))]
    curve, other = next((c, o) for _, c, p, o in iv if p)
    X = [x for x, _ in xs_pos]
    near = lambda x: min(range(len(X)), key=lambda i: abs(X[i] - x))
    zeros = {}
    for x, c, mt, o, pt in re.findall(r'inner sep=0pt\] at \(([\d.]+),[-\d.]+\)\{\\ar\{\$(.*?)\$ (\S+?)\}\\\\ \$(.*?)\$\\\\ \\ar\{(?:في النقطة|عند)\}\\\\ \$(.*?)\$\};', s):
        zeros[near(float(x))] = pt if mt == 'يقطع' else (pt, mt)
    bars = tuple(near(float(x)) for x in re.findall(r'\\draw\[double,thick\] \(([\d.]+),', s))
    return dict(xs=[b for _, b in xs_pos], diff=diff, zeros=zeros, between=between, curve=curve,
                other=other, W=W, bars=bars)

for f in sys.argv[1:]:
    t = open(f).read(); n = 0
    def rep(m):
        global n
        s = m.group(0)
        if r'\ar{الوضع}\\ \ar{النسبي}' not in s:
            return s
        a = parse(s); n += 1
        out = vtab(a['xs'], a['diff'], a['zeros'], a['between'], a['curve'], a['other'], W=a['W'], bars=a['bars'])
        return re.search(r'\\begin\{tikzpicture\}.*\\end\{tikzpicture\}', out, re.S).group(0)
    t = PIC.sub(rep, t)
    open(f, 'w').write(t)
    print(f, n)
