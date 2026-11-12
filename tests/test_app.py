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


def test_keyboard_types_and_draws():
    at = AppTest.from_file(APP, default_timeout=240)
    at.run()
    keys = {b.key: b for b in at.button if b.key}
    at.button(key="kba_0_3_1").click().run()              # C : clear f
    for k in ["kbf_0_2_0", "kbv_0_0_0", "kbo_0_0_3", "kbo_0_2_7", "kbv_0_0_0"]:   # e^( x ) - x
        at.button(key=k).click().run()
    assert at.session_state["f_val"] == "e^(x)-x"
    at.button(key="kba_0_3_0").click().run()              # ⌫
    assert at.session_state["f_val"] == "e^(x)-"
    at.button(key="kbv_0_0_0").click().run()
    at.button(key="kbg_0_3_6").click().run()              # ⏎ draws it
    assert at.session_state["active_f"] == "e^(x)-x"
    assert not at.exception and not at.error
    assert len(keys) > 40
