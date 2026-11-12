"""MathLive output (ascii-math) -> app syntax -> the same SymPy function."""
import os, sys
import pytest
import sympy as sp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fuzz"))
from mathinput_convert import ascii_to_app
from verify_extras import parse, x

E, ln = sp.exp, sp.log
CASES = {
    "(x-1)/(e^x)+1": (x - 1) / E(x) + 1, "sqrt(x^2-4)": sp.sqrt(x**2 - 4), "ln (x)+2x": ln(x) + 2 * x,
    "x+1+xe^(-2x)": x + 1 + x * E(-2 * x), "|x+1|+x": sp.Abs(x + 1) + x, "ln ((x+1)/(x-1))": ln((x + 1) / (x - 1)),
    "2e^(-x)+x": 2 * E(-x) + x, "xln x-x": x * ln(x) - x, "root(3)(x)": sp.cbrt(x), "exp (x)": E(x),
    "(2x+1)/(x+1)": (2 * x + 1) / (x + 1), "e^(2x)-4e^x+2": E(2 * x) - 4 * E(x) + 2, "(ln x)/(x)": ln(x) / x,
    "|x|/(x)": sp.Abs(x) / x, "x|x-1|": x * sp.Abs(x - 1), "(x^2+mx+1)/(x-1)": None,
}


@pytest.mark.parametrize("raw", list(CASES))
def test_mathlive_output_parses_to_the_same_function(raw):
    want = CASES[raw]
    got = parse(ascii_to_app(raw))
    if want is not None:
        assert sp.simplify(got - want) == 0
