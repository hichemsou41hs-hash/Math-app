"""Run every generated function through the real app (Streamlit AppTest), 4 in parallel; JSONL report."""
import json, os, sys, time, traceback
sys.path.insert(0, os.path.dirname(__file__))
from gen import gen

APP = os.path.join(os.path.dirname(__file__), "..", "..", "app.py")

def one(f):
    import warnings; warnings.filterwarnings("ignore")
    from streamlit.testing.v1 import AppTest
    t = time.time()
    r = {"f": f}
    try:
        at = AppTest.from_file(APP, default_timeout=180)
        at.run()
        at.text_input(key="f_val").set_value(f)
        at.button[[b.label for b in at.button].index("✅ تأكيد ورسم الدالة")].click()
        at.run()
        r["exc"] = [e.value[:300] for e in at.exception]
        r["err"] = [e.value[:200] for e in at.error]
        r["warn"] = [w.value[:200] for w in at.warning]
        r["expanders"] = len(at.expander)
    except Exception as e:
        r["harness"] = f"{type(e).__name__}: {str(e)[:300]}"
    r["sec"] = round(time.time() - t, 1)
    return r

def isolated(f, limit=200):
    """One subprocess per function: a hang or crash cannot block the campaign."""
    import subprocess
    code = "import sys,json;sys.path.insert(0,%r);from run_app import one;print('@@'+json.dumps(one(%r),ensure_ascii=False))" % (os.path.dirname(os.path.abspath(__file__)), f)
    t = time.time()
    try:
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=limit).stdout
        line = [l for l in out.splitlines() if l.startswith("@@")]
        return json.loads(line[-1][2:]) if line else {"f": f, "harness": "no result (crash)", "sec": round(time.time() - t, 1)}
    except subprocess.TimeoutExpired:
        return {"f": f, "timeout": limit, "sec": limit}


if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    out = sys.argv[2] if len(sys.argv) > 2 else "app_report.jsonl"
    fs = gen(n)
    with ThreadPoolExecutor(4) as p, open(out, "w") as fo:
        for i, r in enumerate(p.map(isolated, fs), 1):
            fo.write(json.dumps(r, ensure_ascii=False) + "\n"); fo.flush()
            if i % 50 == 0:
                print(i, flush=True)
