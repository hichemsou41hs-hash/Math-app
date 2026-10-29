UNIT='الدالة اللوغاريتمية النيبيرية'
FIELD='تحليل'
LEVEL='3 ع ت'
TOOLS=r'المنهاج ، الكتاب المدرسي ، الآلة الحاسبة العلمية ، برمجية Geogebra.'
S=[]
# ---------------------------------------------------------------- 14
G14=GR(r'''\draw[gray,dashed] (-2.4,-2.4)--(5,5) node[above right]{$y=x$};
\draw[cDef,very thick,domain=-2.4:1.6,samples=80] plot (\x,{exp(\x)}) node[above]{$(C_{\exp})$};
\draw[cThm,very thick,domain=0.09:5,samples=80] plot (\x,{ln(\x)}) node[below]{$(C_{\ln})$};
\fill[cDef] (0,1) circle (2pt) node[above left]{$(0;1)$}; \fill[cThm] (1,0) circle (2pt) node[below right]{$(1;0)$};
\fill[cThm] (2.718,1) circle (2pt) node[below right]{$(e;1)$};''',(-2.6,5.2),(-2.6,5.2),x=0.85,y=0.75)
S.append(sess('14',r'الدالة اللوغاريتمية النيبيرية: تعريف ، اتجاه التغير ، معادلات ومتراجحات',
[r'الدالة الأسية: خواصها واتجاه تغيرها ، مبرهنة القيم المتوسطة.'],
[r'تعريف الدالة $\ln$ ومعرفة خواصها المميزة.',r'حل معادلات ومتراجحات تتضمن $\ln$.'],TOOLS,
r'التذكير بمبرهنة القيم المتوسطة ، وبأن $e^x>0$ وأن الدالة الأسية متزايدة تمامًا.',
ACT('05')+r'\ (نشاط 2 صفحة 22) نقبل أنه من أجل كل عدد حقيقي $a>0$ توجد قيمة وحيدة $b$ حيث $e^b=a$.'
+Q(r'عيّن العدد $b$ في الحالات: $a=1$ ، $a=e$ ، $a=\dfrac1e$ ، $a=e^2$.',r'بالآلة الحاسبة ، عيّن قيمة تقريبية إلى $10^{-3}$ للعدد $b$ حيث $e^b=2$.',r'إذا كان $e^{b}=2$ فما العدد $b^{\prime}$ حيث $e^{b^{\prime}}=\dfrac12$ ؟',r'بيّن أن النقطة $M(a;b)$ هي نظيرة النقطة $N(b;a)$ من منحنى الدالة الأسية بالنسبة إلى المستقيم $y=x$.')
+DIS()+Q(r'$e^0=1$ إذن $b=\RR{0}$ ؛ $e^1=e$ إذن $b=\RR{1}$ ؛ $e^{-1}=\dfrac1e$ إذن $b=\RR{-1}$ ؛ $e^2=e^2$ إذن $b=\RR{2}$.',
   r'$e^{0{,}693}\approx2{,}000$ ، إذن $b\approx\RR{0{,}693}$ (لاحظ $0<b<1$ لأن $e^0=1<2<e$).',
   r'$e^{-b}=\dfrac1{e^b}=\dfrac12$ ، إذن $b^{\prime}=\RR{-b}$.',
   r'$e^b=a$ يعني $N(b;a)$ على منحنى الأسية ، و $M(a;b)$ نظيرتها بالنسبة إلى $y=x$: المنحنيان \RR{متناظران}.'),
DEF()+r'\ من أجل كل عدد حقيقي $a$ من $]0;+\infty[$ يوجد عدد حقيقي وحيد $b$ حيث $e^b=a$ ، يسمى \textbf{اللوغاريتم النيبيري} للعدد $a$ ونرمز له $\RR{\ln a}$.\par \textbf{الدالة اللوغاريتمية النيبيرية} $\ln$ هي الدالة التي ترفق بكل $x$ من $]0;+\infty[$ العدد $\ln x$.'
+L('cRem','نتائج')+Q(r'من أجل $x>0$ و $y\in\mathbb R$: $\RR{\ln x=y}$ يعني $\RR{x=e^y}$.',r'من أجل $x>0$: $\RR{e^{\ln x}=x}$ ؛ ومن أجل كل $x$ من $\mathbb R$: $\RR{\ln\left(e^x\right)=x}$.',r'$\RR{\ln1=0}$ و $\RR{\ln e=1}$.')
+PRO()+r'\ الدالة $\ln$ \RR{متزايدة تمامًا على $]0;+\infty[$}.'
+PRF()+r'\ ليكن $0<a<b$: $e^{\ln a}<e^{\ln b}$ ، وبما أن الدالة الأسية متزايدة تمامًا فإن $\ln a<\ln b$.'
+L('cRem','نتائج')+r'\ من أجل كل $x>0$ و $y>0$:'+Q(r'$\RR{\ln x=\ln y}$ يعني $\RR{x=y}$ ؛ $\RR{\ln x<\ln y}$ يعني $\RR{x<y}$.',r'$\ln x>0$ يعني $x>1$ ؛ $\ln x<0$ يعني $0<x<1$.')
+EX('جدول التغيرات والتمثيل البياني')+VAR(['0','1','e',r'+\infty'],r'\ln x',r'\ln^{\prime}(x)',['||','+','','+','','+',''],['','0','1',''],['l','m','m','h'])+G14
+MET('حل معادلة أو متراجحة')+Q(r'نعيّن مجموعة الحلول الممكنة $D$ (ما داخل $\ln$ موجب تمامًا).',r'نحوّل: $\ln u=\ln v$ تعني $u=v$ ؛ $\ln u=k$ تعني $u=e^k$ ؛ $\ln u<\ln v$ تعني $u<v$.',r'نأخذ الحلول التي تنتمي إلى $D$.')
+EX(r'أمثلة: حل في $\mathbb R$')+Q(r'$\ln(2x+1)=0$: $D=\left]-\frac12;+\infty\right[$ ؛ $2x+1=e^0=1$ ، $x=0\in D$: $\RR{S=\{0\}}$.',
   r'$\ln(x-2)=-1$: $D=]2;+\infty[$ ؛ $x-2=e^{-1}$ ، $x=2+\dfrac1e\in D$: $\RR{S=\left\{2+\frac1e\right\}}$.',
   r'$\ln(x^2-1)=\ln x$: $D=]1;+\infty[$ ؛ $x^2-1=x$ ، أي $x^2-x-1=0$.\par الحلان $\dfrac{1-\sqrt5}2\notin D$ و $\dfrac{1+\sqrt5}2\approx1{,}62\in D$: $\RR{S=\left\{\frac{1+\sqrt5}2\right\}}$.',
   r'$e^{2x}-3e^x+2=0$: نضع $X=e^x>0$: $(X-1)(X-2)=0$ ، $e^x=1$ أو $e^x=2$: $\RR{S=\{0;\ln2\}}$.')
+WARN()+r'\ لا نحل قبل تعيين $D$ ، ولا ننسى التحقق أن الحلول تنتمي إليها.',
TT()+r'\par حل في $\mathbb R$ ما يلي:'+Q(r'$\ln(2-x)<0$.',r'$\ln(x-5)\geqslant-2$.',r'$\ln(2x+1)>\ln x$.',r'$x\ln x-\ln x\geqslant0$.',r'$2(\ln x)^2-\ln x-1=0$.')
+SOL()+Q(r'$D=]-\infty;2[$ ؛ $\ln(2-x)<\ln1$ تكافئ $2-x<1$ ، أي $x>1$: $\RR{S=]1;2[}$.',
   r'$D=]5;+\infty[$ ؛ $x-5\geqslant e^{-2}$ ، أي $x\geqslant5+e^{-2}$: $\RR{S=\left[5+e^{-2};+\infty\right[}$.',
   r'$D=]0;+\infty[$ ؛ $2x+1>x$ تكافئ $x>-1$ ، صحيحة على $D$: $\RR{S=]0;+\infty[}$.',
   r'$D=]0;+\infty[$ ؛ $(x-1)\ln x\geqslant0$ ، و $x-1$ و $\ln x$ لهما نفس الإشارة دائمًا (كلاهما سالب على $]0;1[$ وموجب على $]1;+\infty[$): $\RR{S=]0;+\infty[}$.',
   r'$D=]0;+\infty[$ ؛ نضع $X=\ln x$: $2X^2-X-1=0$ ، $X=1$ أو $X=-\dfrac12$.\par $\ln x=1$ يعني $x=e$ ؛ $\ln x=-\dfrac12$ يعني $x=e^{-\frac12}=\dfrac1{\sqrt e}$: $\RR{S=\left\{\frac1{\sqrt e};e\right\}}$.')
+HW(r'التمرينان 59 و 61 صفحة 106.'),
[r'تذكير.',r'مناقشة النشاط من طرف التلاميذ.',r'ربط النشاط بالمفهوم.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 15
S.append(sess('15',r'الخواص الجبرية للدالة اللوغاريتمية',
[r'تعريف الدالة $\ln$ ، خواص الدالة الأسية.'],
[r'معرفة الخواص الجبرية للدالة $\ln$ وتوظيفها في الحساب وحل المعادلات والمتراجحات.'],TOOLS,
r'التذكير بخواص الدالة الأسية: $e^{x+y}=e^xe^y$ و $e^{nx}=(e^x)^n$.',
ACT('06')+r'\ $a$ و $b$ عددان حقيقيان موجبان تمامًا. نضع $\alpha=\ln(ab)$ و $\beta=\ln a+\ln b$.'+Q(r'احسب $e^\alpha$ و $e^\beta$.',r'قارن بين $\alpha$ و $\beta$.')
+DIS()+Q(r'$e^\alpha=e^{\ln(ab)}=ab$ ؛ $e^\beta=e^{\ln a+\ln b}=e^{\ln a}\times e^{\ln b}=ab$.',r'$e^\alpha=e^\beta$ ، إذن $\alpha=\beta$ ، أي $\RR{\ln(ab)=\ln a+\ln b}$.'),
PRO('الخاصية الأساسية')+r'\ من أجل كل عددين $a$ و $b$ من $]0;+\infty[$: $\RR{\ln(a\times b)=\ln a+\ln b}$.\par (تعمم إلى جداء عدة أعداد موجبة تمامًا.)'
+L('cRem','نتائج')+r'\ من أجل كل $a>0$ و $b>0$ ومن أجل كل عدد صحيح $n$:'
+Q(r'$\RR{\ln\dfrac1a=-\ln a}$ ؛ $\RR{\ln\dfrac ab=\ln a-\ln b}$.',r'$\RR{\ln\left(a^n\right)=n\ln a}$.',r'$\RR{\ln\sqrt a=\dfrac12\ln a}$.')
+PRF()+QN(1,r'$\ln a+\ln\dfrac1a=\ln\left(a\times\dfrac1a\right)=\ln1=0$ ، ومنه $\ln\dfrac1a=-\ln a$.')
+r'\par $\ln\dfrac ab=\ln\left(a\times\dfrac1b\right)=\ln a+\ln\dfrac1b=\ln a-\ln b$.'
+QN(2,r'$e^{n\ln a}=\left(e^{\ln a}\right)^n=a^n$ ، ومنه $\ln\left(a^n\right)=n\ln a$.')
+QN(3,r'$a=\left(\sqrt a\right)^2$ ، إذن $\ln a=2\ln\sqrt a$ ، أي $\ln\sqrt a=\dfrac12\ln a$.')
+EX('أمثلة')+Q(r'$\ln9=\ln3^2=\RR{2\ln3}$ ؛ $\ln8=\ln2^3=\RR{3\ln2}$ ؛ $\ln\sqrt e=\RR{\dfrac12}$.',
   r'$A=\ln12-\ln3=\ln\dfrac{12}3=\ln4=\RR{2\ln2}$.',r'$B=\ln\left(e^2\right)+\ln\dfrac1e=2-1=\RR{1}$.',r'$C=3\ln2+\ln\dfrac18=\ln8-\ln8=\RR{0}$.')
+EX('حل معادلة')+r'\ $\ln x+\ln(x-2)=\ln3$: $D=]2;+\infty[$.'+Q(r'$\ln\big[x(x-2)\big]=\ln3$ ، أي $x^2-2x-3=0$ ، $(x-3)(x+1)=0$.',r'$x=3\in D$ و $x=-1\notin D$: $\RR{S=\{3\}}$.')
+WARN()+r'\ $\ln(a+b)\neq\ln a+\ln b$ ، و $\ln\dfrac ab\neq\dfrac{\ln a}{\ln b}$.',
TT('1')+r'\par احسب بدلالة العدد الطبيعي $n\geqslant2$ المجموع: $S_n=\ln\dfrac12+\ln\dfrac23+\ln\dfrac34+\dots+\ln\dfrac{n-1}n$.'
+L('cMeth','تمرين تطبيقي 2')+r'\par حل في $\mathbb R$:'+Q(r'$\ln(x-1)+\ln(x+2)\leqslant2\ln2$.',r'$\ln(x+1)-\ln(x-1)>0$.')
+SOL('حل التمرين التطبيقي 1')+r'\par $S_n=\ln\left(\dfrac12\times\dfrac23\times\dfrac34\times\dots\times\dfrac{n-1}n\right)$ (البسوط تختصر مع المقامات).\par $S_n=\ln\dfrac1n=\RR{-\ln n}$.'
+SOL('حل التمرين التطبيقي 2')+Q(r'$D=]1;+\infty[$ ؛ $\ln\big[(x-1)(x+2)\big]\leqslant\ln4$ ، أي $x^2+x-2\leqslant4$.\par $x^2+x-6\leqslant0$ ، $(x+3)(x-2)\leqslant0$ ، $-3\leqslant x\leqslant2$ ، مع $x>1$: $\RR{S=]1;2]}$.',
   r'$D=]1;+\infty[$ ؛ $\ln(x+1)>\ln(x-1)$ تكافئ $x+1>x-1$ ، صحيحة دائمًا: $\RR{S=]1;+\infty[}$.')
+HW(r'التمرينان 67 و 68 صفحة 107.'),
[r'تذكير.',r'مناقشة النشاط.',r'البراهين مع التلاميذ.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 16
S.append(sess('16',r'اشتقاقية الدالة $\ln$ ودراسة الدالة $\ln\circ u$',
[r'مشتقة دالة مركبة ، الدالة $\ln$ وخواصها.'],
[r'حساب مشتقة الدالة $\ln$ ومشتقة الدالة $\ln\circ u$ ودراسة اتجاه تغيرها.'],TOOLS,
r'التذكير بمشتقة دالة مركبة.',
ACT('07')+r'\ نقبل أن $\ln$ مستمرة وقابلة للاشتقاق على $]0;+\infty[$. نعتبر $f(x)=e^{\ln x}$ على $]0;+\infty[$.'+Q(r'احسب $f^{\prime}(x)$ باستعمال مشتقة مركب دالتين.',r'بملاحظة أن $f(x)=x$ ، احسب $f^{\prime}(x)$ مجددًا.',r'استنتج $\ln^{\prime}(x)$.')
+DIS()+Q(r'$f^{\prime}(x)=\ln^{\prime}(x)\times e^{\ln x}=\ln^{\prime}(x)\times x$.',r'$f(x)=x$ ، إذن $f^{\prime}(x)=1$.',r'$x\,\ln^{\prime}(x)=1$ ، أي $\RR{\ln^{\prime}(x)=\dfrac1x}$.'),
PRO('خاصية 1')+r'\ الدالة $\ln$ مستمرة على $]0;+\infty[$.'
+PRO('خاصية 2')+r'\ الدالة $\ln$ قابلة للاشتقاق على $]0;+\infty[$ و $\RR{\ln^{\prime}(x)=\dfrac1x}$.'
+L('cMeth','المماس والوضع النسبي')+Q(r'المماس عند $1$: $y=\ln^{\prime}(1)(x-1)+\ln1$ ، أي $\RR{(T):\ y=x-1}$.',r'نضع $g(x)=\ln x-(x-1)$: $g^{\prime}(x)=\dfrac1x-1=\dfrac{1-x}x$ ، موجبة على $]0;1[$ وسالبة على $]1;+\infty[$.',r'$g$ تبلغ قيمتها الحدية الكبرى $g(1)=0$ ، إذن $g(x)\leqslant0$ ، أي $\RR{\ln x\leqslant x-1}$:')
+VP(['0','1',r'+\infty'],r'\ln x-(x-1)',{1:'A(1;0)'},['تحت','تحت'],r'(C_{\ln})','(T)',meet='يمس')
+PRO(r'اتجاه تغير $\ln\circ u$')+r'\ إذا كانت $u$ معرفة وموجبة تمامًا على مجال $I$ فإن للدالتين $u$ و $\ln\circ u$ \RR{نفس اتجاه التغير} على $I$ (لأن $\ln$ متزايدة تمامًا).'
+EX()+r'\ $f(x)=\ln\left(\dfrac5{x-2}\right)$ على $]2;+\infty[$: $u(x)=\dfrac5{x-2}$ متناقصة تمامًا وموجبة ، إذن \RR{$f$ متناقصة تمامًا على $]2;+\infty[$}.'
+PRO('المشتقة')+r'\ إذا كانت $u$ قابلة للاشتقاق وموجبة تمامًا على $I$: $\RR{(\ln\circ u)^{\prime}(x)=\dfrac{u^{\prime}(x)}{u(x)}}$.'
+PRF()+r'\ حسب مشتقة مركب دالتين: $(\ln\circ u)^{\prime}(x)=u^{\prime}(x)\times\ln^{\prime}\big(u(x)\big)=u^{\prime}(x)\times\dfrac1{u(x)}$.'
+EX('أمثلة')+Q(r'$f(x)=\ln\left(x^2+x+1\right)$ على $\mathbb R$ ($x^2+x+1>0$ لأن $\Delta=-3<0$): $\RR{f^{\prime}(x)=\dfrac{2x+1}{x^2+x+1}}$.',r'$g(x)=\ln\left(e^{-x}+3\right)$ على $\mathbb R$: $\RR{g^{\prime}(x)=\dfrac{-e^{-x}}{e^{-x}+3}}$.'),
TT()+r'\par ادرس اتجاه تغير الدالة $f$ في كل حالة:'+Q(r'$f(x)=2x+\ln x$ ، $D_f=]0;+\infty[$.',r'$f(x)=x^2+2x+\ln(x+1)$ ، $D_f=]-1;+\infty[$.',r'$f(x)=x+5+6\ln\left(\dfrac x{x-1}\right)$ ، $D_f=]-\infty;0[$.',r'$f(x)=1+\dfrac{2\ln x}x$ ، $D_f=]0;+\infty[$.')
+SOL()+Q(r'$f^{\prime}(x)=2+\dfrac1x>0$ على $]0;+\infty[$: \RR{$f$ متزايدة تمامًا}.',
   r'$f^{\prime}(x)=2x+2+\dfrac1{x+1}=2(x+1)+\dfrac1{x+1}>0$ لأن $x+1>0$: \RR{$f$ متزايدة تمامًا}.',
   r'$u(x)=\dfrac x{x-1}>0$ على $]-\infty;0[$ (البسط والمقام سالبان).\par $\dfrac{u^{\prime}(x)}{u(x)}=\dfrac{-1}{(x-1)^2}\times\dfrac{x-1}x=\dfrac{-1}{x(x-1)}$.\par $f^{\prime}(x)=1-\dfrac6{x(x-1)}=\dfrac{x^2-x-6}{x(x-1)}=\dfrac{(x-3)(x+2)}{x(x-1)}$.\par على $]-\infty;0[$: $x(x-1)>0$ و $x-3<0$ ، فإشارة $f^{\prime}(x)$ عكس إشارة $x+2$:'
   +VAR([r'-\infty','-2','0'],r'f(x)',r'f^{\prime}(x)',['','+','0','-','||'],['',r'3+6\ln\frac23',''],['l','h','l'])
   +r'$f(-2)=3+6\ln\dfrac23\approx\RR{0{,}57}$.',
   r'$f^{\prime}(x)=\dfrac{2\times\frac1x\times x-2\ln x}{x^2}=\dfrac{2(1-\ln x)}{x^2}$.\par $f^{\prime}(x)>0$ يعني $\ln x<1$ ، أي $x<e$:'
   +VAR(['0','e',r'+\infty'],r'f(x)',r'f^{\prime}(x)',['||','+','0','-',''],['',r'1+\frac2e',''],['l','h','l'])
   +r'$f(e)=\RR{1+\dfrac2e}\approx1{,}74$.')
+HW(r'التمرينان 87 و 88 صفحة 108 ، والتمرينان 95 و 97 صفحة 109.'),
[r'تذكير.',r'التلاميذ يبرهنون الخاصية.',r'الوضع النسبي بجدول.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 17
S.append(sess('17',r'اللوغاريتم العشري وتطبيقاته',
[r'الدالة $\ln$ وخواصها الجبرية.'],
[r'معرفة خواص دالة اللوغاريتم العشري وتطبيقاتها.'],TOOLS,
r'كم رقمًا يكتب به العدد $2^{100}$ ؟',
ACT('08')+r'\ نعرف الدالة $\log$ على $]0;+\infty[$ بـ: $\log x=\dfrac{\ln x}{\ln10}$.'+Q(r'احسب $\log1$ و $\log10$ و $\log100$.',r'بيّن أن $\log(ab)=\log a+\log b$.',r'بيّن أن $\log10^n=n$ من أجل كل عدد صحيح $n$.')
+DIS()+Q(r'$\log1=\dfrac0{\ln10}=\RR{0}$ ؛ $\log10=\RR{1}$ ؛ $\log100=\dfrac{2\ln10}{\ln10}=\RR{2}$.',r'$\log(ab)=\dfrac{\ln a+\ln b}{\ln10}=\RR{\log a+\log b}$.',r'$\log10^n=\dfrac{n\ln10}{\ln10}=\RR{n}$.'),
DEF()+r'\ دالة \textbf{اللوغاريتم العشري} هي الدالة $\log$ المعرفة على $]0;+\infty[$ بـ: $\RR{\log x=\dfrac{\ln x}{\ln10}}$.'
+PRO('خواص')+r'\ من أجل كل $a>0$ و $b>0$ ومن أجل كل عدد صحيح $n$:'+Q(r'$\log(ab)=\log a+\log b$ ؛ $\log\dfrac ab=\log a-\log b$ ؛ $\log a^n=n\log a$.',r'$\RR{\log10^n=n}$.',r'$\log$ \RR{متزايدة تمامًا على $]0;+\infty[$} لأن $\ln10>0$.')
+L('cRem','نتيجة')+r'\ إذا كان $10^n\leqslant x<10^{n+1}$ فإن $\RR{n\leqslant\log x<n+1}$.'
+EX()+r'\ $x=3{,}87\times10^7$: $10^7<x<10^8$ ، إذن $\RR{7<\log x<8}$.'
+MET(r'عدد أرقام عدد طبيعي $x\geqslant1$')+Q(r'نحسب $\log x$ ونعيّن جزءه الصحيح $p$.',r'$p\leqslant\log x<p+1$ ، أي $10^p\leqslant x<10^{p+1}$.',r'عدد أرقام $x$ هو $\RR{p+1}$.')
+EX('تطبيق')+r'\ عدد أرقام $n=2017^{2018}$:'+Q(r'$\log n=2018\log2017\approx6668{,}897$ ، الجزء الصحيح $6668$.',r'$10^{6668}\leqslant n<10^{6669}$: عدد الأرقام \RR{6669}.')
+L('cSec','في الكيمياء')+r'\ درجة الحموضة: $\RR{pH=-\log\left[H_3O^+\right]}$ (التركيز بـ $mol/L$). مثال: $\left[H_3O^+\right]=2{,}5\times10^{-4}$: $pH=-\log\left(2{,}5\times10^{-4}\right)\approx\RR{3{,}60}$.'
+L('cSec','في الزلازل')+r'\ درجة زلزال شدته $I$: $\RR{M=\log\dfrac I{I_0}}$ ($I_0$ شدة مرجعية). زلزال أشد بـ $10$ مرات: $\log\dfrac{10I}{I_0}=1+M$ ، أي \RR{تزيد الدرجة بـ $1$}.',
TT()+r'\par'+Q(r'كم رقمًا يكتب به العدد $2^{100}$ ؟',r'احسب $pH$ محلول تركيزه $\left[H_3O^+\right]=4\times10^{-5}\ mol/L$.',r'حل في $\mathbb R$: $\log(2x+1)=1+\log(x-1)$.')
+SOL()+Q(r'$\log2^{100}=100\log2\approx30{,}103$ ، الجزء الصحيح $30$: عدد الأرقام \RR{31}.',
   r'$pH=-\log\left(4\times10^{-5}\right)=5-\log4\approx\RR{4{,}40}$.',
   r'$D=]1;+\infty[$ ؛ $1+\log(x-1)=\log\big[10(x-1)\big]$ ، إذن $2x+1=10x-10$ ، $x=\dfrac{11}8\in D$: $\RR{S=\left\{\frac{11}8\right\}}$.')
+HW(r'التمارين 98 و 100 و 101 صفحة 109.'),
[r'سؤال تحفيزي.',r'مناقشة النشاط.',r'تطبيقات من العلوم.',r'نهاية المحور: فرض أو معالجة.']))
