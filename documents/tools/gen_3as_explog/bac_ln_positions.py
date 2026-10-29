import re
exec(open('/home/user/Math-app/documents/tools/vtab.py').read())
M,P=r'-\infty',r'+\infty'
F,D=r'(C_f)',r'(\Delta)'
C=[  # (anchor, occurrence, mode, vtab args)
(r'على $]-1;0[$: $(C_f)$ \textbf{فوق} المستقيم',1,'list',(['-1','0',P],'f(x)-(x-1)',{1:'A(0;-1)'},['فوق','تحت'],F,D,{'bars':(0,)})),
(r'على $\left]\frac12;1\right[\cup]\alpha;+\infty[$: $(C_f)$ \textbf{تحت} $(d)$',1,'list',([r'\frac12','1',r'\alpha',P],'f(x)-x',{1:'A(1;1)',2:r'B(\alpha;\alpha)'},['تحت','فوق','تحت'],F,'(d)',{'bars':(0,)})),
(r'\textbf{النتيجة:} المنحنى $(C_f)$ يقع \textbf{تحت} المستقيم $(\Delta)$ على $]-\infty;0[$.',1,'after',([M,'0'],'f(x)-(x+5)',{},['تحت'],F,D,{'bars':(1,)})),
(r'على $]-1;\sqrt e-1[$: $(C_f)$ \textbf{تحت} $(\Delta)$',1,'list',(['-1',r'\sqrt e-1',P],'f(x)-x',{1:r'A\left(\sqrt e-1;\sqrt e-1\right)'},['تحت','فوق'],F,D,{'bars':(0,)})),
(r'$(C_f)$ \textbf{تحت} $(\Delta)$ على $]0;1[$، و\textbf{فوق} $(\Delta)$ على $]1;+\infty[$، ويقطعه في النقطة $(1;1)$.',1,'sent',(['0','1',P],'f(x)-1',{1:'A(1;1)'},['تحت','فوق'],F,D,{'bars':(0,)})),
(r'على $]0;\alpha[$: $(\gamma)$ يقع',1,'list',(['0',r'\alpha',P],r'\ln x-(-x+3)',{1:r'A(\alpha;3-\alpha)'},['تحت','فوق'],r'(\gamma)',D,{'bars':(0,)})),
(r'$(C)$ \textbf{تحت} $(\Delta)$ على $]0;1[$',1,'sent',(['0','1',P],'f(x)-(x-1)',{1:'A(1;0)'},['تحت','فوق'],'(C)',D,{'bars':(0,)})),
(r'على $]1;+\infty[$: $x+1>0$ إذن',1,'list',([M,'-1','1',P],r'f(x)-\frac23x',{},['فوق','','تحت'],F,D,{'bars':(1,2)})),
(r'على $]0;2[$: $f(x)-\ln x<0$',1,'list',(['0','2',P],r'f(x)-\ln x',{},['تحت','فوق'],F,r'(\Gamma)',{'bars':(0,1)})),
(r'\item على $]0;1[$: $\ln x<0$ إذن $(C_f)$ فوق $(\Delta)$.',1,'list',(['0','1',P],'f(x)-(x-1)',{1:'A(1;0)'},['فوق','تحت'],F,D,{'bars':(0,)})),
(r'على $]-\infty;0[$ و $]0;1[$: $(C_f)$ فوق $(\Delta)$.',1,'list',([M,'0','1',P],'f(x)-(2x-1)',{2:'A(1;1)'},['فوق','فوق','تحت'],F,D,{'bars':(1,)})),
(r'على $]0;1[$: $(C_f)$ فوق $(\Delta)$ ؛',1,'list',(['0','1',P],'f(x)+x',{1:'A(1;-1)'},['فوق','تحت'],F,D,{'bars':(0,)})),
(r'\item على $]0;1[$: $\ln x<0$ إذن $(C_f)$ فوق $(\Delta)$.',2,'list',(['0','1',P],'f(x)-(x-2)',{1:'A(1;-1)'},['فوق','تحت'],F,D,{'bars':(0,)})),
(r'$-2<x<-1$: $0<x+2<1$',1,'list',(['-2','-1',P],'f(x)-(x+1)',{1:'A(-1;0)'},['تحت','فوق'],F,D,{'bars':(0,)})),
(r'على $]-\infty;1[$: $x-2<0$',1,'list',([M,'1','2',P],'f(x)-(-2x+3)',{},['تحت','','فوق'],F,D,{'bars':(1,2)})),
(r'على $]0;e[$: $\ln x<1$: $(C_f)$ تحت $(\Delta)$.',1,'list',(['0','e',P],r'f(x)-\left(-\frac12x+2\right)',{1:r'A\left(e;2-\frac e2\right)'},['تحت','فوق'],F,D,{'bars':(0,)})),
(r'على $]1;e[$: $f(x)+2<0$',1,'list',(['1','e',P],'f(x)+2',{1:'A(e;-2)'},['تحت','فوق'],F,D,{'bars':(0,)})),
(r'على $]0;1[$: $\ln x<0$، إذن $(C_f)$ تحت $(\Gamma)$',1,'list',(['0','1',P],r'f(x)-\ln(x+1)',{1:r'A(1;\ln2)'},['تحت','فوق'],F,r'(\Gamma)',{'bars':(0,)})),
(r'على $\left]0;\frac1{\sqrt e}\right[$',1,'list',(['0',r'\frac1{\sqrt e}',P],r'f(x)-\ln x',{1:r'A\left(\frac1{\sqrt e};-\frac12\right)'},['فوق','تحت'],F,r'(\Gamma)',{'bars':(0,)})),
(r'على $\left]0;e^{-\frac32}\right[$: $(C_f)$ تحت $(\Delta)$؛',1,'list',(['0',r'e^{-\frac32}',P],'f(x)+x+2',{1:r'A\left(e^{-\frac32};-e^{-\frac32}-2\right)'},['تحت','فوق'],F,D,{'bars':(0,)})),
(r'على $]-2;e-2[$: $(C_f)$ فوق $(C_h)$',1,'list',(['-2','e-2',P],'f(x)-h(x)',{1:'A(e-2;0)'},['فوق','تحت'],F,'(C_h)',{'bars':(0,)})),
(r'على $]0;e[$: $f(x)-x>0$، $(C_f)$ فوق $(\Delta)$؛',1,'list',(['0','e',P],'f(x)-x',{},['فوق','تحت'],F,D,{'bars':(0,1)})),
(r'$(C_f)$ فوق $(\Delta)$ على $]-\infty;1-\frac1e[$',1,'sent',([M,r'1-\frac1e','1',r'1+\frac1e',P],'f(x)-(x-2)',{1:r'A\left(1-\frac1e;-1-\frac1e\right)',3:r'B\left(1+\frac1e;-1+\frac1e\right)'},['فوق','تحت','فوق','تحت'],F,D,{'bars':(2,)})),
(r'على $]0;1[$: $-\ln x>0$، \bxt{$(C_f)$ فوق $(T)$}',1,'list',(['0','1',P],'f(x)-x',{0:'O(0;0)',1:'A(1;1)'},['فوق','تحت'],F,'(T)',{})),
(r'على $]-1;\alpha[$: $(C)$ يقع فوق $(\Gamma)$',1,'list',(['-1',r'\alpha',P],r'(1+x^2)-y_{\Gamma}',{1:r'A\left(\alpha;1+\alpha^2\right)'},['فوق','تحت'],'(C)',r'(\Gamma)',{'bars':(0,)})),
(r'$(C_f)$ فوق $(\Delta)$ على $]0;\alpha[$، وتحته',1,'list',(['0',r'\alpha',P],'f(x)-x',{0:'O(0;0)',1:r'A(\alpha;\alpha)'},['فوق','تحت'],F,D,{})),
(r'على $]0;1[$: $f(x)-x>0$، $(C_f)$ فوق $(\Delta)$.',1,'list',(['0','1',P],'f(x)-x',{0:'O(0;0)',1:'B(1;1)'},['فوق','تحت'],F,D,{})),
(r'من أجل $x\in]0;1[$: $\ln x<0$ إذن $f(x)-(x+1)>0$',1,'list',(['0','1',P],'f(x)-(x+1)',{0:'A(0;1)'},['فوق','تحت'],F,D,{'bars':(1,)})),
(r'على $]-\infty;-1[$ و $]0;1[$: $(C_f)$ فوق $(\Delta)$.',1,'list',([M,'-1','0','1',P],r'f(x)-y_{\Delta}',{1:r'A\left(-1;\frac{e+1}2\right)',3:r'B\left(1;\frac{e-1}2\right)'},['فوق','تحت','فوق','تحت'],F,D,{'bars':(2,)})),
(r'على $\Big]0;\dfrac1e\Big[$',1,'list',(['0',r'\frac1e',P],'f(x)-1',{1:r'A\left(\frac1e;1\right)'},['تحت','فوق'],F,D,{'bars':(0,)})),
(r'على $\big]0;e^{-\frac32}\big[$',1,'list',(['0',r'e^{-\frac32}',P],'f(x)+x',{1:r'A\left(e^{-\frac32};-e^{-\frac32}\right)'},['تحت','فوق'],F,D,{'bars':(0,)})),
(r'على $]0;1[$ و $]e;+\infty[$: $(C_f)$ فوق $(C_g)$.',1,'list',(['0','1','e',P],'f(x)-g(x)',{1:'A(1;-1)',2:'B(e;0)'},['فوق','تحت','فوق'],F,'(C_g)',{'bars':(0,)})),
(r'إذن $f(x)-x>0$: \bxt{$(C_f)$ فوق $(T)$ على',1,'after',(['-1','0','3'],'f(x)-x',{1:('O(0;0)','يمس')},['فوق','فوق'],F,'(T)',{'bars':(0,)})),
(r'على $]0;1[$: $\ln x<0$ ، $(C_f)$ فوق $(\delta)$.',1,'list',(['0','1',P],r'f(x)-\ln x',{1:'A(1;0)'},['فوق','تحت'],F,r'(\delta)',{'bars':(0,)})),
]
p='bac_ln_3as.tex'; L=open(p).read().split('\n')
edits=[]
for anc,occ,mode,a in C:
    idx=[i for i,l in enumerate(L) if anc in l]
    assert len(idx)>=occ,(anc,len(idx))
    i=idx[occ-1]
    xs,d,z,b,c,o,kw=a
    tab=vtab(xs,d,z,b,c,o,**kw).split('\n')
    if mode=='after':
        edits.append((i+1,i,tab)); continue
    if mode=='list':
        s=i
        while not L[s].startswith(r'\begin{itemize}'): s-=1
        e=i
        while not L[e].startswith(r'\end{itemize}'): e+=1
    else:
        s=e=i
    # drop a plain sign table (only x + one difference row) just before
    j=s-1
    while j>=0 and not L[j].strip(): j-=1
    if L[j].strip()==r'\end{TAB}':
        k=j
        while L[k].strip()!=r'\begin{TAB}': k-=1
        blk=L[k:j+1]
        if sum(1 for x in blk if 'tkzTabLine' in x)==1 and not any('tkzTabVar' in x for x in blk) and blk[1].count('/')<=3:
            s=k
    edits.append((s,e,tab))
edits.sort(key=lambda r:-r[0])
for s,e,tab in edits:
    L[s:e+1]=tab
t='\n'.join(L)
if r'\newenvironment{FIG}' not in t:
    t=t.replace(r'\begin{document}',r'\newenvironment{FIG}{\par\begin{center}\begin{LTR}}{\end{LTR}\end{center}}'+'\n'+r'\begin{document}',1)
open(p,'w').write(t); print(len(edits))
