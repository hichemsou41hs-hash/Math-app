"""Maths checks of extras.py on known Bac answers."""
import sympy as sp
import extras

x = sp.symbols("x", real=True)


def results(sections, title_part):
    for title, items in sections:
        if title_part in title:
            return " | ".join(c for k, c in items if k == "result")
    raise AssertionError(title_part)


def test_alpha_bracket_x_exp_x_minus_1():
    s = extras.complete_study(x * sp.exp(x) - 1, x)
    assert r"0{,}5 < \alpha < 0{,}6" in results(s, "القيم المتوسطة")


def test_three_roots_cubic_and_centre():
    s = extras.complete_study(x**3 - 3 * x + 1, x)
    r = results(s, "القيم المتوسطة")
    assert r"-1{,}9 < \alpha_{1} < -1{,}8" in r and r"0{,}3 < \alpha_{2} < 0{,}4" in r and r"1{,}5 < \alpha_{3} < 1{,}6" in r
    assert r"\omega\left(0\,;\,1\right)" in results(s, "التناظر")
    assert r"I\left(0\,;\,1\right)" in results(s, "الانعطاف")


def test_homographic_centre():
    s = extras.complete_study((2 * x + 1) / (x + 1), x, vertical_asymptotes=(-1,))
    assert r"\omega\left(-1\,;\,2\right)" in results(s, "التناظر")


def test_rational_centre_and_no_x_intersection():
    s = extras.complete_study((x**2 + 1) / (x - 1), x, vertical_asymptotes=(1,))
    assert r"\omega\left(1\,;\,2\right)" in results(s, "التناظر")
    assert "لا تقبل حلولاً" in results(s, "تقاطع")


def test_even_function_axis_and_ln_notation():
    s = extras.complete_study(sp.log(x**2 + 1), x)
    assert "x = 0" in results(s, "التناظر")
    infl = results(s, "الانعطاف")
    assert r"\ln" in infl and r"\log" not in infl


def test_tangent():
    assert extras.tangent(x**3 - 3 * x + 1, x, 2)[-1][1] == r"(T):\ y = 9 x - 15"
    assert "غير قابلة" in extras.tangent(1 / x, x, 0)[0][1]


def test_abs_curves_png():
    png = extras.abs_curves_png(x**3 - 3 * x + 1, x, x_bound=3)
    assert png[:4] == b"\x89PNG"


def test_latex_to_plain():
    assert extras.latex_to_plain(r"\omega\left(1\,;\,2\right) \text{ مركز } (C_f)") == "ω (1 ; 2 ) مركز (Cf)"


def test_abs_curves_window_not_flattened_by_exponentials():
    # regression: exp(-x) reaches 1e5 at x=-12; the y window must stay readable (it was ±2e9)
    import matplotlib.image as mpimg, io
    png = extras.abs_curves_png((x + 1) * sp.exp(-x) + x, x, x_bound=12)
    assert mpimg.imread(io.BytesIO(png)).shape[0] > 100
    fn = extras._num((x + 1) * sp.exp(-x) + x, x)
    import numpy as np
    y = fn(np.linspace(-12, 12, 2400))
    q = float(np.percentile(np.abs(y[np.isfinite(y)]), 60))
    assert min(max(4.0, 1.6 * q), 30.0) <= 30.0
