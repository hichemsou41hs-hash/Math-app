UNIT='الأعداد المركبة والتحويلات النقطية'
FIELD='أعداد وحساب'
LEVEL='3 ع ت / 3 ر / 3 ت ر'
TOOLS=r'المنهاج ، الكتاب المدرسي (الجزء الثاني) ، الآلة الحاسبة ، أدوات الهندسة.'
S=[]
exec(open('/home/user/Math-app/documents/tools/gen_3as_explog/sess_post.py').read())
G67=GR(r'''\draw[cDef,thick,->] (0,0)--(2,3) node[above right]{$M(z)$};
\draw[dashed] (2,0)--(2,3)--(0,3); \node[below right] at (2,0){$x$}; \node[left] at (0,3){$y$};
\draw[cThm] (0.7,0) arc (0:56:0.7); \node[cThm] at (1,0.4){$\theta$};
\node[cDef] at (0.6,1.7){$|z|$};''',(-1,3.5),(-0.8,3.6),1,1,[1],[1])
G75=GR(r'''\draw[cDef,thick,fill=cDef!10] (1,0)--(3,1)--(2,3)--(0,2)--cycle;
\fill[cThm] (1,0) circle (1.5pt) node[below right]{$A(1)$}; \fill[cThm] (3,1) circle (1.5pt) node[right]{$B(3+i)$};
\fill[cThm] (2,3) circle (1.5pt) node[above]{$C(2+3i)$}; \fill[cThm] (0,2) circle (1.5pt) node[left]{$D(2i)$};
\draw[cThm,->] (1.5,0.25) arc (27:117:0.55);''',(-1.5,4),(-0.8,3.6),0.9,0.9,[2,3],[1,3])
# ---------------------------------------------------------------- 67
S.append(sess('67',r'مجموعة الأعداد المركبة: الشكل الجبري ، التمثيل ، العمليات',
[r'الأشعة والمعلم ، المعادلات من الدرجة الثانية في $\mathbb R$.'],
[r'التعرف على الرموز والاصطلاحات ، والتمثيل الهندسي لعدد مركب ، وإجراء العمليات الحسابية.'],TOOLS,
r'هل للمعادلة $x^2+1=0$ حلول في $\mathbb R$ ؟',
ACT('01')+r'\ نقبل وجود عدد $i$ حيث $i^2=-1$ ، ونحسب بنفس قواعد $\mathbb R$.'+Q(r'احسب $i^3$ ، $i^4$ ، $(1+i)^2$.',r'انشر $(2+3i)(1-i)$.',r'اكتب $\dfrac1{1+i}$ على الشكل $x+iy$.')
+DIS()+Q(r'$i^3=i^2\times i=\RR{-i}$ ؛ \quad $i^4=(i^2)^2=\RR{1}$ ؛ \quad $(1+i)^2=1+2i+i^2=\RR{2i}$.',r'$(2+3i)(1-i)=2-2i+3i-3i^2=2+i+3=\RR{5+i}$.',r'نضرب في $1-i$: $\dfrac{1-i}{(1+i)(1-i)}=\dfrac{1-i}{1-i^2}=\RR{\dfrac12-\dfrac12i}$.'),
DEF()+r'\ كل عدد مركب يكتب بطريقة وحيدة $\RR{z=x+iy}$ ($x,y\in\mathbb R$): $x=\mathrm{Re}(z)$ الجزء الحقيقي ، $y=\mathrm{Im}(z)$ الجزء التخيلي. $z$ حقيقي إذا كان $y=0$ ، وتخيلي صرف إذا كان $x=0$.'
+PRO()+Q(r'$x+iy=x^{\prime}+iy^{\prime}\iff x=x^{\prime}$ و $y=y^{\prime}$.',r'$i^{4k}=1$ ، $i^{4k+1}=i$ ، $i^{4k+2}=-1$ ، $i^{4k+3}=-i$.')
+DEF('التمثيل الهندسي')+r'\ في معلم متعامد ومتجانس $(O;\vec u,\vec v)$ نرفق بـ $z=x+iy$ النقطة $M(x;y)$ والشعاع $\overrightarrow{OM}$: $z$ \textbf{لاحقة} $M$.'+G67
+EX('أمثلة محلولة')+Q(r'$i^{2026}$: $2026=4\times506+2$ ، إذن $i^{2026}=\RR{-1}$.',r'$\dfrac{2+i}{1-i}=\dfrac{(2+i)(1+i)}{2}=\dfrac{2+3i+i^2}2=\RR{\dfrac12+\dfrac32i}$.')
+WARN()+r'\ لا ترتيب في $\mathbb C$: لا نكتب $z>z^{\prime}$.',
TT()+Q(r'اكتب على الشكل الجبري: $z=\dfrac{3-i}{1+2i}$.',r'عيّن العدد الحقيقي $m$ حتى يكون $(m+i)(1+i)$ تخيليًا صرفًا.')
+SOL()+Q(r'$z=\dfrac{(3-i)(1-2i)}{1+4}=\dfrac{3-6i-i+2i^2}{5}=\RR{\dfrac15-\dfrac75i}$.',r'$(m+i)(1+i)=(m-1)+i(m+1)$: تخيلي صرف إذا كان $m-1=0$ ، أي $\RR{m=1}$.')
+HW(r'تمارين من باب الأعداد المركبة.'),
[r'سؤال تاريخي.',r'تمديد الحساب.',r'المستوي المركب.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 68
S.append(sess('68',r'مرافق عدد مركب وخواصه',
[r'الشكل الجبري.'],
[r'استعمال خواص المرافق ، وحل معادلات تتضمن $\overline z$.'],TOOLS,
r'ما نظيرة النقطة $M(z)$ بالنسبة إلى محور الفواصل؟',
ACT('02')+r'\ $z=x+iy$.'+Q(r'ما لاحقة نظيرة $M(z)$ بالنسبة إلى محور الفواصل؟',r'احسب $z+\overline z$ ، $z-\overline z$ ، $z\overline z$ حيث $\overline z=x-iy$.')
+DIS()+Q(r'النظيرة $M^{\prime}(x;-y)$ لاحقتها $\RR{x-iy}$: نسميها \textbf{مرافق} $z$.',r'$z+\overline z=\RR{2x}$ ؛ \quad $z-\overline z=\RR{2iy}$ ؛ \quad $z\overline z=x^2-(iy)^2=\RR{x^2+y^2}$.'),
DEF()+r'\ مرافق $z=x+iy$ هو $\RR{\overline z=x-iy}$.'
+PRO()+Q(r'$z+\overline z=2\,\mathrm{Re}(z)$ ، $z-\overline z=2i\,\mathrm{Im}(z)$ ، $z\overline z=x^2+y^2$.',r'$\overline{z+z^{\prime}}=\overline z+\overline{z^{\prime}}$ ، $\overline{zz^{\prime}}=\overline z\,\overline{z^{\prime}}$ ، $\overline{z^n}=\overline z^{\,n}$ ، $\overline{\left(\dfrac z{z^{\prime}}\right)}=\dfrac{\overline z}{\overline{z^{\prime}}}$.',r'$z$ حقيقي إذا وفقط إذا كان $z=\overline z$ ؛ \quad $z$ تخيلي صرف إذا وفقط إذا كان $z=-\overline z$.')
+EX('أمثلة محلولة')+Q(r'حل $2z+i\overline z=3$: نضع $z=x+iy$: $2x+2iy+ix+y=3$.',r'$(2x+y)+i(x+2y)=3$: $2x+y=3$ و $x+2y=0$ ، إذن $x=2$ ، $y=-1$: $\RR{z=2-i}$.',r'$Z=z^2+\overline z^{\,2}$: $\overline Z=\overline z^{\,2}+z^2=Z$ ، إذن $Z$ \RR{حقيقي}.')
+WARN()+r'\ في معادلة فيها $z$ و $\overline z$ نضع $z=x+iy$ ونطابق الجزأين الحقيقي والتخيلي.',
TT()+Q(r'حل في $\mathbb C$: $z+2\overline z=6-i$.')
+SOL()+Q(r'$x+iy+2x-2iy=3x-iy=6-i$.',r'$3x=6$ و $-y=-1$: $\RR{z=2+i}$.')
+HW(r'تمارين من باب الأعداد المركبة.'),
[r'سؤال هندسي.',r'الخواص في جدول.',r'المطابقة.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 69
S.append(sess('69',r'طويلة عدد مركب وتفسيرها الهندسي',
[r'المرافق ، المسافة في معلم.'],
[r'حساب طويلة عدد مركب ، وتوظيفها في حساب مسافات وتعيين مجموعات نقط.'],TOOLS,
r'ما المسافة $OM$ حيث $M(3;4)$ ؟',
ACT('03')+Q(r'احسب $OM$ حيث $M$ لاحقتها $z=3+4i$ ، وقارنها بـ $\sqrt{z\overline z}$.',r'$A(z_A)$ و $B(z_B)$: عبّر عن $AB$ بدلالة $z_B-z_A$.')
+DIS()+Q(r'$OM=\sqrt{9+16}=\RR{5}$ و $z\overline z=25$: $\RR{OM=\sqrt{z\overline z}}$.',r'$\overrightarrow{AB}$ لاحقته $z_B-z_A$: $\RR{AB=|z_B-z_A|}$.'),
DEF()+r'\ طويلة $z=x+iy$: $\RR{|z|=\sqrt{x^2+y^2}=\sqrt{z\overline z}}$.'
+PRO()+Q(r'$|zz^{\prime}|=|z|\,|z^{\prime}|$ ، $\left|\dfrac z{z^{\prime}}\right|=\dfrac{|z|}{|z^{\prime}|}$ ، $|z^n|=|z|^n$ ، $|\overline z|=|z|$.',r'$\RR{AB=|z_B-z_A|}$.')
+MET('مجموعات نقط')+Q(r'$|z-z_A|=r$ ($r>0$): \RR{دائرة} مركزها $A$ ونصف قطرها $r$.',r'$|z-z_A|=|z-z_B|$: \RR{محور} القطعة $[AB]$.')
+EX('أمثلة محلولة')+Q(r'$|1+i\sqrt3|=\sqrt{1+3}=\RR{2}$ ؛ \quad $|(1+i)(3-4i)|=\sqrt2\times5=\RR{5\sqrt2}$.',r'$|z-1|=|z+i|$: $AM=BM$ مع $A(1)$ و $B(-i)$: \RR{محور القطعة $[AB]$}.')
+WARN()+r'\ $|z+z^{\prime}|\neq|z|+|z^{\prime}|$ عمومًا.',
TT()+Q(r'عيّن مجموعة النقط $M(z)$ حيث $|z-2i|=3$.',r'احسب $\left|\dfrac{1+i}{\sqrt3-i}\right|$.')
+SOL()+Q(r'$AM=3$ مع $A(2i)$: \RR{دائرة مركزها $A(0;2)$ ونصف قطرها $3$}.',r'$\dfrac{|1+i|}{|\sqrt3-i|}=\RR{\dfrac{\sqrt2}2}$.')
+HW(r'تمارين من باب الأعداد المركبة.'),
[r'سؤال.',r'تفسير هندسي.',r'رسم المجموعات.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 70
S.append(sess('70',r'المعادلات من الدرجة الثانية في $\mathbb C$ ، الجذران التربيعيان',
[r'المميز ، الشكل الجبري ، المرافق.'],
[r'حل معادلات من الدرجة الثانية بمعاملات حقيقية ومعادلات تؤول إليها ، وتعيين الجذرين التربيعيين لعدد مركب (علوم تجريبية).'],TOOLS,
r'$z^2-2z+5=0$: $\Delta=-16<0$. هل انتهى الأمر في $\mathbb C$ ؟',
ACT('04')+Q(r'اكتب $-16$ على الشكل $(\delta)^2$ في $\mathbb C$.',r'حل $z^2-2z+5=0$ بنفس دساتير $\mathbb R$.')
+DIS()+Q(r'$-16=16i^2=\RR{(4i)^2}$.',r'$z=\dfrac{2\pm4i}2=\RR{1\pm2i}$ (حلان مترافقان).'),
PRO()+r'\ $az^2+bz+c=0$ ($a,b,c$ حقيقية ، $a\neq0$) ، $\Delta=b^2-4ac$:'+Q(r'$\Delta\geqslant0$: حلول حقيقية كما في $\mathbb R$.',r'$\Delta<0$: حلان مترافقان $\RR{z=\dfrac{-b\pm i\sqrt{-\Delta}}{2a}}$.')
+EX('أمثلة محلولة')+Q(r'$z^2+z+1=0$: $\Delta=-3$ ، $\RR{z=\dfrac{-1\pm i\sqrt3}2}$.',r'$z^3-1=0$: $(z-1)(z^2+z+1)=0$: $\RR{z\in\left\{1;\dfrac{-1+i\sqrt3}2;\dfrac{-1-i\sqrt3}2\right\}}$.')
+MET('الجذران التربيعيان (علوم تجريبية)')+r'\ لـ $3+4i$: نبحث عن $(x+iy)^2=3+4i$:'
+Q(r'$x^2-y^2=3$ ، $2xy=4$ ، و $x^2+y^2=|3+4i|=5$.',r'$x^2=4$ ، $y^2=1$ ، و $xy>0$: الجذران $\RR{2+i}$ و $\RR{-2-i}$ (تحقق: $(2+i)^2=3+4i$ \ck).')
+WARN()+r'\ لا نكتب $\sqrt{-16}$ ؛ نكتب $-16=(4i)^2$.',
TT()+Q(r'حل في $\mathbb C$: $z^2-6z+13=0$.',r'حل في $\mathbb C$: $(z^2+4)(z^2-2z+2)=0$.')
+SOL()+Q(r'$\Delta=36-52=-16$: $z=\dfrac{6\pm4i}2=\RR{3\pm2i}$.',r'$z^2=-4=(2i)^2$: $z=\pm2i$ ؛ $\Delta=-4$: $z=1\pm i$: $\RR{\{2i;-2i;1+i;1-i\}}$.')
+HW(r'تمارين من باب الأعداد المركبة.'),
[r'سؤال.',r'تمديد المميز.',r'جذور مترافقة.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 71
S.append(sess('71',r'عمدة عدد مركب ، الشكل المثلثي',
[r'الطويلة ، الزوايا الموجهة ، الدائرة المثلثية.'],
[r'حساب عمدة عدد مركب غير معدوم ، والانتقال من الشكل الجبري إلى المثلثي والعكس.'],TOOLS,
r'ما قيس الزاوية بين $\vec u$ و $\overrightarrow{OM}$ حيث $M(1;1)$ ؟',
ACT('05')+r'\ $z=1+i$.'+Q(r'احسب $|z|$.',r'احسب $\dfrac{x}{|z|}$ و $\dfrac{y}{|z|}$ ، واستنتج قيسًا $\theta$ للزاوية $(\vec u;\overrightarrow{OM})$.')
+DIS()+Q(r'$|z|=\RR{\sqrt2}$.',r'$\cos\theta=\dfrac1{\sqrt2}=\dfrac{\sqrt2}2$ و $\sin\theta=\dfrac{\sqrt2}2$: $\RR{\theta=\dfrac\pi4}$ ، و $z=\sqrt2\left(\cos\dfrac\pi4+i\sin\dfrac\pi4\right)$.'),
DEF()+r'\ عمدة $z\neq0$: قيس $\theta$ للزاوية $(\vec u;\overrightarrow{OM})$ ، ونكتب $\arg z=\theta\ [2\pi]$. الشكل المثلثي: $\RR{z=r(\cos\theta+i\sin\theta)}$ حيث $r=|z|$ ، $\cos\theta=\dfrac xr$ ، $\sin\theta=\dfrac yr$.'
+PRO()+Q(r'$\arg(zz^{\prime})=\arg z+\arg z^{\prime}$ ؛ \quad $\arg\dfrac z{z^{\prime}}=\arg z-\arg z^{\prime}$ ؛ \quad $\arg z^n=n\arg z$.',r'$\arg\overline z=-\arg z$ ؛ \quad $\arg(-z)=\arg z+\pi$ \quad $[2\pi]$.')
+EX('أمثلة محلولة')+Q(r'$1+i\sqrt3$: $r=2$ ، $\cos\theta=\dfrac12$ ، $\sin\theta=\dfrac{\sqrt3}2$: $\RR{2\left(\cos\dfrac\pi3+i\sin\dfrac\pi3\right)}$.',r'$-1+i$: $r=\sqrt2$ ، $\cos\theta=-\dfrac{\sqrt2}2$ ، $\sin\theta=\dfrac{\sqrt2}2$: $\RR{\sqrt2\left(\cos\dfrac{3\pi}4+i\sin\dfrac{3\pi}4\right)}$.')
+WARN()+r'\ نحدد الربع من إشارتي $\cos\theta$ و $\sin\theta$ معًا ، و $r>0$ دائمًا.',
TT()+Q(r'اكتب $z=-\sqrt3-i$ على الشكل المثلثي.',r'استنتج عمدة لـ $z^2$.')
+SOL()+Q(r'$r=2$ ، $\cos\theta=-\dfrac{\sqrt3}2$ ، $\sin\theta=-\dfrac12$: $\RR{\theta=-\dfrac{5\pi}6}$.',r'$\arg z^2=2\times\left(-\dfrac{5\pi}6\right)=-\dfrac{5\pi}3\equiv\RR{\dfrac\pi3}\ [2\pi]$.')
+HW(r'تمارين من باب الأعداد المركبة.'),
[r'سؤال.',r'الدائرة المثلثية.',r'الزوايا الشهيرة.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 72
S.append(sess('72',r'الشكل الأسي ، ترميز أولر ، دستور موافر',
[r'الشكل المثلثي ، خواص العمدة.'],
[r'الانتقال من الشكل الجبري إلى الأسي والعكس ، واستعمال دستور موافر.'],TOOLS,
r'كيف نحسب $(1+i)^8$ بسرعة؟',
ACT('06')+r'\ نضع $f(\theta)=\cos\theta+i\sin\theta$.'+Q(r'احسب $f(\theta)\times f(\theta^{\prime})$ وبسّط.',r'ماذا تذكرك هذه القاعدة؟')
+DIS()+Q(r'$f(\theta)f(\theta^{\prime})=\cos\theta\cos\theta^{\prime}-\sin\theta\sin\theta^{\prime}+i(\sin\theta\cos\theta^{\prime}+\cos\theta\sin\theta^{\prime})=\RR{f(\theta+\theta^{\prime})}$.',r'نفس قاعدة الأسس $e^ae^b=e^{a+b}$: نكتب $\RR{f(\theta)=e^{i\theta}}$ (ترميز أولر).'),
DEF()+r'\ $e^{i\theta}=\cos\theta+i\sin\theta$ ؛ الشكل الأسي لـ $z\neq0$: $\RR{z=re^{i\theta}}$ ($r=|z|$ ، $\theta=\arg z$).'
+PRO()+Q(r'$re^{i\theta}\times r^{\prime}e^{i\theta^{\prime}}=rr^{\prime}e^{i(\theta+\theta^{\prime})}$ ؛ \quad $\dfrac{re^{i\theta}}{r^{\prime}e^{i\theta^{\prime}}}=\dfrac r{r^{\prime}}e^{i(\theta-\theta^{\prime})}$.',r'$\left(re^{i\theta}\right)^n=r^ne^{in\theta}$ ؛ \quad $\overline{e^{i\theta}}=e^{-i\theta}$.')
+PRO('دستور موافر')+r'\ $\RR{(\cos\theta+i\sin\theta)^n=\cos n\theta+i\sin n\theta}$.'
+EX('أمثلة محلولة')+Q(r'$(1+i)^8=\left(\sqrt2e^{i\frac\pi4}\right)^8=16e^{2i\pi}=\RR{16}$.',r'$\dfrac{1+i}{1-i}=\dfrac{\sqrt2e^{i\frac\pi4}}{\sqrt2e^{-i\frac\pi4}}=e^{i\frac\pi2}=\RR{i}$.',r'من $(\cos\theta+i\sin\theta)^2=\cos2\theta+i\sin2\theta$: $\RR{\cos2\theta=\cos^2\theta-\sin^2\theta}$ و $\RR{\sin2\theta=2\sin\theta\cos\theta}$.')
+WARN()+r'\ $r>0$ في الشكل الأسي: $-2e^{i\frac\pi3}=2e^{i\frac{4\pi}3}$.',
TT()+Q(r'احسب $(1+i\sqrt3)^6$.',r'اكتب $z=\dfrac{(1+i)^4}{(\sqrt3+i)^2}$ على الشكل الأسي.')
+SOL()+Q(r'$\left(2e^{i\frac\pi3}\right)^6=64e^{2i\pi}=\RR{64}$.',r'$\dfrac{\left(\sqrt2e^{i\frac\pi4}\right)^4}{\left(2e^{i\frac\pi6}\right)^2}=\dfrac{4e^{i\pi}}{4e^{i\frac\pi3}}=\RR{e^{i\frac{2\pi}3}}$.')
+HW(r'تمارين من باب الأعداد المركبة.'),
[r'تحدٍّ.',r'ترميز أولر.',r'دستور موافر.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 73
S.append(sess('73',r'توظيف الطويلة والعمدة في الهندسة',
[r'الطويلة والعمدة ، الزوايا الموجهة.'],
[r'التعبير عن خواص أشكال هندسية بالأعداد المركبة ، وتوظيف خواص الطويلة والعمدة لحل مسائل.'],TOOLS,
r'كيف نبرهن بالأعداد المركبة أن مثلثًا متقايس الأضلاع؟',
ACT('07')+r'\ $A$ ، $B$ ، $C$ نقط متمايزة.'+Q(r'ما طويلة $\dfrac{z_C-z_A}{z_B-z_A}$ ؟',r'ما عمدته؟')
+DIS()+Q(r'$\left|\dfrac{z_C-z_A}{z_B-z_A}\right|=\RR{\dfrac{AC}{AB}}$.',r'$\arg\dfrac{z_C-z_A}{z_B-z_A}=\arg(z_C-z_A)-\arg(z_B-z_A)=\RR{(\overrightarrow{AB};\overrightarrow{AC})}\ [2\pi]$.'),
PRO()+r'\ $\RR{\left|\dfrac{z_C-z_A}{z_B-z_A}\right|=\dfrac{AC}{AB}}$ و $\RR{\arg\dfrac{z_C-z_A}{z_B-z_A}=(\overrightarrow{AB};\overrightarrow{AC})}\ [2\pi]$.'
+MET('طبيعة مثلث')+Q(r'النسبة $=e^{\pm i\frac\pi3}$: مثلث \RR{متقايس الأضلاع}.',r'النسبة $=\pm i$: مثلث \RR{قائم ومتساوي الساقين} في $A$.',r'النسبة حقيقية: النقط \RR{على استقامة واحدة}.',r'النسبة تخيلية صرفة: المثلث \RR{قائم} في $A$.')
+EX('أمثلة محلولة')+Q(r'$A(0)$ ، $B(2)$ ، $C(1+i\sqrt3)$: $\dfrac{z_C-z_A}{z_B-z_A}=\dfrac{1+i\sqrt3}2=e^{i\frac\pi3}$: \RR{متقايس الأضلاع}.',r'$A(1)$ ، $B(2+i)$ ، $C(4+3i)$: $\dfrac{z_C-z_A}{z_B-z_A}=\dfrac{3+3i}{1+i}=3$ حقيقي: \RR{على استقامة واحدة}.')
+WARN()+r'\ ترتيب النقط في النسبة يحدد الزاوية: $\dfrac{z_C-z_A}{z_B-z_A}$ تعطي $(\overrightarrow{AB};\overrightarrow{AC})$.',
TT()+r'\par $A(1+i)$ ، $B(3+2i)$ ، $C(3i)$.'+Q(r'احسب $\dfrac{z_C-z_A}{z_B-z_A}$.',r'استنتج طبيعة المثلث $ABC$.')
+SOL()+Q(r'$\dfrac{-1+2i}{2+i}=\dfrac{(-1+2i)(2-i)}{5}=\dfrac{-2+i+4i+2}{5}=\RR{i}$.',r'$AC=AB$ و $(\overrightarrow{AB};\overrightarrow{AC})=\dfrac\pi2$: \RR{قائم ومتساوي الساقين في $A$}.')
+HW(r'تمارين من باب الأعداد المركبة.'),
[r'سؤال.',r'تفسير النسبة.',r'جدول الحالات.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 74
S.append(sess('74',r'الكتابة المركبة للتحويلات: الانسحاب ، التحاكي ، الدوران',
[r'التحويلات النقطية (السنة الثانية) ، الشكل الأسي.'],
[r'تعيين الكتابة المركبة لتحويل ، والتعرف على تحويل من كتابته المركبة.'],TOOLS,
r'ما الذي يفعله الضرب في $i$ بنقطة من المستوي؟',
ACT('08')+r'\ $z^{\prime}=iz$.'+Q(r'قارن $|z^{\prime}|$ و $|z|$.',r'قارن $\arg z^{\prime}$ و $\arg z$ ، واستنتج طبيعة التحويل.')
+DIS()+Q(r'$|z^{\prime}|=|i||z|=\RR{|z|}$: $OM^{\prime}=OM$.',r'$\arg z^{\prime}=\arg z+\dfrac\pi2$: \RR{دوران مركزه $O$ وزاويته $\frac\pi2$}.'),
PRO('الكتابات المركبة')+Q(r'انسحاب شعاعه $\vec w(b)$: $\RR{z^{\prime}=z+b}$.',r'تحاكٍ مركزه $\Omega(\omega)$ ونسبته $k$: $\RR{z^{\prime}-\omega=k(z-\omega)}$.',r'دوران مركزه $\Omega(\omega)$ وزاويته $\theta$: $\RR{z^{\prime}-\omega=e^{i\theta}(z-\omega)}$.')
+MET('التعرف على $z^{\prime}=az+b$')+Q(r'$a=1$: انسحاب ؛ $a$ حقيقي يختلف عن $1$: تحاكٍ نسبته $a$ ؛ $|a|=1$ و $a\neq1$: دوران زاويته $\arg a$.',r'المركز: النقطة الصامدة $\omega=a\omega+b$ ، أي $\omega=\dfrac b{1-a}$.')
+EX('أمثلة محلولة')+Q(r'$z^{\prime}=iz+1+i$: $|i|=1$ ، $\arg i=\dfrac\pi2$: دوران.',r'$\omega=\dfrac{1+i}{1-i}=\RR{i}$: \RR{دوران مركزه $\Omega(i)$ وزاويته $\frac\pi2$}.',r'$z^{\prime}=z+2-i$: \RR{انسحاب شعاعه $\vec w(2-i)$}.')
+WARN()+r'\ في الدوران نكتب $z^{\prime}-\omega=e^{i\theta}(z-\omega)$ وليس $z^{\prime}=e^{i\theta}z$ (إلا إذا كان المركز $O$).',
TT()+Q(r'تعرّف على التحويل $z^{\prime}=-2z+3$.',r'اكتب الكتابة المركبة للدوران الذي مركزه $\Omega(1)$ وزاويته $\dfrac\pi2$.')
+SOL()+Q(r'$a=-2$ حقيقي: تحاكٍ نسبته $-2$ ؛ $\omega=\dfrac3{1+2}=1$: \RR{تحاكٍ مركزه $\Omega(1)$ ونسبته $-2$}.',r'$z^{\prime}-1=i(z-1)$ ، أي $\RR{z^{\prime}=iz+1-i}$.')
+HW(r'تمارين من باب الأعداد المركبة.'),
[r'سؤال.',r'تفسير الضرب.',r'جدول الكتابات.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 75
S.append(sess('75',r'حل مسائل هندسية بالتحويلات والأعداد المركبة',
[r'الكتابة المركبة للتحويلات.'],
[r'حل مسائل هندسية باستعمال الانسحابات والتحاكيات والدورانات.'],TOOLS,
r'نعرف رأسين متتاليين لمربع: كيف نحسب الرأسين الآخرين؟',
ACT('09')+r'\ $ABCD$ مربع مباشر ، $A(1)$ ، $B(3+i)$.'+Q(r'$D$ صورة $B$ بأي دوران؟ احسب $z_D$.',r'احسب $z_C$ (متوازي أضلاع).')
+DIS()+Q(r'الدوران الذي مركزه $A$ وزاويته $\dfrac\pi2$: $z_D=z_A+i(z_B-z_A)=1+i(2+i)=\RR{2i}$.',r'$\overrightarrow{DC}=\overrightarrow{AB}$: $z_C=z_D+z_B-z_A=2i+2+i=\RR{2+3i}$.')
+G75,
MET()+Q(r'نترجم الوضعية الهندسية إلى تحويل (دوران ، تحاكٍ ، انسحاب).',r'نكتب كتابته المركبة ، ثم نحسب اللواحق.')
+EX('أمثلة محلولة')+Q(r'مثلث متقايس الأضلاع مباشر $ABC$ مع $A(0)$ ، $B(2)$: $z_C=e^{i\frac\pi3}z_B=2\left(\dfrac12+i\dfrac{\sqrt3}2\right)=\RR{1+i\sqrt3}$.',r'صورة $M(2+i)$ بالتحاكي الذي مركزه $O$ ونسبته $3$: $\RR{6+3i}$.')
+WARN()+r'\ نراعي الاتجاه: مباشر (زاوية $+\frac\pi2$) أو غير مباشر ($-\frac\pi2$).',
TT()+r'\par $A(i)$ ، $B(2+i)$.'+Q(r'عيّن لاحقة $C$ حيث $ABC$ قائم ومتساوي الساقين في $A$ ومباشر.')
+SOL()+Q(r'$z_C=z_A+i(z_B-z_A)=i+i\times2=\RR{3i}$.')
+HW(r'تمارين من باب الأعداد المركبة.'),
[r'سؤال.',r'ترجمة هندسية.',r'رسم الشكل.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 76
S.append(sess('76',r'التشابه المباشر: تعريف ، كتابته المركبة ، عناصره',
[r'التحويلات المألوفة وكتاباتها المركبة.'],
[r'التعرف على التشابه المباشر وتعيين عناصره المميزة.'],TOOLS,
r'ما التحويل الذي يكبّر ويدير في آن واحد؟',
ACT('10')+r'\ $z^{\prime}=(1+i)z$.'+Q(r'قارن $|z^{\prime}|$ بـ $|z|$ ، و $\arg z^{\prime}$ بـ $\arg z$.',r'صف التحويل.')
+DIS()+Q(r'$|z^{\prime}|=\sqrt2|z|$ ؛ \quad $\arg z^{\prime}=\arg z+\dfrac\pi4$.',r'تكبير بالنسبة $\sqrt2$ ودوران بـ $\dfrac\pi4$ حول $O$: \RR{تشابه مباشر}.'),
DEF()+r'\ \textbf{التشابه المباشر} تحويل كتابته المركبة $\RR{z^{\prime}=az+b}$ مع $a\in\mathbb C^*$.'
+PRO('العناصر المميزة ($a\neq1$)')+Q(r'النسبة $\RR{k=|a|}$ ، الزاوية $\RR{\theta=\arg a}$ ، المركز $\RR{\omega=\dfrac b{1-a}}$.',r'الانسحابات والدورانات والتحاكيات حالات خاصة ، والتشابه الذي نسبته $1$ \textbf{تقايس}.')
+EX('أمثلة محلولة')+Q(r'$z^{\prime}=(1+i)z+2$: $k=\RR{\sqrt2}$ ، $\theta=\RR{\dfrac\pi4}$ ، $\omega=\dfrac2{-i}=\RR{2i}$.',r'$z^{\prime}=-3iz$: $k=\RR{3}$ ، $\theta=\RR{-\dfrac\pi2}$ ، المركز $\RR{O}$.')
+WARN()+r'\ إذا كان $a=1$ فهو انسحاب (لا مركز له).',
TT()+Q(r'عيّن عناصر التشابه $z^{\prime}=(1+i\sqrt3)z-i\sqrt3$.')
+SOL()+Q(r'$k=|1+i\sqrt3|=\RR{2}$ ؛ \quad $\theta=\RR{\dfrac\pi3}$.',r'$\omega=\dfrac{-i\sqrt3}{1-1-i\sqrt3}=\RR{1}$.')
+HW(r'تمارين من باب التشابهات.'),
[r'سؤال.',r'مثال بالضرب.',r'جدول العناصر.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 77
S.append(sess('77',r'التحليل القانوني لتشابه مباشر ، مركب تشابهين',
[r'التشابه المباشر وعناصره.'],
[r'تعيين التحليل القانوني لتشابه مباشر ، وتعيين مركب تشابهين.'],TOOLS,
r'هل يمكن كتابة تشابه كتركيب تحويلين أبسط؟',
ACT('11')+r'\ $s$: $z^{\prime}-\omega=ke^{i\theta}(z-\omega)$.'+Q(r'$r$: $z_1-\omega=e^{i\theta}(z-\omega)$ و $h$: $z^{\prime}-\omega=k(z_1-\omega)$. احسب $h\circ r$.',r'هل $r\circ h=h\circ r$ ؟')
+DIS()+Q(r'$z^{\prime}-\omega=k\,e^{i\theta}(z-\omega)$: $\RR{h\circ r=s}$.',r'$ke^{i\theta}=e^{i\theta}k$: \RR{نعم} ، الترتيب لا يهم لأن لهما نفس المركز.'),
PRO('التحليل القانوني')+r'\ التشابه $s$ الذي مركزه $\Omega$ ونسبته $k$ وزاويته $\theta$: $\RR{s=h\circ r=r\circ h}$ حيث $h$ التحاكي $(\Omega;k)$ و $r$ الدوران $(\Omega;\theta)$.'
+PRO('مركب تشابهين')+r'\ مركب تشابهين مباشرين تشابه مباشر: \RR{النسبة جداء النسبتين} و\RR{الزاوية مجموع الزاويتين}.'
+EX('أمثلة محلولة')+Q(r'$s_1$: $z^{\prime}=2z+1$ ، $s_2$: $z^{\prime}=iz$: $s_2\circ s_1$: $z^{\prime\prime}=i(2z+1)=\RR{2iz+i}$.',r'نسبته $\RR{2}$ ، زاويته $\RR{\dfrac\pi2}$ ، مركزه $\omega=\dfrac i{1-2i}=\RR{\dfrac{-2+i}5}$.')
+WARN()+r'\ عمومًا $s_2\circ s_1\neq s_1\circ s_2$: $s_1\circ s_2$: $z^{\prime\prime}=2iz+1$.',
TT()+Q(r'$s$: $z^{\prime}=(1+i)z$. عيّن $s\circ s$ وعناصره.')
+SOL()+Q(r'$z^{\prime\prime}=(1+i)^2z=\RR{2iz}$: نسبته $\RR{2}$ ، زاويته $\RR{\dfrac\pi2}$ ، مركزه $\RR{O}$.')
+HW(r'تمارين من باب التشابهات.'),
[r'سؤال.',r'التحليل.',r'جدول المركب.',r'تقويم فردي.']))
# ---------------------------------------------------------------- 78
S.append(sess('78',r'خواص التشابه المباشر وحل مسائل',
[r'التشابه المباشر ، التحليل القانوني.'],
[r'توظيف خواص التشابه لحل مسائل هندسية ، وتعيين تشابه يحول نقطتين إلى نقطتين.'],TOOLS,
r'كم تشابهًا مباشرًا يحول $A$ إلى $A^{\prime}$ و $B$ إلى $B^{\prime}$ ؟',
ACT('12')+r'\ $A(0)\mapsto A^{\prime}(1)$ ، $B(1)\mapsto B^{\prime}(1+i)$.'+Q(r'اكتب الجملة التي يحققها $a$ و $b$ في $z^{\prime}=az+b$.',r'حلها وعيّن عناصر التشابه.')
+DIS()+Q(r'$b=1$ و $a+b=1+i$.',r'$\RR{a=i}$ ، $\RR{b=1}$: $z^{\prime}=iz+1$: دوران زاويته $\dfrac\pi2$ ومركزه $\omega=\dfrac1{1-i}=\RR{\dfrac{1+i}2}$.'),
PRO()+Q(r'التشابه المباشر يحافظ على \RR{نسب المسافات والزوايا الموجهة} والاستقامية والتوازي.',r'من أجل $A\neq B$ و $A^{\prime}\neq B^{\prime}$ يوجد تشابه مباشر وحيد: $\RR{a=\dfrac{z_{B^{\prime}}-z_{A^{\prime}}}{z_B-z_A}}$ ، $\RR{b=z_{A^{\prime}}-az_A}$.',r'صورة دائرة مركزها $\Omega$ ونصف قطرها $R$: دائرة مركزها $s(\Omega)$ ونصف قطرها $kR$.')
+EX('مثال محلول')+r'\ $s$: $z^{\prime}=2iz-i$ ، والدائرة $(\mathcal C)$: مركزها $\Omega(1)$ ونصف قطرها $1$.'
+Q(r'$s(\Omega)$: $2i\times1-i=\RR{i}$ ؛ \quad $k=|2i|=2$.',r'صورة $(\mathcal C)$: \RR{دائرة مركزها $(0;1)$ ونصف قطرها $2$}.')
+WARN()+r'\ صورة دائرة دائرة: نحول المركز ونضرب نصف القطر في $k$.',
TT()+Q(r'عيّن التشابه الذي يحول $A(1)$ إلى $A^{\prime}(i)$ و $B(2)$ إلى $B^{\prime}(3i)$.',r'عيّن عناصره.')
+SOL()+Q(r'$a=\dfrac{3i-i}{2-1}=\RR{2i}$ ؛ \quad $b=i-2i\times1=\RR{-i}$: $z^{\prime}=2iz-i$.',r'$k=\RR{2}$ ، $\theta=\RR{\dfrac\pi2}$ ، $\omega=\dfrac{-i}{1-2i}=\RR{\dfrac{2-i}5}$.')
+HW(r'مسائل من باب التشابهات.'),
[r'سؤال.',r'جملة معادلتين.',r'رسم الصور.',r'نهاية المحور: فرض أو مراجعة.']))
S=post(S,('تعريف','خاصية','طريقة','التمثيل','دستور','الكتابات','التعرف','العناصر','التحليل','مركب','طبيعة','مجموعات','الجذران'))
