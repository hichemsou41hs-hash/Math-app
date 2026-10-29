# Adds a graphical explanation for each transformation of (C_f) in documents/nihayat/molakhas_nihayat_3as.tex
p='/home/user/Math-app/documents/nihayat/molakhas_nihayat_3as.tex'; t=open(p).read()
F=r'0.5*(\x)^2-(\x)-1.5'
def gr(extra, xr=(-4,5), yr=(-3.2,3.5)):
    return (r'\begin{GR}{%g}{%g}{%g}{%g}{0.5}'%(xr[0],xr[1],yr[0],yr[1])+'\n'+r'\Ticks{-3,-2,-1,1,2,3,4}{-3,-2,-1,1,2,3}'+'\n'+extra+'\n'+r'\end{GR}')
cf=r'\draw[cDef,thick,dashed,domain=-2.4:4.3,samples=80] plot(\x,{%s}); \node[cDef] at (-2.9,2.6){$(C_f)$};'%F
def blk(title, text, graph):
    return r'\begin{mithal}['+title+']\n'+r'\RL{0.56}{'+text+'}{0.4}{'+graph+'}\n'+r'\end{mithal}'
B=[r'''\begin{mithal}[الدالة المرجعية للشروح البيانية]
نأخذ في كل الحالات $f(x)=\frac12x^{2}-x-\frac32$.\par
$(C_f)$ قطع مكافئ رأسه $S(1;-2)$ ، ويقطع محور الفواصل في $(-1;0)$ و $(3;0)$.\par
نرسم $(C_f)$ \textbf{متقطعًا بالأزرق} ، و $(C_g)$ \textbf{متصلًا بالأحمر}.
\end{mithal}''']
B.append(blk(r'الحالة 1: $g(x)=f(x+b)+k$ -- الانسحاب',
r'''\textbf{الشرح:}\par
إذا كانت $M(x;y)$ من $(C_f)$ فإن $M'(x-b;\,y+k)$ من $(C_g)$.\par
السبب: $g(x-b)=f(x)+k=y+k$.\par
كل نقطة تتحرك أفقيًا بـ $-b$ وعموديًا بـ $k$: \ \bx{\vec u\begin{pmatrix}-b\\ k\end{pmatrix}}.\par\smallskip
\textbf{مثال:} $g(x)=f(x-2)+1$.\par
$b=-2$ و $k=1$ ، إذن $\vec u\begin{pmatrix}2\\ 1\end{pmatrix}$.\par
الرأس $S(1;-2)$ يصير $S'(3;-1)$.''',
gr(cf+'\n'+r'\draw[cThm,very thick,domain=-0.4:5,samples=80] plot(\x,{0.5*(\x-2)^2-(\x-2)-0.5}); \node[cThm] at (4.4,3.2){$(C_g)$};'+'\n'+r'\draw[-{Stealth},thick,cEx] (1,-2)--(3,-1); \node[cEx] at (2.3,-2.2){$\vec u$}; \fill (1,-2) circle (1.5pt) node[below]{$S$}; \fill (3,-1) circle (1.5pt) node[right]{$S^{\prime}$};',xr=(-4,5.2))))
B.append(blk(r'الحالة 2: $g(x)=-f(x)$ -- تناظر بالنسبة إلى محور الفواصل',
r'''\textbf{الشرح:}\par
إذا كانت $M(x;y)$ من $(C_f)$ فإن $M'(x;-y)$ من $(C_g)$.\par
نفس الفاصلة ، والترتيبان متعاكسان.\par
نقطتا محور الفواصل $(-1;0)$ و $(3;0)$ لا تتغيران.\par
الرأس $S(1;-2)$ يصير $S'(1;2)$: المنحنى «ينقلب».''',
gr(cf+'\n'+r'\draw[cThm,very thick,domain=-2.4:4.3,samples=80] plot(\x,{-(%s)}); \node[cThm] at (3.7,-2.7){$(C_g)$};'%F+'\n'+r'\draw[densely dotted,cEx] (1,-2)--(1,2); \fill (1,-2) circle (1.5pt) node[below right]{$S$}; \fill (1,2) circle (1.5pt) node[above right]{$S^{\prime}$};')))
B.append(blk(r'الحالة 3: $g(x)=f(-x)$ -- تناظر بالنسبة إلى محور التراتيب',
r'''\textbf{الشرح:}\par
إذا كانت $M(x;y)$ من $(C_f)$ فإن $M'(-x;y)$ من $(C_g)$.\par
السبب: $g(-x)=f(x)=y$.\par
نفس الترتيب ، والفاصلتان متعاكستان.\par
النقطة $(0;-1{,}5)$ على محور التراتيب لا تتغير.\par
الرأس $S(1;-2)$ يصير $S'(-1;-2)$.''',
gr(cf+'\n'+r'\draw[cThm,very thick,domain=-4.3:2.4,samples=80] plot(\x,{0.5*(\x)^2+(\x)-1.5}); \node[cThm] at (-3.5,-1.4){$(C_g)$};'+'\n'+r'\draw[densely dotted,cEx] (1,-2)--(-1,-2); \fill (1,-2) circle (1.5pt) node[below]{$S$}; \fill (-1,-2) circle (1.5pt) node[below]{$S^{\prime}$};',xr=(-4.5,4.5))))
B.append(blk(r'الحالة 4: $g(x)=|f(x)|$',
r'''\textbf{الشرح:}\par
\textbullet\ حيث $f(x)\geqslant0$: $g(x)=f(x)$.\par
$(C_g)$ \textbf{ينطبق} على $(C_f)$ على $]-\infty;-1]$ و $[3;+\infty[$.\par
\textbullet\ حيث $f(x)\leqslant0$: $g(x)=-f(x)$.\par
$(C_g)$ \textbf{نظير} $(C_f)$ بالنسبة إلى محور الفواصل على $[-1;3]$.\par
$(C_g)$ يقع دائمًا فوق محور الفواصل ، والرأس $S(1;-2)$ يصير $S'(1;2)$.''',
gr(cf+'\n'+r'\draw[cThm,very thick,domain=-2.4:-1,samples=30] plot(\x,{%s}); \draw[cThm,very thick,domain=-1:3,samples=60] plot(\x,{-(%s)}); \draw[cThm,very thick,domain=3:4.3,samples=30] plot(\x,{%s}); \node[cThm] at (4.4,3.2){$(C_g)$};'%(F,F,F)+'\n'+r'\fill (1,-2) circle (1.5pt) node[below right]{$S$}; \fill (1,2) circle (1.5pt) node[above right]{$S^{\prime}$};')))
B.append(blk(r'الحالة 5: $g(x)=f(|x|)$',
r'''\textbf{الشرح:}\par
\textbullet\ من أجل $x\geqslant0$: $|x|=x$ ، إذن $g(x)=f(x)$.\par
$(C_g)$ \textbf{ينطبق} على $(C_f)$ على يمين محور التراتيب.\par
\textbullet\ $g(-x)=f(|-x|)=g(x)$: $g$ \textbf{زوجية}.\par
نكمل اليسار \textbf{بالتناظر} بالنسبة إلى محور التراتيب.\par
الجزء الأيسر من $(C_f)$ ($x<0$) لا يُستعمل.''',
gr(cf+'\n'+r'\draw[cThm,very thick,domain=0:4.3,samples=60] plot(\x,{%s}); \draw[cThm,very thick,domain=-4.3:0,samples=60] plot(\x,{0.5*(\x)^2+(\x)-1.5}); \node[cThm] at (-3.7,2.7){$(C_g)$};'%F+'\n'+r'\fill (1,-2) circle (1.5pt) node[below]{$S$}; \fill (-1,-2) circle (1.5pt) node[below]{$S^{\prime}$};',xr=(-4.5,4.5))))
anchor=r'''\item $g(x)=f(|x|)$: $(C_g)$ ينطبق على $(C_f)$ من أجل $x\geqslant0$، ونكمل بالتناظر بالنسبة إلى محور التراتيب ($g$ زوجية).
\end{itemize}
\end{khassia}'''
assert t.count(anchor)==1 and 'الدالة المرجعية للشروح البيانية' not in t
t=t.replace(anchor,anchor+'\n'+'\n\n'.join(B))
open(p,'w').write(t); print('ok')
