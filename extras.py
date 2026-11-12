# -*- coding: utf-8 -*-
"""Bac-style complements to the function study (teacher's request):
intersections with the axes, intermediate value theorem with a bracket for alpha,
tangent at a point, symmetry (centre / axis), inflection points, and the curves of
|f(x)| and f(|x|).  Pure functions: they take a SymPy expression and return sections
of ('text' | 'math' | 'result', content) items that the app shows on screen and in the PDF."""
import io
import math
from functools import partial

import numpy as np
import sympy as sp
from scipy.optimize import brentq

LATEX = partial(sp.latex, ln_notation=True)   # Algerian notation: ln, not log

X_RANGE = 12.0      # numeric scan window [-X_RANGE, X_RANGE]
N_SCAN = 4001


# ----------------------------------------------------------------- helpers
def _num(f, x):
    """Vectorised numeric f. Distributions from |x| (DiracDelta) count as 0, an infinite value as NaN,
    a constant result is broadcast to the input shape."""
    f = sp.sympify(f).replace(sp.DiracDelta, lambda *a: sp.S.Zero)
    f = f.subs({sp.zoo: sp.nan, sp.oo: sp.nan, -sp.oo: sp.nan})
    g = sp.lambdify(x, f, modules=["numpy"])

    def ev(v):
        v = np.asarray(v, dtype=float)
        with np.errstate(all="ignore"):
            try:
                r = np.asarray(g(v), dtype=complex)
            except (TypeError, ValueError, ZeroDivisionError, NameError):
                r = np.full(v.shape, np.nan, dtype=complex)
        r = np.broadcast_to(r, v.shape)
        out = np.where(np.abs(r.imag) < 1e-9, r.real, np.nan)
        return out if out.shape else float(out)
    return ev


def _fmt(v, nd=2):
    v = float(v)
    if not math.isfinite(v):
        return "?"
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return ("%.*f" % (nd, v)).rstrip("0").rstrip(".").replace(".", "{,}")


def _lat(e):
    try:
        return LATEX(sp.nsimplify(e, rational=False) if e.is_Float else e)
    except Exception:
        return LATEX(e)


def _exact(e, timeout_ops=60):
    """A short exact form when SymPy finds one, else None."""
    try:
        s = sp.simplify(e)
        if s.is_real is False or sp.count_ops(s) > timeout_ops:
            return None
        return s
    except Exception:
        return None


def _grid(fn):
    xs = np.linspace(-X_RANGE, X_RANGE, N_SCAN)
    ys = fn(xs)
    ys = np.where(np.isfinite(ys), ys, np.nan)
    return xs, ys


def _roots(fn, xs=None, ys=None):
    """Numeric zeros of fn on the scan window (sign changes refined by brentq, no poles)."""
    if xs is None:
        xs, ys = _grid(fn)
    out = []
    flat = _zero_runs(xs, ys)
    for i in range(len(xs) - 1):
        a, b, fa, fb = xs[i], xs[i + 1], ys[i], ys[i + 1]
        if not (np.isfinite(fa) and np.isfinite(fb)) or any(lo - 1e-9 <= a <= hi + 1e-9 for lo, hi in flat):
            continue
        if fa == 0:
            out.append(float(a))
        elif fa * fb < 0:
            try:
                r = brentq(lambda t: float(fn(t)), a, b, xtol=1e-12)
            except Exception:
                continue
            d = 1e-7 * max(1.0, abs(r))
            # a real zero: f small at r and on both sides (not a pole, not a jump like (x-1)/|x-1|)
            fl, f0, fr = fn(r - d), fn(r), fn(r + d)
            if np.isfinite(fl) and np.isfinite(f0) and np.isfinite(fr) and abs(f0) < 1e-6 and abs(fr - fl) < 1e-3:
                out.append(float(r))
    res = []
    for r in sorted(out):
        if not res or abs(r - res[-1]) > 1e-6:
            res.append(r)
    return res


def _zero_runs(xs, ys, min_len=4):
    """Intervals where f is identically 0 (|x+1|+x on ]-inf;-1]): [(lo, hi)]."""
    z = np.isfinite(ys) & (np.abs(ys) < 1e-12)
    runs, i = [], 0
    while i < len(z):
        if z[i]:
            j = i
            while j + 1 < len(z) and z[j + 1]:
                j += 1
            if j - i + 1 >= min_len:
                runs.append((float(xs[i]), float(xs[j])))
            i = j + 1
        else:
            i += 1
    return runs


