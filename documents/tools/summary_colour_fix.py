import re, sys
p=sys.argv[1]; t=open(p).read()
exec(open('/home/user/Math-app/documents/tools/gen_3as_explog/sess_post.py').read().split('# 2)')[0])
# colours: results red, laws blue
t=t.replace(r"\newcommand{\bx}[1]{\ensuremath{\colorbox{cDef!12}{$\displaystyle #1$}}}",r"\newcommand{\bx}[1]{\ensuremath{\colorbox{cDef!12}{$\displaystyle\color{cThm}#1$}}}"+"\n"+r"\newcommand{\LW}[1]{{\color{cDef}#1}}  % law / formula colour")
t=t.replace(r"\newtcbox{\bxtbox}{on line,colback=cDef!12,",r"\newtcbox{\bxtbox}{on line,coltext=cThm,colback=cDef!12,")
if r'\relpenalty=10000' not in t:
    t=t.replace(r'\begin{document}',r'\relpenalty=10000\binoppenalty=10000\tolerance=9000\emergencystretch=0.3\linewidth'+'\n'+r'\begin{document}',1)
a=r"""$\pgcd(24;18)=6$،\quad $\pgcd(27;140)=1$،\quad $\pgcd(150;240)=30$،\quad $\pgcd(-85;-25)=\pgcd(85;25)=5$."""
t=t.replace(a,r"""$\pgcd(24;18)=\bx{6}$ \qquad $\pgcd(27;140)=\bx{1}$ \qquad $\pgcd(150;240)=\bx{30}$\par
$\pgcd(-85;-25)=\pgcd(85;25)=\bx{5}$""")
def wrap(m):
    s=m.group(0); nl=s.index('\n'); head,body=s[:nl],s[nl:]
    def w(mm):
        x=mm.group(1)
        if x.startswith(r'\LW{') or x.strip().startswith(r'\bx'): return mm.group(0)
        return '$'+r'\LW{'+x+'}'+'$'
    body=re.sub(r'(?<!\\)\$([^$]+)\$',w,body)
    body=re.sub(r'\\\[(.+?)\\\]',lambda mm:r'\['+r'\LW{'+mm.group(1)+'}'+r'\]',body,flags=re.S)
    return head+body
t=re.sub(r'\\begin\{(khassia|tarif|tariqa)\}.*?\\end\{\1\}',wrap,t,flags=re.S)
# long computations in examples/solutions: own display line when the sentence is too long for one line
REL=re.compile(r'=|\\equiv|\\iff|\\Rightarrow|\\mid')
W=lambda s:_w(s) if s.startswith('$') else len(re.sub(r'\\[a-zA-Z]+|[{}\s]','',s))*0.8
def conv_block(b):
    out=[]; skip=0
    for line in b.split('\n'):
        if re.search(r'\\begin\{(align|tabular|center|tikzpicture|GR)',line): skip+=1
        parts=re.split(r'(?<!\\)(\$[^$]+\$)',line)
        if skip or line.strip().startswith(r'\[') or '$' not in line or sum(W(q) for q in parts)<=70:
            out.append(line)
        else:
            res=''; pre=0
            for i,q in enumerate(parts):
                if q.startswith('$') and REL.search(q) and _w(q)>=16 and (pre>=3 or i+1<len(parts) and len(parts[i+1].strip())>3):
                    res+='\n\\[ '+q[1:-1]+' \\]\n'; pre=0
                else:
                    res+=q; pre+=W(q)
            out.append(res)
        if re.search(r'\\end\{(align\*?|tabular|center|tikzpicture|GR)',line): skip=max(0,skip-1)
    return '\n'.join(out)
t=re.sub(r'\\begin\{(mithal|hal)\}.*?\\end\{\1\}',lambda m:conv_block(m.group(0)),t,flags=re.S)
t=re.sub(r'\\\]\s*[،,.؛:]\s*',r'\\]'+'\n',t)
open(p,'w').write(t)
