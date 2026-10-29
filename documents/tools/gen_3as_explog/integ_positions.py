exec(open('/home/user/Math-app/documents/tools/vtab_apply.py').read())
M,P=r'-\infty',r'+\infty'; F,D=r'(C_f)',r'(\Delta)'
d='/home/user/Math-app/documents/integrales/'
print(apply(d+'molakhas_integ_3as.tex',[
(r'\tkzTabLine{,\text{\scriptsize\ar{$(C_f)$ فوق $(C_g)$}},}',1,'tab',(['-2','1'],'f(x)-g(x)',{0:'A(-2;0)',1:'B(1;3)'},['فوق'],F,'(C_g)',{})),
(r'\tkzTabLine{,\text{\scriptsize\ar{$(C_f)$ فوق $(\Delta)$}},}',1,'tab',(['0',r'\lambda'],'f(x)-(x+1)',{},['فوق'],F,D,{})),
(r'\tkzTabLine{d,\text{\scriptsize\ar{$(C_f)$ تحت $(\Delta)$}},t,',1,'tab',(['0','1',P],'f(x)-(x-1)',{1:'A(1;0)'},['تحت','فوق'],F,D,{'bars':(0,)})),
]))
print(apply(d+'tamarin_integ_3as.tex',[
(r'\tkzTabLine{,\text{\ar{$(C_f)$ تحت $(xx\')$}},,\text{\ar{$(C_f)$ فوق $(xx\')$}},}'.replace("\\'","'"),1,'tab',(['0','2','3'],'f(x)',{0:'O(0;0)',1:'A(2;0)'},['تحت','فوق'],F,"(xx')",{})),
(r'\tkzTabLine{,\text{\ar{$(C_g)$ تحت $(C_f)$}},',1,'tab',([M,'-1','2',P],'g(x)-f(x)',{1:'A(-1;1)',2:'B(2;4)'},['تحت','فوق','تحت'],'(C_g)','(C_f)',{})),
(r'\tkzTabLine{,\text{\ar{$(C_f)$ تحت $(\Delta)$}},,\text{\ar{$(C_f)$ فوق $(\Delta)$}},}',1,'tab',(['0','1',P],'f(x)-(x-1)',{1:'A(1;0)'},['تحت','فوق'],F,D,{'bars':(0,)})),
(r'\tkzTabLine{,\text{\ar{$(C_f)$ تحت $(xx\')$}},,\text{\ar{$(C_f)$ فوق $(xx\')$}},}'.replace("\\'","'"),2,'tab',([M,'1',P],'f(x)',{1:'A(1;0)'},['تحت','فوق'],F,"(xx')",{})),
(r'\tkzTabLine{,\text{\ar{$(C_f)$ فوق $(\Delta)$}},}',1,'tab',([M,P],'f(x)-(x-1)',{},['فوق'],F,D,{})),
]))
