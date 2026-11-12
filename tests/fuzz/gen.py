"""Generator of Bac-style functions (as a pupil would type them) for the large fuzz campaign."""
import random

def gen(n=600, seed=2027):
    R = random.Random(seed)
    c = lambda lo=-4, hi=4, nz=True: R.choice([k for k in range(lo, hi + 1) if (k != 0 or not nz)])
    def s(k):  # signed term
        return f"+{k}" if k >= 0 else f"{k}"
    T = [
        lambda: f"x^3{s(c())}x^2{s(c())}x{s(c())}",
        lambda: f"{c()}x^2{s(c())}x{s(c())}",
        lambda: f"x^4{s(c())}x^2{s(c())}",
        lambda: f"({c()}x{s(c())})/(x{s(c())})",
        lambda: f"(x^2{s(c())}x{s(c())})/(x{s(c())})",
        lambda: f"(x^2{s(c())})/(x^2{s(c(1,4))})",
        lambda: f"x{s(c())}{s(c())}/(x{s(c())})",
        lambda: f"x{s(c())}{s(c())}/(x{s(c())})^2",
        lambda: f"({c()}x{s(c())})e^x{s(c())}",
        lambda: f"({c()}x{s(c())})exp(-x)",
        lambda: f"x{s(c())}{s(c())}exp(-x)",
        lambda: f"x{s(c())}{s(c())}x*exp(x)",
        lambda: f"exp(2x){s(c())}exp(x){s(c())}",
        lambda: f"x{s(c())}{s(c(1,4))}/(exp(x)+1)",
        lambda: f"exp(x)/(exp(x)+{c(1,4)})",
        lambda: f"(x^2{s(c())})exp(-x)",
        lambda: f"x^2*exp(x){s(c())}",
        lambda: f"{c()}x{s(c())}+ln(x)",
        lambda: f"ln(x)/x{s(c())}",
        lambda: f"x{s(c())}{s(c())}ln(x)/x",
        lambda: f"x*ln(x){s(c())}x",
        lambda: f"(ln(x))^2{s(c())}ln(x)",
        lambda: f"ln(x^2{s(c(1,4))})",
        lambda: f"ln((x+{c(1,3)})/(x-{c(1,3)}))",
        lambda: f"x-ln(exp(x)+1)",
        lambda: f"x{s(c())}+ln(x+{c(1,3)})",
        lambda: f"sqrt(x^2{s(c())})",
        lambda: f"x+sqrt(x^2+{c(1,4)})",
        lambda: f"sqrt({c(1,3)}x{s(c())})",
        lambda: f"x*sqrt(x+{c(1,3)})",
        lambda: f"abs(x{s(c())})+x",
        lambda: f"(x{s(c())})/abs(x{s(c())})+x",
        lambda: f"(x^2+m*x{s(c())})/(x{s(c())})",
        lambda: f"x{s(c())}+m*exp(-x)",
        lambda: f"(x+m)exp(x)",
        lambda: f"x^3-3x+m",
        lambda: f"(2x+m)/(x-1)",
        lambda: f"m*x+ln(x)",
    ]
    out, seen = [], set()
    i = 0
    while len(out) < n and i < n * 20:
        i += 1
        f = R.choice(T)().replace("+-", "-").replace("--", "+")
        if f not in seen:
            seen.add(f); out.append(f)
    return out

if __name__ == "__main__":
    fs = gen()
    print(len(fs)); print("\n".join(fs[:15]))
