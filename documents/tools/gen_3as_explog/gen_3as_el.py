import sys, re
D0='/tmp/claude-0/-home-user-Math-app/edf6d12c-f942-5224-90ee-6cbaa794c825/scratchpad/p2/'
which=sys.argv[1]
exec(open(D0+'hdr_ln.py').read()); exec(open(D0+'explog_helpers.py').read())
exec(open(D0+('sess_exp3.py' if which=='exp' else 'sess_ln3.py')).read())
import importlib.util; spec=importlib.util.spec_from_file_location('gf',D0+'ge_format.py'); gf=importlib.util.module_from_spec(spec); spec.loader.exec_module(gf)
if which=='exp':
    TITLE='الدالة الأسية'; OUT='modhakira_wahda2a_3as'; START=10; CNT='4 مذكرات (8 ساعات)'
    items=['الدالة الأسية: تعريف وخواص جبرية.','إشارة الدالة الأسية واتجاه تغيرها ، معادلات ومتراجحات.',r'دراسة الدوال $x\mapsto e^{u(x)}$ و $x\mapsto e^{kx}$.',r'المعادلات التفاضلية $y^{\prime}=ay+b$.']
else:
    TITLE='الدالة اللوغاريتمية النيبيرية'; OUT='modhakira_wahda2b_3as'; START=14; CNT='4 مذكرات (8 ساعات)'
    items=['الدالة اللوغاريتمية: تعريف ، اتجاه التغير ، معادلات ومتراجحات.','الخواص الجبرية للدالة اللوغاريتمية.',r'اشتقاقية الدالة $\ln$ ودراسة الدالة $\ln\circ u$.','اللوغاريتم العشري وتطبيقاته.']
cover=r'''\begin{LTR}
\begin{tcolorbox}[enhanced,colback=cThm!85!black,colframe=cThm!85!black,arc=3mm,halign=center,boxrule=0pt,top=12pt,bottom=12pt,before upper={\selectlanguage{arabic}}]
{\color{white}\fontsize{24}{30}\selectfont\bfseries مذكرات محور: '''+TITLE+r'''}\\[8pt]
{\color{white}\large السنة الثالثة ثانوي -- علوم تجريبية}\\[4pt]
{\color{white}\large '''+CNT+r''' -- السنة الدراسية 2026-2027}
\end{tcolorbox}
\end{LTR}
\begin{BOX}{cThm}{يتضمن هذا العمل}
\begin{enumerate}[label=\textbf{مذكرة \arabic{enumi}:},leftmargin=6em,start='''+str(START)+r''']
'''+''.join(r'\item '+i+'\n' for i in items)+r'''\end{enumerate}
الحلول مفصّلة: المعطيات بالأسود ، \T{العناوين} و\RR{النتائج} بلون مختلف ، وكل سؤال في سطر.
\end{BOX}
'''
hdr=EXTRA+r'\SetHeader{\small\bfseries\color{cSec}مذكرات محور: '+TITLE+r'}{\small\color{cSec}السنة الثالثة ثانوي -- علوم تجريبية}'+'\n'+r'\begin{document}'+'\n'
body=re.sub(r'\\par(?=[\u0600-\u06FF(])',r'\\par ',hdr+cover+boxify(boxify(''.join(S),'RR'),'T'))
body=gf.widen_tables(body)
P=pre
# agreed layout: wide «سير الحصة» column, formulas never split, narrow side margins
P=P.replace('[a4paper,margin=1.7cm,','[a4paper,margin=1.2cm,')
o=r'''\begin{LTR}\renewcommand{\arraystretch}{1.25}
\begin{longtable}{|p{0.17\textwidth}|>{\centering\arraybackslash}p{0.06\textwidth}|p{0.53\textwidth}|>{\centering\arraybackslash}p{0.12\textwidth}|}'''
assert o in P
P=P.replace(o,r'''\begin{LTR}\renewcommand{\arraystretch}{1.25}\setlength{\tabcolsep}{4pt}\relpenalty=10000\binoppenalty=10000\tolerance=9000\emergencystretch=0.3\linewidth
\begin{longtable}{|p{0.09\textwidth}|>{\centering\arraybackslash}p{0.05\textwidth}|p{0.71\textwidth}|>{\centering\arraybackslash}p{0.09\textwidth}|}''')
P=P.replace(r'\ar{\textbf{توجيهات وتعاليق}} & \ar{\textbf{المدة}}',r'\ar{\footnotesize\textbf{توجيهات وتعاليق}} & \ar{\footnotesize\textbf{المدة}}').replace(r'\ar{\textbf{مراحل الحصة}}',r'\ar{\footnotesize\textbf{مراحل الحصة}}')
o2=r'\newcommand{\Row}[4]{\ar{\small #4} & \ar{#3} & \ar{#2}'
assert o2 in P
P=P.replace(o2,r'\newcommand{\Row}[4]{\ar{\small #4} & \ar{#3} & \ar{\RaggedEnd #2}')
P=P.replace(r'\newcommand{\Row}[4]',r'\newcommand{\RaggedEnd}{\leftskip=0pt plus 1fil\relax}'+'\n'+r'\newcommand{\Row}[4]',1)
open(OUT+'.tex','w').write(P+body+r'\end{document}'+'\n')
print(OUT,len(S))