def _bound(v, lo_edge, hi_edge):
    if v <= lo_edge + 1e-6:
        return r"-\infty"
    if v >= hi_edge - 1e-6:
        return r"+\infty"
    return _fmt(round(v, 2))


def _sign_changes(fn, xs, ys):
    """Zeros of fn where its sign really changes (for f'' -> inflection)."""
    return [r for r in _roots(fn, xs, ys)
            if np.isfinite(fn(r - 1e-4)) and np.isfinite(fn(r + 1e-4)) and fn(r - 1e-4) * fn(r + 1e-4) < 0]


def _exact_root(f, x, r):
    """Exact value of a numeric root r when SymPy solves f=0 exactly near r."""
    try:
        sols = sp.solveset(f, x, domain=sp.S.Reals)
        if isinstance(sols, sp.FiniteSet):
            for s in sols:
                if s.is_real and abs(float(s) - r) < 1e-6 and sp.count_ops(s) < 40:
                    return s
    except Exception:
        pass
    try:
        q = sp.nsimplify(r, [sp.E, sp.sqrt(2), sp.sqrt(3), sp.sqrt(5)], tolerance=1e-10)
        if sp.count_ops(q) < 12 and abs(float(f.subs(x, q))) < 1e-9:
            return q
    except Exception:
        pass
    return None


# ----------------------------------------------------------------- sections
def axes_intersections(f, x, fn):
    items = []
    y0 = fn(0.0)
    if np.isfinite(y0):
        v = _exact(f.subs(x, 0))
        items += [("text", "مع حامل محور التراتيب: نحسب $f(0)$ :"),
                  ("math", r"f(0) = " + (_lat(v) if v is not None else _fmt(y0))),
                  ("result", r"(C_f) \cap (y'y) = \left\{ \left(0\,;\,%s\right) \right\}" % (_lat(v) if v is not None else _fmt(y0)))]
    else:
        items.append(("text", "العدد $0$ لا ينتمي إلى $D_f$ ، إذن $(C_f)$ لا يقطع حامل محور التراتيب."))
    xs, ys = _grid(fn)
    flat = _zero_runs(xs, ys)
    roots = _roots(fn, xs, ys)
    items.append(("text", "مع حامل محور الفواصل: نحل المعادلة $f(x)=0$ :"))
    for lo, hi in flat:
        lb, hb = _bound(lo, xs[0], xs[-1]), _bound(hi, xs[0], xs[-1])
        items.append(("result", r"f(x) = 0 \text{ على المجال } %s%s\,;\,%s%s" % (
            "]" if lb.endswith("infty") else "[", lb, hb, "[" if hb.endswith("infty") else "]")))
        items.append(("text", "على هذا المجال المنحنى $(C_f)$ ينطبق على حامل محور الفواصل."))
    if flat and not roots:
        items.append(("data", {"roots": [], "flat": flat}))
        return items, []
    if not roots:
        items.append(("result", r"\text{المعادلة لا تقبل حلولاً: } (C_f) \text{ لا يقطع } (x'x)"))
        return items, []
    pts, approx = [], []
    for r in roots:
        q = _exact_root(f, x, r)
        if q is not None:
            pts.append(r"\left(%s\,;\,0\right)" % _lat(q))
        else:
            approx.append(r)
            pts.append(r"\left(\alpha_{%d}\,;\,0\right)" % len(approx) if len(roots) > 1 else r"\left(\alpha\,;\,0\right)")
    items.append(("result", r"(C_f) \cap (x'x) = \left\{ %s \right\}" % r" \,;\, ".join(pts)))
    items.append(("data", {"roots": roots}))
    if approx:
        items.append(("text", "الحلول غير الصريحة نحصرها بمبرهنة القيم المتوسطة (الفقرة الموالية)."))
    return items, approx


