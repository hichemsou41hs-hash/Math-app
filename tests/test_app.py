"""Automated checks of the app on Bac-style functions: run `python -m pytest tests -q` before every deploy.
Each function is analysed by the real app (Streamlit AppTest); no exception and no error message allowed."""
import os
import pytest
from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(__file__), "..", "app.py")

BAC_FUNCTIONS = [
    "(x^2+1)/(x-1)", "x+1-exp(x)", "x*ln(x)", "sqrt(x^2-4)", "(2x+1)/(x+1)",
    "x^3-3x+1", "(x-1)*exp(2x)", "x-1+ln(x)/x", "exp(x)/x", "x+exp(-x)",
    "(x^2-3x+3)/(x-1)", "ln(x^2+1)", "(x^2+m*x+1)/(x-1)", "x^2*exp(-x)", "(x+1)*exp(-x)+x",
]
REJECTED = ["9^9^9", "x^1000000000", "abc", "__import__"]


def analyse(f):
    at = AppTest.from_file(APP, default_timeout=240)
    at.run()
    at.text_input(key="f_val").set_value(f)
    at.button[[b.label for b in at.button].index("✅ تأكيد ورسم الدالة")].click()
    at.run()
    return at


@pytest.mark.parametrize("f", BAC_FUNCTIONS)
def test_bac_function_is_analysed(f):
    at = analyse(f)
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error, [e.value for e in at.error]


@pytest.mark.parametrize("f", REJECTED)
def test_dangerous_input_is_rejected_fast(f):
    at = analyse(f)
    assert not at.exception
    assert at.error, "expected a clear error message"



def test_answer_order_and_ln_m_discussion():
    """Teacher's order: study (limits, derivative, variations, asymptotes) -> Bac questions -> discussion.
    With y = ln(m) the discussion starts at m > 0 (no ]-inf;0] row)."""
    at = AppTest.from_file(APP, default_timeout=240)
    at.run()
    at.text_input(key="f_val").set_value("-x*ln(x)+x")
    at.text_input(key="g_val").set_value("ln(m)")
    at.button[[b.label for b in at.button].index("✅ تأكيد ورسم الدالة")].click()
    at.run()
    assert not at.exception and not at.error
    labels = [e.label for e in at.expander]
    study = next(i for i, l in enumerate(labels) if "دراسة الدالة الشاملة" in l)
    bac = next(i for i, l in enumerate(labels) if "أسئلة البكالوريا" in l)
    assert study < bac
    md = " ".join(m.value for m in at.markdown)
    assert r"\infty ; 0]" not in md and "]0 ; 1]" in md
    texts = [m.value for m in at.markdown]
    disc = next(i for i, t in enumerate(texts) if "📌 المناقشة البيانية" in t)
    limits = next(i for i, t in enumerate(texts) if "حساب النهايات" in t)
    assert limits < disc
