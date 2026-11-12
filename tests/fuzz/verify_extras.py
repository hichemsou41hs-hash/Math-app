"""Independent numeric verification of extras.complete_study on the generated functions.
Truth comes from a dense scan (200 001 points) and finite differences, not from extras' own code."""
import ast, json, os, re, sys, time, warnings
import numpy as np, sympy as sp
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import extras
from gen import gen
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# the app's own input clean-up (fix_implicit_mult, clean_ocr_math), taken from app.py without running Streamlit
src = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
ns = {"re": re, "sp": sp}
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("clean_ocr_math", "fix_implicit_mult"):
        exec(ast.get_source_segment(src, node), ns)
x = sp.symbols("x", real=True)
LD = {"x": x, "e": sp.E, "E": sp.E, "pi": sp.pi, "ln": sp.log, "log": sp.log, "exp": sp.exp, "sqrt": sp.sqrt,
      "abs": sp.Abs, "Abs": sp.Abs}

def parse(s):
    return parse_expr(ns["fix_implicit_mult"](s), local_dict=LD, transformations=standard_transformations + (implicit_multiplication_application,))

def data(sections, key):
    return [c[key] for _, items in sections for k, c in items if k == "data" and key in c]

def true_roots(fn):
    xs = np.linspace(-12, 12, 200001); ys = fn(xs)
    out = []
    for i in np.where(np.isfinite(ys[:-1]) & np.isfinite(ys[1:]) & (np.sign(ys[:-1]) * np.sign(ys[1:]) <= 0))[0]:
        a, b = xs[i], xs[i + 1]
        if ys[i] == 0: r = a
        elif ys[i + 1] == 0: continue
        else:
            for _ in range(60):
                m = (a + b) / 2
                (a, b) = (a, m) if np.sign(fn(a)) * np.sign(fn(m)) <= 0 else (m, b)
            r = (a + b) / 2
        if abs(fn(r)) < 1e-6 and (not out or abs(r - out[-1]) > 1e-4):
            out.append(r)
    return out

def check(fstr):
    t = time.time(); prob = []
    try:
        f = parse(fstr)
    except Exception as e:
        return {"f": fstr, "parse": str(e)[:100]}
    try:
        S = extras.complete_study(f, x)
    except Exception as e:
        return {"f": fstr, "crash": f"{type(e).__name__}: {str(e)[:200]}"}
    fn = extras._num(f, x)
    tr = true_roots(fn)
    rep = sorted(sum(data(S, "roots"), []))
    if len(rep) != len(tr) or any(abs(a - b) > 1e-4 for a, b in zip(rep, tr)):
        prob.append(f"roots reported {np.round(rep,4).tolist()} true {np.round(tr,4).tolist()}")
    for a, b, r in data(S, "alpha"):
        inside = [q for q in tr if a < q < b]
        if not (a < r < b) or len(inside) != 1 or not fn(a) * fn(b) < 0:
            prob.append(f"alpha bracket [{a},{b}] r={r} true_inside={inside}")
    for x0, s0, y0 in data(S, "tangent"):
        h = 1e-6
        if abs(fn(x0) - y0) > 1e-6 * max(1, abs(y0)) or abs((fn(x0 + h) - fn(x0 - h)) / (2 * h) - s0) > 1e-3 * max(1, abs(s0)):
            prob.append(f"tangent x0={x0} slope={s0} y0={y0}")
    pts = np.array([-3.3, -1.7, -0.9, 0.45, 1.3, 2.6, 3.9, 5.2])
    for a, b in data(S, "centre"):
        u, v = fn(2 * a - pts), fn(pts); ok = np.isfinite(u) & np.isfinite(v)
        if not ok.any() or not np.allclose((u + v)[ok], 2 * b, atol=1e-6):
            prob.append(f"centre ({a},{b}) wrong")
    for a in data(S, "axis"):
        u, v = fn(2 * a - pts), fn(pts); ok = np.isfinite(u) & np.isfinite(v)
        if not ok.any() or not np.allclose(u[ok], v[ok], atol=1e-6):
            prob.append(f"axis x={a} wrong")
    for xi in sum(data(S, "inflection"), []):
        h = 1e-3; d2 = lambda z: (fn(z + h) - 2 * fn(z) + fn(z - h)) / h**2
        if not (d2(xi - 0.01) * d2(xi + 0.01) < 0):
            prob.append(f"inflection x={xi} no sign change of f''")
    return {"f": fstr, "problems": prob, "sec": round(time.time() - t, 2)}

if __name__ == "__main__":
    fs = [s for s in gen(int(sys.argv[1]) if len(sys.argv) > 1 else 600) if "m" not in s.replace("exp", "")]
    bad = 0
    for s in fs:
        r = check(s)
        if r.get("problems") or r.get("crash") or r.get("parse") or r.get("sec", 0) > 10:
            bad += 1; print(json.dumps(r, ensure_ascii=False), flush=True)
    print(f"checked {len(fs)} functions, {bad} with problems")