def ivt(f, x, fn, dfn, approx_roots):
    """Each non-explicit root: f continuous and strictly monotone on [a;b] (width 0.1), f(a)f(b)<0."""
    items = []
    if not approx_roots:
        return [("text", "كل حلول المعادلة $f(x)=0$ صريحة، فلا حاجة إلى الحصر.")]
    for k, r in enumerate(approx_roots, 1):
        name = r"\alpha" if len(approx_roots) == 1 else r"\alpha_{%d}" % k
        a = math.floor(r * 10) / 10
        if abs(r - a) < 1e-9:
            a -= 0.1
        b = a + 0.1
        fa, fb = float(fn(a)), float(fn(b))
        d = dfn(np.linspace(a, b, 60))
        mono = np.all(np.isfinite(d)) and (np.all(d > 0) or np.all(d < 0))
        if not (np.isfinite(fa) and np.isfinite(fb) and fa * fb < 0 and mono):
            items.append(("math", r"%s \approx %s" % (name, _fmt(r, 3))))
            continue
        sense = "متزايدة تمامًا" if d[0] > 0 else "متناقصة تمامًا"
        items += [
            ("text", "الدالة $f$ مستمرة و%s على المجال $[%s\\,;\\,%s]$ ، ولدينا:" % (sense, _fmt(a, 1), _fmt(b, 1))),
            ("math", r"f(%s) \approx %s \quad ; \quad f(%s) \approx %s" % (_fmt(a, 1), _fmt(fa, 3), _fmt(b, 1), _fmt(fb, 3))),
            ("text", "إذن $f(%s)\\times f(%s)<0$ ، وحسب مبرهنة القيم المتوسطة المعادلة $f(x)=0$ تقبل حلاً وحيدًا $%s$ حيث:" % (_fmt(a, 1), _fmt(b, 1), name)),
            ("result", r"%s < %s < %s \qquad (%s \approx %s)" % (_fmt(a, 1), name, _fmt(b, 1), name, _fmt(r, 3))),
            ("data", {"alpha": (a, b, r)}),
        ]
    return items


def tangent(f, x, x0):
    x0 = sp.nsimplify(x0)
    try:
        y0 = sp.simplify(f.subs(x, x0))
        d = sp.diff(f, x)
        s0 = sp.simplify(d.subs(x, x0))
        if not (y0.is_real and s0.is_real) or y0.has(sp.zoo, sp.oo, sp.nan) or s0.has(sp.zoo, sp.oo, sp.nan):
            return [("text", "الدالة $f$ غير قابلة للاشتقاق عند $x_0=%s$ (أو غير معرّفة)." % _lat(x0))]
        line = sp.expand(s0 * (x - x0) + y0)
        return [
            ("text", "معادلة المماس $(T)$ للمنحنى $(C_f)$ عند النقطة ذات الفاصلة $x_0=%s$ :" % _lat(x0)),
            ("math", r"(T):\ y = f'(x_0)(x-x_0) + f(x_0)"),
            ("math", r"f(%s) = %s \quad ; \quad f'(%s) = %s" % (_lat(x0), _lat(y0), _lat(x0), _lat(s0))),
            ("result", r"(T):\ y = %s" % _lat(line)),
            ("data", {"tangent": (float(x0), float(s0), float(y0))}),
        ]
    except Exception:
        return [("text", "تعذّر حساب المماس عند هذه النقطة.")]


def symmetry(f, x, fn, candidates):
    """Centre w(a;b): f(2a-x)+f(x)=2b ; axis x=a: f(2a-x)=f(x). Checked numerically, then symbolically."""
    pts = np.array([-3.7, -2.2, -1.3, -0.4, 0.6, 1.9, 2.8, 4.1])
    seen = set()
    for a in candidates:
        try:
            a = sp.nsimplify(a)
            af = float(a)
        except Exception:
            continue
        if a in seen:
            continue
        seen.add(a)
        u, v = fn(2 * af - pts), fn(pts)
        ok = np.isfinite(u) & np.isfinite(v)
        if ok.sum() < 4:
            continue
        if np.allclose((u - v)[ok], 0, atol=1e-7):
            if sp.simplify(f.subs(x, 2 * a - x) - f) == 0:
                return [("text", "من أجل كل $x$ من $D_f$ : $(2\\times%s - x) \\in D_f$ و" % _lat(a)),
                        ("math", r"f(%s - x) = f(x)" % _lat(2 * a)),
                        ("result", r"\text{المستقيم } x = %s \text{ محور تناظر للمنحنى } (C_f)" % _lat(a)),
                        ("data", {"axis": af})]
        sm = (u + v)[ok]
        if np.allclose(sm, sm[0], atol=1e-7):
            s = sp.simplify(f.subs(x, 2 * a - x) + f)
            if s.free_symbols == set():
                b = sp.simplify(s / 2)
                return [("text", "من أجل كل $x$ من $D_f$ : $(2\\times%s - x) \\in D_f$ و" % _lat(a)),
                        ("math", r"f(%s - x) + f(x) = %s = 2\times %s" % (_lat(2 * a), _lat(s), _lat(b))),
                        ("result", r"\omega\left(%s\,;\,%s\right) \text{ مركز تناظر للمنحنى } (C_f)" % (_lat(a), _lat(b))),
                        ("data", {"centre": (af, float(b))})]
    return [("text", "لم نجد مركز تناظر ولا محور تناظر بسيطًا للمنحنى $(C_f)$ (نختبر $x=0$ والمقاربات العمودية والقيم الحدية ونقط الانعطاف).")]


