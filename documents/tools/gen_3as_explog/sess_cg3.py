UNIT='التزايد المقارن ودراسة الدوال'
FIELD='تحليل'
LEVEL='3 ع ت'
TOOLS=r'المنهاج ، الكتاب المدرسي ، الآلة الحاسبة العلمية ، برمجية Geogebra.'
S=[]
L_=lambda a,e:r'\lim\limits_{x\to %s}%s'%(a,e)
# ---------------------------------------------------------------- 23
S.append(sess('23',r'قوى عدد حقيقي موجب تمامًا ، الدالة $x\mapsto a^x$',
[r'الدالتان الأسية واللوغاريتمية وخواصهما.'],
[r'تعريف $a^x$ واستعمال خواصه.',r'دراسة الدالة $x\mapsto a^x$ وحل معادلات ومتراجحات.'],TOOLS,
r'نعرف $2^3$ و $2^{-1}$ و $2^{\frac12}$: فما معنى $2^{\sqrt2}$ ؟',
ACT('01')+r'\ (نشاط 01 صفحة 120) $a$ عدد حقيقي موجب تمامًا و $n$ عدد صحيح.'
+Q(r'بيّن أن $a^n=e^{n\ln a}$.',r'احسب بهذه الكتابة $2^3$ و $2^{-1}$.',r'اقترح تعريفًا للعدد $2^{\sqrt2}$ واحسب قيمة تقريبية له.')
+DIS()+Q(r'$a=e^{\ln a}$ ، إذن $a^n=\left(e^{\ln a}\right)^n=\RR{e^{n\ln a}}$.',r'$2^3=e^{3\ln2}=\RR{8}$ ؛ $2^{-1}=e^{-\ln2}=\RR{\dfrac12}$.',r'نمدد الكتابة: $2^{\sqrt2}=e^{\sqrt2\ln2}\approx\RR{2{,}665}$.'),
DEF()+r'\ من أجل كل عدد حقيقي $a>0$ ومن أجل كل عدد حقيقي $x$: $\RR{a^x=e^{x\ln a}}$.'
+PRO('قواعد الحساب')+r'\ من أجل $a>0$ ، $b>0$ و $x$ ، $y$ حقيقيين:'
+Q(r'$\RR{a^{x+y}=a^x\times a^y}$ ؛ $\RR{a^{-x}=\dfrac1{a^x}}$ ؛ $\RR{a^{x-y}=\dfrac{a^x}{a^y}}$.',r'$\RR{\left(a^x\right)^y=a^{xy}}$ ؛ $\RR{(ab)^x=a^x\,b^x}$.',r'$\RR{\ln\left(a^x\right)=x\ln a}$.')
+PRF()+r'\ $a^{x+y}=e^{(x+y)\ln a}=e^{x\ln a}\times e^{y\ln a}=a^x\times a^y$ (بنفس الطريقة للبقية).'
+PRO('الدالة $x\mapsto a^x$')+Q(r'مشتقتها: $\left(a^x\right)^{\prime}=\left(e^{x\ln a}\right)^{\prime}=\RR{(\ln a)\,a^x}$.',r'إذا كان $a>1$: $\ln a>0$ ، \RR{متزايدة تمامًا} ، $\lim\limits_{x\to+\infty}a^x=+\infty$ و $\lim\limits_{x\to-\infty}a^x=0$.',r'إذا كان $0<a<1$: $\ln a<0$ ، \RR{متناقصة تمامًا} ، $\lim\limits_{x\to+\infty}a^x=0$ و $\lim\limits_{x\to-\infty}a^x=+\infty$.')
+EX('أمثلة محلولة')+Q(r'$2^x=8$: $2^x=2^3$ ، إذن $\RR{x=3}$.',
   r'$3^{2x}=5$: $2x\ln3=\ln5$ ، إذن $\RR{x=\dfrac{\ln5}{2\ln3}}\approx0{,}73$.',
   r'$4^x-3\times2^x+2=0$: نضع $X=2^x>0$ ، $4^x=X^2$: $X^2-3X+2=0$ ، $X=1$ أو $X=2$:\par $2^x=1$ يعطي $x=0$ ، و $2^x=2$ يعطي $x=1$: $\RR{S=\{0;1\}}$.',
   r'$\left(\frac12\right)^x\geqslant\frac18$: $\left(\frac12\right)^x\geqslant\left(\frac12\right)^3$ ، والدالة متناقصة تمامًا ($a=\frac12<1$) ، إذن $\RR{x\leqslant3}$.')
+WARN()+r'\ $a^x$ معرف من أجل $a>0$ فقط ، و $(-2)^x$ غير معرف عمومًا.',
TT()+r'\par'+Q(r'حل في $\mathbb R$: $2^{x+1}=3^x$.',r'احسب مشتقة $f(x)=3^x$ وادرس اتجاه تغيرها.',r'احسب $\lim\limits_{x\to+\infty}\left(\frac23\right)^x$.')
+SOL()+Q(r'نأخذ $\ln$ للطرفين: $(x+1)\ln2=x\ln3$ ، أي $x(\ln3-\ln2)=\ln2$:\par $\RR{x=\dfrac{\ln2}{\ln\frac32}}\approx1{,}71$.',
   r'$f^{\prime}(x)=\RR{(\ln3)\,3^x}>0$ لأن $\ln3>0$: \RR{$f$ متزايدة تمامًا على $\mathbb R$}.',
   r'$0<\frac23<1$ ، إذن $\RR{\lim\limits_{x\to+\infty}\left(\frac23\right)^x=0}$ (لأن $x\ln\frac23\to-\infty$).')
+HW(r'تمارين من باب التزايد المقارن.'),
[r'سؤال تحفيزي.',r'مناقشة النشاط.',r'الخواص تُبرهن.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 24
S.append(sess('24',r'الجذر النوني ، دوال القوى $x\mapsto x^\alpha$',
[r'قوى عدد حقيقي ، مبرهنة القيم المتوسطة.'],
[r'تعريف الجذر النوني لعدد موجب.',r'دراسة الدوال $x\mapsto x^\alpha$.'],TOOLS,
r'ما العدد الموجب الذي مكعبه $27$ ؟ والذي مكعبه $2$ ؟',
ACT('02')+r'\ (نشاط 02 صفحة 120) نعتبر $g(x)=x^3$ على $[0;+\infty[$.'
+Q(r'ادرس اتجاه تغير $g$ ونهايتها عند $+\infty$.',r'بيّن أنه من أجل كل $a\geqslant0$ يوجد عدد وحيد $b\geqslant0$ حيث $b^3=a$.',r'عيّن $b$ لما $a=27$ ، ثم قيمة تقريبية لما $a=2$.')
+DIS()+Q(r'$g^{\prime}(x)=3x^2\geqslant0$: $g$ \RR{مستمرة ومتزايدة تمامًا} ، و $\lim\limits_{x\to+\infty}x^3=+\infty$.',r'$g$ تقابل من $[0;+\infty[$ نحو $[0;+\infty[$ (مبرهنة القيم المتوسطة): للمعادلة $b^3=a$ \RR{حل وحيد}.',r'$b=\RR{3}$ ؛ $b=2^{\frac13}=e^{\frac13\ln2}\approx\RR{1{,}26}$.'),
DEF()+r'\ $n$ عدد طبيعي ($n\geqslant2$) و $a\geqslant0$: \textbf{الجذر النوني} $\sqrt[n]a$ هو العدد الموجب الوحيد $b$ حيث $b^n=a$.\par ومن أجل $a>0$: $\RR{\sqrt[n]a=a^{\frac1n}=e^{\frac1n\ln a}}$.'
+EX('أمثلة')+Q(r'$\sqrt[3]{27}=\RR{3}$ ؛ $\sqrt[4]{16}=\RR{2}$ ؛ $\sqrt[3]{8^2}=8^{\frac23}=\left(8^{\frac13}\right)^2=\RR{4}$.',r'$x^3=5$ على $[0;+\infty[$: $x=\sqrt[3]5=5^{\frac13}\approx\RR{1{,}71}$.')
+PRO('دوال القوى')+r'\ $\alpha$ عدد حقيقي و $x>0$: $x^\alpha=e^{\alpha\ln x}$.'
+Q(r'المشتقة: $\left(x^\alpha\right)^{\prime}=\dfrac\alpha x\,e^{\alpha\ln x}=\RR{\alpha\,x^{\alpha-1}}$.',r'إذا كان $\alpha>0$: \RR{متزايدة تمامًا} ، $\lim\limits_{x\to0^+}x^\alpha=0$ و $\lim\limits_{x\to+\infty}x^\alpha=+\infty$.',r'إذا كان $\alpha<0$: \RR{متناقصة تمامًا} ، $\lim\limits_{x\to0^+}x^\alpha=+\infty$ و $\lim\limits_{x\to+\infty}x^\alpha=0$.')
+WARN()+r'\ نعرف $\sqrt[n]a$ في هذا المستوى من أجل $a\geqslant0$ فقط.',
TT()+r'\par'+Q(r'احسب $f^{\prime}(x)$ حيث $f(x)=x^{\frac32}$ على $]0;+\infty[$.',r'بسّط $A=\dfrac{\sqrt[3]{4}\times\sqrt[3]{2}}{\sqrt[4]{16}}$.',r'احسب $\lim\limits_{x\to+\infty}x^{-\frac12}$.')
+SOL()+Q(r'$f^{\prime}(x)=\dfrac32x^{\frac12}=\RR{\dfrac32\sqrt x}$.',r'$\sqrt[3]4\times\sqrt[3]2=\sqrt[3]8=2$ و $\sqrt[4]{16}=2$ ، إذن $\RR{A=1}$.',r'$\alpha=-\frac12<0$ ، إذن $\RR{\lim\limits_{x\to+\infty}x^{-\frac12}=0}$.')
+HW(r'تمارين من باب التزايد المقارن.'),
[r'سؤال.',r'مناقشة النشاط.',r'الحاسبة.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 25
S.append(sess('25',r'التزايد المقارن للدوال $x\mapsto e^x$ و $x\mapsto x^n$',
[r'نهايات الدالة الأسية ، الاشتقاق ، اتجاه التغير.'],
[r'معرفة وتوظيف النهايات المرجعية للتزايد المقارن بين الدالة الأسية ودوال القوى.'],TOOLS,
r'من يكبر أسرع لما $x\to+\infty$: $e^x$ أم $x^{10}$ ؟ (نجرب بالحاسبة $x=10$ ، $50$).',
ACT('03')+r'\ $f$ الدالة المعرفة على $[0;+\infty[$ بـ: $f(x)=e^x-\dfrac{x^2}2$.'
+Q(r'ادرس اتجاه تغير $f^{\prime}$ على $[0;+\infty[$.',r'استنتج إشارة $f^{\prime}(x)$ ، ثم اتجاه تغير $f$.',r'استنتج إشارة $f(x)$ ، ثم أن $e^x>\dfrac{x^2}2$.',r'احسب $\lim\limits_{x\to+\infty}\dfrac{e^x}x$ ، ثم استنتج $\lim\limits_{x\to-\infty}xe^x$.')
+DIS()+QN(1,r'$f^{\prime}(x)=e^x-x$ ، $f^{\prime\prime}(x)=e^x-1\geqslant0$ على $[0;+\infty[$: \RR{$f^{\prime}$ متزايدة}.')
+QN(2,r'$f^{\prime}(x)\geqslant f^{\prime}(0)=1>0$: \RR{$f$ متزايدة تمامًا على $[0;+\infty[$}.')
+QN(3,r'$f(x)\geqslant f(0)=1>0$ ، إذن $\RR{e^x>\dfrac{x^2}2}$.')
+QN(4,r'من أجل $x>0$: $\dfrac{e^x}x>\dfrac x2$ و $\dfrac x2\to+\infty$ ، إذن $\RR{\lim\limits_{x\to+\infty}\dfrac{e^x}x=+\infty}$ (المقارنة).')
+r'\par نضع $t=-x\to+\infty$: $xe^x=-\dfrac t{e^t}=-\dfrac1{\frac{e^t}t}\to\RR{0}$.',
PRO('خواص')+Q(r'$\RR{\lim\limits_{x\to+\infty}\dfrac{e^x}x=+\infty}$ و $\RR{\lim\limits_{x\to-\infty}xe^x=0}$.',r'من أجل كل عدد طبيعي $n\neq0$: $\RR{\lim\limits_{x\to+\infty}\dfrac{e^x}{x^n}=+\infty}$ و $\RR{\lim\limits_{x\to-\infty}x^ne^x=0}$.')
+REM()+r'\ عند اللانهاية \RR{تتفوق الدالة الأسية على الدالة قوة}.'
+EX('أمثلة محلولة')+Q(r'$\lim\limits_{x\to+\infty}\dfrac{e^{x^3}}{x^3}$: نضع $X=x^3\to+\infty$: $\dfrac{e^X}X\to\RR{+\infty}$.',
   r'$\lim\limits_{x\to+\infty}\dfrac{e^{x^2}}x=\lim\limits_{x\to+\infty}x\times\dfrac{e^{x^2}}{x^2}=(+\infty)\times(+\infty)=\RR{+\infty}$.',
   r'$\lim\limits_{x\to+\infty}\dfrac{e^{2x-1}}x=\lim\limits_{x\to+\infty}\dfrac2e\times\dfrac{e^{2x}}{2x}=\RR{+\infty}$ (نضع $X=2x$).',
   r'$\lim\limits_{x\to+\infty}\left(x^5+3-e^x\right)=\lim\limits_{x\to+\infty}e^x\left(\dfrac{x^5}{e^x}+\dfrac3{e^x}-1\right)=(+\infty)\times(0+0-1)=\RR{-\infty}$.',
   r'$\lim\limits_{x\to+\infty}\dfrac{e^x-x}x=\lim\limits_{x\to+\infty}\left(\dfrac{e^x}x-1\right)=\RR{+\infty}$.',
   r'$\lim\limits_{x\to-\infty}\left(x^2-3\right)e^x=\lim\limits_{x\to-\infty}\left(x^2e^x-3e^x\right)=0-0=\RR{0}$.',
   r'$\lim\limits_{x\to-\infty}xe^{3x-1}=\lim\limits_{x\to-\infty}\dfrac1{3e}\times(3x)e^{3x}=\RR{0}$ (نضع $X=3x\to-\infty$).')
+WARN()+r'\ نحلل العبارة أولًا لإظهار إحدى النهايات المرجعية.',
TT()+r'\par احسب:'+Q(r'$\lim\limits_{x\to+\infty}x^2e^{-x}$.',r'$\lim\limits_{x\to+\infty}\left(e^{2x}-x^3\right)$.',r'$\lim\limits_{x\to-\infty}\left(x+1\right)e^{x}$.')
+SOL()+Q(r'$x^2e^{-x}=\dfrac{x^2}{e^x}=\dfrac1{\frac{e^x}{x^2}}\to\RR{0}$.',r'$e^{2x}-x^3=e^{2x}\left(1-\dfrac{x^3}{e^{2x}}\right)$ ، و $\dfrac{x^3}{e^{2x}}=\dfrac18\times\dfrac{(2x)^3}{e^{2x}}\to0$ ، إذن النهاية $\RR{+\infty}$.',r'$(x+1)e^x=xe^x+e^x\to0+0=\RR{0}$.')
+HW(r'التمرينان 40 و 41 صفحة 136.'),
[r'تحدٍّ بالحاسبة.',r'مناقشة النشاط من طرف التلاميذ.',r'جدول النهايات يُحفظ.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 26
S.append(sess('26',r'التزايد المقارن للدوال $x\mapsto\ln x$ و $x\mapsto x^n$ ، نهايات بالعدد المشتق',
[r'التزايد المقارن للدالة الأسية ، العدد المشتق.'],
[r'معرفة وتوظيف النهايات المرجعية للتزايد المقارن بين الدالة اللوغاريتمية ودوال القوى.',r'حساب نهايات بالتعرف على عدد مشتق.'],TOOLS,
r'التذكير بأن $\lim\limits_{t\to+\infty}\dfrac t{e^t}=0$.',
ACT('04')+Q(r'من أجل $x>0$ نضع $t=\ln x$. احسب $\lim\limits_{x\to+\infty}\dfrac{\ln x}x$.',r'نضع $u=\dfrac1x$. بيّن أن $x\ln x=-\dfrac{\ln u}u$ ، ثم استنتج $\lim\limits_{x\to0^+}x\ln x$.')
+DIS()+Q(r'$x=e^t$ و $t\to+\infty$ لما $x\to+\infty$: $\dfrac{\ln x}x=\dfrac t{e^t}\to\RR{0}$.',r'$x\ln x=\dfrac1u\ln\dfrac1u=-\dfrac{\ln u}u$ ، و $u\to+\infty$ لما $x\to0^+$: $\RR{\lim\limits_{x\to0^+}x\ln x=0}$.'),
PRO('خواص')+Q(r'$\RR{\lim\limits_{x\to+\infty}\dfrac{\ln x}x=0}$ و $\RR{\lim\limits_{x\to0^+}x\ln x=0}$.',r'من أجل كل عدد طبيعي $n\neq0$: $\RR{\lim\limits_{x\to+\infty}\dfrac{\ln x}{x^n}=0}$ و $\RR{\lim\limits_{x\to0^+}x^n\ln x=0}$.')
+REM()+r'\ عند اللانهاية \RR{تتفوق الدالة قوة على الدالة اللوغاريتمية}.'
+EX('أمثلة محلولة')+Q(r'$\lim\limits_{x\to+\infty}(x-\ln x)=\lim\limits_{x\to+\infty}x\left(1-\dfrac{\ln x}x\right)=(+\infty)\times1=\RR{+\infty}$.',
   r'$\lim\limits_{x\to0^+}(1-x)\ln x$: $1-x\to1$ و $\ln x\to-\infty$: النهاية $\RR{-\infty}$.',
   r'$\lim\limits_{x\to+\infty}\dfrac{\ln x}{4x^3-x^2+3}=\lim\limits_{x\to+\infty}\dfrac{\ln x}{x^3}\times\dfrac1{4-\frac1x+\frac3{x^3}}=0\times\dfrac14=\RR{0}$.',
   r'$\lim\limits_{x\to+\infty}\left(x^2+2x-\ln x\right)=\lim\limits_{x\to+\infty}x\left(x+2-\dfrac{\ln x}x\right)=\RR{+\infty}$.',
   r'$\lim\limits_{x\to0^+}\left(x^3-x\right)\ln x=\lim\limits_{x\to0^+}\left(x^2\times x\ln x-x\ln x\right)=0-0=\RR{0}$.')
+MET('نهايات بالتعرف على عدد مشتق')+Q(r'$\lim\limits_{x\to0}\dfrac{e^x-1}x=\exp^{\prime}(0)=\RR{1}$.',r'$\lim\limits_{x\to0}\dfrac{\ln(1+x)}x=\RR{1}$ (العدد المشتق لـ $x\mapsto\ln(1+x)$ عند $0$).',r'مثال: $\lim\limits_{x\to+\infty}x\left(e^{\frac1x}-1\right)$: نضع $h=\frac1x\to0^+$: $\dfrac{e^h-1}h\to\RR{1}$.'),
TT()+r'\par احسب:'+Q(r'$\lim\limits_{x\to+\infty}\dfrac{\ln x}{\sqrt x}$.',r'$\lim\limits_{x\to0}\dfrac{e^{2x}-1}x$.',r'$\lim\limits_{x\to+\infty}x\ln\left(1+\dfrac1x\right)$.')
+SOL()+Q(r'نضع $X=\sqrt x$: $\ln x=2\ln X$ ، إذن $\dfrac{\ln x}{\sqrt x}=2\times\dfrac{\ln X}X\to\RR{0}$.',r'$\dfrac{e^{2x}-1}x=2\times\dfrac{e^{2x}-1}{2x}\to2\times1=\RR{2}$.',r'نضع $h=\frac1x\to0^+$: $\dfrac{\ln(1+h)}h\to\RR{1}$.')
+HW(r'التمرينان 42 و 45 صفحة 136 ، والتمرين 67 صفحة 140.'),
[r'تذكير.',r'مناقشة النشاط من طرف التلاميذ.',r'نقارن الطرق.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 27
G27=GR(r'''\draw[cDef,very thick,domain=-1.6:6,samples=100] plot (\x,{(\x+1)*exp(-\x)}) node[above]{$(C_f)$};
\draw[cRem!80!black,thick,dashed,domain=-1.6:-0.2] plot (\x,{2.718*(\x+1)}) node[above]{$(T)$};
\fill[cThm] (0,1) circle (2pt) node[above right]{$(0;1)$}; \fill[cThm] (-1,0) circle (2pt) node[below left]{$(-1;0)$};''',(-2.2,6.3),(-3.2,1.8),x=1,y=1.1)
G27b=GR(r'''\draw[cRem!80!black,thick,dashed,domain=-1:4.5] plot (\x,{\x-1}) node[right]{$(\Delta)$};
\draw[cDef,very thick,domain=-1.6:4.5,samples=100] plot (\x,{\x-1+exp(-\x)}) node[above]{$(C_g)$};
\fill[cThm] (0,0) circle (2pt);''',(-2,4.8),(-2.2,4),x=1,y=0.85)
S.append(sess('27',r'دراسة دوال أسية',
[r'المشتقات ، التزايد المقارن ، المستقيم المقارب.'],
[r'دراسة دالة أسية كاملة وتمثيلها البياني.'],TOOLS,
r'ما خطوات دراسة دالة؟',
ACT('05')+r'\ $f(x)=(x+1)e^{-x}$ على $\mathbb R$.'+Q(r'احسب نهايتي $f$ عند $-\infty$ و $+\infty$.',r'احسب $f^{\prime}(x)$ وادرس إشارتها.',r'شكّل جدول التغيرات.')
+DIS()+QN(1,r'عند $-\infty$: $x+1\to-\infty$ و $e^{-x}\to+\infty$: $\RR{\lim\limits_{x\to-\infty}f(x)=-\infty}$.')
+r'\par عند $+\infty$: $f(x)=\dfrac x{e^x}+\dfrac1{e^x}\to0+0$: $\RR{\lim\limits_{x\to+\infty}f(x)=0}$ ، والمستقيم $y=0$ مقارب أفقي.'
+QN(2,r'$f^{\prime}(x)=e^{-x}-(x+1)e^{-x}=\RR{-xe^{-x}}$ ، وإشارتها إشارة $-x$.')
+QN(3,'جدول التغيرات:')+VAR([r'-\infty','0',r'+\infty'],'f(x)',r'f^{\prime}(x)',['','+','0','-',''],[r'-\infty','1','0'],['l','h','l']),
MET('خطوات دراسة دالة')+Q(r'مجموعة التعريف والنهايات (التزايد المقارن) والمستقيمات المقاربة.',r'المشتقة وإشارتها ، ثم جدول التغيرات.',r'نقط خاصة (تقاطع مع المحورين ، مماسات) ، ثم الرسم.')
+EX('تكملة الدراسة')+Q(r'تقاطع مع محور الفواصل: $f(x)=0\iff x=-1$: النقطة $\RR{(-1;0)}$.',r'المماس عند $-1$: $f^{\prime}(-1)=e$ ، إذن $\RR{(T):\ y=e(x+1)}$.')+G27
+WARN()+r'\ إشارة $u(x)\,e^{v(x)}$ هي إشارة $u(x)$ لأن $e^{v(x)}>0$.',
TT()+r'\par $g(x)=x-1+e^{-x}$ على $\mathbb R$.'+Q(r'احسب نهايتي $g$ عند $\pm\infty$.',r'ادرس اتجاه تغير $g$.',r'بيّن أن $(\Delta):y=x-1$ مقارب مائل ، وادرس الوضع النسبي.')
+SOL()+Q(r'عند $+\infty$: $e^{-x}\to0$ ، إذن $\RR{\lim\limits_{x\to+\infty}g(x)=+\infty}$.\par عند $-\infty$: $g(x)=e^{-x}\left(xe^x-e^x+1\right)$ و $xe^x\to0$ ، إذن $\RR{\lim\limits_{x\to-\infty}g(x)=+\infty}$.',
   r'$g^{\prime}(x)=1-e^{-x}$ ، موجبة إذا كان $e^{-x}<1$ أي $x>0$:'
   +VAR([r'-\infty','0',r'+\infty'],'g(x)',r'g^{\prime}(x)',['','-','0','+',''],[r'+\infty','0',r'+\infty'],['h','l','h']),
   r'$g(x)-(x-1)=e^{-x}\xrightarrow[x\to+\infty]{}0$: $(\Delta)$ مقارب مائل بجوار $+\infty$ ، و $e^{-x}>0$:'
   +VP([r'-\infty',r'+\infty'],'g(x)-(x-1)',{},['فوق'],'(C_g)',r'(\Delta)')+G27b)
+HW(r'تمارين من باب التزايد المقارن.'),
[r'سؤال تلخيصي.',r'عمل بالأفواج.',r'الحاسبة للتحقق.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 28
G28=GR(r'''\draw[cDef,very thick,domain=0.55:8,samples=120] plot (\x,{ln(\x)/\x}) node[above]{$(C_f)$};
\draw[densely dotted] (2.718,0)--(2.718,0.368)--(0,0.368); \node[below] at (2.718,0){$e$}; \node[left] at (0,0.368){$\frac1e$};
\fill[cThm] (1,0) circle (2pt) node[below right]{$(1;0)$};''',(-0.4,8.3),(-1.4,0.8),x=0.85,y=2.6)
S.append(sess('28',r'دراسة دوال لوغاريتمية ، حل مشكلات',
[r'دراسة دالة ، التزايد المقارن.'],
[r'دراسة دالة لوغاريتمية وتوظيفها في حل مشكلات.'],TOOLS,
r'أيهما أكبر: $e^\pi$ أم $\pi^e$ ؟',
ACT('06')+r'\ $f(x)=\dfrac{\ln x}x$ على $]0;+\infty[$.'+Q(r'احسب نهايتي $f$ عند $0^+$ و $+\infty$.',r'احسب $f^{\prime}(x)$ وشكّل جدول التغيرات.')
+DIS()+QN(1,r'عند $0^+$: $\ln x\to-\infty$ و $\dfrac1x\to+\infty$: $\RR{\lim\limits_{x\to0^+}f(x)=-\infty}$ (مقارب عمودي $x=0$).')
+r'\par عند $+\infty$: $\RR{\lim\limits_{x\to+\infty}\dfrac{\ln x}x=0}$ (مقارب أفقي $y=0$).'
+QN(2,r'$f^{\prime}(x)=\dfrac{\frac1x\times x-\ln x}{x^2}=\RR{\dfrac{1-\ln x}{x^2}}$ ، موجبة إذا كان $x<e$:')
+VAR(['0','e',r'+\infty'],'f(x)',r'f^{\prime}(x)',['||','+','0','-',''],[r'-\infty',r'\frac1e','0'],['l','h','l']),
EX('المنحنى')+r'\ القيمة الحدية العظمى $f(e)=\dfrac1e$ ، والتقاطع مع محور الفواصل في $(1;0)$.'+G28
+EX('حل المشكلة')+Q(r'$\pi>e$ و $f$ متناقصة تمامًا على $[e;+\infty[$ ، إذن $f(\pi)<f(e)$: $\dfrac{\ln\pi}\pi<\dfrac1e$.',r'أي $e\ln\pi<\pi$ ، أي $\ln\left(\pi^e\right)<\ln\left(e^\pi\right)$ ، ومنه $\RR{\pi^e<e^\pi}$.')
+WARN()+r'\ لا ننسى مجموعة التعريف $]0;+\infty[$ عند دراسة دالة لوغاريتمية.',
TT()+r'\par $g(x)=x\ln x-x$ على $]0;+\infty[$.'+Q(r'احسب نهايتي $g$ عند $0^+$ و $+\infty$.',r'ادرس اتجاه تغير $g$.',r'حل المعادلة $g(x)=0$.')
+SOL()+Q(r'عند $0^+$: $x\ln x\to0$ و $x\to0$: $\RR{\lim\limits_{x\to0^+}g(x)=0}$.\par عند $+\infty$: $g(x)=x(\ln x-1)\to\RR{+\infty}$.',
   r'$g^{\prime}(x)=\ln x+x\times\dfrac1x-1=\RR{\ln x}$ ، موجبة إذا كان $x>1$:'
   +VAR(['0','1',r'+\infty'],'g(x)',r'g^{\prime}(x)',['||','-','0','+',''],['0','-1',r'+\infty'],['h','l','h']),
   r'$x(\ln x-1)=0$ و $x>0$ ، إذن $\ln x=1$: $\RR{S=\{e\}}$.')
+HW(r'مسائل من باب التزايد المقارن.'),
[r'لغز.',r'دراسة كاملة.',r'رسم المنحنى.',r'نهاية المحور: فرض أو مراجعة.']))
