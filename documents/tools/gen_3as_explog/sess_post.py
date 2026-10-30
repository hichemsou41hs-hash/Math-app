# shared post-processing of the lesson-plan sessions (exec'd by sess_*.py)
# 1) a long formula after some text goes to its own line, so a line never stretches around it
def _w(s):
    s=re.sub(r'\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}',lambda m:max(m.group(1),m.group(2),key=len),s)
    s=re.sub(r'\\(left|right|quad|qquad|limits|displaystyle|mathbb|RR|LW|textbf|ck|overline)','',s)
    s=re.sub(r'\\[a-zA-Z]+','x',s)
    return len(re.sub(r'[{}$^_ ]','',s))
def brk(x):
    parts=re.split(r'(\$[^$]+\$)',x); out=''; acc=0
    for q in parts:
        if q.startswith('$') and _w(q)>=14 and acc>=4 and acc+_w(q)>46 and not out.rstrip().endswith(r'\par'):
            out+=r'\par '
            acc=0
        out+=q; acc+=_w(q)
    return out
# 2) laws and formulas of the labelled law parts in colour (\LW); results stay red (\RR)
def _law(seg,laws):
    m=re.match(r'\\Lab\{[^{}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}',seg)
    if not m or not any(k in m.group(1)[:14] for k in laws): return seg
    head,rest=seg[:m.end()],seg[m.end():]
    if 'tikzpicture' in rest or 'tabular' in rest: return seg
    return head+re.sub(r'(?<!\\)\$([^$]+)\$',lambda q:'$'+r'\LW{'+q.group(1)+'}$',rest)
def post(S,laws):
    S=[re.sub(r'\\par(?![a-zA-Z])',chr(0),s) for s in S]
    S=[r'\par'.join(p if ('tikzpicture' in p or 'tabular' in p) else brk(p) for p in s.split(chr(0))) for s in S]
    return [r'\Lab{'.join(_law(r'\Lab{'+x,laws)[5:] if i else x for i,x in enumerate(s.split(r'\Lab{'))) for s in S]