def inflection(f, x):
    try:
        d2 = sp.simplify(sp.diff(f, x, 2))
    except Exception:
        return [("text", "تعذّر حساب المشتقة الثانية.")], []
    fn2 = _num(d2, x)
    xs, ys = _grid(fn2)
    fn = _num(f, x)
    roots = [r for r in _sign_changes(fn2, xs, ys) if np.isfinite(fn(r))]   # only points of D_f
    items = [("math", r"f''(x) = %s" % LATEX(d2))]
    if not roots:
        items.append(("result", r"f'' \text{ لا تنعدم مغيّرة إشارتها: } (C_f) \text{ لا يقبل نقطة انعطاف}"))
        return items, []
    fn = _num(f, x)
    pts = []
    for r in roots:
        q = _exact_root(d2, x, r)
        xv = _lat(q) if q is not None else _fmt(r, 3)
        yq = _exact(f.subs(x, q)) if q is not None else None
        yv = _lat(yq) if yq is not None else _fmt(fn(r), 3)
        pts.append(r"I\left(%s\,;\,%s\right)" % (xv, yv))
    items.append(("text", "$f''$ تنعدم عند الفواصل التالية مغيّرة إشارتها، إذن $(C_f)$ يقبل نقطة انعطاف:"))
    items.append(("result", r" \quad ; \quad ".join(pts)))
    items.append(("data", {"inflection": roots}))
    return items, roots


def complete_study(f, x, x0=None, vertical_asymptotes=()):
    """All sections for f (SymPy expr in real x).  x0: tangent abscissa (default: first point of D_f among 0,1,-1,2)."""
    fn = _num(f, x)
    dfn = _num(sp.diff(f, x), x)
    sections = []
    ax_items, approx = axes_intersections(f, x, fn)
    sections.append(("تقاطع المنحنى $(C_f)$ مع حاملي محوري الإحداثيات", ax_items))
    sections.append(("مبرهنة القيم المتوسطة: حصر حلول المعادلة $f(x)=0$", ivt(f, x, fn, dfn, approx)))
    if x0 is None:
        x0 = next((c for c in (0, 1, -1, 2, 3) if np.isfinite(fn(float(c))) and np.isfinite(dfn(float(c)))), 1)
    sections.append(("معادلة المماس $(T)$", tangent(f, x, x0)))
    infl_items, infl_roots = inflection(f, x)
    xs, ys = _grid(dfn)
    crit = [round(r, 6) for r in _roots(dfn, xs, ys)]
    cands = [0] + list(vertical_asymptotes) + crit + [round(r, 6) for r in infl_roots]
    sections.append(("التناظر", symmetry(f, x, fn, cands)))
    sections.append(("نقطة الانعطاف", infl_items))
    return sections


