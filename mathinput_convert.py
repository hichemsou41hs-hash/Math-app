"""MathLive ascii-math -> the app's input syntax (then the usual fix_implicit_mult / parse_expr checks)."""
import re

_FUN = r"(ln|exp|sqrt|cbrt|sin|cos|tan|log)"


def _abs_bars(s):
    """|a| -> abs(a). A bar opens after the start, an operator or '(' ; otherwise it closes."""
    out, stack = [], []
    for i, ch in enumerate(s):
        if ch != "|":
            out.append(ch)
            continue
        prev = "".join(out).rstrip()[-1:] if out else ""
        if not stack or prev in ("", "(", "+", "-", "*", "/", "^", ","):
            out.append("abs(")
            stack.append(i)
        else:
            out.append(")")
            stack.pop()
    out.append(")" * len(stack))
    return "".join(out)


def ascii_to_app(s):
    if not s:
        return ""
    s = s.replace("⋅", "*").replace("·", "*").replace("×", "*").replace("÷", "/").replace("−", "-")
    s = s.replace("\\", "")
    s = re.sub(r"root\(3\)\(", "cbrt(", s)
    s = re.sub(_FUN + r"\s+\(", r"\1(", s)                                   # ln (x) -> ln(x)
    s = re.sub(_FUN + r"\s+([A-Za-z0-9]+(?:\^[A-Za-z0-9]+)?)", r"\1(\2)", s)  # ln x -> ln(x)
    s = _abs_bars(s)
    s = re.sub(r"(?<![A-Za-z])" + _FUN, r" \1", s)                            # xln( -> x ln( (implicit product)
    return re.sub(r"\s+", " ", s).strip()
