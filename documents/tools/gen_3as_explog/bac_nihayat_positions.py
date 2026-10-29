exec(open('/home/user/Math-app/documents/tools/vtab_apply.py').read())
M,P=r'-\infty',r'+\infty'; F,D=r'(C_f)',r'(\Delta)'
p='bac_nihayat_3as.tex'
t=open(p).read()
o=r"\tkzTabLine{,\hbox{\ar{\footnotesize تحت $(\Delta)$}},d,\hbox{\ar{\footnotesize فوق $(\Delta)$}},z,\hbox{\ar{\footnotesize تحت $(\Delta)$}},d,\hbox{\ar{\footnotesize فوق $(\Delta)$}},}"
assert t.count(o)==1
t=t.replace(o+'\n','').replace(r",$g(x)-1$/0.7,\ar{الوضع النسبي}/1}{$-\infty$,$-3$,$0$,$2$,$+\infty$}",r",$g(x)-1$/0.7}{$-\infty$,$-3$,$0$,$2$,$+\infty$}")
open(p,'w').write(t)
A1=r'\tkzTabLine{,\hbox{\ar{\footnotesize $(C_f)$ فوق $(\Delta)$}},z,\hbox{\ar{\footnotesize $(C_f)$ تحت $(\Delta)$}},}'
C=[
(r'$(C_f)$ فوق $(\Delta)$}},t,\text{\ar{$(C_f)$ تحت $(\Delta)$}},}',1,'tab',([M,r'\frac13',P],r'f(x)-\left(\frac12x+\frac12\right)',{1:r'A\left(\frac13;\frac23\right)'},['فوق','تحت'],F,D,{})),
(r'وبما أن $g(x)-x=\dfrac4{x+1}>0$ على $[0;+\infty[$ فإن $(C_g)$ فوق $(\Delta)$.',1,'after',(['0',P],'g(x)-x',{},['فوق'],'(C_g)',D,{})),
(r'و $(\Gamma)$ فوقه دائما لأن $\dfrac1{(x+1)^{2}}>0$.',1,'after',(['-1',P],'f(x)-(x+1)',{},['فوق'],r'(\Gamma)','(y=x+1)',{'bars':(0,)})),
(r'$(C_f)$ فوق $(\Delta)$}},t,\text{\ar{$(C_f)$ تحت $(\Delta)$}},}',2,'tab',([M,'-3',P],'f(x)-x',{1:'A(-3;-3)'},['فوق','تحت'],F,D,{})),
(r'\tkzTabLine{d,\text{\ar{$(C_f)$ تحت $(D)$}},}',1,'tab',(['-1',P],'f(x)-x',{},['تحت'],F,'(D)',{'bars':(0,)})),
(r'$(C_f)$ فوق $y=4$}},d,',1,'tab',([M,'-1','3',P],'f(x)-4',{},['فوق','تحت','فوق'],F,'(y=4)',{'bars':(1,2)})),
(r'\tkzTabLine{d,\hbox{\ar{\footnotesize $(C_f)$ فوق $(\Delta)$}},z,',1,'tab',(['-2','0','2'],'f(x)-2',{1:r'\omega(0;2)'},['فوق','تحت'],F,D,{'bars':(0,2)})),
(A1,1,'tab',([M,'-4',P],'f(x)-x',{1:'A(-4;-4)'},['فوق','تحت'],F,D,{})),
(r'\tkzTabLine{,\hbox{\ar{\footnotesize $(C_f)$ تحت $(\Delta)$}},z,\hbox{\ar{\footnotesize فوق $(\Delta)$}},d,',1,'tab',([M,'-2','-1',P],'f(x)-(x+1)',{1:'A(-2;-1)'},['تحت','فوق','فوق'],F,D,{'bars':(2,)})),
(r'\tkzTabLine{,\hbox{\ar{\footnotesize $(C_f)$ تحت $(\Delta)$}},d,\hbox{\ar{\footnotesize $(C_f)$ فوق $(\Delta)$}},d,',1,'tab',([M,'-1','1',P],'f(x)-x',{},['تحت','فوق','تحت'],F,D,{'bars':(1,2)})),
(r'$(C_f)$ تحت $(\Gamma)$}},d,',1,'tab',([M,'-1',P],'f(x)-k(x)',{},['تحت','فوق'],F,r'(\Gamma)',{'bars':(1,)})),
(r'\tkzTabLine{,\hbox{\ar{\footnotesize $(C_f)$ تحت $(\Delta)$}},d,\hbox{\ar{\footnotesize $(C_f)$ فوق $(\Delta)$}},}',1,'tab',([M,'1',P],'f(x)-(x+1)',{},['تحت','فوق'],F,D,{'bars':(1,)})),
(r'\tkzTabLine{,\hbox{\ar{\footnotesize $(C_f)$ تحت $(T)$}},z,',1,'tab',([M,'0',P],r'f(x)+\frac12x',{1:'O(0;0)'},['تحت','فوق'],F,'(T)',{})),
(A1,2,'tab',([M,r'\frac13',P],r'f(x)-\left(\frac32x+\frac52\right)',{1:r'A\left(\frac13;3\right)'},['فوق','تحت'],F,D,{})),
(r'\tkzTabLine{,\hbox{\ar{\footnotesize $(C_f)$ تحت $(\Delta)$}},z,\hbox{\ar{\footnotesize $(C_f)$ فوق $(\Delta)$}},}',1,'tab',([M,'-1',P],'f(x)+x',{1:'A(-1;1)'},['تحت','فوق'],F,D,{})),
(r'\tkzTabLine{,\hbox{\ar{\footnotesize $(C_f)$ فوق $(\Delta)$}},z,\hbox{\ar{\footnotesize تحت $(\Delta)$}},d,',1,'tab',([M,'1','2',P],'f(x)-x',{1:'A(1;1)'},['فوق','تحت','تحت'],F,D,{'bars':(2,)})),
(r'\QQ{5} $g(x)-1=\dfrac{4x}{(x+3)(x-2)}$:',1,'after_tab',([M,'-3','0','2',P],'g(x)-1',{2:'A(0;1)'},['تحت','فوق','تحت','فوق'],'(C_g)','(y=1)',{'bars':(1,3)})),
(r'\textbf{الوضع النسبي:} $f(x)-x=-\dfrac{2}{\sqrt{x+1}}<0$ من أجل كل $x>-1$:',1,'after',(['-1',P],'f(x)-x',{},['تحت'],'(C)',D,{'bars':(0,)})),
]
L=open(p).read().split('\n')
for k,c in enumerate(C):
    if c[2]=='after_tab':
        i=[j for j,l in enumerate(L) if c[0] in l][0]
        while L[i].strip()!=r'\end{TAB}': i+=1
        C[k]=(L[i],sum(1 for l in L[:i+1] if l==L[i]),'after',c[3])
print(apply(p,C))