# ----------------------------------------------------------------- |f| and f(|x|)
def abs_curves_png(f, x, x_bound=6.0, y_lim=None, dark=True):
    """Two panels: (C_f) dashed with |f(x)|, and with f(|x|).  Returns PNG bytes."""
    from matplotlib.figure import Figure
    fn = _num(f, x)
    xs = np.linspace(-x_bound, x_bound, 2400)
    y = fn(xs)
    y_abs = np.abs(y)
    y_even = fn(np.abs(xs))
    bg, fg, grid = ("#0F172A", "#E2E8F0", "#334155") if dark else ("white", "#1F3A5F", "#CBD5E1")
    fig = Figure(figsize=(7.5, 10.5))     # one under the other: each curve uses the full width on a phone
    fig.patch.set_facecolor(bg)
    axs = fig.subplots(2, 1)
    if y_lim is None:
        # robust window: exponential functions reach 1e9 at the edges, which flattened both curves
        fin = np.abs(y[np.isfinite(y)])
        q = float(np.percentile(fin, 60)) if fin.size else 4.0
        h = min(max(4.0, 1.6 * q), 30.0)
        y_lim = (-h, h)
    y_lim = (min(y_lim[0], -1.0), max(y_lim[1], -y_lim[0], 1.0))   # room for |f(x)| above the axis
    for ax, yt, title, col in ((axs[0], y_abs, "|f(x)|", "#F97316"), (axs[1], y_even, "f(|x|)", "#22C55E")):
        ax.set_facecolor(bg)
        ax.axhline(0, color=fg, lw=0.8)
        ax.axvline(0, color=fg, lw=0.8)
        ax.grid(color=grid, lw=0.5)
        ax.plot(xs, np.where(np.abs(y) < 1e3, y, np.nan), "--", color="#60A5FA", lw=1.3, label="(Cf)")
        ax.plot(xs, np.where(np.abs(yt) < 1e3, yt, np.nan), color=col, lw=2.4, label="y = " + title)
        ax.set_xlim(-x_bound, x_bound)
        ax.set_ylim(*y_lim)
        ax.tick_params(colors=fg, labelsize=8)
        for s in ax.spines.values():
            s.set_color(grid)
        ax.legend(loc="upper left", fontsize=12, facecolor=bg, edgecolor=grid, labelcolor=fg)
        ax.tick_params(colors=fg, labelsize=11)
        ax.set_title("y = " + title, color=col, fontsize=17)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor=bg)
    return buf.getvalue()


ABS_EXPLAIN = [
    ("text", "منحنى الدالة $x \\mapsto |f(x)|$ : ينطبق على $(C_f)$ في المجالات التي يكون فيها $f(x) \\geq 0$ ، "
             "وهو نظير $(C_f)$ بالنسبة لحامل محور الفواصل في المجالات التي يكون فيها $f(x) < 0$."),
    ("text", "منحنى الدالة $x \\mapsto f(|x|)$ : الدالة زوجية، فمنحناها متناظر بالنسبة لحامل محور التراتيب؛ "
             "ينطبق على $(C_f)$ من أجل $x \\geq 0$ ، ونرسم نظيره بالنسبة لحامل محور التراتيب من أجل $x < 0$."),
]


# ----------------------------------------------------------------- PDF helpers
_SYM = {r"\alpha": "α", r"\omega": "ω", r"\infty": "∞", r"\cap": "∩", r"\times": "×", r"\leq": "≤",
        r"\geq": "≥", r"\approx": "≈", r"\in": "∈", r"\mapsto": "↦", r"\cup": "∪", r"\neq": "≠"}


def latex_to_plain(s):
    """Simple inline LaTeX -> Unicode text for a PDF line (fpdf cannot typeset maths)."""
    import re
    s = s.replace("$", "")
    s = re.sub(r"\\text\{([^{}]*)\}", r" \1 ", s)
    for k, v in _SYM.items():
        s = re.sub(re.escape(k) + r"(?![A-Za-z])", v, s)
    for _ in range(3):
        s = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\^\{([^{}]*)\}", r"^(\1)", s)
    s = re.sub(r"_\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"_([A-Za-z0-9])", r"\1", s)
    s = s.replace("{,}", ",").replace(r"\,", " ").replace(r"\;", " ").replace(r"\ ", " ")
    s = re.sub(r"\\(left|right|quad|qquad|displaystyle)", " ", s)
    s = re.sub(r"\\([A-Za-z]+)", r"\1", s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def math_png(latex, color="#1F3A5F", fontsize=17):
    """One line of maths rendered by matplotlib mathtext (white background) -> PNG bytes, or None."""
    from matplotlib.figure import Figure
    try:
        fig = Figure(figsize=(0.01, 0.01))
        fig.text(0, 0, "$%s$" % latex.replace(r"\left(", "(").replace(r"\right)", ")"), fontsize=fontsize, color=color)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=170, bbox_inches="tight", pad_inches=0.06, facecolor="white")
        return buf.getvalue()
    except Exception:
        return None
