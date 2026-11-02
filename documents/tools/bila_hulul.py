"""Exercise sheet without solutions: drop every hal environment, retitle. Usage: python3 bila_hulul.py file.tex -> file_bila_hulul.tex"""
import re, sys
src = sys.argv[1]; out = src[:-4] + '_bila_hulul.tex'
t = open(src).read()
head, body = t.split(r'\begin{document}', 1)
# a remark box right after a solution belongs to that solution: drop it too
body, n = re.subn(r'\\begin\{hal\}.*?\\end\{hal\}(\s*\\begin\{molahada\}.*?\\end\{molahada\})?\n?', '', body, flags=re.S)
# titles
for a, b in [(r'سلسلة تمارين مع الحلول المفصلة', r'سلسلة تمارين (بدون حلول)'),
             (r'،? ?مع الحلول المفصلة خطوة بخطوة', r' -- بدون حلول (للتدرّب)'),
             (r'،? ?مع الحلول المفصلة', r' -- بدون حلول (للتدرّب)'),
             (r'مع الحلول', r'بدون حلول')]:
    body = re.sub(a, b, body)
body = re.sub(r'--[ ]+--', '--', body)
head = head.replace('{تمرين محلول \\theexo}', '{تمرين \\theexo}')
body = re.sub(r'\n{3,}', '\n\n', body)
open(out, 'w').write(head + r'\begin{document}' + body)
print(out, n)
