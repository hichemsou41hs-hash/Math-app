# Builds the body of documents/ln/molakhas_ln_3as.tex (rich summary, relative-position tables in the teacher's model)
import re
exec(open('/home/user/Math-app/documents/tools/vtab.py').read())
M, P = r'-\infty', r'+\infty'
SG = lambda xs, rows: (r'\begin{TAB}' + '\n' + r'\tkzTabInit[lgt=2.6,espcl=2.4]{$x$/1,' +
                       ','.join('$%s$/1' % r for r, _ in rows) + '}{' + ','.join('$%s$' % x for x in xs) + '}\n' +
                       ''.join(r'\tkzTabLine{%s}' % l + '\n' for _, l in rows) + r'\end{TAB}')
B = []
B.append(r'''\begin{document}
\begin{LTR}
\begin{tcolorbox}[enhanced,colback=cSec,colframe=cSec,arc=3mm,halign=center,boxrule=0pt,top=12pt,bottom=12pt,before upper={\selectlanguage{arabic}}]
{\color{white}\fontsize{28}{34}\selectfont\bfseries الدالة اللوغاريتمية النيبيرية}\\[8pt]
{\color{white}\large ملخص شامل: كل عنصر بأمثلة محلولة خطوة بخطوة ، وتمارين من نمط البكالوريا}\\[5pt]
{\color{white}\large السنة الثالثة ثانوي -- الشعب العلمية}
\end{tcolorbox}
\end{LTR}

\begin{BOX}{cSec}{محتوى الملخص}
\begin{multicols}{2}
\begin{enumerate}[label=\arabic*.]
\item التعريف ونتائجه المباشرة
\item مجموعة التعريف
\item الخواص الجبرية
\item إشارة عبارات لوغاريتمية
\item المعادلات
\item المتراجحات
\item النهايات والنهايات الشهيرة
\item الاشتقاق والدالة $\ln u$
\item دراسة الدالة $\ln$ والوضع النسبي
\item دالتان مرجعيتان
\item اللوغاريتم العشري
\item تمارين محلولة (نمط البكالوريا)
\item أخطاء شائعة وخلاصة الطرائق
\end{enumerate}
\end{multicols}
\end{BOX}
''')
# 1 ------------------------------------------------------------------
B.append(r'''\section{التعريف ونتائجه المباشرة}
\begin{tarif}
الدالة الأسية مستمرة ومتزايدة تمامًا على $\R$ وتأخذ قيمها في $]0;+\infty[$؛ إذن من أجل كل عدد حقيقي $x>0$ يوجد عدد حقيقي وحيد $y$ يحقق $e^{y}=x$ ، نسميه \textbf{اللوغاريتم النيبيري} للعدد $x$ ونرمز له $\ln x$:
\[ \bx{y=\ln x \iff x=e^{y}}\qquad (x>0,\ y\in\R) \]
الدالة $\ln$ معرفة على $]0;+\infty[$ فقط.
\end{tarif}

\begin{khassia}[نتائج مباشرة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $\ln 1=0$ لأن $e^{0}=1$ ؛ و $\ln e=1$ لأن $e^{1}=e$.
\item من أجل كل $x>0$: $e^{\ln x}=x$ ؛ ومن أجل كل $y\in\R$: $\ln\left(e^{y}\right)=y$.
\item الدالتان $\ln$ و $\exp$ متعاكستان: منحنياهما متناظران بالنسبة إلى المستقيم $y=x$.
\end{enumerate}
\end{khassia}

\begin{mithal}[أمثلة محلولة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $\ln\left(e^{3}\right)=\bx{3}$ ؛ \ $\ln\dfrac1{e^{2}}=\ln\left(e^{-2}\right)=\bx{-2}$ ؛ \ $\ln\sqrt e=\ln\left(e^{\frac12}\right)=\bx{\frac12}$.
\item $e^{\ln5}=\bx{5}$ ؛ \ $e^{2\ln3}=\left(e^{\ln3}\right)^{2}=3^{2}=\bx{9}$ ؛ \ $e^{-\ln2}=\dfrac1{e^{\ln2}}=\bx{\frac12}$.
\item حل $e^{x}=5$: \ $x=\ln5$ \ (تعريف $\ln$)، إذن \bx{S=\{\ln5\}}.
\item حل $\ln x=-1$: \ $x=e^{-1}=\dfrac1e$ ، و $\dfrac1e>0$ ، إذن \bx{S=\left\{\frac1e\right\}}.
\end{enumerate}
\end{mithal}
''')
# 2 ------------------------------------------------------------------
B.append(r'''\section{مجموعة التعريف}
\begin{tariqa}[تعيين مجموعة التعريف]
\begin{itemize}
\item $x\mapsto\ln\big(u(x)\big)$ معرفة من أجل كل $x$ يحقق $\bx{u(x)>0}$.
\item $x\mapsto\ln|u(x)|$ معرفة من أجل كل $x$ يحقق $\bx{u(x)\neq0}$.
\item إذا وُجد مقام أو عدة لوغاريتمات: نأخذ \textbf{تقاطع} كل الشروط.
\end{itemize}
\end{tariqa}

\begin{mithal}[أمثلة محلولة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $f(x)=\ln(3x-12)$: \ $3x-12>0\iff x>4$ ، إذن \bx{D_f=]4;+\infty[}.
\item $g(x)=\ln\left(18-2x^{2}\right)$: \ $18-2x^{2}>0\iff x^{2}<9\iff -3<x<3$ ، إذن \bx{D_g=]-3;3[}.
\item $h(x)=\ln|x-2|$: \ $x-2\neq0$ ، إذن \bx{D_h=\R-\{2\}}.
\item $k(x)=\ln\left(\dfrac{x-1}{x+2}\right)$: ندرس إشارة الكسر:
''' + SG(['-\\infty', '-2', '1', '+\\infty'], [('x-1', ',-,t,-,z,+,'), ('x+2', ',-,z,+,t,+,'), (r'\frac{x-1}{x+2}', ',+,d,-,z,+,')]) + r'''
الكسر موجب تمامًا خارج $[-2;1]$ ، إذن \bx{D_k=]-\infty;-2[\cup]1;+\infty[}.
\item $m(x)=\ln x+\ln(4-x)$: \ $x>0$ و $4-x>0$ ، إذن \bx{D_m=]0;4[}.
\item $p(x)=\dfrac{\ln x}{x-1}$: \ $x>0$ و $x\neq1$ ، إذن \bx{D_p=]0;1[\cup]1;+\infty[}.
\end{enumerate}
\end{mithal}
''')
# 3 ------------------------------------------------------------------
B.append(r'''\section{الخواص الجبرية}
\begin{khassia}
من أجل كل عددين حقيقيين موجبين تمامًا $a$ و $b$ ، ومن أجل كل عدد صحيح نسبي $n$:
\begin{align*}
\ln(ab)&=\ln a+\ln b & \ln\left(\frac{1}{a}\right)&=-\ln a & \ln\left(\frac{a}{b}\right)&=\ln a-\ln b\\
\ln\left(a^{n}\right)&=n\ln a & \ln\sqrt{a}&=\frac{1}{2}\ln a & \ln\left(e^{n}\right)&=n
\end{align*}
\end{khassia}

\begin{tariqa}[البرهان (فكرة)]
$e^{\ln a+\ln b}=e^{\ln a}\times e^{\ln b}=ab=e^{\ln(ab)}$ ، والدالة الأسية تقابل ، إذن $\ln(ab)=\ln a+\ln b$. \ وبتطبيقها: $\ln a+\ln\frac1a=\ln1=0$ ، ومنه بقية الخواص.
\end{tariqa}

\begin{molahada}
\begin{itemize}
\item من أجل كل $a\neq0$: $\ln\left(a^{2}\right)=2\ln|a|$ وليس $2\ln a$.
\item $\ln(a+b)\neq\ln a+\ln b$ ، و $\ln\dfrac ab\neq\dfrac{\ln a}{\ln b}$.
\end{itemize}
\end{molahada}

\begin{mithal}[أمثلة محلولة: التبسيط والكتابة بدلالة $\ln2$ و $\ln3$]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $A=\ln12-\ln3+2\ln\dfrac12=\ln\dfrac{12}{3}-2\ln2=\ln4-2\ln2=2\ln2-2\ln2=\bx{0}$.
\item $B=\ln\left(e^{2}\right)+\ln\dfrac1e-\ln\sqrt e=2-1-\dfrac12=\bx{\frac12}$.
\item $\ln72=\ln\left(2^{3}\times3^{2}\right)=\bx{3\ln2+2\ln3}$.
\item $\ln\sqrt{12}=\dfrac12\ln\left(2^{2}\times3\right)=\dfrac12\left(2\ln2+\ln3\right)=\bx{\ln2+\frac12\ln3}$.
\item $\ln\dfrac{16}{27}=\ln2^{4}-\ln3^{3}=\bx{4\ln2-3\ln3}$.
\item من أجل $x>1$: $\ln\left(x^{2}-1\right)-\ln(x+1)=\ln\dfrac{(x-1)(x+1)}{x+1}=\bx{\ln(x-1)}$.
\item $\ln\left(e^{3x}\right)-\ln\left(e^{x}\right)+\ln\dfrac1{e^{2x}}=3x-x-2x=\bx{0}$.
\end{enumerate}
\end{mithal}
''')
# 4 ------------------------------------------------------------------
B.append(r'''\section{إشارة عبارات لوغاريتمية}
\begin{khassia}
$\ln x<0\iff 0<x<1$ ؛ \ $\ln x=0\iff x=1$ ؛ \ $\ln x>0\iff x>1$.
\end{khassia}
''' + SG(['0', '1', '+\\infty'], [(r'\ln x', 'd,-,z,+,')]) + r'''

\begin{tariqa}[إشارة $\ln u(x)$ أو $\ln u(x)-k$]
$\ln u(x)>0\iff u(x)>1$ ؛ \ $\ln u(x)-k>0\iff u(x)>e^{k}$ (مع $u(x)>0$).
\end{tariqa}

\begin{mithal}[أمثلة محلولة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $\ln(x-1)$ على $]1;+\infty[$: موجبة إذا كان $x-1>1$ أي $x>2$:
''' + SG(['1', '2', '+\\infty'], [(r'\ln(x-1)', 'd,-,z,+,')]) + r'''
\item $1-\ln x$ على $]0;+\infty[$: موجبة إذا كان $\ln x<1$ أي $x<e$:
''' + SG(['0', 'e', '+\\infty'], [(r'1-\ln x', 'd,+,z,-,')]) + r'''
\item $x\ln x$ على $]0;+\infty[$: $x>0$ ، فالإشارة إشارة $\ln x$: سالبة على $]0;1[$ وموجبة على $]1;+\infty[$.
\item $(x-1)\ln x$ على $]0;+\infty[$: العاملان لهما نفس الإشارة دائمًا:
''' + SG(['0', '1', '+\\infty'], [('x-1', 'd,-,z,+,'), (r'\ln x', 'd,-,z,+,'), (r'(x-1)\ln x', 'd,+,z,+,')]) + r'''
\end{enumerate}
\end{mithal}
''')
# 5 ------------------------------------------------------------------
B.append(r'''\section{المعادلات}
\begin{khassia}
من أجل كل عددين حقيقيين موجبين تمامًا $a$ و $b$: \ $\bx{\ln a=\ln b\iff a=b}$ ؛ ومن أجل كل $k\in\R$: $\bx{\ln a=k\iff a=e^{k}}$.
\end{khassia}

\begin{tariqa}[حل معادلة لوغاريتمية]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item نعيّن مجموعة الحلول الممكنة $D$ (شروط وجود اللوغاريتمات).
\item نكتب المعادلة على الشكل $\ln a=\ln b$ (أو $\ln a=k$) بالخواص الجبرية.
\item نحل $a=b$ (أو $a=e^{k}$).
\item نحتفظ فقط بالحلول التي تنتمي إلى $D$.
\end{enumerate}
\end{tariqa}

\begin{mithal}[أمثلة محلولة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $\ln(2x-1)=\ln(x+3)$: \ $D=\left]\frac12;+\infty\right[$ ؛ \ $2x-1=x+3\iff x=4\in D$ ، إذن \bx{S=\{4\}}.
\item $\ln(3x-2)=2$: \ $D=\left]\frac23;+\infty\right[$ ؛ \ $3x-2=e^{2}\iff x=\dfrac{e^{2}+2}{3}\in D$ ، إذن \bx{S=\left\{\frac{e^{2}+2}{3}\right\}}.
\item $\ln x+\ln(x-2)=\ln3$: \ $D=]2;+\infty[$ ؛ \ $\ln\big[x(x-2)\big]=\ln3\iff x^{2}-2x-3=0\iff(x-3)(x+1)=0$.\par
$3\in D$ و $-1\notin D$ ، إذن \bx{S=\{3\}}.
\item $\ln\left(x^{2}\right)=\ln(x+2)$: \ $D=]-2;0[\cup]0;+\infty[$ ؛ \ $x^{2}=x+2\iff(x-2)(x+1)=0$ ، والحلان في $D$: \bx{S=\{-1;2\}}.
\item $(\ln x)^{2}-\ln x-2=0$: \ $D=]0;+\infty[$ ؛ نضع $t=\ln x$: $t^{2}-t-2=0\iff t=2$ أو $t=-1$.\par
$\ln x=2\iff x=e^{2}$ ؛ \ $\ln x=-1\iff x=e^{-1}$ ، إذن \bx{S=\left\{e^{-1};e^{2}\right\}}.
\item $e^{2x}-3e^{x}+2=0$: نضع $X=e^{x}>0$: $X^{2}-3X+2=0\iff X=1$ أو $X=2$ ، ومنه $x=0$ أو $x=\ln2$: \bx{S=\{0;\ln2\}}.
\item $e^{x}=3e^{-x}$: نضرب في $e^{x}$: $e^{2x}=3\iff 2x=\ln3$ ، إذن \bx{S=\left\{\frac{\ln3}{2}\right\}}.
\item $2^{x}=5$: \ $2^{x}=e^{x\ln2}$ ، إذن $x\ln2=\ln5$ أي \bx{x=\frac{\ln5}{\ln2}\approx2{,}32}.
\end{enumerate}
\end{mithal}
''')
# 6 ------------------------------------------------------------------
B.append(r'''\section{المتراجحات}
\begin{khassia}
الدالة $\ln$ متزايدة تمامًا على $]0;+\infty[$ ، إذن من أجل $a>0$ و $b>0$: \ $\bx{\ln a<\ln b\iff a<b}$ ؛ و $\bx{\ln a<k\iff 0<a<e^{k}}$.
\end{khassia}

\begin{mithal}[أمثلة محلولة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $\ln(x-1)<0$: \ $D=]1;+\infty[$ ؛ \ $\ln(x-1)<\ln1\iff x-1<1\iff x<2$ ، إذن \bx{S=]1;2[}.
\item $\ln(2x+1)\geqslant\ln(x+4)$: \ $D=\left]-\frac12;+\infty\right[$ ؛ \ $2x+1\geqslant x+4\iff x\geqslant3$ ، إذن \bx{S=[3;+\infty[}.
\item $\ln x+\ln(x-1)\leqslant\ln2$: \ $D=]1;+\infty[$ ؛ \ $x(x-1)\leqslant2\iff x^{2}-x-2\leqslant0\iff -1\leqslant x\leqslant2$.\par
مع $x>1$: \bx{S=]1;2]}.
\item $(\ln x)^{2}-\ln x-2>0$: نضع $t=\ln x$: $(t-2)(t+1)>0\iff t<-1$ أو $t>2$.\par
$\ln x<-1\iff 0<x<e^{-1}$ ؛ \ $\ln x>2\iff x>e^{2}$ ، إذن \bx{S=\left]0;e^{-1}\right[\cup\left]e^{2};+\infty\right[}.
\item $e^{x}>3$: \ $x>\ln3$ ، إذن \bx{S=]\ln3;+\infty[}.
\item أصغر عدد طبيعي $n$ حيث $(0{,}9)^{n}<0{,}01$: \ $n\ln0{,}9<\ln0{,}01$ ، و $\ln0{,}9<0$ فيتغير الاتجاه:\par
$n>\dfrac{\ln0{,}01}{\ln0{,}9}\approx43{,}7$ ، إذن \bx{n=44}.
\end{enumerate}
\end{mithal}
''')
# 7 ------------------------------------------------------------------
B.append(r'''\section{النهايات والنهايات الشهيرة}
\begin{khassia}[نهايات أساسية]
\[ \lim_{x\to0^{+}}\ln x=-\infty \qquad\qquad \lim_{x\to+\infty}\ln x=+\infty \]
المستقيم $x=0$ (محور التراتيب) مقارب عمودي للمنحنى.
\end{khassia}

\begin{khassia}[النهايات الشهيرة ($n\in\mathbb N^{*}$)]
\begin{align*}
\lim_{x\to+\infty}\frac{\ln x}{x}&=0 & \lim_{x\to0^{+}}x\ln x&=0 & \lim_{x\to0}\frac{\ln(1+x)}{x}&=1\\
\lim_{x\to+\infty}\frac{\ln x}{x^{n}}&=0 & \lim_{x\to0^{+}}x^{n}\ln x&=0 & \lim_{x\to1}\frac{\ln x}{x-1}&=1
\end{align*}
نقول: عند $+\infty$ «$x^{n}$ يتغلب على $\ln x$».
\end{khassia}

\begin{mithal}[أمثلة محلولة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $\lim\limits_{x\to+\infty}(x-\ln x)$: حالة $\infty-\infty$ ؛ \ $x-\ln x=x\left(1-\dfrac{\ln x}{x}\right)$ و $\dfrac{\ln x}{x}\to0$ ، إذن النهاية \bx{+\infty}.
\item $\lim\limits_{x\to0^{+}}(x-1)\ln x$: \ $x-1\to-1$ و $\ln x\to-\infty$ ، إذن النهاية \bx{+\infty}.
\item $\lim\limits_{x\to0^{+}}\left(x\ln x-x\right)=0-0=\bx{0}$.
\item $\lim\limits_{x\to+\infty}\dfrac{\ln x}{x^{2}}=\bx{0}$ (النهاية الشهيرة مع $n=2$).
\item $\lim\limits_{x\to0}\dfrac{\ln(1+2x)}{x}=\lim\limits_{x\to0}2\times\dfrac{\ln(1+2x)}{2x}=2\times1=\bx{2}$ (نضع $X=2x\to0$).
\item $\lim\limits_{x\to+\infty}x\ln\left(1+\dfrac1x\right)$: نضع $X=\dfrac1x\to0^{+}$: $\dfrac{\ln(1+X)}{X}\to1$ ، إذن النهاية \bx{1}.
\item $\lim\limits_{x\to+\infty}\big(\ln(x+1)-\ln x\big)=\lim\limits_{x\to+\infty}\ln\dfrac{x+1}{x}=\ln1=\bx{0}$.
\item $\lim\limits_{x\to+\infty}\dfrac{\ln\left(x^{2}+1\right)}{x}$: نكتب $\ln\left(x^{2}+1\right)=2\ln x+\ln\left(1+\dfrac1{x^{2}}\right)$ ، إذن:
\[\frac{\ln(x^{2}+1)}{x}=2\,\frac{\ln x}{x}+\frac1x\ln\left(1+\frac1{x^{2}}\right)\xrightarrow[x\to+\infty]{}2\times0+0\times0=\bx{0}\]
\end{enumerate}
\end{mithal}
''')
# 8 ------------------------------------------------------------------
B.append(r'''\section{الاشتقاق والدالة $\ln u$}
\begin{khassia}
\begin{itemize}
\item الدالة $\ln$ قابلة للاشتقاق على $]0;+\infty[$ و $\bx{\left(\ln x\right)'=\frac{1}{x}}$.
\item إذا كانت $u$ قابلة للاشتقاق وموجبة تمامًا على مجال $I$: $\bx{\big(\ln u\big)'=\frac{u'}{u}}$ ، وللدالتين $\ln u$ و $u$ نفس اتجاه التغير.
\item إذا كانت $u$ قابلة للاشتقاق ولا تنعدم على $I$: $\big(\ln|u|\big)'=\dfrac{u'}{u}$.
\end{itemize}
\end{khassia}

\begin{mithal}[أمثلة محلولة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $f(x)=\ln\left(x^{2}+1\right)$ على $\R$: \ $f'(x)=\bx{\dfrac{2x}{x^{2}+1}}$ ، من إشارة $x$: $f$ متناقصة على $]-\infty;0]$ ومتزايدة على $[0;+\infty[$.
\item $g(x)=x\ln x-x$ على $]0;+\infty[$: \ $g'(x)=\ln x+x\times\dfrac{1}{x}-1=\bx{\ln x}$.
\item $h(x)=\ln\dfrac{x-1}{x+1}$ على $]1;+\infty[$: \ $u'(x)=\dfrac{2}{(x+1)^{2}}$ ، إذن $h'(x)=\dfrac{2}{(x+1)^{2}}\times\dfrac{x+1}{x-1}=\bx{\dfrac{2}{x^{2}-1}}>0$.
\item $k(x)=(\ln x)^{2}$ على $]0;+\infty[$: \ $k'(x)=2\times\dfrac{1}{x}\times\ln x=\bx{\dfrac{2\ln x}{x}}$.
\item $p(x)=\ln|2x-4|$ على $\R-\{2\}$: \ $p'(x)=\bx{\dfrac{2}{2x-4}=\dfrac1{x-2}}$.
\item $q(x)=\dfrac{\ln x}{x}$ على $]0;+\infty[$: \ $q'(x)=\dfrac{\frac1x\times x-\ln x}{x^{2}}=\bx{\dfrac{1-\ln x}{x^{2}}}$.
\item \textbf{مماس:} معادلة المماس لمنحنى $f(x)=\ln(2x-1)$ عند $x_0=1$: \ $f(1)=0$ و $f'(x)=\dfrac2{2x-1}$ ، $f'(1)=2$ ، إذن \bx{y=2x-2}.
\end{enumerate}
\end{mithal}
''')
# 9 ------------------------------------------------------------------
B.append(r'''\section{دراسة الدالة $\ln$ والوضع النسبي}
\begin{khassia}[جدول التغيرات]
من أجل كل $x>0$: $\left(\ln x\right)'=\dfrac{1}{x}>0$ ، إذن $\ln$ متزايدة تمامًا على $]0;+\infty[$.
\end{khassia}
\begin{TAB}
\tkzTabInit[lgt=2.2,espcl=4]{$x$/1,$\frac{1}{x}$/1,$\ln x$/2}{$0$,$+\infty$}
\tkzTabLine{d,+,}
\tkzTabVar{D-/$-\infty$,+/$+\infty$}
\end{TAB}

\begin{khassia}[المماس عند $1$ ووضعية المنحنى]
المماس عند النقطة ذات الفاصلة $1$: $y=\ln'(1)(x-1)+\ln1$ ، أي \bx{(T):\ y=x-1}.\par
نضع $\varphi(x)=\ln x-(x-1)$: \ $\varphi'(x)=\dfrac{1}{x}-1=\dfrac{1-x}{x}$ ، موجبة على $]0;1[$ وسالبة على $]1;+\infty[$ ؛ قيمتها الحدية العظمى $\varphi(1)=0$ ، إذن $\varphi(x)\leqslant0$ أي $\bx{\ln x\leqslant x-1}$:
\end{khassia}
''' + vtab(['0', '1', P], r'\ln x-(x-1)', {1: ('A(1;0)', 'يمس')}, ['تحت', 'تحت'], r'(C_{\ln})', '(T)', bars=(0,)) + r'''

\begin{GR}{-3}{5}{-3}{5}{0.85}
\draw[gray,dashed] (-3,-3)--(5,5) node[pos=0.93,right]{$y=x$};
\draw[cDef,very thick,domain=0.04:5,samples=120] plot(\x,{ln(\x)});
\draw[cThm,very thick,domain=-3:1.6,samples=80] plot(\x,{exp(\x)});
\draw[cRem,thick,domain=-1.5:5] plot(\x,{\x-1});
\fill (1,0) circle (1.5pt) node[below right]{$1$};
\fill (2.718,1) circle (1.5pt);
\draw[dotted] (2.718,0)--(2.718,1)--(0,1);
\node[below] at (2.718,0){$e$};
\node[left] at (0,1){$1$};
\node[cDef] at (4.3,1.1){$y=\ln x$};
\node[cThm] at (2.1,4.4){$y=e^{x}$};
\node[cRem] at (4.2,2.6){$y=x-1$};
\end{GR}
''')
# 10 -----------------------------------------------------------------
B.append(r'''\section{دالتان مرجعيتان}
\subsection{الدالة $x\mapsto x\ln x$ على $]0;+\infty[$}
\begin{mithal}[دراسة كاملة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item \textbf{النهايات:} $\lim\limits_{x\to0^{+}}x\ln x=0$ (شهيرة) ؛ \ $\lim\limits_{x\to+\infty}x\ln x=+\infty$.
\item \textbf{المشتقة:} $(x\ln x)'=\ln x+1$ ، وتنعدم عند $\ln x=-1$ أي $x=e^{-1}$.
\item القيمة الحدية الصغرى: $e^{-1}\ln e^{-1}=\bx{-\frac1e}$.
\end{enumerate}
\begin{TAB}
\tkzTabInit[lgt=2.2,espcl=3]{$x$/1,$\ln x+1$/1,$x\ln x$/2}{$0$,$\frac1e$,$+\infty$}
\tkzTabLine{d,-,z,+,}
\tkzTabVar{D+/$0$,-/$-\frac1e$,+/$+\infty$}
\end{TAB}
\end{mithal}

\subsection{الدالة $x\mapsto\dfrac{\ln x}{x}$ على $]0;+\infty[$}
\begin{mithal}[دراسة كاملة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item \textbf{النهايات:} $\lim\limits_{x\to0^{+}}\dfrac{\ln x}{x}=-\infty$ (لأن $\ln x\to-\infty$ و $\frac1x\to+\infty$) ؛ \ $\lim\limits_{x\to+\infty}\dfrac{\ln x}{x}=0$: مقارب أفقي $y=0$.
\item \textbf{المشتقة:} $\dfrac{1-\ln x}{x^{2}}$ ، موجبة إذا كان $x<e$.
\item القيمة الحدية العظمى: $\dfrac{\ln e}{e}=\bx{\frac1e}$. \ \textbf{تطبيق:} من أجل كل $x>0$: $\ln x\leqslant\dfrac xe$.
\end{enumerate}
\begin{TAB}
\tkzTabInit[lgt=2.2,espcl=3]{$x$/1,$1-\ln x$/1,$\frac{\ln x}{x}$/2}{$0$,$e$,$+\infty$}
\tkzTabLine{d,+,z,-,}
\tkzTabVar{D-/$-\infty$,+/$\frac1e$,-/$0$}
\end{TAB}
\end{mithal}
''')
# 11 -----------------------------------------------------------------
B.append(r'''\section{اللوغاريتم العشري}
\begin{tarif}
\textbf{اللوغاريتم العشري} هو الدالة المعرفة على $]0;+\infty[$ بـ: $\bx{\log x=\frac{\ln x}{\ln 10}}$.
\end{tarif}
\begin{khassia}
للدالة $\log$ نفس الخواص الجبرية لـ $\ln$ ؛ \ $\log1=0$ ، $\log10=1$ ؛ ومن أجل كل $n\in\mathbb Z$: $\log\left(10^{n}\right)=n$ ؛ \ $\log x=a\iff x=10^{a}$.\par
إذا كان $10^{p}\leqslant x<10^{p+1}$ ($x\geqslant1$) فإن عدد أرقام $x$ هو $p+1$.
\end{khassia}
\begin{mithal}[أمثلة محلولة]
\begin{enumerate}[label=\textbf{\arabic*.}]
\item $\log1000=\log10^{3}=\bx{3}$ ؛ \ $\log0{,}01=\log10^{-2}=\bx{-2}$.
\item $\log x=2\iff x=10^{2}=\bx{100}$.
\item $\log x+\log(x-3)=1$: \ $D=]3;+\infty[$ ؛ \ $x(x-3)=10\iff x^{2}-3x-10=0\iff(x-5)(x+2)=0$ ، إذن \bx{S=\{5\}}.
\item عدد أرقام $2^{100}$: \ $\log2^{100}=100\log2\approx30{,}1$ ، إذن $10^{30}\leqslant2^{100}<10^{31}$: \bx{31} رقمًا.
\item \textbf{الكيمياء:} $\text{pH}=-\log\left[\text{H}_{3}\text{O}^{+}\right]$ ؛ إذا كان $\left[\text{H}_{3}\text{O}^{+}\right]=2{,}5\times10^{-4}$ فإن $\text{pH}\approx\bx{3{,}60}$.
\end{enumerate}
\end{mithal}
''')
# 12 -----------------------------------------------------------------
G1 = r'''\begin{GR}{-0.5}{5}{-1.5}{4.5}{1}
\Ticks{1,2,3,4}{1,2,3,4}
\draw[cRem,thick,domain=-0.5:5] plot(\x,{\x-1});
\draw[cDef,very thick,domain=0.28:5,samples=150] plot(\x,{\x-1-ln(\x)/\x});
\fill (1,0) circle (1.6pt) node[below right]{$A$};
\node[cDef] at (0.9,3.6){$(C_f)$};
\node[cRem] at (4.2,2.6){$(\Delta)$};
\end{GR}'''
G2 = r'''\begin{GR}{-0.5}{6}{-4}{5}{0.9}
\Ticks{1,2,3,4,5}{-3,-2,-1,1,2,3,4}
\draw[cRem,thick,domain=-0.5:6] plot(\x,{\x-1}) node[above left]{$(\Delta)$};
\draw[cEx,thick,dashed,domain=0.3:6] plot(\x,{\x-1+2/2.71828}) node[above left]{$(T)$};
\draw[cDef,very thick,domain=0.46:6,samples=200] plot(\x,{\x-1+2*ln(\x)/\x});
\fill (1,0) circle (1.6pt) node[below right]{$A$};
\fill (2.718,2.454) circle (1.6pt) node[above left]{$B$};
\node[cDef] at (1.1,-3){$(C_f)$};
\end{GR}'''
B.append(r'''\origNeedspace{26\baselineskip}\section{تمارين محلولة (نمط البكالوريا)}
\begin{tmr}
\textbf{I.} $g$ الدالة المعرفة على $]0;+\infty[$ بـ: $g(x)=x^{2}-1+\ln x$.
\begin{sq}
\qa ادرس اتجاه تغير الدالة $g$.
\qb احسب $g(1)$ ثم استنتج إشارة $g(x)$.
\end{sq}
\textbf{II.} $f$ الدالة المعرفة على $]0;+\infty[$ بـ: $f(x)=x-1-\dfrac{\ln x}{x}$ ، و $(C_f)$ تمثيلها البياني.
\begin{sq}
\qa احسب $\lim\limits_{x\to0^{+}}f(x)$ و $\lim\limits_{x\to+\infty}f(x)$.
\qb بيّن أنه من أجل كل $x>0$: $f'(x)=\dfrac{g(x)}{x^{2}}$ ، ثم شكّل جدول تغيرات $f$.
\qc بيّن أن $(\Delta):y=x-1$ مقارب مائل لـ $(C_f)$ ، وادرس الوضع النسبي ، ثم ارسم.
\end{sq}
\end{tmr}
\begin{hal}
\textbf{I.}
\pa $g'(x)=2x+\dfrac{1}{x}>0$ على $]0;+\infty[$ ، إذن \bxt{$g$ متزايدة تمامًا على $]0;+\infty[$}.
\pb $g(1)=1-1+\ln1=0$ ، و $g$ متزايدة تمامًا:
''' + SG(['0', '1', '+\\infty'], [('g(x)', 'd,-,z,+,')]) + r'''

\textbf{II.}
\pa عند $0^{+}$: $\dfrac{\ln x}{x}\to-\infty$ ، إذن $\lim\limits_{x\to0^{+}}f(x)=\bx{+\infty}$ ؛ \ عند $+\infty$: $\dfrac{\ln x}{x}\to0$ ، إذن $\lim\limits_{x\to+\infty}f(x)=\bx{+\infty}$.
\pb $\left(\dfrac{\ln x}{x}\right)'=\dfrac{1-\ln x}{x^{2}}$ ، ومنه $f'(x)=1-\dfrac{1-\ln x}{x^{2}}=\dfrac{x^{2}-1+\ln x}{x^{2}}=\bx{\frac{g(x)}{x^{2}}}$ ؛ و $f(1)=0$:
\begin{TAB}
\tkzTabInit[lgt=2.2,espcl=2.8]{$x$/1,$f'(x)$/1,$f(x)$/2}{$0$,$1$,$+\infty$}
\tkzTabLine{d,-,z,+,}
\tkzTabVar{D+/$+\infty$,-/$0$,+/$+\infty$}
\end{TAB}
\pc $f(x)-(x-1)=-\dfrac{\ln x}{x}\xrightarrow[x\to+\infty]{}0$ ، إذن \bx{(\Delta):y=x-1} مقارب مائل بجوار $+\infty$.\par
إشارة الفرق هي إشارة $-\ln x$ (لأن $x>0$):
''' + vtab(['0', '1', P], 'f(x)-(x-1)', {1: 'A(1;0)'}, ['فوق', 'تحت'], r'(C_f)', r'(\Delta)', bars=(0,)) + '\n' + G1 + r'''
\end{hal}

\begin{tmr}
$f$ الدالة المعرفة على $]0;+\infty[$ بـ: $f(x)=x-1+\dfrac{2\ln x}{x}$.
\begin{sq}
\qa احسب نهايتي $f$ عند $0^{+}$ وعند $+\infty$.
\qb بيّن أن $f'(x)=\dfrac{g(x)}{x^{2}}$ حيث $g(x)=x^{2}+2-2\ln x$ ، ثم بيّن أن $g(x)>0$ واستنتج اتجاه تغير $f$.
\qc بيّن أن $(\Delta):y=x-1$ مقارب مائل لـ $(C_f)$ ، وادرس الوضع النسبي.
\qd بيّن أن $(C_f)$ يقبل مماسًا $(T)$ يوازي $(\Delta)$ ، اكتب معادلته ثم ارسم.
\end{sq}
\end{tmr}
\begin{hal}
\pa عند $0^{+}$: $\ln x\to-\infty$ و $\dfrac1x\to+\infty$ ، إذن $\dfrac{2\ln x}{x}\to-\infty$ و \bx{\lim_{x\to0^{+}}f(x)=-\infty} (مقارب عمودي $x=0$).\par
عند $+\infty$: $\dfrac{\ln x}{x}\to0$ ، إذن \bx{\lim_{x\to+\infty}f(x)=+\infty}.
\pb $f'(x)=1+2\times\dfrac{1-\ln x}{x^{2}}=\dfrac{x^{2}+2-2\ln x}{x^{2}}=\bx{\frac{g(x)}{x^{2}}}$.\par
$g'(x)=2x-\dfrac2x=\dfrac{2(x-1)(x+1)}{x}$: $g$ متناقصة على $]0;1]$ ومتزايدة على $[1;+\infty[$ ، قيمتها الحدية الصغرى $g(1)=3>0$ ، إذن $g(x)>0$ و \bxt{$f$ متزايدة تمامًا على $]0;+\infty[$}.
\begin{TAB}
\tkzTabInit[lgt=2.2,espcl=4]{$x$/1,$f'(x)$/1,$f(x)$/2}{$0$,$+\infty$}
\tkzTabLine{d,+,}
\tkzTabVar{D-/$-\infty$,+/$+\infty$}
\end{TAB}
\pc $f(x)-(x-1)=\dfrac{2\ln x}{x}\xrightarrow[x\to+\infty]{}0$ ، إذن \bx{(\Delta):y=x-1} مقارب مائل بجوار $+\infty$.\par
إشارة الفرق هي إشارة $\ln x$:
''' + vtab(['0', '1', P], 'f(x)-(x-1)', {1: 'A(1;0)'}, ['تحت', 'فوق'], r'(C_f)', r'(\Delta)', bars=(0,)) + r'''
\pd $(T)\parallel(\Delta)$ معناه $f'(x)=1$: \ $\dfrac{2(1-\ln x)}{x^{2}}=0\iff\ln x=1\iff x=e$.\par
$f(e)=e-1+\dfrac2e$ ، إذن $(T):\ y=(x-e)+e-1+\dfrac2e$ ، أي \bx{(T):\ y=x-1+\frac2e} ، يمس $(C_f)$ في $B\left(e;e-1+\frac2e\right)$.
''' + G2 + r'''
\end{hal}
''')
# 13 -----------------------------------------------------------------
B.append(r'''\section{أخطاء شائعة}
\begin{BOX}{cThm}{تجنّب هذه الأخطاء}
\begin{enumerate}[label=\textbf{\arabic*.}]
\item حل معادلة أو متراجحة دون تعيين مجموعة التعريف $D$ ، أو قبول حلول خارجها.
\item $\ln(a+b)=\ln a+\ln b$ \ (خطأ) ؛ \ $\ln\dfrac ab=\dfrac{\ln a}{\ln b}$ \ (خطأ).
\item $\ln\left(x^{2}\right)=2\ln x$ على مجال يحتوي أعدادًا سالبة؛ الصحيح $2\ln|x|$.
\item نسيان تغيير اتجاه المتباينة عند القسمة على عدد سالب مثل $\ln0{,}9$.
\item $(\ln u)'=\dfrac1u$ \ (خطأ) ؛ الصحيح $\dfrac{u'}{u}$.
\item كتابة $\ln x>0$ على $]0;+\infty[$ كلها؛ الصحيح: فقط من أجل $x>1$.
\end{enumerate}
\end{BOX}

\section{خلاصة الطرائق}
\begin{center}
\begin{tabular}{|p{0.62\textwidth}|p{0.3\textwidth}|}\hline
\rowcolor{cSec!12}\textbf{الطريقة} & \textbf{المطلوب}\\\hline
نحل $u(x)>0$ (أو $u(x)\neq0$ في حالة $\ln|u|$) ، ونأخذ تقاطع الشروط. & مجموعة تعريف $\ln u$\\\hline
$\ln u>0\iff u>1$ ؛ $\ln u-k>0\iff u>e^{k}$. & إشارة عبارة لوغاريتمية\\\hline
الشروط ، ثم $\ln a=\ln b\iff a=b$ (أو $a=e^{k}$) ، ثم نحتفظ بالحلول التي تحقق الشروط. & معادلة لوغاريتمية\\\hline
الشروط ، ثم $\ln a<\ln b\iff a<b$ ، ثم تقاطع الحلول مع الشروط. & متراجحة لوغاريتمية\\\hline
نضع $t=\ln x$ (أو $X=e^{x}$) فنحصل على معادلة من الدرجة الثانية. & معادلة من الشكل $a(\ln x)^{2}+b\ln x+c=0$\\\hline
$a^{x}=e^{x\ln a}$ ، ثم نأخذ $\ln$ للطرفين. & معادلة أسية من الشكل $a^{x}=b$\\\hline
نخرج الحد الغالب ونستعمل النهايات الشهيرة ($x^{n}$ يتغلب على $\ln x$). & حالة عدم تعيين\\\hline
$\left(\ln u\right)'=\frac{u'}{u}$ ؛ و $\ln u$ لها نفس اتجاه تغير $u$. & مشتقة $\ln u$\\\hline
ندرس دالة مساعدة $g$ ونستنتج إشارتها من رتابتها وجذرها. & إشارة المشتقة\\\hline
$\lim\big(f(x)-(ax+b)\big)=0$ ، ثم جدول الوضع النسبي لإشارة الفرق. & المقارب المائل والوضع النسبي\\\hline
$\log x=\frac{\ln x}{\ln10}$ ؛ عدد أرقام $x$ هو $p+1$ حيث $p$ الجزء الصحيح لـ $\log x$. & اللوغاريتم العشري\\\hline
\end{tabular}
\end{center}
\end{document}
''')
p = '/home/user/Math-app/documents/ln/molakhas_ln_3as.tex'
t = open(p).read()
pre = t[:t.index(r'\begin{document}')]
if r'\newenvironment{FIG}' not in pre:
    pre += r'\newenvironment{FIG}{\par\begin{center}\begin{LTR}}{\end{LTR}\end{center}}' + '\n'
if r'\origNeedspace' not in pre:
    pre += r'\let\origNeedspace\Needspace' + '\n'
open(p, 'w').write(pre + '\n'.join(B))
print('ok')
