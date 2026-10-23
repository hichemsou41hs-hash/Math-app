#!/usr/bin/env python3
"""tex2docx.py -- convert the teacher's Arabic XeLaTeX documents to editable Word files.

Usage:
    python3 tex2docx.py FILE.tex [FILE2.tex ...] [-o OUT.docx] [--cache DIR] [--keep]

One .docx per .tex (default: same name next to the .tex).

Pipeline
  1. split preamble / body, drop comments;
  2. every figure (TAB, GR, CP, ... = any environment or macro whose preamble
     definition contains a tikzpicture, plus bare tikzpicture) is compiled with
     the document's own preamble (one xelatex batch, one page per figure),
     rasterised at 200 dpi, trimmed and cached by sha1(preamble + source);
  3. LaTeX is rewritten to something pandoc understands; tcolorbox environments,
     centering, page breaks, labelled items, header rows ... become text markers
     (U+27E6 ... U+27E7) that survive pandoc;
  4. pandoc (LaTeX -> docx, math -> native OMML) with a generated reference.docx
     (Amiri, RTL);
  5. python-docx/lxml post-processing turns the markers into shaded boxes
     (1-cell tables), sets RTL everywhere, styles tables, header/footer.
"""
import argparse, hashlib, os, re, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor

DPI = 200
FONT = "Amiri"
FOOTER = "الأستاذ سوايسية هشام للرياضيات"
M_OPEN, M_CLOSE = "\u27e6", "\u27e7"          # ⟦ ⟧
MK = re.compile(M_OPEN + r"([^" + M_CLOSE + r"]*)" + M_CLOSE)

COLORS = {"cDef": "1F4E9C", "cThm": "B3261E", "cRem": "2E7D32", "cEx": "C76B00",
          "cMeth": "6A1B9A", "cSol": "00695C", "cSec": "1F3A68"}
BOXENVS = {  # env: (color, default title)
    "tarif": ("cDef", "تعريف"), "khassia": ("cThm", "خاصية"), "molahada": ("cRem", "ملاحظة"),
    "mithal": ("cEx", "مثال"), "tariqa": ("cMeth", "طريقة")}
ARLETTERS = ["أ", "ب", "جـ", "د", "هـ"]


def mk(s):
    return M_OPEN + s + M_CLOSE


# ----------------------------------------------------------------- LaTeX parsing helpers
def skip_ws(s, i):
    while i < len(s) and s[i] in " \t\n":
        i += 1
    return i


def read_group(s, i, o="{", c="}"):
    """s[i] must be `o`; return (content, index after closing)."""
    assert s[i] == o, (s[i:i + 40])
    depth, j = 0, i
    while j < len(s):
        ch = s[j]
        if ch == "\\":
            j += 2
            continue
        if o == "[" and ch == "{":   # braces protect ] [ inside optional arguments
            _, j = read_group(s, j)
            continue
        if ch == o:
            depth += 1
        elif ch == c:
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced group at %d: %s" % (i, s[i:i + 60]))


def read_args(s, i, nopt=0, nreq=0, opt_any=False):
    """Read up to nopt optional [..] then nreq {..} args starting at i (spaces allowed)."""
    opts, reqs = [], []
    for _ in range(nopt):
        k = skip_ws(s, i)
        if k < len(s) and s[k] == "[":
            v, i = read_group(s, k, "[", "]")
            opts.append(v)
        else:
            opts.append(None)
    for _ in range(nreq):
        k = skip_ws(s, i)
        if k < len(s) and s[k] == "{":
            v, i = read_group(s, k)
        else:  # single token argument
            m = re.match(r"\\[A-Za-z]+|.", s[k:])
            v, i = m.group(0), k + len(m.group(0))
        reqs.append(v)
    return opts, reqs, i


def find_env_end(s, name, start):
    """start = index right after \\begin{name}...; return (body_end, after_end)."""
    b, e = "\\begin{%s}" % name, "\\end{%s}" % name
    depth, j = 1, start
    while True:
        nb, ne = s.find(b, j), s.find(e, j)
        if ne < 0:
            raise ValueError("no \\end{%s}" % name)
        if 0 <= nb < ne:
            depth += 1
            j = nb + len(b)
        else:
            depth -= 1
            if depth == 0:
                return ne, ne + len(e)
            j = ne + len(e)


def replace_macro(s, name, nopt, nreq, fn):
    """Replace every \\name{..}.. by fn(opts, reqs). Innermost-safe (re-scans)."""
    pat = re.compile(r"\\" + re.escape(name) + r"(?![A-Za-z])")
    out, pos = [], 0
    while True:
        m = pat.search(s, pos)
        if not m:
            out.append(s[pos:])
            return "".join(out)
        opts, reqs, end = read_args(s, m.end(), nopt, nreq)
        out.append(s[pos:m.start()])
        out.append(fn(opts, reqs))
        pos = end


def strip_comments(s):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) if "%" in ln else ln for ln in s.split("\n"))


DEF_RE = re.compile(r"\\(providecommand|newcommand|renewcommand|newenvironment|renewenvironment|"
                    r"tikzset|definecolor|colorlet|newcolumntype|pgfmathsetmacro|DeclareMathOperator)(\*?)(?![A-Za-z])")
DEF_ARGS = {  # (name args incl. braces/cs, optional args, mandatory body args)
    "providecommand": (1, 2, 1), "newcommand": (1, 2, 1), "renewcommand": (1, 2, 1),
    "newenvironment": (1, 2, 2), "renewenvironment": (1, 2, 2), "tikzset": (0, 0, 1),
    "definecolor": (0, 0, 3), "colorlet": (0, 0, 2), "newcolumntype": (1, 1, 1), "pgfmathsetmacro": (1, 0, 1),
    "DeclareMathOperator": (1, 0, 1)}


def hoist_definitions(body):
    """Move \newcommand/\newenvironment/\tikzset... found in the body to the preamble.
    \renewcommand{\arraystretch} stays (it is just dropped later)."""
    hoisted, out, pos = [], [], 0
    while True:
        m = DEF_RE.search(body, pos)
        if not m:
            out.append(body[pos:])
            break
        kind = m.group(1)
        nname, nopt, nreq = DEF_ARGS[kind]
        i = m.end()
        try:
            if nname:
                k = skip_ws(body, i)
                if body[k] == "{":
                    _, i = read_group(body, k)
                else:
                    mm = re.match(r"\\[A-Za-z@]+", body[k:])
                    i = k + mm.end()
            _, _, i = read_args(body, i, nopt, nreq)
        except Exception:
            out.append(body[pos:m.end()]); pos = m.end(); continue
        stmt = body[m.start():i]
        out.append(body[pos:m.start()])
        if "arraystretch" in stmt[:40]:
            out.append(stmt)
        else:
            hoisted.append(stmt)
        pos = i
    return "".join(out), "\n".join(hoisted)


def split_document(tex):
    i = tex.index("\\begin{document}")
    j = tex.index("\\end{document}")
    return tex[:i], tex[i + len("\\begin{document}"):j]


# ----------------------------------------------------------------- figures
def figure_names(preamble):
    """Environments / macros whose definition draws with TikZ."""
    envs, macros = {"tikzpicture"}, set()
    for m in re.finditer(r"\\(?:re)?newenvironment\{([A-Za-z]+)\}", preamble):
        line_end = preamble.find("\n\\new", m.end())
        if "tikzpicture" in preamble[m.end(): line_end if line_end > 0 else None][:600]:
            envs.add(m.group(1))
    for m in re.finditer(r"\\(?:provide|new|renew)command\{\\([A-Za-z]+)\}(\[\d\])?", preamble):
        line_end = preamble.find("\n\\new", m.end())
        body = preamble[m.end(): line_end if line_end > 0 else None][:800]
        if "begin{tikzpicture}" in body:
            macros.add((m.group(1), int(m.group(2)[1]) if m.group(2) else 0))
    macros = {x for x in macros if x[0] not in ("fbicon", "igicon", "tgicon", "PageBox", "SocialRow")}
    return envs, macros


class Figures:
    def __init__(self, preamble, cache):
        self.preamble = preamble
        self.cache = cache
        self.items = []  # (key, source, inline)
        os.makedirs(cache, exist_ok=True)

    def add(self, src, inline):
        key = hashlib.sha1((self.preamble + "\0" + src).encode()).hexdigest()[:16]
        self.items.append((key, src, inline))
        return mk("FIG|%s|%d" % (key, inline))

    def png(self, key):
        return os.path.join(self.cache, key + ".png")

    def build(self, log):
        todo, seen = [], set()
        for key, src, inline in self.items:
            if key not in seen and not os.path.exists(self.png(key)):
                todo.append((key, src, inline))
            seen.add(key)
        log("figures: %d total, %d to compile" % (len(seen), len(todo)))
        if not todo:
            return
        tmp = tempfile.mkdtemp(prefix="tex2docx_")
        try:
            ok = self._compile(todo, tmp, log)
            if not ok:  # fall back to one document per figure
                log("batch compile mismatch -> compiling figures one by one")
                with ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
                    list(ex.map(lambda it: self._compile([it], tempfile.mkdtemp(dir=tmp), log), todo))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _compile(self, items, tmp, log):
        pre = self.preamble
        # tall page, same text width; no header/footer
        pre += "\n\\geometry{paperheight=100cm,top=1cm,bottom=1cm}\n"
        body = []
        for key, src, inline in items:
            body.append("\\begin{LTR}\\noindent " + src + "\\end{LTR}\\par\\clearpage\n")
        doc = pre + "\\begin{document}\\pagestyle{empty}\n" + "".join(body) + "\\end{document}\n"
        with open(os.path.join(tmp, "f.tex"), "w") as f:
            f.write(doc)
        subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error" if len(items) == 1 else "-interaction=nonstopmode", "f.tex"],
                       cwd=tmp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf = os.path.join(tmp, "f.pdf")
        if not os.path.exists(pdf):
            log("  !! figure compile failed: %s" % items[0][1][:80].replace("\n", " "))
            return False
        n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
        if n != len(items):
            return False
        subprocess.run(["pdftoppm", "-r", str(DPI), "-png", pdf, os.path.join(tmp, "p")], check=True)
        pages = sorted(f for f in os.listdir(tmp) if f.startswith("p-") and f.endswith(".png"))

        def trim(args):
            (key, _, _), page = args
            # Pillow, not ImageMagick: "convert" clashes with a Windows system command
            from PIL import Image, ImageChops, ImageOps
            im = Image.open(os.path.join(tmp, page)).convert("RGB")
            box = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
            if box:
                im = im.crop(box)
            ImageOps.expand(im, border=4, fill="white").save(self.png(key))
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
            list(ex.map(trim, zip(items, pages)))
        return True

    def size_cm(self, key):
        from PIL import Image
        w, h = Image.open(self.png(key)).size
        return w / DPI * 2.54, h / DPI * 2.54


def extract_figures(body, preamble, figs):
    envs, macros = figure_names(preamble)
    for name in envs - {"tikzpicture"}:   # plain-TeX form \TAB ... \endTAB
        body = re.sub(r"\\end%s(?![A-Za-z])" % name, r"\\end{%s}" % name, body)
        body = re.sub(r"\\%s(?![A-Za-z])" % name, r"\\begin{%s}" % name, body)
    # environments (outermost first, scanning left to right)
    pat = re.compile(r"\\begin\{(" + "|".join(sorted(envs, key=len, reverse=True)) + r")\}")
    out, pos = [], 0
    while True:
        m = pat.search(body, pos)
        if not m:
            out.append(body[pos:])
            break
        name = m.group(1)
        _, after = find_env_end(body, name, m.end())
        src = body[m.start():after]
        inline = name == "tikzpicture" and "baseline" in src[:120]
        out.append(body[pos:m.start()])
        out.append(figs.add(src, inline) if inline else "\n\n" + figs.add(src, False) + "\n\n")
        pos = after
    body = "".join(out)
    for name, n in macros:
        body = replace_macro(body, name, 0, n,
                             lambda o, r, name=name: figs.add("\\%s%s" % (name, "".join("{%s}" % x for x in r)), True))
    body = replace_macro(body, "tikz", 1, 1, lambda o, r: figs.add("\\tikz[%s]{%s}" % (o[0] or "", r[0]), True))
    return body


# ----------------------------------------------------------------- body rewriting
def clean_inline(s):
    """Strip font/colour commands from banner/header text."""
    s = re.sub(r"\\(color|textcolor)\{[^}]*\}", "", s)
    s = re.sub(r"\\fontsize\{[^}]*\}\{[^}]*\}", "", s)
    s = re.sub(r"\\(selectfont|bfseries|mdseries|large|Large|LARGE|huge|Huge|small|footnotesize|normalsize|centering)(?![A-Za-z])", "", s)
    s = re.sub(r"\\(ar|foreignlanguage\{[a-z]+\})", "", s)
    s = s.replace("--", "–")
    s = re.sub(r"[{}]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def rewrite_body(body, meta):
    exo = [0]

    # title banner(s)
    def banner(m):
        content = re.sub(r"^\s*\[[^\]]*\{[^}]*\}[^\]]*\]|^\s*\[[^\]]*\]", "", m.group(1), count=1)
        lines = [clean_inline(x) for x in re.split(r"\\\\(?:\[[^\]]*\])?", content)]
        lines = [x for x in lines if x]
        return "\n\n" + mk("TITLE+") + "\n\n" + "\n\n".join(lines) + "\n\n" + mk("TITLE-") + "\n\n"
    body = re.sub(r"\\begin\{tcolorbox\}(.*?)\\end\{tcolorbox\}", banner, body, flags=re.S)

    # boxes
    def box_begin(color, title):
        return "\n\n" + mk("B+|" + color) + " " + title + "\n\n"
    BOX_END = "\n\n" + mk("B-") + "\n\n"
    for env, (col, deft) in BOXENVS.items():
        body = replace_macro(body, "begin{%s}" % env, 1, 0, lambda o, r, col=col, deft=deft: box_begin(col, o[0] or deft))
        body = body.replace("\\end{%s}" % env, BOX_END)

    def tamrin(o, r):
        exo[0] += 1
        return box_begin("cSec", "التمرين %d: %s" % (exo[0], r[0]))

    def tmr(o, r):
        exo[0] += 1
        return box_begin("cSec", "تمرين محلول %d" % exo[0])

    # tamrin / tmr / hal in document order (counter)
    pat = re.compile(r"\\begin\{(tamrin|tmr|hal)\}")
    out, pos = [], 0
    while True:
        m = pat.search(body, pos)
        if not m:
            out.append(body[pos:])
            break
        out.append(body[pos:m.start()])
        if m.group(1) == "tamrin":
            _, r, end = read_args(body, m.end(), 0, 1)
            out.append(tamrin(None, r))
        elif m.group(1) == "tmr":
            out.append(tmr(None, None))
            end = m.end()
        else:
            out.append(box_begin("cSol", "حل التمرين %d" % exo[0]))
            end = m.end()
        pos = end
    body = "".join(out)
    for env in ("tamrin", "tmr", "hal"):
        body = body.replace("\\end{%s}" % env, BOX_END)
    body = replace_macro(body, "begin{BOX}", 0, 2, lambda o, r: box_begin(r[0], r[1]))
    body = body.replace("\\end{BOX}", BOX_END)
    body = replace_macro(body, "begin{arbox}", 1, 2, lambda o, r: box_begin(r[0], r[1]))
    body = body.replace("\\end{arbox}", BOX_END)

    # language wrappers
    body = re.sub(r"\\(begin|end)\{LTR\}", "", body)
    body = re.sub(r"\\begin\{otherlanguage\}\{[a-z]+\}|\\end\{otherlanguage\}", "", body)
    body = re.sub(r"\\selectlanguage\{[a-z]+\}", "", body)
    body = replace_macro(body, "foreignlanguage", 0, 2, lambda o, r: "{%s}" % r[1])
    body = replace_macro(body, "ar", 0, 1, lambda o, r: "{%s}" % r[0])

    # highlights
    body = replace_macro(body, "bxt", 0, 1, lambda o, r: "\\textsc{%s}" % r[0])

    # sub-questions
    for k, letter in enumerate(ARLETTERS):
        q = "abcde"[k]
        body = re.sub(r"\\q%s(?![A-Za-z])\s*" % q, "\n\n" + mk("IND") + "\\\\textbf{(%s)} " % letter, body)
        body = re.sub(r"\\p%s(?![A-Za-z])\s*" % q, "\n\n\\\\textbf{(%s)} " % letter, body)
    body = re.sub(r"\\begin\{sq\}|\\end\{sq\}", "\n\n", body)
    body = replace_macro(body, "QQ", 0, 1, lambda o, r: "\n\n\\textbf{%s.} " % r[0])
    body = replace_macro(body, "ABC", 0, 3, lambda o, r: "\n\n\\textbf{(أ)} %s\\qquad \\textbf{(ب)} %s\\qquad \\textbf{(جـ)} %s\n\n" % tuple(r))

    # lists whose items all carry a label -> plain indented paragraphs
    def labelled_lists(s, env):
        out, pos = [], 0
        pat = re.compile(r"\\begin\{%s\}(\[[^\]]*\])?" % env)
        while True:
            m = pat.search(s, pos)
            if not m:
                out.append(s[pos:])
                return "".join(out)
            bend, after = find_env_end(s, env, m.end())
            inner = s[m.end():bend]
            items = re.findall(r"\\item(?![A-Za-z])\s*(\[)?", inner)
            out.append(s[pos:m.start()])
            if items and all(items) and "\\begin{%s}" % env not in inner:
                inner = re.sub(r"\\item\s*\[([^\]]*)\]\s*", lambda mm: "\n\n" + mk("IND") + mm.group(1) + " ", inner)
                out.append("\n\n" + inner + "\n\n")
            else:
                out.append(s[m.start():m.end()] if not m.group(1) else "\\begin{%s}" % env)
                out.append(labelled_lists(inner, env))
                out.append("\\end{%s}" % env)
            pos = after
    for env in ("itemize", "enumerate"):
        body = labelled_lists(body, env)

    # side-by-side blocks
    def twocol(o, r):
        w1, w2 = (re.sub(r"[^\d.]", "", x) or "0.5" for x in (r[0], r[2]))
        return ("\n\n" + mk("MP+|" + w1) + "\n\n" + r[1] + "\n\n" + mk("MP-") + "\n\n" + mk("MP+|" + w2) + "\n\n"
                + r[3] + "\n\n" + mk("MP-") + "\n\n")
    body = replace_macro(body, "TwoCol", 0, 4, twocol)
    body = replace_macro(body, "RL", 0, 4, lambda o, r: twocol(None, [r[2], r[3], r[0], r[1]]))
    body = re.sub(r"\\begin\{minipage\}(\[[^\]]*\])?\{[^}]*\}", "\n\n" + mk("MP+") + "\n\n", body)
    body = body.replace("\\end{minipage}", "\n\n" + mk("MP-") + "\n\n")
    body = re.sub(r"\\begin\{multicols\}\{\d+\}|\\end\{multicols\}", "\n\n", body)

    # centering, page breaks, spacing
    body = body.replace("\\begin{center}", "\n\n" + mk("C+") + "\n\n").replace("\\end{center}", "\n\n" + mk("C-") + "\n\n")
    body = re.sub(r"\\(clearpage|newpage)\b", "\n\n" + mk("PB") + "\n\n", body)
    body = re.sub(r"\\(origNeedspace|Needspace\*?)\{[^}]*\}", "", body)
    body = re.sub(r"\\(vspace|hspace)\*?\{[^}]*\}", " ", body)
    body = re.sub(r"\\(smallskip|medskip|bigskip|noindent|centering|hfill|tiny|scriptsize|footnotesize|small|normalsize|large|Large|LARGE)(?![A-Za-z])", "", body)
    body = re.sub(r"\\renewcommand\{\\arraystretch\}\{[^}]*\}", "", body)
    body = re.sub(r"\\newline(?![A-Za-z])\s*", mk("BR") + " ", body)
    body = re.sub(r"\\rule(\[[^\]]*\])?\{[^}]*\}\{[^}]*\}", "", body)        # struts
    body = re.sub(r"\\\\\s*\[[-\d.]+\s*(pt|em|ex|mm|cm)\]", r"\\\\", body)   # \\[4pt] -> \\

    # tables
    def colspec(m):
        spec = m.group(1)
        spec = re.sub(r"[><@!]\{(?:[^{}]|\{[^{}]*\})*\}", "", spec)
        spec = re.sub(r"[MLR](?=\{)", "p", spec)   # custom array column types (M{..} etc.) -> p{..}
        spec = spec.replace("|", "").replace("C", "c").replace("\\textwidth", "\\linewidth")
        spec = re.sub(r"\{([\d.]+)\s*cm\}", lambda mm: "{%.3f\\linewidth}" % (float(mm.group(1)) / TEXT_W), spec)
        return "\\begin{tabular}{%s}" % spec
    body = re.sub(r"\\begin\{tabular\}\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}", colspec, body)
    body = re.sub(r"\\rowcolor(\[[^\]]*\])?\{[^}]*\}\s*", mk("HDR"), body)
    body = re.sub(r"\\cellcolor(\[[^\]]*\])?\{[^}]*\}\s*", mk("CELL"), body)
    body = body.replace("\\arraybackslash", "")
    return body


# ----------------------------------------------------------------- math / text segmentation
ARABIC = re.compile(r"[\u0600-\u06FF]")
MATH_ENVS = ("align*", "align", "equation*", "equation", "gather*", "gather", "multline*", "eqnarray*")


def segments(s):
    """Yield (kind, text) with kind in 'text', 'inline', 'display', 'env' (text includes delimiters)."""
    i, start, n = 0, 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            if s.startswith("\\[", i) or s.startswith("\\(", i):
                close = "\\]" if s[i + 1] == "[" else "\\)"
                j = s.find(close, i + 2)
                if j < 0:
                    break
                yield "text", s[start:i]
                yield ("display" if close == "\\]" else "inline"), s[i:j + 2]
                i = start = j + 2
                continue
            m = re.match(r"\\begin\{(" + "|".join(re.escape(e) for e in MATH_ENVS) + r")\}", s[i:])
            if m:
                _, after = find_env_end(s, m.group(1), i + m.end())
                yield "text", s[start:i]
                yield "env", s[i:after]
                i = start = after
                continue
            i += 2
            continue
        if c == "$":
            disp = s.startswith("$$", i)
            d = "$$" if disp else "$"
            j = i + len(d)
            while j < n:
                if s[j] == "\\":
                    j += 2
                    continue
                if s.startswith(d, j):
                    break
                j += 1
            yield "text", s[start:i]
            yield ("display" if disp else "inline"), s[i:j + len(d)]
            i = start = j + len(d)
            continue
        i += 1
    yield "text", s[start:]


SPACES = [(r"\qquad", "\u2003\u2003"), (r"\quad", "\u2003"), (r"\,", "\u2009"), (r"\;", " "), (r"\enspace", "\u2002")]


def text_spaces(t):
    for a, b in SPACES:
        t = re.sub(re.escape(a) + r"(?![A-Za-z])", b, t)
    return t


def split_arabic_math(inner, display):
    """Split math content at top-level \\text{arabic} into [('m',..),('t',..)]."""
    parts, buf, depth, i = [], [], 0, 0
    while i < len(inner):
        mt = re.match(r"\\(text|mbox|textrm|textnormal)\{", inner[i:]) if depth == 0 else None
        if mt:
            content, end = read_group(inner, i + mt.end() - 1)
            if ARABIC.search(content):
                parts.append(("m", "".join(buf))); buf = []
                parts.append(("t", content))
                i = end
                continue
        ch = inner[i]
        if ch == "\\":
            buf.append(inner[i:i + 2]); i += 2; continue
        depth += ch == "{"
        depth -= ch == "}"
        buf.append(ch); i += 1
    parts.append(("m", "".join(buf)))
    if len(parts) == 1:
        return None
    out = []
    for k, v in parts:
        if k == "t":
            out.append(v)
        else:
            core = re.sub(r"\\(qquad|quad|,|;|!|enspace)(?![A-Za-z])", " ", v).strip()
            if core:
                lead = "\u2003" if re.match(r"\s*\\q", v) else " "
                trail = "\u2003" if re.search(r"\\q+uad\s*$", v) else " "
                sp = r"(?:\s|\\[ ,;:!]|\\q?quad(?![A-Za-z]))+"
                vv = re.sub("^" + sp + "|" + sp + "$", "", v)
                if re.fullmatch(r"[.,;:]+", vv):
                    out.append(vv)
                else:
                    out.append(lead + "$" + ("\\displaystyle " if display else "") + vv + "$" + trail)
            else:
                out.append(text_spaces(v) if v.strip() else " ")
    return "".join(out)


def fix_math_text(body):
    out = []
    for kind, t in segments(body):
        if kind == "text":
            out.append(text_spaces(t))
        elif kind in ("inline", "display"):
            d = 2 if t.startswith(("$$", "\\[", "\\(")) else 1
            inner = t[d:-d]
            r = split_arabic_math(inner, kind == "display")
            if r is None:
                out.append(t)
            elif kind == "display":
                out.append("\n\n" + mk("C+") + "\n\n" + r + "\n\n" + mk("C-") + "\n\n")
            else:
                out.append(r)
        else:
            out.append(t)
    return "".join(out)


PANDOC_MACROS = r"""
\newcommand{\N}{\mathbb{N}}\newcommand{\Z}{\mathbb{Z}}\newcommand{\D}{\mathbb{D}}
\newcommand{\Q}{\mathbb{Q}}\newcommand{\R}{\mathbb{R}}\newcommand{\C}{\mathbb{C}}
\newcommand{\pgcd}{\operatorname{PGCD}}\newcommand{\ppcm}{\operatorname{PPCM}}
\newcommand{\bx}[1]{\ensuremath{\boxed{#1}}}
\newcommand{\ok}{$\checkmark$}
\newcommand{\texttimes}{×}
\newcommand{\limn}{\lim\limits_{n\to+\infty}}
\newcommand{\dx}{\,\mathrm{d}x}\newcommand{\dt}{\,\mathrm{d}t}\newcommand{\ua}{\ \mathrm{u.a}}
"""


_NOT_MATH = re.compile(r"tikz|tcb|\\begin|\\color|\\fill|\\draw|\\node|\\foreignlanguage|\\ar\b|\\selectfont|\\hbox|\\vbox|\\par\b|\\item|TwoCol|baselineskip|Needspace|@")


def math_macros(preamble, body):
    """Pure-math \\newcommand definitions of the document (e.g. \\V for vectors), so pandoc
    expands them; otherwise a math span using them is left as raw text. Only macros that
    the body actually uses inside math are passed on."""
    used = set()
    for mm in re.finditer(r"\$\$.*?\$\$|\$[^$]*\$|\\\[.*?\\\]", body, re.S):
        used.update(re.findall(r"\\([A-Za-z]+)", mm.group(0)))
    have = set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", PANDOC_MACROS)) | {"dots", "ldots", "cdots"}
    out = []
    for m in re.finditer(r"\\(?:provide|new|renew)command\*?\s*\{?\\([A-Za-z]+)\}?\s*(\[\d\])?\s*(?=\{)", preamble):
        name = m.group(1)
        if name in have or name not in used:
            continue
        try:
            _, (defn,), _ = read_args(preamble, m.end(), 0, 1)
        except Exception:
            continue
        if _NOT_MATH.search(defn):
            continue
        out.append("\\newcommand{\\%s}%s{%s}" % (name, m.group(2) or "", defn))
        have.add(name)
    for m in re.finditer(r"\\DeclareMathOperator\*?\{\\([A-Za-z]+)\}\{([^{}]*)\}", preamble):
        if m.group(1) not in have:
            out.append("\\newcommand{\\%s}{\\operatorname{%s}}" % (m.group(1), m.group(2)))
    return "\n".join(out) + "\n"


def header_text(preamble):
    m = re.search(r"^\\SetHeader", preamble, re.M)
    if not m:
        return "", ""
    _, r, _ = read_args(preamble, m.end(), 0, 2)
    return clean_inline(r[0]), clean_inline(r[1])


# ----------------------------------------------------------------- reference.docx
def make_reference(path):
    subprocess.run(["pandoc", "-o", path, "--print-default-data-file", "reference.docx"], check=True)
    d = docx.Document(path)
    st = d.styles
    for s in st:
        if s.type != 1:  # paragraph/char styles only
            continue
        rpr = s.element.get_or_add_rPr()
        fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = OxmlElement("w:rFonts")
            rpr.insert(0, fonts)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            fonts.set(qn(a), FONT)
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            if fonts.get(qn(a)) is not None:
                del fonts.attrib[qn(a)]
    byname = {x.name: x for x in st}
    normal = byname["Normal"]
    normal.font.size = Pt(13)
    rpr = normal.element.get_or_add_rPr()
    for tag, val in (("w:szCs", "26"),):
        e = OxmlElement(tag); e.set(qn("w:val"), val); rpr.append(e)
    lang = OxmlElement("w:lang"); lang.set(qn("w:val"), "fr-FR"); lang.set(qn("w:bidi"), "ar-DZ"); rpr.append(lang)
    ppr = normal.element.get_or_add_pPr()
    ppr.append(OxmlElement("w:bidi"))
    for name, col, size in (("Heading 1", "1F3A68", 18), ("Heading 2", "8F1E18", 15), ("Heading 3", "1F3A68", 13)):
        if name in byname:
            h = byname[name]
            h.font.color.rgb = RGBColor.from_string(col)
            h.font.size = Pt(size)
            h.font.bold = True
            hr = h.element.get_or_add_rPr()
            e = OxmlElement("w:szCs"); e.set(qn("w:val"), str(size * 2)); hr.append(e)
            e = OxmlElement("w:bCs"); hr.append(e)
    if "Heading 1" in byname:  # rule under section titles
        p = byname["Heading 1"].element.get_or_add_pPr()
        bdr = OxmlElement("w:pBdr"); b = OxmlElement("w:bottom")
        for k, v in (("w:val", "single"), ("w:sz", "8"), ("w:space", "1"), ("w:color", "8FA0BC")):
            b.set(qn(k), v)
        bdr.append(b); p.append(bdr)
    for name in ("Body Text", "First Paragraph", "Compact"):
        if name in byname:
            pf = byname[name].paragraph_format
            pf.space_before, pf.space_after = Pt(2), Pt(3)
    for stl in d.styles.element.findall(qn("w:style")):
        fix_order(stl)
    for e in d.styles.element.iter():
        if e.text and e.text.strip() and e.tag in (qn("w:rPr"), qn("w:pPr"), qn("w:style")):
            e.text = None   # stray '>' in pandoc's default reference.docx
    sect = d.sections[0]
    sect.page_width, sect.page_height = Cm(21), Cm(29.7)
    sect.left_margin = sect.right_margin = Cm(1.7)
    sect.top_margin, sect.bottom_margin = Cm(2.0), Cm(2.0)
    d.save(path)


# ----------------------------------------------------------------- post-processing
def mix(hexcol, pct, other="FFFFFF"):
    a = [int(hexcol[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(other[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join("%02X" % round(x * pct / 100 + y * (100 - pct) / 100) for x, y in zip(a, b))


def color_hex(spec):
    """xcolor-ish: cDef, cDef!80!black, cSec!12."""
    parts = spec.split("!")
    base = COLORS.get(parts[0], "1F3A68")
    if len(parts) >= 2:
        other = {"black": "000000", "white": "FFFFFF"}.get(parts[2] if len(parts) > 2 else "white", "FFFFFF")
        base = mix(base, int(parts[1]), other)
    return base


def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn("w:" + k), str(v))
    return e


def set_shd(parent_pr, fill):
    for old in parent_pr.findall(qn("w:shd")):
        parent_pr.remove(old)
    parent_pr.append(el("w:shd", val="clear", color="auto", fill=fill))


def borders(tag, color, sz=8, sides=("top", "left", "bottom", "right", "insideH", "insideV"), val="single"):
    b = OxmlElement(tag)
    for s in sides:
        b.append(el("w:" + s, val=val, sz=sz, space=0, color=color))
    return b


def para_text(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))


def strip_marker(p):
    """Remove the ⟦...⟧ marker text from paragraph p; return marker string."""
    found = None
    for t in p.iter(qn("w:t")):
        if t.text and M_OPEN in t.text:
            m = MK.search(t.text)
            if m:
                found = m.group(1)
                t.text = (t.text[:m.start()] + t.text[m.end():]).lstrip()
                break
    # drop now-empty runs at the start
    return found


def new_table(widths_cm, bidi=False):
    tbl = OxmlElement("w:tbl")
    pr = OxmlElement("w:tblPr")
    pr.append(el("w:tblW", w=int(sum(widths_cm) / 2.54 * 1440), type="dxa"))
    pr.append(el("w:jc", val="center"))
    if bidi:
        pr.append(OxmlElement("w:bidiVisual"))
    pr.append(el("w:tblLayout", type="fixed"))
    tbl.append(pr)
    grid = OxmlElement("w:tblGrid")
    for w in widths_cm:
        grid.append(el("w:gridCol", w=int(w / 2.54 * 1440)))
    tbl.append(grid)
    return tbl


def new_cell(width_cm):
    tc = OxmlElement("w:tc")
    tcpr = OxmlElement("w:tcPr")
    tcpr.append(el("w:tcW", w=int(width_cm / 2.54 * 1440), type="dxa"))
    tc.append(tcpr)
    return tc


def ensure_ppr(p):
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        p.insert(0, ppr)
    return ppr


def set_jc(p, val):
    ppr = ensure_ppr(p)
    for old in ppr.findall(qn("w:jc")):
        ppr.remove(old)
    ppr.append(el("w:jc", val=val))


def color_runs(p, hexcol, bold=False, size=None):
    for r in p.iter(qn("w:r"), qn("m:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is None:
            rpr = OxmlElement("w:rPr")
            mrpr = r.find(qn("m:rPr"))
            if mrpr is not None:   # m:r content order: m:rPr, w:rPr, m:t
                mrpr.addnext(rpr)
            else:
                r.insert(0, rpr)
        rpr.append(el("w:color", val=hexcol))
        if bold:
            rpr.append(OxmlElement("w:b")); rpr.append(OxmlElement("w:bCs"))
        if size:
            rpr.append(el("w:sz", val=size * 2)); rpr.append(el("w:szCs", val=size * 2))


TEXT_W = 21 - 2 * 1.7


def postprocess(path, out, head, foot, figs):
    d = docx.Document(path)
    body = d.element.body

    # --- 1. figures: replace FIG markers by pictures
    for p in list(body.iter(qn("w:p"))):
        txt = para_text(p)
        if M_OPEN + "FIG|" not in txt:
            continue
        # rebuild paragraph content: split text on markers, insert pictures
        P = docx.text.paragraph.Paragraph(p, d._body)
        runs = list(p.iter(qn("w:r")))
        for r in runs:
            t = r.find(qn("w:t"))
            if t is None or not t.text or M_OPEN + "FIG|" not in t.text:
                continue
            parts = re.split("(" + M_OPEN + r"FIG\|[0-9a-f]+\|\d" + M_CLOSE + ")", t.text)
            anchor = r
            for part in parts:
                if not part:
                    continue
                m = re.match(M_OPEN + r"FIG\|([0-9a-f]+)\|(\d)" + M_CLOSE, part)
                nr = deepcopy(r)
                for c in list(nr):
                    if c.tag != qn("w:rPr"):
                        nr.remove(c)
                if m:
                    key, inline = m.group(1), m.group(2) == "1"
                    if not os.path.exists(figs.png(key)):
                        print("  !! missing figure %s (compile failed) -> placeholder" % key, file=sys.stderr)
                        tt = el("w:t"); tt.text = "[شكل غير متوفر]"; nr.append(tt)
                        anchor.addnext(nr); anchor = nr
                        continue
                    w, h = figs.size_cm(key)
                    if w > TEXT_W - 0.6:
                        h, w = h * (TEXT_W - 0.6) / w, TEXT_W - 0.6
                    tmp_run = P.add_run()
                    tmp_run.add_picture(figs.png(key), width=Cm(w))
                    nr = tmp_run._r
                    p.remove(nr)
                else:
                    tt = el("w:t"); tt.text = part; tt.set(qn("xml:space"), "preserve"); nr.append(tt)
                anchor.addnext(nr)
                anchor = nr
            r.getparent().remove(r)
        if not para_text(p).strip():
            set_jc(p, "center")

    # --- 2. block markers (boxes, title, centre, side-by-side)
    stack = []
    for p in list(body):
        if p.tag != qn("w:p"):
            continue
        txt = para_text(p).strip()
        m = MK.match(txt)
        if not m:
            continue
        tag = m.group(1)
        if tag.startswith(("B+", "TITLE+", "C+", "MP+")):
            stack.append((tag, p))
        elif tag in ("B-", "TITLE-", "C-", "MP-"):
            if not stack:
                p.getparent().remove(p); continue
            btag, bp = stack.pop()
            inner = []
            n = bp.getnext()
            while n is not None and n is not p:
                inner.append(n)
                n = n.getnext()
            if btag.startswith("B+"):
                make_box(bp, inner, btag.split("|", 1)[1])
            elif btag == "TITLE+":
                make_title(bp, inner)
                bp.getparent().remove(bp)
            elif btag == "C+":
                for e in inner:
                    if e.tag == qn("w:p"):
                        set_jc(e, "center")
                    elif e.tag == qn("w:tbl"):
                        pr = e.find(qn("w:tblPr"))
                        for o in pr.findall(qn("w:jc")):
                            pr.remove(o)
                        pr.append(el("w:jc", val="center"))
                bp.getparent().remove(bp)
            elif btag.startswith("MP+"):
                wrap = OxmlElement("w:MPGROUP")  # temporary holder
                wrap.set("frac", btag.split("|", 1)[1] if "|" in btag else "")
                bp.addprevious(wrap)
                for e in inner:
                    wrap.append(e)
                bp.getparent().remove(bp)
            p.getparent().remove(p)
    # group consecutive MPGROUPs into a borderless table (LTR: source order = left to right)
    for holder in list(body.iter(qn("w:MPGROUP"))):
        if holder.getparent() is None:
            continue
        group = [holder]
        n = holder.getnext()
        while n is not None and (n.tag == qn("w:MPGROUP") or (n.tag == qn("w:p") and not para_text(n).strip()
                                                                and not list(n.iter(qn("w:drawing"))))):
            if n.tag == qn("w:MPGROUP"):
                group.append(n)
            n = n.getnext()
        if len(group) > 1 and any(g.find(".//" + qn("w:tbl")) is not None or g.find(qn("w:tbl")) is not None
                                  for g in group):
            # a box (table) beside a figure does not fit in half a page in Word: it gets clipped.
            # Stack the columns instead, right column first (Arabic reading order), figures centred.
            anchor = group[0]
            for g in reversed(group):
                for e in list(g):
                    if e.tag == qn("w:p") and list(e.iter(qn("w:drawing"))):
                        set_jc(e, "center")
                    anchor.addprevious(e)
            for g in group:
                g.getparent().remove(g)
            continue
        try:
            fr = [float(g.get("frac")) for g in group]
            ws = [TEXT_W * f / sum(fr) for f in fr]
        except (TypeError, ValueError):
            ws = [TEXT_W / len(group)] * len(group)
        tbl = new_table(ws)
        tbl.find(qn("w:tblPr")).append(borders("w:tblBorders", "FFFFFF", 0, val="nil"))
        tr = OxmlElement("w:tr")
        tbl.append(tr)
        for g, w in zip(group, ws):
            tc = new_cell(w)
            for e in list(g):
                tc.append(e)
            if not len(tc.findall(qn("w:p"))) and not len(tc.findall(qn("w:tbl"))):
                tc.append(OxmlElement("w:p"))
            if tc[-1].tag == qn("w:tbl"):
                tc.append(OxmlElement("w:p"))
            tr.append(tc)
        group[0].addprevious(tbl)
        for g in group:
            g.getparent().remove(g)
    # line breaks (\newline, also valid inside table cells)
    for t in list(body.iter(qn("w:t"))):
        if not t.text or mk("BR") not in t.text:
            continue
        r = t.getparent()
        pieces = t.text.split(mk("BR"))
        t.text = pieces[0]
        anchor = r
        for piece in pieces[1:]:
            nr = deepcopy(r)
            for c in list(nr):
                if c.tag != qn("w:rPr"):
                    nr.remove(c)
            nr.append(OxmlElement("w:br"))
            tt = el("w:t"); tt.text = piece.lstrip(); tt.set(qn("xml:space"), "preserve"); nr.append(tt)
            anchor.addnext(nr); anchor = nr
    # page breaks and inline markers
    for p in list(body.iter(qn("w:p"))):
        txt = para_text(p)
        if M_OPEN not in txt:
            continue
        if txt.strip() == mk("PB"):
            for r in list(p):
                if r.tag != qn("w:pPr"):
                    p.remove(r)
            r = OxmlElement("w:r"); r.append(el("w:br", type="page")); p.append(r)
            continue
        while True:
            tag = strip_marker(p)
            if tag is None:
                break
            if tag == "IND":
                ppr = ensure_ppr(p)
                ppr.append(el("w:ind", left=567))  # ECMA-376: in a bidi paragraph w:left is the leading (right) side; LibreOffice ignores it
            elif tag in ("HDR", "CELL"):
                tc = p.getparent()
                if tc.tag != qn("w:tc"):
                    continue
                cells = [tc] if tag == "CELL" else tc.getparent().findall(qn("w:tc"))
                for c in cells:
                    tcpr = c.find(qn("w:tcPr"))
                    if tcpr is None:
                        tcpr = OxmlElement("w:tcPr"); c.insert(0, tcpr)
                    set_shd(tcpr, color_hex("cSec!12"))
            else:
                print("  ?? unknown marker", tag, file=sys.stderr)

    # --- 3. \bxt highlights: smallCaps runs -> shaded runs
    for rpr in list(body.iter(qn("w:rPr"))):
        sc = rpr.find(qn("w:smallCaps"))
        if sc is not None:
            rpr.remove(sc)
            set_shd(rpr, color_hex("cDef!12"))

    # --- 3b. two tables in a row (or a table followed by text) must not touch: Word glues them
    for tbl in list(body.iter(qn("w:tbl"))):
        nxt = tbl.getnext()
        if nxt is not None and nxt.tag == qn("w:tbl"):
            tbl.addnext(OxmlElement("w:p"))
        elif nxt is not None and nxt.tag == qn("w:p"):
            ppr = ensure_ppr(nxt)
            if ppr.find(qn("w:spacing")) is None:
                ppr.append(el("w:spacing", before=120))
    # --- 4. data tables (from tabular): borders, LTR column order, RTL cell text
    for tbl in body.iter(qn("w:tbl")):
        pr = tbl.find(qn("w:tblPr"))
        if pr.find(qn("w:tblStyle")) is not None and pr.find(qn("w:tblBorders")) is None:
            for o in pr.findall(qn("w:bidiVisual")):
                pr.remove(o)
            pr.append(borders("w:tblBorders", "000000", 4))
            for o in pr.findall(qn("w:jc")):
                pr.remove(o)
            pr.append(el("w:jc", val="center"))
            nested = tbl.getparent().tag == qn("w:tc")
            avail = int((TEXT_W - (0.8 if nested else 0.2)) / 2.54 * 1440)
            cols = tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol"))
            if len({c.get(qn("w:w")) for c in cols}) == 1 and pr.find(qn("w:tblW")).get(qn("w:type")) == "auto":
                # no explicit widths in the source: size the columns by their content ourselves
                # (Word keeps pandoc's equal grid, which cuts a long first column such as lim f(x))
                need = [3.0] * len(cols)
                for tr in tbl.findall(qn("w:tr")):
                    for k, tc in enumerate(tr.findall(qn("w:tc"))[:len(cols)]):
                        txt = "".join(t.text or "" for t in tc.iter() if t.tag in (qn("w:t"), qn("m:t")))
                        need[k] = max(need[k], len(txt.strip()) + 1.5)
                tot_need = sum(need)
                # ~190 twips per character + 300 for the cell margins ("β\\α" must not wrap)
                raw = [n * 190 + 300 for n in need]
                scale = min(avail / sum(raw), 1.0)
                ws = [int(r_ * scale) for r_ in raw]
                for c, w_ in zip(cols, ws):
                    c.set(qn("w:w"), str(w_))
                for o in pr.findall(qn("w:tblW")) + pr.findall(qn("w:tblLayout")):
                    pr.remove(o)
                pr.append(el("w:tblW", w=sum(ws), type="dxa"))
                pr.append(el("w:tblLayout", type="fixed"))
                for tr in tbl.findall(qn("w:tr")):
                    for tc, w_ in zip(tr.findall(qn("w:tc")), ws):
                        tcpr = tc.find(qn("w:tcPr"))
                        if tcpr is None:
                            tcpr = OxmlElement("w:tcPr"); tc.insert(0, tcpr)
                        for o in tcpr.findall(qn("w:tcW")):
                            tcpr.remove(o)
                        tcpr.insert(0, el("w:tcW", w=w_, type="dxa"))
                for o in pr.findall(qn("w:jc")):
                    pr.remove(o)
                pr.append(el("w:jc", val="center"))
                for tc in tbl.iter(qn("w:tc")):
                    for cp in tc.findall(qn("w:p")):
                        ppr = ensure_ppr(cp)
                        if ppr.find(qn("w:bidi")) is None:
                            ppr.append(OxmlElement("w:bidi"))
                        if ppr.find(qn("w:jc")) is None:
                            ppr.append(el("w:jc", val="center"))
                continue
            tot = sum(int(c.get(qn("w:w"))) for c in cols) or 1
            f = min(1.0, avail / tot)
            for c in cols:
                c.set(qn("w:w"), str(int(int(c.get(qn("w:w"))) * f)))
            for o in pr.findall(qn("w:tblW")):
                pr.remove(o)
            pr.append(el("w:tblW", w=int(tot * f), type="dxa"))
            for tc in tbl.iter(qn("w:tc")):
                for cp in tc.findall(qn("w:p")):
                    ppr = ensure_ppr(cp)
                    if ppr.find(qn("w:bidi")) is None:
                        ppr.append(OxmlElement("w:bidi"))
                    if ppr.find(qn("w:jc")) is None:
                        ppr.append(el("w:jc", val="center"))

    # --- 5. RTL on every paragraph + every run
    for p in body.iter(qn("w:p")):
        ppr = ensure_ppr(p)
        if ppr.find(qn("w:bidi")) is None:
            b = OxmlElement("w:bidi")
            ps = ppr.find(qn("w:pStyle"))
            (ps.addnext(b) if ps is not None else ppr.insert(0, b))
    for r in body.iter(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is None:
            rpr = OxmlElement("w:rPr"); r.insert(0, rpr)
        txt = "".join(t.text or "" for t in r.findall(qn("w:t")))
        latin = re.search(r"[A-Za-z0-9]", txt) and not ARABIC.search(txt)
        if rpr.find(qn("w:rtl")) is None and not latin:
            rpr.append(OxmlElement("w:rtl"))
        if latin and re.search(r"[A-Za-z]", txt) and r.getparent().tag == qn("w:p"):
            t0 = r.find(qn("w:t"))   # LRM: keep a leading number inside the Latin run (e.g. "5 nCr 2")
            if t0 is not None and t0.text and not t0.text.startswith("\u200e"):
                t0.text = "\u200e" + t0.text
    fix_order(body)

    # --- 6. header / footer
    sect = d.sections[0]
    sect.header_distance, sect.footer_distance = Cm(0.8), Cm(0.8)
    hp = sect.header.paragraphs[0]
    rp = hp.add_run(head[0]); rp.bold = True; rp.font.color.rgb = RGBColor.from_string("1F3A68")
    hp.add_run("\t\t")
    r2 = hp.add_run(head[1]); r2.font.color.rgb = RGBColor.from_string("1F3A68")
    para_rule(hp._p, "bottom")
    fp = sect.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run(FOOTER + "   |   prof_hicham_math   |   "); r.bold = True
    add_page_field(fp)
    para_rule(fp._p, "top")
    for p in list(sect.header.paragraphs) + list(sect.footer.paragraphs):
        ppr = ensure_ppr(p._p); ppr.insert(0, OxmlElement("w:bidi"))
        for rr in p._p.iter(qn("w:r")):
            rpr = rr.find(qn("w:rPr"))
            if rpr is None:
                rpr = OxmlElement("w:rPr"); rr.insert(0, rpr)
            rpr.append(OxmlElement("w:rtl")); rpr.append(el("w:sz", val=20)); rpr.append(el("w:szCs", val=20))
    fix_order(sect.header._element); fix_order(sect.footer._element)
    pgmar = sect._sectPr.find(qn("w:pgMar"))
    if pgmar is not None and pgmar.get(qn("w:gutter")) is None:
        pgmar.set(qn("w:gutter"), "0")
    d.save(out)


def fix_order(body):
    """w:pPr children must come in schema order; move bidi/jc/ind/shd into a valid order."""
    order = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid",
             "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
             "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]
    rorder = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline",
              "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing", "w",
              "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign",
              "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"]
    tcorder = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
               "textDirection", "tcFitText", "vAlign", "hideMark"]
    tblorder = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize",
                "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook",
                "tblCaption", "tblDescription"]

    def reorder(e, ordr):
        kids = list(e)
        seen = {}
        for k in kids:  # keep last occurrence of duplicates
            seen[k.tag] = k
        kids = list(seen.values())
        idx = {qn("w:" + n): i for i, n in enumerate(ordr)}
        kids.sort(key=lambda k: idx.get(k.tag, 999))
        for k in list(e):
            e.remove(k)
        for k in kids:
            e.append(k)
    for e in body.iter(qn("w:pPr")):
        reorder(e, order)
    for e in body.iter(qn("w:rPr")):
        if e.getparent().tag in (qn("w:r"), qn("m:r"), qn("w:pPr"), qn("w:style")):
            reorder(e, rorder)
    for e in body.iter(qn("w:tcPr")):
        reorder(e, tcorder)
    for e in body.iter(qn("w:tblPr")):
        reorder(e, tblorder)


def para_rule(p, side):
    ppr = ensure_ppr(p)
    bdr = OxmlElement("w:pBdr")
    bdr.append(el("w:" + side, val="single", sz=6, space=4, color="1F3A68"))
    ppr.append(bdr)
    ppr.append(el("w:tabs"))
    tabs = ppr.find(qn("w:tabs"))
    tabs.append(el("w:tab", val="center", pos=4960))
    tabs.append(el("w:tab", val="right", pos=9920))


def add_page_field(p):
    for typ, txt in (("begin", None), (None, " PAGE "), ("separate", None), (None, "1"), ("end", None)):
        r = OxmlElement("w:r")
        if typ:
            r.append(el("w:fldChar", fldCharType=typ))
        elif txt == " PAGE ":
            it = OxmlElement("w:instrText"); it.text = txt; it.set(qn("xml:space"), "preserve"); r.append(it)
        else:
            t = OxmlElement("w:t"); t.text = txt; r.append(t)
        p._p.append(r)


def make_box(title_p, inner, colspec):
    base = color_hex(colspec)
    frame = mix(base, 80, "000000")
    back = mix(base, 5)
    W = TEXT_W - 0.2
    tbl = new_table([W])
    pr = tbl.find(qn("w:tblPr"))
    pr.append(borders("w:tblBorders", frame, 10, ("top", "left", "bottom", "right", "insideH")))
    mar = el("w:tblCellMar")
    for s_, v in (("top", 40), ("left", 140), ("bottom", 60), ("right", 140)):
        mar.append(el("w:" + s_, w=v, type="dxa"))
    pr.append(mar)
    # row 1: title (white bold on the frame colour)
    tr1 = OxmlElement("w:tr")
    trpr = OxmlElement("w:trPr"); trpr.append(OxmlElement("w:cantSplit")); tr1.append(trpr)
    tc1 = new_cell(W); set_shd(tc1.find(qn("w:tcPr")), frame); tr1.append(tc1)
    # row 2: content
    tr2 = OxmlElement("w:tr")
    tc = new_cell(W); set_shd(tc.find(qn("w:tcPr")), back); tr2.append(tc)
    tbl.append(tr1); tbl.append(tr2)
    title_p.addprevious(tbl)
    strip_marker(title_p)
    ppr = ensure_ppr(title_p)
    for o in ppr.findall(qn("w:pStyle")):
        ppr.remove(o)
    ppr.append(el("w:spacing", before=0, after=0))
    ppr.append(el("w:keepNext"))
    color_runs(title_p, "FFFFFF", bold=True)
    tc1.append(title_p)
    for e in inner:
        tc.append(e)
    if not len(tc.findall(qn("w:p"))) or tc[-1].tag != qn("w:p"):
        tc.append(OxmlElement("w:p"))
    after = OxmlElement("w:p")  # small gap after the box
    ap = ensure_ppr(after); ap.append(el("w:spacing", before=0, after=0))
    tbl.addnext(after)


def make_title(marker_p, inner):
    base = COLORS["cSec"]
    tbl = new_table([TEXT_W])
    pr = tbl.find(qn("w:tblPr"))
    pr.append(borders("w:tblBorders", base, 4, ("top", "left", "bottom", "right")))
    tr = OxmlElement("w:tr"); tc = new_cell(TEXT_W); set_shd(tc.find(qn("w:tcPr")), base)
    tr.append(tc); tbl.append(tr)
    marker_p.addprevious(tbl)
    first = True
    for e in inner:
        if e.tag == qn("w:p"):
            set_jc(e, "center")
            color_runs(e, "FFFFFF", bold=first, size=26 if first else 15)
            ppr = ensure_ppr(e)
            for o in ppr.findall(qn("w:pStyle")):
                ppr.remove(o)
            ppr.append(el("w:spacing", before=120 if first else 0, after=120))
            first = False
        tc.append(e)
    tbl.addnext(OxmlElement("w:p"))


# ----------------------------------------------------------------- driver
def convert(tex_path, out_path, cache, keep=False, log=print):
    t0 = time.time()
    tex = strip_comments(open(tex_path, encoding="utf-8").read())
    preamble, body = split_document(tex)
    body, hoisted = hoist_definitions(body)
    if hoisted:
        preamble = preamble + "\n% --- definitions hoisted from the body\n" + hoisted + "\n"
    figs = Figures(preamble, cache)
    body = extract_figures(body, preamble, figs)
    body = rewrite_body(body, {})
    body = fix_math_text(body)
    # limits written UNDER lim (x→a below the word), also inline: saves room on the line
    body = re.sub(r"\\lim(?![A-Za-z])(\s*)_", r"\\lim\\limits\1_", body)
    figs.build(log)
    t1 = time.time()
    work = tempfile.mkdtemp(prefix="tex2docx_w_")
    ref = os.path.join(work, "reference.docx")
    make_reference(ref)
    src = os.path.join(work, "in.tex")
    with open(src, "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\n" + PANDOC_MACROS + math_macros(preamble, body) + "\\begin{document}\n" + body + "\n\\end{document}\n")
    raw = os.path.join(work, "raw.docx")
    r = subprocess.run(["pandoc", "--verbose", "-f", "latex", "-t", "docx", "--number-sections",
                        "--reference-doc", ref, "-M", "lang=ar-DZ", "-M", "dir=rtl", "-o", raw, src],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("pandoc failed:\n" + r.stderr)
    skipped = sorted(set(re.findall(r"Skipped '([^']*)'", r.stderr)))
    if skipped:
        log("pandoc skipped: " + ", ".join(s[:40] for s in skipped))
    postprocess(raw, out_path, header_text(preamble), FOOTER, figs)
    if keep:
        log("work dir: " + work)
    else:
        shutil.rmtree(work, ignore_errors=True)
    log("%s -> %s  (figures %.1fs, total %.1fs)" % (tex_path, out_path, t1 - t0, time.time() - t0))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex", nargs="+")
    ap.add_argument("-o", "--out", help="output .docx (only with a single input)")
    ap.add_argument("--cache", default=os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), "tex2docx"))
    ap.add_argument("--keep", action="store_true", help="keep the pandoc work directory")
    a = ap.parse_args()
    for t in a.tex:
        out = a.out if (a.out and len(a.tex) == 1) else os.path.splitext(t)[0] + ".docx"
        convert(t, out, a.cache, a.keep)


if __name__ == "__main__":
    main()
