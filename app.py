# ==================== بداية الجزء (1/4) ====================
import streamlit as st
import base64
import io
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import threading
from matplotlib.figure import Figure

class _AbortAnalysis(BaseException):
    """تُرفع بهدوء من نقاط فحص الوقت عند انتهاء المهلة (BaseException كي لا تبتلعها except Exception)."""
    pass

_DEADLINES = {}

def _check_deadline():
    d = _DEADLINES.get(threading.get_ident())
    if d is not None and time.time() > d:
        raise _AbortAnalysis()

def new_fig(figsize=None):
    fig = Figure(figsize=figsize)
    ax = fig.subplots()
    return fig, ax

import matplotlib.ticker as ticker
import sympy as sp
from scipy.signal import find_peaks
import time
import warnings
import re
import os
import urllib.request
import urllib.error
import tempfile
from PIL import Image, ImageOps, ImageEnhance
from sympy.parsing.sympy_parser import parse_expr as _raw_parse_expr, standard_transformations, implicit_multiplication_application

# ---- طبقة أمان موسعة: تشمل الدوال المثلثية العكسية والجذر التكعيبي ----
_SAFE_TOKEN = re.compile(r'(?:x|m|e|E|pi|ln|log|exp|sqrt|cbrt|abs|Abs|cos|sin|tan|asin|acos|atan|sign)+')

def real_odd_powers(expr):
    """تحويل القوى الكسرية ذات المقام الفردي (مثل x^(1/3)) إلى صيغة حقيقية صالحة للأعداد السالبة والموجبة."""
    if expr is None or not hasattr(expr, 'replace'):
        return expr
    try:
        def _is_odd_rat_pow(e):
            return e.is_Pow and isinstance(e.args[1], sp.Rational) and e.args[1].q > 1 and (e.args[1].q % 2 == 1)
        def _conv_odd_pow(e):
            base, r = e.args
            if not base.free_symbols:
                return e
            p_num, q_den = int(r.p), int(r.q)
            abs_part = sp.Pow(sp.Abs(base), sp.Rational(p_num, q_den))
            if p_num % 2 != 0:
                return sp.sign(base) * abs_part
            return abs_part
        return expr.replace(_is_odd_rat_pow, _conv_odd_pow)
    except Exception:
        return expr

def parse_expr(s, *args, **kwargs):
    s = str(s)
    if len(s) > 220 or re.search(r'[^0-9A-Za-z+\-*/().\s]', s):
        raise ValueError("رمز غير مسموح في العبارة")
    for tok in re.findall(r'[A-Za-z_]+', s):
        if not _SAFE_TOKEN.fullmatch(tok):
            raise ValueError("كلمة غير مسموحة: " + tok)
    res = _raw_parse_expr(s, *args, **kwargs)
    if sp.count_ops(res) > 350:
        raise ValueError("العبارة معقدة جداً")
    return real_odd_powers(res)

try:
    st.set_option('runner.magicEnabled', False)
except Exception:
    pass

from matplotlib import font_manager as _fm

def _fetch_font(fname, url):
    try:
        if not os.path.exists(fname) or os.path.getsize(fname) < 10000:
            req_f = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_f, timeout=15) as resp_f, open(fname, 'wb') as out_f:
                out_f.write(resp_f.read())
        return fname if os.path.getsize(fname) > 10000 else None
    except Exception:
        return None

@st.cache_resource
def _setup_report_fonts():
    loaded = 0
    for fname_f in ("Amiri-Regular.ttf", "Amiri-Bold.ttf"):
        path_f = _fetch_font(fname_f, "https://github.com/google/fonts/raw/main/ofl/amiri/" + fname_f)
        if path_f:
            try:
                _fm.fontManager.addfont(path_f)
                loaded += 1
            except Exception:
                pass
    if loaded:
        matplotlib.rcParams['font.family'] = ['Amiri', 'DejaVu Sans']
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    return loaded

_setup_report_fonts()

manifest_data = """
{
  "name": "المناقشة البيانية ودراسة تغيرات دالة - الأستاذ سوايسية هشام",
  "short_name": "المناقشة البيانية",
  "description": "تطبيق تعليمي لدراسة اتجاه تغير دالة والمناقشة البيانية",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#0f172a",
  "orientation": "portrait-primary",
  "lang": "ar",
  "dir": "rtl",
  "icons": [
    {
      "src": "https://raw.githubusercontent.com/hichemsou41hs-hash/Math-app/main/favicon_512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ]
}
"""

b64_manifest = base64.b64encode(manifest_data.encode('utf-8')).decode('utf-8')

try:
    from fpdf import FPDF
    import arabic_reshaper
    from bidi.algorithm import get_display
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

warnings.filterwarnings("ignore")

st.set_page_config(page_title="المناقشة البيانية ودراسة تغيرات دالة", page_icon="📈", layout="centered")

st.markdown(
    f'<link rel="manifest" href="data:application/manifest+json;base64,{b64_manifest}">',
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: white; }
    .title-dis { text-align: center; color: #FFD700 !important; font-size: 34px; font-weight: bold; margin-bottom: 4px; line-height: 1.3; }
    .title-hes { text-align: center; color: #FFFFFF !important; font-size: 25px; font-weight: bold; margin-top: 0px; margin-bottom: 25px; }
    
    .footer-social { margin-top: 35px; padding: 15px; background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 15px; direction: rtl; }
    .footer-text { color: #FFD700 !important; font-size: 17px !important; font-weight: bold !important; margin: 0 !important; }
    .social-links-group { display: flex; gap: 12px; direction: ltr; }
    .social-btn { display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 30px; color: white !important; text-decoration: none !important; font-weight: bold; font-size: 15px; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .social-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 14px rgba(0,0,0,0.4); color: white !important; }
    .fb-btn { background: #1877F2; border: 1px solid #3b82f6; }
    .ig-btn { background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); border: 1px solid #ec4899; }

    .step-box-lim { text-align: right; direction: rtl; color: #FBBF24 !important; font-size: 16px !important; font-weight: bold !important; margin-top: 5px; margin-bottom: -8px; }
    .step-box-deriv { text-align: right; direction: rtl; color: #FB923C !important; font-size: 16px !important; font-weight: bold !important; margin-top: 8px; margin-bottom: -8px; }
    .step-box-final { text-align: right; direction: rtl; color: #4ADE80 !important; font-size: 17px !important; font-weight: bold !important; margin-top: 10px; margin-bottom: -8px; }

    div[data-testid="stAlert"] { direction: rtl !important; text-align: right !important; border-radius: 8px !important; }
    div[data-testid="stAlert"] p { font-size: 16px !important; font-weight: bold !important; line-height: 1.8 !important; }
    
    .katex {
        direction: ltr !important;
        unicode-bidi: isolate !important;
        display: inline-block !important;
    }
    .katex-display, div[data-testid="stLatex"] {
        direction: ltr !important;
        display: block !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        max-width: 100% !important;
        padding: 4px 8px !important;
        -webkit-overflow-scrolling: touch !important;
    }

    label, div[data-testid="stRadio"] p, div[data-testid="stTextInput"] label p { font-weight: bold !important; font-size: 17px !important; color: #00E5FF !important; }
    .stTextInput label { direction: rtl !important; text-align: right !important; display: block;}
    .stTextInput > div > div > input { background-color: #1E293B; color: white; border: 1px solid #00E5FF; font-size: 18px; direction: ltr !important; }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) { display: grid !important; grid-template-columns: repeat(6, 1fr) !important; gap: 5px !important; background-color: #1E293B !important; padding: 5px !important; border-radius: 8px !important; margin-bottom: 2px !important; }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) > div[data-testid="column"] { width: 100% !important; min-width: 0 !important; max-width: 100% !important; flex: none !important; padding: 0 !important; display: block !important; }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button { width: 100% !important; height: 48px !important; padding: 0px !important; margin: 0 !important; border-radius: 6px !important; background-color: #334155 !important; color: #00E5FF !important; border: 1px solid #475569 !important; box-shadow: 0 4px 0 #090e1a !important; transition: all 0.1s !important; }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button:active { transform: translateY(4px) !important; box-shadow: 0 0 0 #090e1a !important; background-color: #00E5FF !important; color: #0F172A !important; }
    
    div[data-testid="stHorizontalBlock"] button * { 
        font-size: 17px !important; 
        overflow: visible !important; 
        text-overflow: clip !important; 
        white-space: nowrap !important;
        letter-spacing: -1px !important; 
    }
    
    button[kind="primary"] { width: 100% !important; height: 50px !important; background-color: #ef4444 !important; color: white !important; font-size: 18px !important; font-weight: bold !important; border-radius: 8px !important; box-shadow: 0 4px 0 #7f1d1d !important; border: none !important; margin-top: 5px !important; }
    button[kind="primary"]:active { transform: translateY(4px) !important; box-shadow: 0 0 0 #7f1d1d !important; background-color: #dc2626 !important; }
    
    [data-testid="stMarkdownContainer"] table { width: 100% !important; border-collapse: collapse !important; border: 2px solid #475569 !important; margin-bottom: 20px !important; }
    [data-testid="stMarkdownContainer"] th { background-color: #1E293B !important; color: #FFFFFF !important; padding: 12px !important; font-size: 19px !important; border: 2px solid #475569 !important; text-align: center !important; }
    [data-testid="stMarkdownContainer"] td { padding: 15px 10px !important; border: 1px solid #334155 !important; text-align: center !important; vertical-align: middle !important; font-size: 18px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-dis'>المناقشة البيانية ودراسة تغيرات دالة</div>", unsafe_allow_html=True)
st.markdown("<div class='title-hes'>الأستاذ سوايسية هشام</div>", unsafe_allow_html=True)

NUMPY_MATH_MAP = {
    'E': np.e, 'e': np.e, 'pi': np.pi,
    'Abs': np.abs, 'abs': np.abs, 'sign': np.sign,
    'sqrt': np.sqrt, 'cbrt': np.cbrt, 'exp': np.exp, 'log': np.log, 'ln': np.log,
    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
    'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan
}

def safe_lambdify(vars_sym, expr):
    expr_real = real_odd_powers(expr)
    try:
        return sp.lambdify(vars_sym, expr_real, modules=[NUMPY_MATH_MAP, 'numpy'])
    except Exception:
        def fallback_fn(*args):
            try:
                if isinstance(vars_sym, (tuple, list)):
                    sub_d = {v: a for v, a in zip(vars_sym, args)}
                    return float(sp.N(expr_real.subs(sub_d)))
                else:
                    arr = args[0]
                    if isinstance(arr, np.ndarray):
                        return np.array([safe_float(expr_real.subs(vars_sym, float(val))) for val in arr], dtype=float)
                    return safe_float(expr_real.subs(vars_sym, float(arr)))
            except Exception:
                return np.nan
        return fallback_fn

def fig_to_bytes(fig, dpi_val=175):
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.05, dpi=dpi_val, facecolor=fig.get_facecolor())
        plt.close(fig)
        data = buf.getvalue()
        if data and len(data) > 100:
            return data
    except Exception:
        pass
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=140)
        plt.close(fig)
        data = buf.getvalue()
        if data and len(data) > 100:
            return data
    except Exception:
        try:
            plt.close(fig)
        except Exception:
            pass
    return None

def safe_float(expr):
    _check_deadline()
    if expr is None:
        return np.nan
    if isinstance(expr, (int, float, np.number)):
        return float(expr)
    if expr == sp.oo or str(expr) == 'oo':
        return float('inf')
    if expr == -sp.oo or str(expr) in ['-oo', '-Infinity']:
        return float('-inf')
    if expr in [sp.zoo, sp.nan] or str(expr) in ['zoo', 'nan']:
        return np.nan
    try:
        val = sp.N(expr)
        if val == sp.oo:
            return float('inf')
        if val == -sp.oo:
            return float('-inf')
        if val in [sp.zoo, sp.nan]:
            return np.nan
        im_part = float(sp.im(val))
        re_part = float(sp.re(val))
        if abs(im_part) > 1e-5:
            return np.nan
        return re_part
    except Exception:
        try:
            c_val = complex(expr)
            return float(c_val.real) if abs(c_val.imag) <= 1e-5 else np.nan
        except Exception:
            return np.nan

def elim_hyperbolic(expr):
    if expr is None or isinstance(expr, (int, float, str, np.number)):
        return expr
    try:
        s_rep = str(expr)
        if any(h_name in s_rep for h_name in ('sinh', 'cosh', 'tanh', 'coth')):
            expr = sp.expand(expr.rewrite(sp.exp))
    except Exception:
        pass
    return expr

def fmt(val):
    if str(val) == 'oo' or val == float('inf'):
        return r"+\infty"
    if str(val) == '-oo' or val == float('-inf'):
        return r"-\infty"
    if str(val) == 'zoo':
        return r"\pm\infty"
    try:
        f_val = safe_float(val)
        if not np.isfinite(f_val):
            return str(val)
        if abs(f_val) > 1e6:
            return str(f_val)
        if int(f_val) == f_val:
            return str(int(f_val))
        return str(round(f_val, 2))
    except Exception:
        return str(val)
# ==================== نهاية الجزء (1/4) ====================
# ==================== بداية الجزء (2/4) ====================
def clean_ocr_math(raw_str):
    if not raw_str:
        return ""
    s = str(raw_str).strip()
    s = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]', '', s)
    s = s.replace('`', '').replace('$', '').strip()
    lines = [line.strip() for line in s.splitlines() if line.strip()]
    if lines:
        for line in lines:
            if any(k in line.lower() for k in ['f(x)', 'x', 'ln', 'exp', 'e^', 'sqrt', '/', 'm', 'abs', '|']):
                s = line
                break
        else:
            s = lines[0]

    s = re.sub(r'^[fFgGhHyY]\s*(\(\s*[xX]\s*\))?\s*[:=]\s*', '', s)
    if '=' in s:
        parts = [p.strip() for p in s.split('=') if p.strip()]
        if len(parts) >= 2:
            s = parts[-1]

    s = s.replace('X', 'x').replace('M', 'm').replace('،', '.').replace(',', '.')
    replacements = {
        '−': '-', '–': '-', '—': '-', 'ｰ': '-',
        '×': '*', '÷': '/', '∕': '/', '⁄': '/', '⋅': '*', '·': '*',
        '（': '(', '）': ')', '［': '(', '］': ')', '[': '(', ']': ')',
        '⁰': '^0', '¹': '^1', '²': '^2', '³': '^3', '⁴': '^4',
        '⁵': '^5', '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9',
        '∛': 'cbrt', '√': 'sqrt', '\\left': '', '\\right': '', '\\cdot': '*', '\\times': '*',
        '\\ln': 'ln', '\\log': 'ln', '\\exp': 'exp', '\\sqrt': 'sqrt',
        '\\pi': 'pi', '\\mathrm{e}': 'e', '\\text{e}': 'e',
        'In(': 'ln(', '1n(': 'ln(', 'LN(': 'ln(', 'EXP(': 'exp(', 'Exp(': 'exp('
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    for _ in range(5):
        new_s = re.sub(r'\\d?frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'((\1)/(\2))', s)
        if new_s == s:
            break
        s = new_s

    s = re.sub(r'sqrt\s*\{([^{}]+)\}', r'sqrt(\1)', s)
    s = re.sub(r'\^\s*\{([^{}]+)\}', r'^(\1)', s)
    s = s.replace('{', '(').replace('}', ')').replace('\\', '')
    s = re.sub(r'\|([^|]+)\|', r'abs(\1)', s)
    s = re.sub(r'\bexp\s*\(', 'e^(', s, flags=re.IGNORECASE)
    return s.strip()

def fix_implicit_mult(expr_str):
    expr_str = clean_ocr_math(expr_str)
    if not expr_str:
        return ""
    if "()" in expr_str:
        expr_str = expr_str.replace("()", "(1)")
    open_p, close_p = expr_str.count('('), expr_str.count(')')
    if open_p > close_p:
        expr_str = expr_str + (')' * (open_p - close_p))
    elif close_p > open_p:
        expr_str = ('(' * (close_p - open_p)) + expr_str
    expr_str = re.sub(r'[\+\-\*\/\^]+$', '', expr_str.strip())
    expr_str = expr_str.replace('^', '**')
    expr_str = re.sub(r'sqrt\s*([xym0-9])', r'sqrt(\1)', expr_str)
    expr_str = re.sub(r'cbrt\s*([xym0-9])', r'cbrt(\1)', expr_str)
    expr_str = re.sub(r'([xym0-9\)])\s*(exp|ln|log|cos|sin|tan|asin|acos|atan|sqrt|cbrt|abs|pi)\b', r'\1*\2', expr_str)
    expr_str = re.sub(r'([xym0-9\)])\s*(e)\b(?![a-zA-Z])', r'\1*\2', expr_str)
    expr_str = re.sub(r'\b(e|pi)\s*([xym0-9\(])', r'\1*\2', expr_str)
    expr_str = re.sub(r'(\))\s*(\()', r'\1*\2', expr_str)
    expr_str = re.sub(r'([0-9])\s*([xym\(])', r'\1*\2', expr_str)
    expr_str = re.sub(r'([xym\)])\s*([0-9])', r'\1*\2', expr_str)
    expr_str = re.sub(r'\b([xm])\s*([xm])\b', r'\1*\2', expr_str)
    return expr_str

def validate_extracted_math(candidate_str):
    try:
        x_sym, m_sym = sp.symbols('x m', real=True)
        local_dict = {
            'x': x_sym, 'm': m_sym, 'e': sp.E, 'E': sp.E, 'pi': sp.pi,
            'ln': sp.log, 'log': sp.log, 'exp': sp.exp, 'sqrt': sp.sqrt,
            'cbrt': lambda arg: sp.Pow(arg, sp.Rational(1, 3)),
            'abs': sp.Abs, 'Abs': sp.Abs, 'cos': sp.cos, 'sin': sp.sin, 'tan': sp.tan,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan
        }
        transformations = (standard_transformations + (implicit_multiplication_application,))
        proc = fix_implicit_mult(candidate_str)
        if not proc:
            return None
        parsed = parse_expr(proc, local_dict=local_dict, transformations=transformations)
        if [s for s in parsed.free_symbols if s not in (x_sym, m_sym)]:
            return None
        return clean_ocr_math(candidate_str)
    except Exception:
        return None

def extract_math_from_image(image_file, api_key):
    try:
        image_file.seek(0)
    except Exception:
        pass

    orig_img = Image.open(image_file).convert("RGB")
    w, h = orig_img.size
    if w < 800 or h < 250:
        scale = max(2, int(900 / max(w, 1)))
        proc_img = orig_img.resize((w * scale, h * scale), Image.Resampling.LANCZOS)
    else:
        proc_img = orig_img.copy()
    proc_img = ImageOps.expand(proc_img, border=25, fill='white')
    proc_img = ImageEnhance.Contrast(proc_img).enhance(1.4)
    proc_img = ImageEnhance.Sharpness(proc_img).enhance(1.6)

    buf = io.BytesIO()
    proc_img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    prompt = (
        "You are a specialized mathematical OCR engine. Read the mathematical function from the image.\n"
        "Output ONLY the right-hand side expression in plain mathematical notation.\n"
        "Strict rules:\n"
        "- Do NOT include 'f(x) =' or 'y ='.\n"
        "- For exponentials, write e^(...) instead of exp(...). Example: x*e^x - e*x - 2 + e.\n"
        "- For fractions, wrap numerator and denominator in parentheses: (numerator)/(denominator).\n"
        "- For natural log, write ln(...). For square root, write sqrt(...). For |x|, write abs(x).\n"
        "- Output ONLY the single-line formula with no markdown, no backticks, and no extra words."
    )

    active_models = []
    try:
        list_url = "https://generativelanguage.googleapis.com/v1beta/models"
        req_list = urllib.request.Request(list_url, headers={'User-Agent': 'Mozilla/5.0', 'x-goog-api-key': api_key})
        with urllib.request.urlopen(req_list, timeout=10) as resp:
            models_data = json.loads(resp.read().decode('utf-8'))
            for m in models_data.get('models', []):
                methods = m.get('supportedGenerationMethods', [])
                m_name = m.get('name', '').replace('models/', '')
                if 'generateContent' in methods and m_name.startswith('gemini'):
                    if not any(bad in m_name for bad in ['1.0', '1.5', 'tts', 'image', 'embedding', 'aqa', 'thinking']):
                        active_models.append(m_name)
    except Exception:
        pass

    preferred_order = [
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite',
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite',
        'gemini-flash-latest',
        'gemini-2.5-pro',
        'gemini-pro-latest'
    ]

    candidate_models = []
    for pm in preferred_order:
        if not active_models or pm in active_models:
            candidate_models.append(pm)
    for am in active_models:
        if am not in candidate_models:
            candidate_models.append(am)

    payload_dict = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": img_b64}}
            ]
        }],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 150
        }
    }
    payload_bytes = json.dumps(payload_dict).encode('utf-8')

    last_err = ""
    for model_name in candidate_models:
        for api_ver in ["v1beta", "v1"]:
            url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{model_name}:generateContent"
            req = urllib.request.Request(
                url,
                data=payload_bytes,
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0', 'x-goog-api-key': api_key},
                method='POST'
            )
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res_json = json.loads(resp.read().decode('utf-8'))
                    candidates = res_json.get('candidates', [])
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        raw_text = "".join(p.get('text', '') for p in parts).strip()
                        if raw_text:
                            valid_expr = validate_extracted_math(raw_text)
                            if valid_expr:
                                return valid_expr, None
                            cleaned = clean_ocr_math(raw_text)
                            if cleaned:
                                return cleaned, None
            except urllib.error.HTTPError as he:
                err_body = ""
                try:
                    err_body = he.read().decode('utf-8')
                except Exception:
                    pass
                if he.code == 404:
                    if not last_err:
                        last_err = f"404 ({model_name})"
                    continue
                elif he.code == 429:
                    last_err = "الخادم مشغول حالياً (تم تجاوز حد الطلبات في الدقيقة)، يرجى الانتظار ثواني والمحاولة مجدداً."
                    break
                else:
                    last_err = f"HTTP {he.code}: {err_body[:120]}"
                    break
            except Exception as e:
                last_err = str(e)
                break

    return None, last_err

def fix_arabic_pdf(text):
    return get_display(arabic_reshaper.reshape(text)) if PDF_ENABLED else text

def fix_arabic_mpl(text):
    return arabic_reshaper.reshape(text) if PDF_ENABLED else text

def sanitize_latex(expr):
    expr = elim_hyperbolic(expr)
    if hasattr(expr, 'has'):
        if expr.has(sp.LambertW) or (hasattr(sp, 'RootOf') and expr.has(sp.RootOf)):
            try:
                fl = safe_float(expr)
                if np.isfinite(fl):
                    return str(int(round(fl))) if abs(fl - round(fl)) < 1e-5 else str(round(fl, 2))
            except Exception:
                pass
        try:
            if not expr.free_symbols and expr.is_Add:
                pos_e, nums, neg_e = [], [], []
                for arg in expr.args:
                    if arg == sp.E or (arg.is_Mul and arg.has(sp.E) and not arg.has(sp.exp(-1)) and not arg.has(1/sp.E) and safe_float(arg) > 0):
                        pos_e.append(sp.latex(arg))
                    elif arg.is_Rational or arg.is_Integer:
                        nums.append(arg)
                    else:
                        neg_e.append(arg)
                if pos_e:
                    res_parts = [pos_e[0]]
                    for pe in pos_e[1:]:
                        res_parts.append(f"+ {pe}" if not pe.startswith('-') else pe)
                    for n_arg in nums:
                        n_lat = sp.latex(n_arg)
                        res_parts.append(f"+ {n_lat}" if not n_lat.startswith('-') else n_lat)
                    for ne_arg in neg_e:
                        if ne_arg == -sp.exp(-1) or ne_arg == -1/sp.E:
                            res_parts.append("- e^{-1}")
                        elif ne_arg == sp.exp(-1) or ne_arg == 1/sp.E:
                            res_parts.append("+ e^{-1}")
                        else:
                            ne_lat = sp.latex(ne_arg)
                            res_parts.append(f"+ {ne_lat}" if not ne_lat.startswith('-') else ne_lat)
                    s_custom = " ".join(res_parts)
                    return s_custom.replace('log', 'ln').replace(r'\left', '').replace(r'\right', '')
        except Exception:
            pass

    if not isinstance(expr, str):
        expr = sp.latex(expr)
    s = str(expr).replace('log', 'ln').replace(r'\left', '').replace(r'\right', '').replace(r'\operatorname', r'\mathrm')
    return s

def format_lim_val(lim_sym):
    lim_sym = elim_hyperbolic(lim_sym)
    if lim_sym == sp.oo or str(lim_sym) == 'oo':
        return r"+\infty"
    if lim_sym == -sp.oo or str(lim_sym) == '-oo':
        return r"-\infty"
    if lim_sym == sp.zoo or str(lim_sym) == 'zoo':
        return r"\pm\infty"
    if lim_sym == sp.nan or str(lim_sym) == 'nan' or 'AccumBounds' in str(lim_sym):
        return r"\text{غير موجودة}"
    return sanitize_latex(lim_sym)

def is_mixed_transcendental(expr, x_sym):
    if not hasattr(expr, 'has'):
        return False
    try:
        has_tr = expr.has(sp.exp, sp.log, sp.sin, sp.cos, sp.tan, sp.asin, sp.acos, sp.atan) or any(
            p.args[0] == sp.E and p.args[1].has(x_sym) for p in expr.atoms(sp.Pow)
        )
        if not has_tr:
            return False
        stripped = expr
        for a in list(expr.atoms(sp.exp, sp.log, sp.sin, sp.cos, sp.tan, sp.asin, sp.acos, sp.atan)):
            if a.has(x_sym):
                stripped = stripped.subs(a, sp.Symbol('C_tr'))
        for p in list(expr.atoms(sp.Pow)):
            if p.args[0] == sp.E and p.args[1].has(x_sym):
                stripped = stripped.subs(p, sp.Symbol('C_tr'))
        if stripped.has(x_sym) and expr.is_Add:
            return True
    except Exception:
        pass
    return False

def safe_solve_real(expr, x_sym, scan_limit=30.0):
    _check_deadline()
    roots = []
    if expr is None or expr == 0:
        return roots
    try:
        if expr.func == sp.exp or (expr.is_Pow and expr.args[0] == sp.E):
            return roots
    except Exception:
        pass
    has_non_alg = hasattr(expr, 'has') and (expr.has(sp.Abs) or expr.has(sp.sign))
    skip_symbolic = has_non_alg or is_mixed_transcendental(expr, x_sym)

    if not skip_symbolic:
        try:
            sol_list = sp.solve(expr, x_sym)
            for r in sol_list:
                r = elim_hyperbolic(r)
                fl = safe_float(r)
                if np.isfinite(fl):
                    if abs(fl - round(fl)) < 1e-6:
                        roots.append(sp.Integer(int(round(fl))))
                    elif hasattr(r, 'has') and (r.has(sp.LambertW) or (hasattr(sp, 'RootOf') and r.has(sp.RootOf))):
                        roots.append(sp.nsimplify(round(fl, 4), tolerance=1e-3))
                    else:
                        roots.append(elim_hyperbolic(sp.simplify(r)))
        except Exception:
            pass
    elif has_non_alg:
        try:
            for abs_atom in expr.atoms(sp.Abs):
                inner_arg = abs_atom.args[0]
                if not (inner_arg.has(sp.Abs) or inner_arg.has(sp.sign)):
                    for r in safe_solve_real(inner_arg, x_sym, scan_limit=scan_limit):
                        fl = safe_float(r)
                        if np.isfinite(fl):
                            chk = safe_float(expr.subs(x_sym, r))
                            if np.isfinite(chk) and abs(chk) < 1e-5:
                                roots.append(sp.Integer(int(round(fl))) if abs(fl - round(fl)) < 1e-6 else elim_hyperbolic(sp.simplify(r)))
        except Exception:
            pass

    try:
        f_num = safe_lambdify(x_sym, expr)
        # إذا كانت الدالة دورية مثلثية نحصر الفحص العددي في [-2pi, 2pi] لمنع ازدحام الجداول
        is_periodic_trig = hasattr(expr, 'has') and expr.has(sp.sin, sp.cos, sp.tan)
        bound_s = 6.5 if is_periodic_trig else scan_limit
        xs = np.linspace(-bound_s, bound_s, 2401)
        with np.errstate(all='ignore'):
            ys = f_num(xs)
        if np.iscomplexobj(ys):
            ys = np.where(np.isreal(ys), ys.real, np.nan)
        if np.isscalar(ys):
            ys = np.full_like(xs, float(ys), dtype=float)
        ys = np.array(ys, dtype=float)
        for i in range(len(ys) - 1):
            if np.isfinite(ys[i]) and np.isfinite(ys[i+1]):
                if abs(ys[i]) < 1e-9:
                    if i == 0:
                        if ys[i] != 0:
                            continue
                    elif not (abs(ys[i]) <= abs(ys[i+1]) and abs(ys[i]) <= abs(ys[i-1])):
                        continue
                    r_num = float(xs[i])
                    if not any(abs(safe_float(er) - r_num) < 1e-3 for er in roots):
                        roots.append(sp.Integer(int(round(r_num))) if abs(r_num - round(r_num)) < 1e-5 else sp.nsimplify(round(r_num, 4), tolerance=1e-3))
                elif ys[i] * ys[i+1] < 0 and abs(ys[i+1] - ys[i]) < 25.0:
                    a_b, b_b = float(xs[i]), float(xs[i+1])
                    fa_b = float(ys[i])
                    for _ in range(25):
                        m_b = 0.5 * (a_b + b_b)
                        with np.errstate(all='ignore'):
                            fm_b = float(f_num(m_b))
                        if not np.isfinite(fm_b):
                            break
                        if abs(fm_b) < 1e-10:
                            a_b = b_b = m_b
                            break
                        if fa_b * fm_b <= 0:
                            b_b = m_b
                        else:
                            a_b = m_b
                            fa_b = fm_b
                    r_num = 0.5 * (a_b + b_b)
                    with np.errstate(all='ignore'):
                        f_chk = float(f_num(r_num))
                    if np.isfinite(f_chk) and abs(f_chk) < 1e-3:
                        if not any(abs(safe_float(er) - r_num) < 1e-3 for er in roots):
                            if abs(r_num - round(r_num)) < 1e-5:
                                roots.append(sp.Integer(int(round(r_num))))
                            elif abs(r_num - 0.5) < 1e-4:
                                roots.append(sp.Rational(1, 2))
                            elif abs(r_num + 0.5) < 1e-4:
                                roots.append(sp.Rational(-1, 2))
                            elif abs(r_num - np.e) < 1e-4:
                                roots.append(sp.E)
                            elif abs(r_num + np.e) < 1e-4:
                                roots.append(-sp.E)
                            elif abs(r_num - 1/np.e) < 1e-4:
                                roots.append(sp.exp(-1))
                            elif abs(r_num + 1/np.e) < 1e-4:
                                roots.append(-sp.exp(-1))
                            elif abs(r_num - np.pi) < 1e-4:
                                roots.append(sp.pi)
                            elif abs(r_num + np.pi) < 1e-4:
                                roots.append(-sp.pi)
                            elif abs(r_num - np.pi/2) < 1e-4:
                                roots.append(sp.pi/2)
                            elif abs(r_num + np.pi/2) < 1e-4:
                                roots.append(-sp.pi/2)
                            else:
                                roots.append(sp.Float(round(r_num, 2)))
    except Exception:
        pass

    unique_roots = []
    for r in roots:
        fl = safe_float(r)
        if np.isfinite(fl) and not any(abs(safe_float(ur) - fl) < 1e-3 for ur in unique_roots):
            unique_roots.append(r)
    return unique_roots

def get_sol_color_pdf(sol_text):
    if "لا توجد" in sol_text or "ليس لها" in sol_text:
        return "#9B2226"
    return "#1F3A5F"

def get_sol_color_html(sol_text):
    if "لا توجد" in sol_text or "ليس لها" in sol_text:
        return "#EF4444"
    if "مضاعف" in sol_text:
        return "#F59E0B"
    if "حل وحيد" in sol_text or "حل واحد" in sol_text:
        return "#4ADE80"
    if "معدوم" in sol_text:
        return "#2DD4BF"
    if "حلان" in sol_text or "مختلفان" in sol_text:
        return "#38BDF8"
    if "ثلاثة" in sol_text:
        return "#F472B6"
    if "أربعة" in sol_text:
        return "#2DD4BF"
    return "#A78BFA"

if 'auto_play' not in st.session_state:
    st.session_state.auto_play = False
if 'f_val' not in st.session_state:
    st.session_state.f_val = "x+1+x*e^(-2*x)"
if 'g_val' not in st.session_state:
    st.session_state.g_val = "m"
if 'active_f' not in st.session_state:
    st.session_state.active_f = st.session_state.f_val
if 'active_g' not in st.session_state:
    st.session_state.active_g = st.session_state.g_val
if 'kbd_target' not in st.session_state:
    st.session_state.kbd_target = "f"

def apply_current_inputs():
    st.session_state.active_f = st.session_state.f_val.strip()
    st.session_state.active_g = st.session_state.g_val.strip() if st.session_state.g_val.strip() else "m"

with st.expander("⌨ لوحة المفاتيح المساعدة", expanded=False):
    t_sel = st.radio("🎯 تحديد خانة الكتابة:", ["f(x) الدالة", "m المستقيم بدلالة"], horizontal=True, key="kbd_radio")
    st.session_state.kbd_target = "f" if t_sel == "f(x) الدالة" else "g"
    def k_click(char):
        target = "f_val" if st.session_state.kbd_target == "f" else "g_val"
        if char == 'DEL':
            st.session_state[target] = st.session_state[target][:-1]
        elif char == 'CLR':
            st.session_state[target] = "" if target == "f_val" else "m"
        else:
            st.session_state[target] += char

    keys = [
        [("x", "x"), ("cos", "cos("), ("sin", "sin("), ("7", "7"), ("8", "8"), ("9", "9")],
        [("m", "m"), ("π", "pi"), ("ln", "ln("), ("4", "4"), ("5", "5"), ("6", "6")],
        [("■/■", "/"), ("√", "sqrt("), ("xⁿ", "^"), ("1", "1"), ("2", "2"), ("3", "3")],
        [("eˣ", "e^("), ("|x|", "abs("), ("=", "="), ("0", "0"), (".", "."), ("⌫", "DEL")],
        [("(", "("), (")", ")"), ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/")]
    ]
    for r_idx, row in enumerate(keys):
        cols = st.columns(6)
        for c_idx, (label, val) in enumerate(row):
            cols[c_idx].button(label, key=f"kb_{r_idx}_{c_idx}", on_click=k_click, args=(val,))
    st.button("مسح الكل (Clear)", on_click=k_click, args=("CLR",), use_container_width=True, type="primary")

api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

col_text, col_img = st.columns(2)
with col_img:
    img_file = st.file_uploader("🖼 ارفع صورة الدالة لاستخراجها آلياً:", type=['png', 'jpg', 'jpeg', 'webp'])
    st.markdown("<div style='font-size:14px; color:#94A3B8; text-align:right; direction:rtl; margin-top:-10px; margin-bottom:10px;'>💡 <b>ملاحظة:</b> في حال وجود ضغط على خادم الذكاء الاصطناعي وفشل قراءة الصورة، يرجى كتابة الدالة يدوياً في الخانة المجاورة.</div>", unsafe_allow_html=True)
    if img_file:
        if not api_key:
            st.error("⚠ خاصية الذكاء الاصطناعي غير مفعلة (ينقص مفتاح API).")
        else:
            if st.button("استخراج الدالة 🤖", use_container_width=True):
                with st.spinner("جاري قراءة الصورة واستخراج العبارة الرياضية..."):
                    extracted_text, err_msg = extract_math_from_image(img_file, api_key)
                    if extracted_text:
                        st.session_state.f_val = extracted_text
                        if not st.session_state.g_val.strip():
                            st.session_state.g_val = "m"
                        apply_current_inputs()
                        st.success(f"✅ تم الاستخراج بنجاح: {extracted_text}")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(f"❌ تعذر استخراج الدالة حالياً: {err_msg}")

with col_text:
    st.text_input("أدخل عبارة الدالة f(x):", key="f_val", max_chars=200, placeholder="مثال: x+1+x*e^(-2*x)", on_change=apply_current_inputs)
    st.text_input("أدخل معادلة المستقيم بدلالة m (تُترك m للمناقشة الأفقية):", key="g_val", max_chars=200, placeholder="m", on_change=apply_current_inputs)
    if st.button("✅ تأكيد ورسم الدالة", use_container_width=True):
        apply_current_inputs()

current_f = st.session_state.active_f
current_g = st.session_state.active_g
# ==================== نهاية الجزء (2/4) ====================
# ==================== بداية الجزء (3/4) ====================
def build_math_context(f_str, g_str, version_tag="v35"):
    cache = {'valid': False, 'error': ''}
    try:
        if not f_str or not f_str.strip():
            cache['error'] = 'EMPTY'
            return cache
        if not g_str or not g_str.strip():
            g_str = "m"

        x_sym, m_sym = sp.symbols('x m', real=True)
        local_dict = {
            'x': x_sym, 'm': m_sym, 'e': sp.E, 'E': sp.E, 'pi': sp.pi,
            'ln': sp.log, 'log': sp.log, 'exp': sp.exp, 'sqrt': sp.sqrt,
            'cbrt': lambda arg: sp.Pow(arg, sp.Rational(1, 3)),
            'abs': sp.Abs, 'Abs': sp.Abs, 'cos': sp.cos, 'sin': sp.sin, 'tan': sp.tan,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan
        }
        transformations = (standard_transformations + (implicit_multiplication_application,))
        f_processed = fix_implicit_mult(f_str)
        g_processed = fix_implicit_mult(g_str) or "m"
        f_expr = elim_hyperbolic(parse_expr(f_processed, local_dict=local_dict, transformations=transformations))
        g_expr = elim_hyperbolic(parse_expr(g_processed, local_dict=local_dict, transformations=transformations))
        
        f_func = safe_lambdify(x_sym, f_expr)
        g_func = safe_lambdify((x_sym, m_sym), g_expr)
        is_periodic_f = hasattr(f_expr, 'has') and f_expr.has(sp.sin, sp.cos, sp.tan)
        
        candidate_v_asymptotes = []
        try:
            if not f_expr.has(sp.Abs):
                n_expr, d_expr = sp.fraction(sp.together(f_expr))
            else:
                n_expr, d_expr = sp.fraction(f_expr)
            if d_expr != 1:
                for r in safe_solve_real(d_expr, x_sym):
                    candidate_v_asymptotes.append(r)
        except Exception:
            pass
        try:
            for pow_atom in f_expr.atoms(sp.Pow):
                base_p, exp_p = pow_atom.args
                fl_exp = safe_float(exp_p)
                if np.isfinite(fl_exp) and base_p.has(x_sym):
                    if fl_exp < 0:
                        for r in safe_solve_real(base_p, x_sym):
                            candidate_v_asymptotes.append(r)
                    elif isinstance(exp_p, sp.Rational) and exp_p.q % 2 == 0:
                        for r in safe_solve_real(base_p, x_sym):
                            candidate_v_asymptotes.append(r)
        except Exception:
            pass
        try:
            for log_expr in f_expr.atoms(sp.log):
                for r in safe_solve_real(log_expr.args[0], x_sym):
                    candidate_v_asymptotes.append(r)
        except Exception:
            pass
        try:
            for tan_expr in f_expr.atoms(sp.tan):
                for r in safe_solve_real(sp.cos(tan_expr.args[0]), x_sym, scan_limit=6.5):
                    candidate_v_asymptotes.append(r)
        except Exception:
            pass
        
        unique_cands = []
        for r in candidate_v_asymptotes:
            fl = safe_float(r)
            if np.isfinite(fl) and not any(abs(safe_float(uc) - fl) < 1e-4 for uc in unique_cands):
                unique_cands.append(r)
        candidate_v_asymptotes = unique_cands

        limit_memo = {}
        def cached_limit(expr_l, val_s, dir_s='+'):
            _check_deadline()
            key = (str(expr_l), str(val_s), str(dir_s))
            if key in limit_memo:
                return limit_memo[key]
            res = None
            try:
                if val_s == sp.oo:
                    res = elim_hyperbolic(sp.limit(expr_l, x_sym, sp.oo))
                elif val_s == -sp.oo:
                    res = elim_hyperbolic(sp.limit(expr_l, x_sym, -sp.oo))
                else:
                    res = elim_hyperbolic(sp.limit(expr_l, x_sym, val_s, dir=dir_s))
            except Exception:
                res = None

            if res is None or (hasattr(res, 'func') and (res.func == sp.Limit or 'AccumBounds' in str(res))):
                if val_s in [sp.oo, -sp.oo] and hasattr(expr_l, 'has') and expr_l.has(sp.sin, sp.cos, sp.tan):
                    if res is not None and 'AccumBounds' in str(res):
                        limit_memo[key] = sp.nan
                        return sp.nan
                try:
                    fn_tmp = safe_lambdify(x_sym, expr_l)
                    if val_s == sp.oo:
                        for x_t in [1e5, 1e3, 200.0, 50.0]:
                            with np.errstate(all='ignore'):
                                y_t = float(fn_tmp(x_t))
                            if np.isfinite(y_t):
                                if abs(y_t) > 1e5:
                                    res = sp.oo if y_t > 0 else -sp.oo
                                else:
                                    res = sp.nsimplify(round(y_t, 3), tolerance=1e-2)
                                break
                    elif val_s == -sp.oo:
                        for x_t in [-1e5, -1e3, -200.0, -50.0]:
                            with np.errstate(all='ignore'):
                                y_t = float(fn_tmp(x_t))
                            if np.isfinite(y_t):
                                if abs(y_t) > 1e5:
                                    res = sp.oo if y_t > 0 else -sp.oo
                                else:
                                    res = sp.nsimplify(round(y_t, 3), tolerance=1e-2)
                                break
                    else:
                        v_fl = safe_float(val_s)
                        sgn_d = 1.0 if dir_s == '+' else -1.0
                        with np.errstate(all='ignore'):
                            y1 = float(fn_tmp(v_fl + sgn_d * 1e-6))
                            y2 = float(fn_tmp(v_fl + sgn_d * 1e-4))
                        if np.isfinite(y1):
                            if abs(y1) > 1e4 and abs(y1) > abs(y2) * 5:
                                res = sp.oo if y1 > 0 else -sp.oo
                            else:
                                res = sp.nsimplify(round(y1, 3), tolerance=1e-2)
                except Exception:
                    res = sp.nan
            limit_memo[key] = res
            return res

        true_v_asymptotes, holes, domain_closed_bounds = [], [], set()
        for r in candidate_v_asymptotes:
            fl_r = safe_float(r)
            try:
                with np.errstate(all='ignore'):
                    ok_right = np.isfinite(float(f_func(fl_r + 1e-4)))
                    ok_left = np.isfinite(float(f_func(fl_r - 1e-4)))
                lim_p = cached_limit(f_expr, r, '+') if ok_right else sp.nan
                lim_m = cached_limit(f_expr, r, '-') if ok_left else sp.nan
                if lim_p in [sp.oo, -sp.oo, sp.zoo] or lim_m in [sp.oo, -sp.oo, sp.zoo]:
                    true_v_asymptotes.append(r)
                else:
                    val_at_r = safe_float(f_expr.subs(x_sym, r))
                    if np.isfinite(val_at_r):
                        domain_closed_bounds.add(round(fl_r, 4))
                    else:
                        val_p = safe_float(lim_p) if ok_right else safe_float(lim_m)
                        if np.isfinite(val_p):
                            holes.append({'sym': r, 'val': fl_r, 'lim': val_p})
            except Exception:
                true_v_asymptotes.append(r)

        unique_asymptotes = [{'type': 'v', 'val': safe_float(r), 'label': f"x={sanitize_latex(r)}"} for r in true_v_asymptotes]

        abs_corner_syms = []
        try:
            for abs_atom in f_expr.atoms(sp.Abs):
                for r_c in safe_solve_real(abs_atom.args[0], x_sym):
                    fl_c = safe_float(r_c)
                    if np.isfinite(fl_c) and not any(abs(fl_c - safe_float(ac)) < 1e-4 for ac in abs_corner_syms):
                        abs_corner_syms.append(r_c)
        except Exception:
            pass

        df_expr = sp.diff(f_expr, x_sym)
        df_clean = df_expr.replace(sp.sign, lambda arg: arg / sp.Abs(arg))
        if not df_clean.has(sp.Abs):
            df_simp = elim_hyperbolic(sp.simplify(df_clean))
            if df_simp.has(sp.Piecewise):
                df_simp = df_clean 
            try:
                df_together = elim_hyperbolic(sp.together(df_simp))
                if not df_together.has(sp.Piecewise):
                    df_simp = df_together
            except Exception:
                pass
            try:
                df_factored = elim_hyperbolic(sp.factor(sp.expand(df_simp)))
                if not df_factored.has(sp.Piecewise) and len(sanitize_latex(df_factored)) <= len(sanitize_latex(df_simp)) + 10:
                    df_simp = df_factored
            except Exception:
                pass
        else:
            df_simp = df_clean
        df_latex_str_safe = sanitize_latex(df_simp)

        sym_extrema = []
        try:
            num_df, _ = sp.fraction(sp.together(df_clean) if not df_clean.has(sp.Abs) else df_clean)
            for r_simp in safe_solve_real(num_df, x_sym):
                if np.isfinite(safe_float(f_expr.subs(x_sym, r_simp))):
                    sym_extrema.append(r_simp)
        except Exception:
            pass

        # تحديد نافذة الرسم الديناميكية التلقائية (Auto-Adaptive Viewport) لتشمل جميع النقاط المهمة
        key_x_floats = [safe_float(r) for r in candidate_v_asymptotes + abs_corner_syms + sym_extrema if np.isfinite(safe_float(r))]
        max_abs_x = max([abs(v) for v in key_x_floats if abs(v) <= 40.0], default=8.0)
        plot_x_bound = float(max(12.0, min(35.0, np.ceil(max_abs_x + 4.0))))
        scan_x_bound = float(plot_x_bound + 3.0)

        x_base = np.linspace(-scan_x_bound, scan_x_bound, 3601)
        extra_x = []
        for a in candidate_v_asymptotes:
            val = safe_float(a)
            if np.isfinite(val) and -scan_x_bound <= val <= scan_x_bound:
                extra_x.append(val)
                for delta in [1e-3, 1e-4, 1e-5]:
                    extra_x.extend([val - delta, val + delta])
        for ac in abs_corner_syms:
            val_c = safe_float(ac)
            if np.isfinite(val_c) and -scan_x_bound <= val_c <= scan_x_bound:
                extra_x.append(val_c)
                    
        x_vals_plot = np.sort(np.concatenate([x_base, extra_x])) if extra_x else x_base

        def process_y_vals(x_arr):
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                y_arr = f_func(x_arr)
            if np.iscomplexobj(y_arr):
                y_arr = np.where(np.isreal(y_arr), y_arr.real, np.nan)
            if np.isscalar(y_arr):
                y_arr = np.full_like(x_arr, y_arr, dtype=float)
            y_arr = np.array(y_arr, dtype=float)
            y_arr[~np.isfinite(y_arr)] = np.nan
            dy = np.abs(np.diff(y_arr))
            for idx in np.where(dy > 35)[0]:
                y_arr[idx] = np.nan
                y_arr[idx+1] = np.nan
            return y_arr

        y_vals_plot = process_y_vals(x_vals_plot)

        def build_derivative_steps():
            steps = []
            try:
                if f_expr.func == sp.Abs and len(f_expr.args) > 0:
                    inner = f_expr.args[0]
                    d_in = elim_hyperbolic(sp.simplify(sp.diff(inner, x_sym)))
                    steps.append({
                        'label': 'قانون مشتق دالة القيمة المطلقة:',
                        'math_list': [
                            r"\left(|u(x)|\right)' = \frac{u'(x) \cdot u(x)}{|u(x)|}",
                            fr"f'(x) = \frac{{({sanitize_latex(d_in)})({sanitize_latex(inner)})}}{{\left|{sanitize_latex(inner)}\right|}}"
                        ]
                    })
                    return steps
                if f_expr.is_Pow and f_expr.args[1] == sp.Rational(1, 2):
                    inner = f_expr.args[0]
                    d_in = elim_hyperbolic(sp.simplify(sp.diff(inner, x_sym)))
                    steps.append({
                        'label': 'قانون مشتق الدالة الجذرية:',
                        'math_list': [
                            r"\left(\sqrt{u(x)}\right)' = \frac{u'(x)}{2\sqrt{u(x)}}",
                            fr"f'(x) = \frac{{{sanitize_latex(d_in)}}}{{2\sqrt{{{sanitize_latex(inner)}}}}}"
                        ]
                    })
                    return steps
                num, den = sp.fraction(f_expr)
                if den != 1 and den.has(x_sym):
                    du = elim_hyperbolic(sp.simplify(sp.diff(num, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a))))
                    dv = elim_hyperbolic(sp.simplify(sp.diff(den, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a))))
                    u_l, v_l = sanitize_latex(num), sanitize_latex(den)
                    du_l, dv_l = sanitize_latex(du), sanitize_latex(dv)
                    steps.append({'label': 'قانون مشتق حاصل قسمة:', 'math_list': [r"f'(x) = \frac{u'(x) \cdot v(x) - v'(x) \cdot u(x)}{(v(x))^2}"]})
                    steps.append({'label': 'حساب مشتق البسط والمقام:', 'math_list': [fr"u(x) = {u_l} \Rightarrow u'(x) = {du_l}", fr"v(x) = {v_l} \Rightarrow v'(x) = {dv_l}"]})
                    steps.append({'label': 'بالتعويض في القانون:', 'math_list': [fr"f'(x) = \frac{{({du_l})({v_l}) - ({dv_l})({u_l})}}{{({v_l})^2}}"]})
                elif f_expr.is_Add:
                    term_derivs, sub_rules = [], []
                    for arg in f_expr.args:
                        d_arg = elim_hyperbolic(sp.simplify(sp.diff(arg, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a))))
                        if arg.is_number:
                            sub_rules.append(fr"({sanitize_latex(arg)})' = 0")
                        else:
                            num_a, den_a = sp.fraction(arg)
                            if den_a != 1 and den_a.has(x_sym):
                                du_a = elim_hyperbolic(sp.simplify(sp.diff(num_a, x_sym)))
                                dv_a = elim_hyperbolic(sp.simplify(sp.diff(den_a, x_sym)))
                                sub_rules.append(fr"\left({sanitize_latex(arg)}\right)' = \frac{{({sanitize_latex(du_a)})({sanitize_latex(den_a)}) - ({sanitize_latex(dv_a)})({sanitize_latex(num_a)})}}{{({sanitize_latex(den_a)})^2}} = {sanitize_latex(d_arg)}")
                            else:
                                sub_rules.append(fr"\left({sanitize_latex(arg)}\right)' = {sanitize_latex(d_arg)}")
                        if d_arg != 0:
                            term_derivs.append(d_arg)
                    for idx_s, rule_str in enumerate(sub_rules):
                        steps.append({'label': f'مشتق الحد ({idx_s + 1}):', 'math_list': [rule_str]})
                    raw_sum = elim_hyperbolic(sp.Add(*term_derivs)) if term_derivs else sp.Integer(0)
                    if sanitize_latex(raw_sum) != df_latex_str_safe:
                        steps.append({'label': 'بجمع المشتقات الجزئية وتبسيط العبارة:', 'math_list': [fr"f'(x) = {sanitize_latex(raw_sum)}"]})
                elif f_expr.is_Mul:
                    x_factors = [f for f in f_expr.as_ordered_factors() if f.has(x_sym)]
                    c_factors = [f for f in f_expr.as_ordered_factors() if not f.has(x_sym)]
                    if len(x_factors) >= 2:
                        u_p, v_p = x_factors[0] * sp.Mul(*c_factors), sp.Mul(*x_factors[1:])
                        du_p = elim_hyperbolic(sp.simplify(sp.diff(u_p, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a))))
                        dv_p = elim_hyperbolic(sp.simplify(sp.diff(v_p, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a))))
                        steps.append({'label': 'قانون مشتق جداء:', 'math_list': [r"f'(x) = u'(x) \cdot v(x) + v'(x) \cdot u(x)"]})
                        steps.append({'label': 'حساب المشتقات الجزئية:', 'math_list': [fr"u(x) = {sanitize_latex(u_p)} \Rightarrow u'(x) = {sanitize_latex(du_p)}", fr"v(x) = {sanitize_latex(v_p)} \Rightarrow v'(x) = {sanitize_latex(dv_p)}"]})
                        steps.append({'label': 'بالتعويض في القانون:', 'math_list': [fr"f'(x) = ({sanitize_latex(du_p)})({sanitize_latex(v_p)}) + ({sanitize_latex(dv_p)})({sanitize_latex(u_p)})"]})
            except Exception:
                pass
            return steps

        deriv_steps_detailed = build_derivative_steps()

        pts_var_exact = [{'val': -np.inf, 'sym': -sp.oo, 'latex_x': r"-\infty", 'type': 'inf'}]
        for r in candidate_v_asymptotes:
            fl_r = safe_float(r)
            p_type = 'bound' if round(fl_r, 4) in domain_closed_bounds else 'v_asym'
            pts_var_exact.append({'val': fl_r, 'sym': r, 'latex_x': sanitize_latex(r), 'type': p_type})
        for r_c in abs_corner_syms:
            val_c = safe_float(r_c)
            if np.isfinite(val_c) and not any(abs(p['val'] - val_c) < 1e-4 for p in pts_var_exact):
                if np.isfinite(safe_float(f_expr.subs(x_sym, r_c))):
                    pts_var_exact.append({'val': val_c, 'sym': r_c, 'latex_x': sanitize_latex(r_c), 'type': 'corner'})
        for r in sym_extrema:
            val = safe_float(r)
            if np.isfinite(val) and not any(abs(p['val'] - val) < 1e-4 for p in pts_var_exact):
                pts_var_exact.append({'val': val, 'sym': r, 'latex_x': sanitize_latex(r), 'type': 'extrema'})

        is_valid_plot = ~np.isnan(y_vals_plot)
        edges = np.diff(is_valid_plot.astype(int))
        starts = np.where(edges == 1)[0] + 1
        if is_valid_plot[0]:
            starts = np.insert(starts, 0, 0)
        ends = np.where(edges == -1)[0]
        if is_valid_plot[-1]:
            ends = np.append(ends, len(y_vals_plot) - 1)

        for s, e in zip(starts, ends):
            segment, seg_x = y_vals_plot[s:e+1], x_vals_plot[s:e+1]
            if len(segment) > 10:
                peaks, _ = find_peaks(segment, prominence=0.02)
                valleys, _ = find_peaks(-segment, prominence=0.02)
                for p_idx in list(peaks) + list(valleys):
                    nx = float(seg_x[p_idx])
                    if is_periodic_f and abs(nx) > 6.5:
                        continue
                    if not any(abs(p['val'] - nx) < 0.1 for p in pts_var_exact):
                        try:
                            sym_nx = sp.Float(round(nx, 2))
                            if np.isfinite(safe_float(f_expr.subs(x_sym, sym_nx))):
                                pts_var_exact.append({'val': safe_float(sym_nx), 'sym': sym_nx, 'latex_x': sanitize_latex(sym_nx), 'type': 'extrema'})
                        except Exception:
                            pass
                
        pts_var_exact.append({'val': np.inf, 'sym': sp.oo, 'latex_x': r"+\infty", 'type': 'inf'})
        pts_var_exact.sort(key=lambda p: p['val'])

        # إذا كانت الدالة دورية مثلثية وكثرت النقاط، نحتفظ بأقرب 7 فواصل للمركز لتفادي ازدحام جدول التغيرات
        if len(pts_var_exact) > 9:
            inner_pts = pts_var_exact[1:-1]
            inner_pts.sort(key=lambda p: abs(p['val']))
            kept_inner = sorted(inner_pts[:7], key=lambda p: p['val'])
            pts_var_exact = [pts_var_exact[0]] + kept_inner + [pts_var_exact[-1]]

        df_func_test = safe_lambdify(x_sym, df_clean)
        for p in pts_var_exact:
            if p['type'] == 'extrema':
                v_test = p['val']
                with np.errstate(all='ignore'):
                    df_val = df_func_test(v_test)
                    df_p, df_m = df_func_test(v_test + 1e-4), df_func_test(v_test - 1e-4)
                diff_lr = abs(df_p - df_m) if (np.isfinite(df_p) and np.isfinite(df_m)) else 999.0
                if not np.isfinite(df_val) or abs(df_p) > 20 or abs(df_m) > 20 or diff_lr > 0.05:
                    p['type'] = 'corner'

        valid_intervals = []
        for i in range(len(pts_var_exact) - 1):
            left, right = pts_var_exact[i]['val'], pts_var_exact[i+1]['val']
            mid = 0 if (left == -np.inf and right == np.inf) else (right - 1 if left == -np.inf else (left + 1 if right == np.inf else (left + right) / 2.0))
            try:
                v_mid = f_func(mid)
                valid_intervals.append(not np.iscomplexobj(v_mid) and np.isfinite(float(v_mid)))
            except Exception:
                valid_intervals.append(False)
            
        while len(valid_intervals) > 0 and not valid_intervals[0]:
            valid_intervals.pop(0)
            pts_var_exact.pop(0)
        while len(valid_intervals) > 0 and not valid_intervals[-1]:
            valid_intervals.pop(-1)
            pts_var_exact.pop(-1)

        domain_intervals_str = []
        i = 0
        while i < len(valid_intervals):
            if valid_intervals[i]:
                start_idx = i
                while i < len(valid_intervals) - 1 and valid_intervals[i+1] and pts_var_exact[i+1]['type'] != 'v_asym':
                    i += 1
                end_idx = i
                l_pt = pts_var_exact[start_idx]
                r_pt = pts_var_exact[end_idx+1]
                l_b = r"-\infty" if l_pt['val'] == -np.inf else l_pt['latex_x']
                r_b = r"+\infty" if r_pt['val'] == np.inf else r_pt['latex_x']
                l_br = "[" if l_pt['type'] == 'bound' else "]"
                r_br = "]" if r_pt['type'] == 'bound' else "["
                domain_intervals_str.append(fr"{l_br}{l_b}; {r_b}{r_br}")
            i += 1
                
        domain_latex_st = r"D_f = \color{#FFD700}{" + (r" \cup ".join(domain_intervals_str) if domain_intervals_str else r"\emptyset") + r"}"
        domain_latex_mpl = r"D_f = " + (r" \cup ".join(domain_intervals_str) if domain_intervals_str else r"\emptyset")

        limits_data_detailed = []
        limits_mpl_items = [{'type': 'domain', 'latex': domain_latex_mpl}]
        oblique_details_list = []

        def build_limit_steps(val_sym, dir_sympy, target_latex, arrow_latex):
            steps_math = []
            step_note = None
            try:
                num, den = sp.fraction(f_expr)
                if den != 1 and not den.is_number:
                    l_num = cached_limit(num, val_sym, dir_sympy)
                    l_den = cached_limit(den, val_sym, dir_sympy)
                    l_num_s, l_den_s = format_lim_val(l_num), format_lim_val(l_den)
                    if l_den == 0 and val_sym not in [sp.oo, -sp.oo]:
                        try:
                            eps = 1e-5 if dir_sympy == '+' else -1e-5
                            d_val = safe_float(den.subs(x_sym, safe_float(val_sym) + eps))
                            l_den_s = "0^+" if d_val > 0 else "0^-"
                        except Exception:
                            pass
                    steps_math.append(fr"\lim_{{x {arrow_latex} {target_latex}}} \left({sanitize_latex(num)}\right) = {l_num_s}")
                    steps_math.append(fr"\lim_{{x {arrow_latex} {target_latex}}} \left({sanitize_latex(den)}\right) = {l_den_s}")
                    if l_num in [sp.oo, -sp.oo] and l_den in [sp.oo, -sp.oo]:
                        step_note = "إزالة حالة عدم التعيين بالتزايد المقارن" if (f_expr.has(sp.exp) or f_expr.has(sp.log)) else "إزالة حالة عدم التعيين بأخذ أكبر حد على أكبر حد"
                elif f_expr.is_Add:
                    has_pos_inf, has_neg_inf = False, False
                    for arg in f_expr.args:
                        if not arg.is_number:
                            l_p = cached_limit(arg, val_sym, dir_sympy)
                            if l_p == sp.oo:
                                has_pos_inf = True
                            if l_p == -sp.oo:
                                has_neg_inf = True
                            steps_math.append(fr"\lim_{{x {arrow_latex} {target_latex}}} \left({sanitize_latex(arg)}\right) = {format_lim_val(l_p)}")
                    if has_pos_inf and has_neg_inf and (f_expr.has(sp.exp) or f_expr.has(sp.log)):
                        step_note = "إزالة حالة عدم التعيين بالتزايد المقارن"
            except Exception:
                pass
            return steps_math, step_note

        def build_geometric_interpretation(val_sym, lim_sym, target_latex):
            try:
                lim_sym = elim_hyperbolic(lim_sym)
                lim_fl = safe_float(lim_sym)
                if val_sym in [sp.oo, -sp.oo]:
                    if np.isfinite(lim_fl):
                        b_lat = sanitize_latex(elim_hyperbolic(sp.simplify(lim_sym)))
                        if not any(a['type'] == 'h' and abs(a['val'] - lim_fl) < 1e-4 for a in unique_asymptotes):
                            unique_asymptotes.append({'type': 'h', 'val': lim_fl, 'label': f"y={b_lat}"})
                        st_txt = fr"📐 **التفسير البياني:** المنحنى $(C_f)$ يقبل مستقيماً مقارباً أفقياً بجوار ${target_latex}$ معادلته: $y = {b_lat}$"
                        mpl_txt = "التفسير البياني: المنحنى يقبل مستقيماً مقارباً أفقياً معادلته:"
                        return st_txt, mpl_txt, f"y = {b_lat}"
                    elif lim_sym in [sp.oo, -sp.oo] or str(lim_sym) in ['oo', '-oo']:
                        x_test_inf = 1e4 if val_sym == sp.oo else -1e4
                        with np.errstate(all='ignore'):
                            a_est = float(f_func(x_test_inf)) / x_test_inf
                        if not np.isfinite(a_est) or abs(a_est) > 500 or abs(a_est) < 1e-5:
                            return None, None, None
                        a_sym = cached_limit(sp.together(f_expr / x_sym), val_sym)
                        a_fl = safe_float(a_sym)
                        if np.isfinite(a_fl) and abs(a_fl) >= 1e-7:
                            diff_expr = sp.together(f_expr - a_sym * x_sym)
                            b_sym = cached_limit(diff_expr, val_sym)
                            b_fl = safe_float(b_sym)
                            if np.isfinite(b_fl):
                                line_expr = elim_hyperbolic(sp.simplify(a_sym * x_sym + b_sym))
                                line_lat = sanitize_latex(line_expr)
                                a_lat = sanitize_latex(elim_hyperbolic(sp.simplify(a_sym)))
                                b_lat = sanitize_latex(elim_hyperbolic(sp.simplify(b_sym)))
                                rem_expr = elim_hyperbolic(sp.simplify(sp.together(f_expr - line_expr)))
                                if not rem_expr.has(sp.Abs):
                                    try:
                                        rem_fact = elim_hyperbolic(sp.factor(sp.expand(rem_expr)))
                                        if not rem_fact.has(sp.Piecewise):
                                            rem_expr = rem_fact
                                    except Exception:
                                        pass
                                rem_lat = sanitize_latex(rem_expr)
                                if not any(a['type'] == 'oblique' and abs(a['a'] - a_fl) < 1e-4 and abs(a['b'] - b_fl) < 1e-4 for a in unique_asymptotes):
                                    unique_asymptotes.append({'type': 'oblique', 'a': a_fl, 'b': b_fl, 'label': f"y={line_lat}"})
                                if not any(abs(od['a_fl'] - a_fl) < 1e-4 and abs(od['b_fl'] - b_fl) < 1e-4 for od in oblique_details_list):
                                    oblique_details_list.append({
                                        'target_latex': target_latex, 'a_sym': a_sym, 'b_sym': b_sym,
                                        'a_fl': a_fl, 'b_fl': b_fl, 'a_lat': a_lat, 'b_lat': b_lat,
                                        'line_expr': line_expr, 'line_lat': line_lat,
                                        'rem_expr': rem_expr, 'rem_lat': rem_lat
                                    })
                        return None, None, None
                else:
                    if lim_sym in [sp.oo, -sp.oo, sp.zoo] or str(lim_sym) in ['oo', '-oo', 'zoo'] or not np.isfinite(lim_fl):
                        st_txt = fr"📐 **التفسير البياني:** المنحنى $(C_f)$ يقبل مستقيماً مقارباً عمودياً (موازياً لمحور التراتيب) معادلته: $x = {target_latex}$"
                        mpl_txt = "التفسير البياني: المنحنى يقبل مستقيماً مقارباً عمودياً معادلته:"
                        return st_txt, mpl_txt, f"x = {target_latex}"
            except Exception:
                pass
            return None, None, None

        def add_limit(val_sym, dir_sympy, target_latex, arrow_latex=r"\to"):
            try:
                lim = cached_limit(f_expr, val_sym, dir_sympy)
                lim_latex = format_lim_val(lim)
                expr_latex = sanitize_latex(f_expr)
                steps_list, step_note = build_limit_steps(val_sym, dir_sympy, target_latex, arrow_latex)
                geo_st_txt, geo_mpl_txt, geo_mpl_math = build_geometric_interpretation(val_sym, lim, target_latex)
                
                latex_streamlit = fr"\lim_{{x {arrow_latex} {target_latex}}} f(x) = \lim_{{x {arrow_latex} {target_latex}}} \left( {expr_latex} \right) = \mathbf{{\color{{#CBD5E1}}{{{lim_latex}}}}}"
                limits_data_detailed.append({
                    'main': latex_streamlit, 'steps': steps_list, 'step_note': step_note, 'geo_txt': geo_st_txt
                })
                lhs_mpl = fr"\lim_{{x {arrow_latex} {target_latex}}} f(x) = \lim_{{x {arrow_latex} {target_latex}}} \left( {expr_latex} \right) ="
                limits_mpl_items.append({'type': 'main', 'lhs': lhs_mpl, 'rhs': fr"{lim_latex}"})
                for stp in steps_list:
                    limits_mpl_items.append({'type': 'step', 'math': stp})
                if step_note:
                    limits_mpl_items.append({'type': 'note', 'text': f"({step_note})"})
                if geo_mpl_txt:
                    limits_mpl_items.append({'type': 'geo', 'text': geo_mpl_txt, 'math': geo_mpl_math})
            except Exception:
                pass

        if len(pts_var_exact) > 0:
            if valid_intervals and valid_intervals[0] and pts_var_exact[0]['sym'] == -sp.oo:
                add_limit(-sp.oo, '+', r"-\infty", r"\to")
            if valid_intervals and valid_intervals[-1] and pts_var_exact[-1]['sym'] == sp.oo:
                add_limit(sp.oo, '-', r"+\infty", r"\to")
            for i, p in enumerate(pts_var_exact):
                if p['type'] == 'v_asym':
                    v_latex = p['latex_x']
                    if i > 0 and valid_intervals[i-1]:
                        add_limit(p['sym'], '-', v_latex, r"\overset{<}{\to}")
                    if i < len(valid_intervals) and valid_intervals[i]:
                        add_limit(p['sym'], '+', v_latex, r"\overset{>}{\to}")

        def exactify_value(val_float, sym_val=None):
            _check_deadline()
            if sym_val is not None:
                try:
                    sym_val = elim_hyperbolic(sp.simplify(sym_val))
                    if not any(bad in str(sym_val) for bad in ["LambertW", "RootOf", "Integral", "zoo", "I", "sinh", "cosh"]):
                        l_str = sanitize_latex(sym_val)
                        if len(l_str) < 30:
                            return l_str
                except Exception:
                    pass
            if abs(val_float - np.e) < 1e-3:
                return "e"
            if abs(val_float + np.e) < 1e-3:
                return "-e"
            if abs(val_float - 1/np.e) < 1e-3:
                return r"\frac{1}{e}"
            if abs(val_float + 1/np.e) < 1e-3:
                return r"-\frac{1}{e}"
            if abs(val_float - (np.e - 2)) < 1e-3:
                return "e - 2"
            if abs(val_float - (np.e - 2 - 1/np.e)) < 1e-3:
                return "e - 2 - e^{-1}"
            if abs(val_float - np.pi) < 1e-3:
                return r"\pi"
            if abs(val_float + np.pi) < 1e-3:
                return r"-\pi"
            if abs(val_float - np.e**2) < 1e-3:
                return "e^2"
            if abs(val_float + np.e**2) < 1e-3:
                return "-e^2"
            if abs(val_float - 2*np.e) < 1e-3:
                return "2e"
            if abs(val_float + 2*np.e) < 1e-3:
                return "-2e"
            if abs(val_float - int(round(val_float))) < 1e-3:
                return str(int(round(val_float)))
            return str(round(val_float, 2)).rstrip('0').rstrip('.') if '.' in str(round(val_float, 2)) else str(round(val_float, 2))

        def extract_sign_factors(rem_expr):
            try:
                if rem_expr.has(sp.Abs):
                    return []
                fact_expr = elim_hyperbolic(sp.factor(sp.expand(rem_expr)))
                num_f, den_f = sp.fraction(sp.together(fact_expr))
                raw_factors = []
                if num_f.is_Mul:
                    raw_factors.extend(list(num_f.args))
                elif num_f != 1:
                    raw_factors.append(num_f)
                if den_f != 1:
                    if den_f.is_Mul:
                        raw_factors.extend(list(den_f.args))
                    else:
                        raw_factors.append(den_f)

                const_coeff = sp.Integer(1)
                pos_exp_factors, var_factors = [], []
                for rf in raw_factors:
                    if rf.is_number:
                        const_coeff *= rf
                    elif rf.func == sp.exp or (rf.is_Pow and rf.args[0] == sp.E):
                        pos_exp_factors.append(rf)
                    else:
                        var_factors.append(rf)

                if 2 <= len(var_factors) <= 3:
                    final_factors = []
                    for idx_vf, vf in enumerate(var_factors):
                        f_item = vf
                        if idx_vf == 0:
                            if const_coeff != 1:
                                f_item = const_coeff * f_item
                            for pef in pos_exp_factors:
                                f_item = f_item * pef
                        f_roots = [safe_float(r) for r in safe_solve_real(vf, x_sym)]
                        final_factors.append({
                            'expr': f_item, 'latex': sanitize_latex(f_item),
                            'func': safe_lambdify(x_sym, f_item),
                            'roots': [r for r in f_roots if np.isfinite(r)]
                        })
                    return final_factors
            except Exception:
                pass
            return []

        rel_pos_tables_info = []
        for od in oblique_details_list:
            rem_expr = od['rem_expr']
            num_rem, den_rem = sp.fraction(sp.together(rem_expr))
            diff_roots = safe_solve_real(num_rem, x_sym)
            rp_pts = [{'val': -np.inf, 'sym': -sp.oo, 'latex_x': r"-\infty", 'type': 'inf'}]
            for r in candidate_v_asymptotes:
                rp_pts.append({'val': safe_float(r), 'sym': r, 'latex_x': sanitize_latex(r), 'type': 'v_asym'})
            for r in diff_roots:
                fl = safe_float(r)
                if np.isfinite(fl) and not any(abs(p['val'] - fl) < 1e-4 for p in rp_pts):
                    if np.isfinite(safe_float(f_expr.subs(x_sym, r))):
                        rp_pts.append({'val': fl, 'sym': r, 'latex_x': sanitize_latex(r), 'type': 'root'})
            rp_pts.append({'val': np.inf, 'sym': sp.oo, 'latex_x': r"+\infty", 'type': 'inf'})
            rp_pts.sort(key=lambda p: p['val'])

            rem_func = safe_lambdify(x_sym, rem_expr)
            rp_signs, rp_mids = [], []
            for idx_rp in range(len(rp_pts) - 1):
                l_v, r_v = rp_pts[idx_rp]['val'], rp_pts[idx_rp+1]['val']
                mid = 0.0 if (l_v == -np.inf and r_v == np.inf) else (r_v - 1.0 if l_v == -np.inf else (l_v + 1.0 if r_v == np.inf else (l_v + r_v)/2.0))
                rp_mids.append(mid)
                try:
                    val_m = float(rem_func(mid))
                    if np.isfinite(val_m):
                        rp_signs.append("+" if val_m > 0 else "-")
                    else:
                        rp_signs.append(None)
                except Exception:
                    rp_signs.append(None)

            while len(rp_signs) > 1 and rp_signs[0] is None:
                rp_signs.pop(0)
                rp_mids.pop(0)
                rp_pts.pop(0)
            while len(rp_signs) > 1 and rp_signs[-1] is None:
                rp_signs.pop(-1)
                rp_mids.pop(-1)
                rp_pts.pop(-1)

            factor_rows = extract_sign_factors(rem_expr)
            n_f_rows = len(factor_rows)
            N_rp = len(rp_pts)
            n_intervals_rp = max(1, N_rp - 1)
            seg_w_rp = 3.6
            x_st_rp = 2.5
            x_max_rp = x_st_rp + n_intervals_rp * seg_w_rp
            tri_half_w = min(0.78, seg_w_rp * 0.22)

            def get_rp_xc(idx_pt):
                return x_st_rp + idx_pt * seg_w_rp
            def get_rp_label_x(idx_pt):
                if idx_pt == 0:
                    return x_st_rp + 0.50
                if idx_pt == N_rp - 1:
                    return x_max_rp - 0.50
                return x_st_rp + idx_pt * seg_w_rp

            y_pos_top = 2.2
            row_h = 0.95
            y_rem_top = y_pos_top + row_h
            y_factors_top = y_rem_top + n_f_rows * row_h
            y_table_top = y_factors_top + row_h

            fig_rp, ax_rp = new_fig(figsize=(max(8.5, x_max_rp * 0.82), max(3.2, y_table_top * 0.65)))
            fig_rp.patch.set_facecolor('white')
            ax_rp.set_facecolor('white')
            ax_rp.axis('off')

            ax_rp.plot([0, x_max_rp], [y_table_top, y_table_top], 'k-', lw=2)
            ax_rp.plot([0, x_max_rp], [y_factors_top, y_factors_top], 'k-', lw=1.5)
            for idx_fr in range(n_f_rows):
                y_line_f = y_factors_top - (idx_fr + 1) * row_h
                ax_rp.plot([0, x_max_rp], [y_line_f, y_line_f], 'k-', lw=1.3)
            ax_rp.plot([0, x_max_rp], [y_pos_top, y_pos_top], 'k-', lw=1.5)
            ax_rp.plot([0, x_max_rp], [0, 0], 'k-', lw=2)
            for xl_rp in [0, x_st_rp, x_max_rp]:
                ax_rp.plot([xl_rp, xl_rp], [0, y_table_top], 'k-', lw=2)

            ax_rp.text(x_st_rp/2, y_factors_top + row_h/2, '$x$', ha='center', va='center', fontsize=16, color='#1F2937', fontweight='bold')
            for idx_fr, f_info in enumerate(factor_rows):
                y_f_c = y_factors_top - (idx_fr + 0.5) * row_h
                try:
                    ax_rp.text(x_st_rp/2, y_f_c, f"${f_info['latex']}$", ha='center', va='center', fontsize=14, color='#1F2937', fontweight='bold')
                except Exception:
                    ax_rp.text(x_st_rp/2, y_f_c, str(f_info['expr']), ha='center', va='center', fontsize=12, color='#1F2937')

            ax_rp.text(x_st_rp/2, y_pos_top + row_h/2, '$f(x) - y$', ha='center', va='center', fontsize=14.5, color='#1F2937', fontweight='bold')
            ax_rp.text(x_st_rp/2, y_pos_top * 0.62, fix_arabic_mpl("الوضع"), ha='center', va='center', fontsize=14, color='#1F2937', fontweight='bold')
            ax_rp.text(x_st_rp/2, y_pos_top * 0.34, fix_arabic_mpl("النسبي"), ha='center', va='center', fontsize=14, color='#1F2937', fontweight='bold')

            for idx_rp, p_rp in enumerate(rp_pts):
                xc_line = get_rp_xc(idx_rp)
                xc_lbl = get_rp_label_x(idx_rp)
                try:
                    ax_rp.text(xc_lbl, y_factors_top + row_h/2, f"${p_rp['latex_x']}$", ha='center', va='center', fontsize=15, fontweight='bold')
                except Exception:
                    ax_rp.text(xc_lbl, y_factors_top + row_h/2, str(p_rp['latex_x']), ha='center', va='center', fontsize=13)

                if p_rp['type'] == 'v_asym' and 0 < idx_rp < N_rp - 1:
                    ax_rp.plot([xc_line-0.05, xc_line-0.05], [0, y_factors_top], 'k-', lw=1.4)
                    ax_rp.plot([xc_line+0.05, xc_line+0.05], [0, y_factors_top], 'k-', lw=1.4)
                elif p_rp['type'] == 'root':
                    ax_rp.plot([xc_line, xc_line], [y_pos_top, y_factors_top], 'k-', lw=1.3)
                    for idx_fr, f_info in enumerate(factor_rows):
                        if any(abs(p_rp['val'] - r_f) < 1e-3 for r_f in f_info['roots']):
                            y_f_c = y_factors_top - (idx_fr + 0.5) * row_h
                            ax_rp.plot(xc_line, y_f_c, marker='o', markersize=9, markerfacecolor='none', markeredgecolor='k', markeredgewidth=1.6)
                    ax_rp.plot(xc_line, y_pos_top + row_h/2, marker='o', markersize=9, markerfacecolor='none', markeredgecolor='k', markeredgewidth=1.6)
                    ax_rp.plot([xc_line, xc_line - tri_half_w], [y_pos_top, 0.0], 'k-', lw=1.4)
                    ax_rp.plot([xc_line, xc_line + tri_half_w], [y_pos_top, 0.0], 'k-', lw=1.4)
                    ax_rp.text(xc_line, y_pos_top * 0.58, "$(C_f)$", ha='center', va='center', fontsize=11.5, color='#1F2937', fontweight='bold')
                    ax_rp.text(xc_line, y_pos_top * 0.35, fix_arabic_mpl("يقطع"), ha='center', va='center', fontsize=11.5, color='#1F2937', fontweight='bold')
                    ax_rp.text(xc_line, y_pos_top * 0.14, "$(\\Delta)$", ha='center', va='center', fontsize=11.5, color='#1F2937', fontweight='bold')

                if idx_rp < N_rp - 1:
                    xc_left, xc_right = get_rp_xc(idx_rp), get_rp_xc(idx_rp + 1)
                    xic = (xc_left + xc_right) / 2.0
                    mid_val = rp_mids[idx_rp]
                    sgn = rp_signs[idx_rp]
                    if sgn is None:
                        ax_rp.add_patch(plt.Rectangle((xc_left, 0), seg_w_rp, y_factors_top, facecolor='#CBD5E1', alpha=0.5))
                    else:
                        for idx_fr, f_info in enumerate(factor_rows):
                            y_f_c = y_factors_top - (idx_fr + 0.5) * row_h
                            try:
                                vf_m = float(f_info['func'](mid_val))
                                f_sgn = "+" if vf_m > 0 else "-"
                                ax_rp.text(xic, y_f_c, f"${f_sgn}$", ha='center', va='center', fontsize=18, color='#1F2937', fontweight='bold')
                            except Exception:
                                pass
                        ax_rp.text(xic, y_pos_top + row_h/2, f"${sgn}$", ha='center', va='center', fontsize=19, color='#1B6B3A' if sgn=='+' else '#9B2226', fontweight='bold')
                        x_vis_l = xc_left + (tri_half_w * 0.55 if p_rp['type'] == 'root' else 0.0)
                        x_vis_r = xc_right - (tri_half_w * 0.55 if rp_pts[idx_rp+1]['type'] == 'root' else 0.0)
                        xic_pos = (x_vis_l + x_vis_r) / 2.0
                        pos_ar = "فوق" if sgn == '+' else "تحت"
                        col_pos = '#1B6B3A' if sgn == '+' else '#9B2226'
                        ax_rp.text(xic_pos + 0.05, y_pos_top * 0.65, "$(C_f)$", ha='left', va='center', fontsize=12.5, color=col_pos, fontweight='bold')
                        ax_rp.text(xic_pos - 0.05, y_pos_top * 0.65, fix_arabic_mpl("يقع"), ha='right', va='center', fontsize=12.5, color=col_pos, fontweight='bold')
                        ax_rp.text(xic_pos + 0.05, y_pos_top * 0.32, fix_arabic_mpl(pos_ar), ha='left', va='center', fontsize=12.5, color=col_pos, fontweight='bold')
                        ax_rp.text(xic_pos - 0.05, y_pos_top * 0.32, "$(\\Delta)$", ha='right', va='center', fontsize=12.5, color=col_pos, fontweight='bold')

            ax_rp.set_xlim(-0.05, x_max_rp + 0.05)
            ax_rp.set_ylim(-0.05, y_table_top + 0.05)
            od['rel_pos_bytes'] = fig_to_bytes(fig_rp)

            fig_ob, ax_ob = new_fig(figsize=(9.5, 3.6))
            fig_ob.patch.set_facecolor('white')
            ax_ob.set_facecolor('white')
            ax_ob.axis('off')
            ax_ob.set_xlim(0, 10)
            ax_ob.set_ylim(0, 5.0)
            ax_ob.text(9.7, 4.4, fix_arabic_mpl("طريقة استنتاج معادلة المستقيم المقارب المائل:"), fontsize=14, ha='right', va='center', color='#0F5E6B', fontweight='bold')
            try:
                ax_ob.text(5.0, 3.5, fr"$a = \lim_{{x \to {od['target_latex']}}} \frac{{f(x)}}{{x}} = {od['a_lat']} \quad , \quad b = \lim_{{x \to {od['target_latex']}}} [f(x) - ({od['a_lat']})x] = {od['b_lat']}$", fontsize=15, ha='center', va='center', color='#1F3A5F')
                ax_ob.text(5.0, 2.5, fr"$\lim_{{x \to {od['target_latex']}}} [f(x) - ({od['line_lat']})] = \lim_{{x \to {od['target_latex']}}} \left({od['rem_lat']}\right) = 0$", fontsize=15, ha='center', va='center', color='#1F2937')
                ax_ob.text(9.7, 1.5, fix_arabic_mpl("ومنه معادلة المقارب المائل وعبارة الفرق للوضع النسبي:"), fontsize=14, ha='right', va='center', color='#0F5E6B', fontweight='bold')
                ax_ob.text(5.0, 0.6, fr"$(\Delta): y = {od['line_lat']} \quad , \quad f(x) - y = {od['rem_lat']}$", fontsize=16, ha='center', va='center', color='#0F5E6B', fontweight='bold')
            except Exception:
                pass
            od['oblique_steps_bytes'] = fig_to_bytes(fig_ob)
            rel_pos_tables_info.append(od)
# ==================== نهاية الجزء (3/4) ====================
# ==================== بداية الجزء (4/4) ====================
        diff_fg = sp.together(f_expr - g_expr)
        A_m = elim_hyperbolic(sp.simplify(sp.diff(diff_fg, m_sym)))
        B_m = elim_hyperbolic(sp.simplify(diff_fg.subs(m_sym, 0)))

        pivot_roots = []
        pivot_x_floats = set()
        try:
            if A_m != 0 and not A_m.has(m_sym) and A_m.has(x_sym):
                for r_piv in safe_solve_real(A_m, x_sym):
                    fl_piv = safe_float(r_piv)
                    if not np.isfinite(fl_piv):
                        continue
                    if any(abs(fl_piv - safe_float(va)) < 1e-4 for va in true_v_asymptotes):
                        continue
                    if any(abs(fl_piv - h['val']) < 1e-4 for h in holes):
                        continue
                    b_val_piv = safe_float(B_m.subs(x_sym, r_piv))
                    f_val_piv = safe_float(f_expr.subs(x_sym, r_piv))
                    if np.isfinite(b_val_piv) and abs(b_val_piv) < 1e-6 and np.isfinite(f_val_piv):
                        if not any(abs(fl_piv - px) < 1e-4 for px in pivot_x_floats):
                            pivot_x_floats.add(fl_piv)
                            pivot_roots.append({
                                'x_val': fl_piv,
                                'sym': r_piv,
                                'sign': 'zero' if abs(fl_piv) < 1e-5 else ('pos' if fl_piv > 0 else 'neg')
                            })
        except Exception:
            pass

        try:
            if g_expr == m_sym:
                m_expr = f_expr
            elif A_m != 0 and not A_m.has(m_sym):
                m_expr = elim_hyperbolic(sp.simplify(-B_m / A_m))
            else:
                m_expr_list = sp.solve(diff_fg, m_sym)
                m_expr = elim_hyperbolic(sp.simplify(m_expr_list[0])) if m_expr_list else f_expr
        except Exception:
            m_expr = f_expr

        m_func_eval = safe_lambdify(x_sym, m_expr)
        m_equals_f = (g_expr == m_sym) or (m_expr == f_expr)

        x_split_syms = [sp.Integer(0)]
        for r in candidate_v_asymptotes:
            x_split_syms.append(r)
        for ac in abs_corner_syms:
            x_split_syms.append(ac)
        for piv in pivot_roots:
            x_split_syms.append(piv['sym'])

        if m_equals_f:
            for r_ex in sym_extrema:
                x_split_syms.append(r_ex)
            dm_expr = df_clean
        else:
            try:
                for abs_atom_m in m_expr.atoms(sp.Abs):
                    for r_cm in safe_solve_real(abs_atom_m.args[0], x_sym):
                        x_split_syms.append(r_cm)
            except Exception:
                pass
            try:
                n_m, d_m = sp.fraction(sp.together(m_expr))
                if d_m != 1:
                    for r in safe_solve_real(d_m, x_sym):
                        x_split_syms.append(r)
            except Exception:
                pass

            dm_raw = sp.diff(m_expr, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a))
            dm_expr = elim_hyperbolic(sp.simplify(dm_raw)) if not dm_raw.has(sp.Abs) else dm_raw
            try:
                num_dm, _ = sp.fraction(dm_expr)
                for r in safe_solve_real(num_dm, x_sym):
                    x_split_syms.append(r)
            except Exception:
                pass

            try:
                x_scan_m = np.linspace(-scan_x_bound, scan_x_bound, 4001)
                with np.errstate(all='ignore'):
                    y_scan_m = m_func_eval(x_scan_m)
                if np.iscomplexobj(y_scan_m):
                    y_scan_m = np.where(np.isreal(y_scan_m), y_scan_m.real, np.nan)
                y_scan_m = np.array(y_scan_m, dtype=float)
                is_v_m = np.isfinite(y_scan_m)
                edges_m = np.diff(is_v_m.astype(int))
                s_m = np.where(edges_m == 1)[0] + 1
                if is_v_m[0]:
                    s_m = np.insert(s_m, 0, 0)
                e_m = np.where(edges_m == -1)[0]
                if is_v_m[-1]:
                    e_m = np.append(e_m, len(y_scan_m) - 1)
                for s_i, e_i in zip(s_m, e_m):
                    seg = y_scan_m[s_i:e_i+1]
                    sx = x_scan_m[s_i:e_i+1]
                    if len(seg) > 10:
                        pks, _ = find_peaks(seg, prominence=0.02)
                        vls, _ = find_peaks(-seg, prominence=0.02)
                        for idx_p in list(pks) + list(vls):
                            xv = float(sx[idx_p])
                            if is_periodic_f and abs(xv) > 6.5:
                                continue
                            if not any(abs(safe_float(xs) - xv) < 0.08 for xs in x_split_syms):
                                x_split_syms.append(sp.Float(round(xv, 2)))
            except Exception:
                pass

        unique_x_splits = [{'val': -np.inf, 'sym': -sp.oo}]
        for r_s in x_split_syms:
            fl = safe_float(r_s)
            if np.isfinite(fl) and not any(abs(p['val'] - fl) < 1e-4 for p in unique_x_splits):
                unique_x_splits.append({'val': fl, 'sym': r_s})
        unique_x_splits.append({'val': np.inf, 'sym': sp.oo})
        unique_x_splits.sort(key=lambda item: item['val'])

        dm_func = df_func_test if m_equals_f else safe_lambdify(x_sym, dm_expr)
        double_root_x_vals = set()
        for item in unique_x_splits:
            xv = item['val']
            if not np.isfinite(xv):
                continue
            if any(abs(xv - safe_float(va)) < 1e-4 for va in candidate_v_asymptotes):
                continue
            if any(abs(xv - safe_float(ac)) < 1e-4 for ac in abs_corner_syms):
                continue
            try:
                with np.errstate(all='ignore'):
                    dm_l = float(dm_func(xv - 1e-3))
                    dm_r = float(dm_func(xv + 1e-3))
                    dm_c = float(dm_func(xv))
                if np.isfinite(dm_l) and np.isfinite(dm_r) and np.isfinite(dm_c):
                    if dm_l * dm_r < 0 and abs(dm_c) < 0.05 and abs(dm_r - dm_l) < 0.5:
                        double_root_x_vals.add(round(xv, 4))
            except Exception:
                pass

        def is_x_in_reduced_domain(x_item):
            xv = x_item['val']
            if not np.isfinite(xv):
                return False
            if any(abs(xv - safe_float(va)) < 1e-4 for va in true_v_asymptotes):
                return False
            if any(abs(xv - h['val']) < 1e-4 for h in holes):
                return False
            if any(abs(xv - px) < 1e-4 for px in pivot_x_floats):
                return False
            try:
                with np.errstate(all='ignore'):
                    fv = float(f_func(xv))
                    mv = float(m_func_eval(xv))
                if np.isfinite(fv) and np.isfinite(mv):
                    return True
                fv_s = safe_float(f_expr.subs(x_sym, x_item['sym']))
                mv_s = safe_float(m_expr.subs(x_sym, x_item['sym']))
                return bool(np.isfinite(fv_s) and np.isfinite(mv_s))
            except Exception:
                return False

        monotonic_branches = []
        point_evaluations = []
        sym_m_critical = []
        m_critical_floats = []
        point_m_map = {}

        def register_crit_m(m_sym_val):
            m_sym_val = elim_hyperbolic(m_sym_val)
            fl = safe_float(m_sym_val)
            if np.isfinite(fl) and abs(fl) < 500:
                sym_m_critical.append(elim_hyperbolic(sp.simplify(m_sym_val)))
                if not any(abs(fl - mc) < 1e-4 for mc in m_critical_floats):
                    m_critical_floats.append(fl)

        for item in unique_x_splits:
            if is_x_in_reduced_domain(item):
                try:
                    m_exact_pt = elim_hyperbolic(sp.simplify(m_expr.subs(x_sym, item['sym'])))
                    m_fl_pt = safe_float(m_exact_pt)
                    if np.isfinite(m_fl_pt):
                        point_m_map[round(item['val'], 5)] = m_exact_pt
                        register_crit_m(m_exact_pt)
                        is_dbl = any(abs(item['val'] - dxv) < 1e-3 for dxv in double_root_x_vals)
                        point_evaluations.append({
                            'x_val': item['val'],
                            'm_val': m_fl_pt,
                            'sign': 'zero' if abs(item['val']) < 1e-5 else ('pos' if item['val'] > 0 else 'neg'),
                            'mult': 'double' if is_dbl else 'single'
                        })
                except Exception:
                    pass

        for idx_b in range(len(unique_x_splits) - 1):
            p_left = unique_x_splits[idx_b]
            p_right = unique_x_splits[idx_b + 1]
            l_v, r_v = p_left['val'], p_right['val']
            mid_x = 0.0 if (l_v == -np.inf and r_v == np.inf) else (r_v - 1.5 if l_v == -np.inf else (l_v + 1.5 if r_v == np.inf else (l_v + r_v) / 2.0))
            try:
                with np.errstate(all='ignore'):
                    f_mid = f_func(mid_x)
                    m_mid = m_func_eval(mid_x)
                if np.iscomplexobj(f_mid) or np.iscomplexobj(m_mid):
                    continue
                if not (np.isfinite(float(f_mid)) and np.isfinite(float(m_mid))):
                    continue
            except Exception:
                continue

            try:
                if np.isfinite(l_v) and round(l_v, 5) in point_m_map:
                    m_left_sym = point_m_map[round(l_v, 5)]
                else:
                    m_left_sym = cached_limit(m_expr, -sp.oo if l_v == -np.inf else p_left['sym'], '+')

                if np.isfinite(r_v) and round(r_v, 5) in point_m_map:
                    m_right_sym = point_m_map[round(r_v, 5)]
                else:
                    m_right_sym = cached_limit(m_expr, sp.oo if r_v == np.inf else p_right['sym'], '-')

                register_crit_m(m_left_sym)
                register_crit_m(m_right_sym)
                ml_fl = safe_float(m_left_sym)
                mr_fl = safe_float(m_right_sym)
                if np.isnan(ml_fl) or np.isnan(mr_fl):
                    continue
                m_low, m_high = min(ml_fl, mr_fl), max(ml_fl, mr_fl)
                branch_sign = 'pos' if mid_x > 0 else 'neg'
                monotonic_branches.append({
                    'm_low': m_low,
                    'm_high': m_high,
                    'sign': branch_sign,
                    'is_const': abs(m_high - m_low) < 1e-5
                })
            except Exception:
                continue

        m_critical_num = sorted(m_critical_floats)

        m_min_val, m_max_val = -6.0, 6.0
        if m_critical_num:
            if m_critical_num[0] - 1.5 < m_min_val:
                m_min_val = float(np.floor(m_critical_num[0] - 1.5))
            if m_critical_num[-1] + 1.5 > m_max_val:
                m_max_val = float(np.ceil(m_critical_num[-1] + 1.5))
        m_min_val, m_max_val = float(max(-30.0, m_min_val)), float(min(30.0, m_max_val))

        # تحديد الارتفاع العمودي التلقائي للمعلم ليشمل الذرى والمقاربات الأفقية
        key_y_floats = [a['val'] for a in unique_asymptotes if a['type'] == 'h' and np.isfinite(a['val'])]
        if m_equals_f:
            key_y_floats.extend([pt['m_val'] for pt in point_evaluations if np.isfinite(pt['m_val'])])
        max_abs_y = max([abs(v) for v in key_y_floats if abs(v) <= 35.0], default=5.0)
        plot_y_bound = float(max(8.0, min(28.0, np.ceil(max_abs_y + 2.5))))

        def get_exact_m(val_float):
            for sm in sym_m_critical:
                try:
                    sm_fl = safe_float(sm)
                    if np.isfinite(sm_fl) and abs(sm_fl - val_float) < 1e-3:
                        res = exactify_value(val_float, sm)
                        if not re.match(r'^-?\d+(\.\d+)?$', res):
                            return res
                except Exception:
                    pass
            return exactify_value(val_float)

        is_rotational_disc = (len(pivot_roots) > 0)

        def get_roots_text_exact(m_test):
            pos_s, neg_s, zero_s = 0, 0, 0
            pos_d, neg_d, zero_d = 0, 0, 0

            for piv in pivot_roots:
                if piv['sign'] == 'pos':
                    pos_s += 1
                elif piv['sign'] == 'neg':
                    neg_s += 1
                else:
                    zero_s += 1

            for br in monotonic_branches:
                if not br['is_const']:
                    if br['m_low'] + 1e-5 < m_test < br['m_high'] - 1e-5:
                        if br['sign'] == 'pos':
                            pos_s += 1
                        else:
                            neg_s += 1

            for pt in point_evaluations:
                if abs(m_test - pt['m_val']) < 1e-4:
                    if pt['mult'] == 'double':
                        if pt['sign'] == 'pos':
                            pos_d += 1
                        elif pt['sign'] == 'neg':
                            neg_d += 1
                        else:
                            zero_d += 1
                    else:
                        if pt['sign'] == 'pos':
                            pos_s += 1
                        elif pt['sign'] == 'neg':
                            neg_s += 1
                        else:
                            zero_s += 1

            total_roots = pos_s + neg_s + zero_s + pos_d + neg_d + zero_d
            if total_roots == 0:
                return "لا توجد حلول"

            if is_rotational_disc:
                if total_roots == 1:
                    if zero_s == 1:
                        return "حل وحيد معدوم"
                    if pos_s == 1:
                        return "حل وحيد موجب"
                    if neg_s == 1:
                        return "حل وحيد سالب"
                    return "حل وحيد"
                if total_roots == 2:
                    if zero_s == 1 and pos_s == 1:
                        return "حلان (أحدهما معدوم والآخر موجب)"
                    if zero_s == 1 and neg_s == 1:
                        return "حلان (أحدهما معدوم والآخر سالب)"
                    if pos_s == 1 and neg_s == 1:
                        return "حلان مختلفان في الإشارة"
                    return "حلان متمايزان"
                if total_roots == 3:
                    if zero_s == 1 and pos_s == 1 and neg_s == 1:
                        return "ثلاثة حلول (معدوم، وموجب، وسالب)"
                    return "ثلاثة حلول متمايزة"

            if total_roots == 1:
                if pos_d == 1:
                    return "حل مضاعف موجب تماماً"
                if neg_d == 1:
                    return "حل مضاعف سالب تماماً"
                if zero_d == 1:
                    return "حل مضاعف معدوم"
                if pos_s == 1:
                    return "حل وحيد موجب تماماً"
                if neg_s == 1:
                    return "حل وحيد سالب تماماً"
                if zero_s == 1:
                    return "حل وحيد معدوم"

            if total_roots == 2 and pos_d == 0 and neg_d == 0 and zero_d == 0:
                if pos_s == 2:
                    return "حلان موجبان تماماً"
                if neg_s == 2:
                    return "حلان سالبان تماماً"
                if pos_s == 1 and neg_s == 1:
                    return "حلان مختلفان في الإشارة"
                if pos_s == 1 and zero_s == 1:
                    return "حلان أحدهما موجب والآخر معدوم"
                if neg_s == 1 and zero_s == 1:
                    return "حلان أحدهما سالب والآخر معدوم"

            if total_roots == 4 and pos_s == 2 and neg_s == 2:
                return "أربعة حلول (حلان موجبان وحلان سالبان)"

            desc = []
            if pos_d == 1 and neg_d == 1:
                desc.append("حلان مضاعفان (أحدهما موجب والآخر سالب)")
            else:
                if pos_d == 1:
                    desc.append("حل مضاعف موجب")
                elif pos_d > 1:
                    desc.append(f"{pos_d} حلول مضاعفة موجبة")
                if neg_d == 1:
                    desc.append("حل مضاعف سالب")
                elif neg_d > 1:
                    desc.append(f"{neg_d} حلول مضاعفة سالبة")
                if zero_d == 1:
                    desc.append("حل مضاعف معدوم")

            if pos_s == 1:
                desc.append("حل موجب")
            elif pos_s == 2:
                desc.append("حلان موجبان")
            elif pos_s > 2:
                desc.append(f"{pos_s} حلول موجبة")

            if neg_s == 1:
                desc.append("حل سالب")
            elif neg_s == 2:
                desc.append("حلان سالبان")
            elif neg_s > 2:
                desc.append(f"{neg_s} حلول سالبة")

            if zero_s == 1:
                desc.append("حل معدوم")

            if pos_s == 2 and neg_s == 1 and pos_d == 0 and neg_d == 0 and zero_s == 0:
                return "ثلاثة حلول: حل سالب وحلان موجبان"
            if pos_s == 1 and neg_s == 2 and pos_d == 0 and neg_d == 0 and zero_s == 0:
                return "ثلاثة حلول: حل موجب وحلان سالبان"

            return " و ".join(desc) if desc else f"{total_roots} حلول"

        atomic_items = []
        if m_critical_num:
            atomic_items.append({'type': 'interval', 'L': float('-inf'), 'H': m_critical_num[0], 'l_closed': False, 'r_closed': False, 'sol': get_roots_text_exact(m_critical_num[0] - 1.0)})
            for i in range(len(m_critical_num)):
                mc = m_critical_num[i]
                atomic_items.append({'type': 'point', 'L': mc, 'H': mc, 'l_closed': True, 'r_closed': True, 'sol': get_roots_text_exact(mc)})
                if i < len(m_critical_num) - 1:
                    mc_next = m_critical_num[i + 1]
                    atomic_items.append({'type': 'interval', 'L': mc, 'H': mc_next, 'l_closed': False, 'r_closed': False, 'sol': get_roots_text_exact((mc + mc_next) / 2.0)})
            atomic_items.append({'type': 'interval', 'L': m_critical_num[-1], 'H': float('inf'), 'l_closed': False, 'r_closed': False, 'sol': get_roots_text_exact(m_critical_num[-1] + 1.0)})
        else:
            atomic_items.append({'type': 'interval', 'L': float('-inf'), 'H': float('inf'), 'l_closed': False, 'r_closed': False, 'sol': get_roots_text_exact(0.0)})

        merged_items = []
        for item in atomic_items:
            if not merged_items:
                merged_items.append(item)
            else:
                prev = merged_items[-1]
                if prev['sol'] == item['sol']:
                    prev['H'] = item['H']
                    prev['r_closed'] = item['r_closed']
                    prev['type'] = 'interval' if prev['L'] != prev['H'] else 'point'
                else:
                    merged_items.append(item)

        final_table = []
        for it in merged_items:
            L, H, sol_text = it['L'], it['H'], it['sol']
            L_latex = r"-\infty" if L == float('-inf') else get_exact_m(L)
            H_latex = r"+\infty" if H == float('inf') else get_exact_m(H)
            if L == float('-inf') and H == float('inf'):
                m_latex = r"m \in \mathbb{R}"
            elif L == H:
                m_latex = fr"m = {L_latex}"
            else:
                l_br = "[" if (it['l_closed'] and L != float('-inf')) else "]"
                r_br = "]" if (it['r_closed'] and H != float('inf')) else "["
                m_latex = fr"m \in {l_br}{L_latex} ; {H_latex}{r_br}"
            final_table.append((m_latex, sol_text, L, H))

        N = len(pts_var_exact)
        def generate_variation_table_bytes():
            if N < 2:
                return None
            n_int_v = max(1, N - 1)
            seg_w_v = 3.2
            x_start_data = 2.0
            x_max = x_start_data + n_int_v * seg_w_v

            def get_v_xc(idx_pt):
                return x_start_data + idx_pt * seg_w_v
            def get_v_label_x(idx_pt):
                if idx_pt == 0:
                    return x_start_data + 0.50
                if idx_pt == N - 1:
                    return x_max - 0.50
                return x_start_data + idx_pt * seg_w_v

            fig_v, ax_v = new_fig(figsize=(max(8.0, x_max * 0.85), 3.5))
            fig_v.patch.set_facecolor('white')
            ax_v.set_facecolor('white')
            ax_v.axis('off')
            for y_line, lw_v in [(6, 2), (5, 1.5), (3.8, 1.5), (0, 2)]:
                ax_v.plot([0, x_max], [y_line, y_line], 'k-', lw=lw_v)
            for x_line in [0, x_start_data, x_max]:
                ax_v.plot([x_line, x_line], [0, 6], 'k-', lw=2)
            ax_v.text(x_start_data / 2, 5.5, '$x$', ha='center', va='center', fontsize=18, color='#1F2937', fontweight='bold')
            ax_v.text(x_start_data / 2, 4.4, "$f'(x)$", ha='center', va='center', fontsize=18, color='#1F2937', fontweight='bold')
            ax_v.text(x_start_data / 2, 1.9, '$f(x)$', ha='center', va='center', fontsize=18, color='#1F2937', fontweight='bold')
            
            signs = []
            for i in range(N - 1):
                left, right = pts_var_exact[i]['val'], pts_var_exact[i+1]['val']
                mid = 0 if (left == -np.inf and right == np.inf) else (right - 1 if left == -np.inf else (left + 1 if right == np.inf else (left + right) / 2.0))
                try:
                    signs.append(None if not np.isfinite(float(f_func(mid))) else ("+" if f_func(mid + 1e-5) > f_func(mid) else "-"))
                except Exception:
                    signs.append(None)
                    
            right_node, left_node = {}, {}
            for i in range(N):
                p = pts_var_exact[i]
                xc_line = get_v_xc(i)
                xc_lbl = get_v_label_x(i)
                ax_v.text(xc_lbl, 5.5, f"${p['latex_x']}$", ha='center', va='center', fontsize=16, fontweight='bold')
                if p['type'] == 'v_asym':
                    ax_v.plot([xc_line-0.05, xc_line-0.05], [0, 5], 'k-', lw=1.5)
                    ax_v.plot([xc_line+0.05, xc_line+0.05], [0, 5], 'k-', lw=1.5)
                elif p['type'] == 'extrema':
                    ax_v.plot([xc_line, xc_line], [3.8, 5], 'k-', lw=1.3)
                    ax_v.plot(xc_line, 4.4, marker='o', markersize=9, markerfacecolor='none', markeredgecolor='k', markeredgewidth=1.6)
                elif p['type'] in ['corner', 'bound']:
                    if 0 < i < N - 1:
                        ax_v.plot([xc_line-0.04, xc_line-0.04], [3.8, 5], 'k-', lw=1.4)
                        ax_v.plot([xc_line+0.04, xc_line+0.04], [3.8, 5], 'k-', lw=1.4)
                if i < N - 1:
                    x_ic = (get_v_xc(i) + get_v_xc(i+1)) / 2.0
                    if not valid_intervals[i]:
                        ax_v.add_patch(plt.Rectangle((xc_line, 0), seg_w_v, 5, facecolor='#CBD5E1', alpha=0.6))
                    else:
                        ax_v.text(x_ic, 4.4, f"${signs[i]}$", ha='center', va='center', fontsize=22, color='#9B2226' if signs[i]=='-' else '#1B6B3A', fontweight='bold')
                if p['type'] == 'inf':
                    try:
                        lim = cached_limit(f_expr, p['sym'])
                        if lim is not None and str(lim) != 'nan' and 'AccumBounds' not in str(lim):
                            if i == 0:
                                right_node[i] = (xc_lbl, format_lim_val(lim))
                            if i == N - 1:
                                left_node[i] = (xc_lbl, format_lim_val(lim))
                    except Exception:
                        pass
                elif p['type'] == 'v_asym':
                    if i > 0 and valid_intervals[i-1]:
                        try:
                            left_node[i] = (xc_line - 0.42, format_lim_val(cached_limit(f_expr, p['sym'], '-')))
                        except Exception:
                            pass
                    if i < N-1 and valid_intervals[i]:
                        try:
                            right_node[i] = (xc_line + 0.42, format_lim_val(cached_limit(f_expr, p['sym'], '+')))
                        except Exception:
                            pass
                elif p['type'] in ['extrema', 'corner', 'bound']:
                    try:
                        sym_y = point_m_map.get(round(p['val'], 5)) if m_equals_f else None
                        if sym_y is None:
                            sym_y = elim_hyperbolic(sp.simplify(f_expr.subs(x_sym, p['sym'])))
                        val_y = safe_float(sym_y)
                        lbl_y = exactify_value(val_y, sym_y)
                        x_pos_n = xc_lbl if (i == 0 or i == N - 1) else xc_line
                        left_node[i] = (x_pos_n, lbl_y)
                        right_node[i] = (x_pos_n, lbl_y)
                    except Exception:
                        pass

            idx_v = 0
            while idx_v < N - 1:
                if not valid_intervals[idx_v]:
                    idx_v += 1
                    continue
                j_end = idx_v
                while (j_end + 1 < N - 1 and valid_intervals[j_end + 1] and
                       pts_var_exact[j_end + 1]['type'] == 'extrema' and
                       signs[j_end + 1] == signs[idx_v]):
                    j_end += 1

                sgn_chain = signs[idx_v]
                s_info, e_info = right_node.get(idx_v), left_node.get(j_end + 1)
                xs_n = s_info[0] if s_info else get_v_label_x(idx_v)
                xe_n = e_info[0] if e_info else get_v_label_x(j_end + 1)
                ys_n = 0.65 if sgn_chain == '+' else 3.15
                ye_n = 3.15 if sgn_chain == '+' else 0.65
                if s_info:
                    ax_v.text(xs_n, ys_n, f"${s_info[1]}$", ha='center', va='center', fontsize=15, color='#9B2226', fontweight='bold', zorder=5)
                if e_info:
                    ax_v.text(xe_n, ye_n, f"${e_info[1]}$", ha='center', va='center', fontsize=15, color='#9B2226', fontweight='bold', zorder=5)
                dx_tot, dy_tot = xe_n - xs_n, ye_n - ys_n
                dist_tot = np.hypot(dx_tot, dy_tot)
                if dist_tot > 0.8:
                    ux, uy = dx_tot / dist_tot, dy_tot / dist_tot
                    ax_v.annotate('', xy=(xe_n - ux * 0.48, ye_n - uy * 0.48), xytext=(xs_n + ux * 0.48, ys_n + uy * 0.48), arrowprops=dict(arrowstyle="->", color="#1F2937", lw=2.2), zorder=3)
                for k_inf in range(idx_v + 1, j_end + 1):
                    m_info = right_node.get(k_inf)
                    if m_info and dx_tot != 0:
                        xm_n, lm_n = m_info
                        ym_n = ys_n + ((xm_n - xs_n) / dx_tot) * dy_tot
                        ax_v.text(xm_n, ym_n, f"${lm_n}$", ha='center', va='center', fontsize=15, color='#9B2226', fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', pad=4.0), zorder=5)
                idx_v = j_end + 1

            ax_v.set_xlim(-0.05, x_max + 0.05)
            ax_v.set_ylim(-0.05, 6.05)
            return fig_to_bytes(fig_v)

        var_table_bytes = generate_variation_table_bytes()

        def render_rows_chunk_to_bytes(rows_chunk):
            if not rows_chunk:
                return None
            total_h = sum(r[2] for r in rows_chunk) + 0.25
            fig_c, ax_c = new_fig(figsize=(9.5, max(0.85, total_h * 0.70)))
            fig_c.patch.set_facecolor('white')
            ax_c.set_facecolor('white')
            ax_c.axis('off')
            ax_c.set_xlim(0, 10)
            ax_c.set_ylim(0, total_h)
            curr_y = total_h - 0.12
            for r_type, content, h_step in rows_chunk:
                y_pos = curr_y - (h_step / 2.0)
                try:
                    if r_type == 'domain':
                        ax_c.text(5.0, y_pos, f"${content}$", fontsize=18, ha='center', va='center', color='#1F3A5F', fontweight='bold')
                    elif r_type == 'main':
                        ax_c.text(7.2, y_pos, f"${content[0]}$", fontsize=16.5, ha='right', va='center', color='#1F3A5F')
                        ax_c.text(7.4, y_pos, f"${content[1]}$", fontsize=18, ha='left', va='center', color='#9B2226', fontweight='bold')
                    elif r_type == 'step_label':
                        ax_c.text(9.7, y_pos, fix_arabic_mpl(content), fontsize=13, ha='right', va='center', color='#0F5E6B', fontweight='bold')
                    elif r_type == 'step_math':
                        ax_c.text(5.0, y_pos, f"$({content})$", fontsize=14, ha='center', va='center', color='#1F2937')
                    elif r_type == 'note_row':
                        ax_c.text(5.0, y_pos, fix_arabic_mpl(content), fontsize=13, ha='center', va='center', color='#0F5E6B', fontweight='bold')
                    elif r_type == 'geo_label':
                        ax_c.text(9.7, y_pos, fix_arabic_mpl(content), fontsize=13.5, ha='right', va='center', color='#0F5E6B', fontweight='bold')
                    elif r_type == 'geo_math':
                        ax_c.text(5.0, y_pos, f"${content}$", fontsize=15.5, ha='center', va='center', color='#0F5E6B', fontweight='bold')
                    elif r_type == 'deriv_label':
                        ax_c.text(9.7, y_pos, fix_arabic_mpl(content), fontsize=14, ha='right', va='center', color='#0F5E6B', fontweight='bold')
                    elif r_type == 'deriv_math':
                        ax_c.text(5.0, y_pos, f"${content}$", fontsize=15, ha='center', va='center', color='#1F2937')
                    elif r_type == 'final_label':
                        ax_c.text(9.7, y_pos, fix_arabic_mpl(content), fontsize=14.5, ha='right', va='center', color='#0F5E6B', fontweight='bold')
                    elif r_type == 'final_math':
                        ax_c.text(5.0, y_pos, f"${content}$", fontsize=17.5, ha='center', va='center', color='#1F3A5F', fontweight='bold')
                except Exception:
                    pass
                curr_y -= h_step
            return fig_to_bytes(fig_c)

        def generate_limits_chunks():
            chunks_bytes = []
            current_block = []
            for idx_item, item in enumerate(limits_mpl_items):
                if item['type'] == 'domain':
                    current_block.append(('domain', item['latex'], 0.85))
                elif item['type'] == 'main':
                    if sum(r[2] for r in current_block) >= 2.8:
                        b_img = render_rows_chunk_to_bytes(current_block)
                        if b_img:
                            chunks_bytes.append(b_img)
                        current_block = []
                    current_block.append(('main', (item['lhs'], item['rhs']), 1.05))
                elif item['type'] == 'step':
                    if idx_item == 0 or limits_mpl_items[idx_item - 1]['type'] not in ['step', 'geo']:
                        current_block.append(('step_label', 'التعليل (لأن):', 0.50))
                    current_block.append(('step_math', item['math'], 0.78))
                elif item['type'] == 'note':
                    current_block.append(('note_row', item['text'], 0.55))
                elif item['type'] == 'geo':
                    current_block.append(('geo_label', item['text'], 0.55))
                    if item['math']:
                        current_block.append(('geo_math', item['math'], 0.70))
            if current_block:
                b_img = render_rows_chunk_to_bytes(current_block)
                if b_img:
                    chunks_bytes.append(b_img)
            return chunks_bytes

        limits_chunks_bytes = generate_limits_chunks

        def generate_deriv_chunks():
            chunks_bytes = []
            current_block = []
            for stp in deriv_steps_detailed:
                if sum(r[2] for r in current_block) >= 3.2:
                    b_img = render_rows_chunk_to_bytes(current_block)
                    if b_img:
                        chunks_bytes.append(b_img)
                    current_block = []
                current_block.append(('deriv_label', stp['label'], 0.55))
                for m_str in stp['math_list']:
                    current_block.append(('deriv_math', m_str, 0.88))
            if sum(r[2] for r in current_block) >= 3.2:
                b_img = render_rows_chunk_to_bytes(current_block)
                if b_img:
                    chunks_bytes.append(b_img)
                current_block = []
            current_block.append(('final_label', 'العبارة النهائية للمشتقة:', 0.60))
            current_block.append(('final_math', fr"f'(x) = {df_latex_str_safe}", 1.15))
            if current_block:
                b_img = render_rows_chunk_to_bytes(current_block)
                if b_img:
                    chunks_bytes.append(b_img)
            return chunks_bytes
            
        deriv_chunks_bytes = generate_deriv_chunks
        
        def generate_eq_bytes():
            g_lat = sanitize_latex(g_expr)
            fig_e, ax_e = new_fig(figsize=(9.5, 1.55))
            fig_e.patch.set_facecolor('white')
            ax_e.set_facecolor('white')
            ax_e.axis('off')
            ax_e.set_xlim(0, 10)
            ax_e.set_ylim(0, 2.0)
            intro_txt = "حلول المعادلة هي فواصل نقط تقاطع منحنى الدالة f مع المستقيم ذو المعادلة:"
            ax_e.text(9.7, 1.45, fix_arabic_mpl(intro_txt), fontsize=14.5, ha='right', va='center', color='#0F5E6B', fontweight='bold')
            try:
                ax_e.text(5.0, 0.55, fr"$f(x) = {g_lat} \quad \Longleftrightarrow \quad y = {g_lat}$", fontsize=17.5, ha='center', va='center', color='#1F3A5F', fontweight='bold')
            except Exception:
                ax_e.text(5.0, 0.55, f"y = {current_g}", fontsize=16, ha='center', va='center', color='#1F3A5F', fontweight='bold')
            return fig_to_bytes(fig_e)
            
        eq_bytes = generate_eq_bytes

        def generate_pdf_discussion_bytes():
            nrows = len(final_table)
            fig_dt, ax_dt = new_fig(figsize=(10, nrows * 0.7 + 0.8))
            fig_dt.patch.set_facecolor('white')
            ax_dt.set_facecolor('white')
            ax_dt.axis('off')
            ax_dt.set_xlim(-0.05, 10.05)
            ax_dt.set_ylim(-0.05, nrows * 0.7 + 0.75)
            for i in range(nrows + 1):
                ax_dt.plot([0, 10], [i * 0.7, i * 0.7], 'k-', lw=1 if 0 < i < nrows else 2)
            for xl in [0, 6, 10]:
                ax_dt.plot([xl, xl], [0, nrows * 0.7 + 0.7], 'k-', lw=2 if xl!=6 else 1)
            ax_dt.plot([0, 10], [nrows * 0.7 + 0.7, nrows * 0.7 + 0.7], 'k-', lw=2)
            ax_dt.add_patch(plt.Rectangle((0, nrows * 0.7), 6, 0.7, facecolor='#1F3A5F'))
            ax_dt.add_patch(plt.Rectangle((6, nrows * 0.7), 4, 0.7, facecolor='#1F3A5F'))
            ax_dt.text(3, nrows * 0.7 + 0.35, fix_arabic_mpl("عدد و إشارة حلول المعادلة"), color='white', fontsize=13.5, fontweight='bold', ha='center', va='center')
            ax_dt.text(8, nrows * 0.7 + 0.35, fix_arabic_mpl("المجال / القيمة المضبوطة"), color='white', fontsize=13, fontweight='bold', ha='center', va='center')
            for i, (m_latex, sol_text, L, H) in enumerate(final_table):
                y_center = (nrows - i - 1) * 0.7 + 0.35
                ax_dt.text(3, y_center, fix_arabic_mpl(sol_text), fontsize=14 if len(sol_text) > 35 else 15.5, ha='center', va='center', color=get_sol_color_pdf(sol_text), fontweight='bold')
                try:
                    ax_dt.text(8, y_center, f"${m_latex}$", fontsize=15.5, ha='center', va='center', color='#1F3A5F')
                except Exception:
                    ax_dt.text(8, y_center, str(m_latex), fontsize=14, ha='center', va='center', color='#1F3A5F')
            return fig_to_bytes(fig_dt)
            
        disc_table_bytes = generate_pdf_discussion_bytes

        cache.update({
            'valid': True, 'f_func': f_func, 'g_func': g_func,
            'x_vals_plot': x_vals_plot, 'y_vals_plot': y_vals_plot,
            'plot_x_bound': plot_x_bound, 'plot_y_bound': plot_y_bound,
            'unique_asymptotes': unique_asymptotes, 'holes': holes,
            'm_critical_num': m_critical_num, 'final_table': final_table,
            'domain_latex_st': domain_latex_st, 'limits_data_detailed': limits_data_detailed,
            'deriv_steps_detailed': deriv_steps_detailed, 'df_latex_str_safe': df_latex_str_safe,
            'var_table_bytes': var_table_bytes,
            'limits_chunks_bytes': limits_chunks_bytes,
            'deriv_chunks_bytes': deriv_chunks_bytes,
            'eq_bytes': eq_bytes,
            'disc_table_bytes': disc_table_bytes, 'rel_pos_tables_info': rel_pos_tables_info,
            'm_min_val': m_min_val, 'm_max_val': m_max_val, 'f_expr': f_expr, 'g_expr': g_expr,
        })
    except Exception as e:
        cache['error'] = str(e)
    return cache

@st.cache_resource
def _ctx_store():
    return {}

def _run_with_deadline(fn, args, seconds):
    box = {}
    def worker():
        _DEADLINES[threading.get_ident()] = time.time() + seconds
        try:
            box['res'] = fn(*args)
        except _AbortAnalysis:
            box['aborted'] = True
        except BaseException as e_w:
            box['res'] = {'valid': False, 'error': str(e_w)}
        finally:
            _DEADLINES.pop(threading.get_ident(), None)
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(seconds + 15)
    if t.is_alive():
        return None
    return box.get('res')

def build_with_timeout(f_str, g_str, tag, seconds=100):
    store = _ctx_store()
    key = (f_str, g_str, tag)
    if key in store:
        return store[key]
    res = _run_with_deadline(build_math_context, (f_str, g_str, tag), seconds)
    if res is None:
        return {'valid': False, 'error': 'انتهت مهلة التحليل؛ الدالة معقدة جداً لهذا الخادم. جرّب دالة أبسط.'}
    if res.get('valid'):
        if len(store) >= 30:
            store.pop(next(iter(store)))
        store[key] = res
    return res

if 'math_cache' not in st.session_state or st.session_state.get('last_f') != current_f or st.session_state.get('last_g') != current_g or st.session_state.get('cache_ver') != "v35":
    with st.spinner("جاري التحليل الرياضي الدقيق..."):
        st.session_state.math_cache = build_with_timeout(current_f, current_g, "v35")
        st.session_state.pdf_data = None
        st.session_state.last_f = current_f
        st.session_state.last_g = current_g
        st.session_state.cache_ver = "v35"

cache = st.session_state.math_cache

if not cache.get('valid'):
    if cache.get('error') == 'EMPTY' or not current_f:
        st.info("✏️ الخانة فارغة حالياً؛ اكتب عبارة الدالة f(x) في الأعلى ثم اضغط على زر «تأكيد ورسم الدالة».")
    else:
        st.error(f"⚠️ صيغة الدالة غير مكتملة. تأكد من كتابة العبارة الرياضية بشكل صحيح ثم اضغط على زر «تأكيد ورسم الدالة». ({cache.get('error', '')})")
else:
    g_latex_disp = sanitize_latex(cache['g_expr'])
    st.latex(rf"\color{{#FFD700}} \begin{{cases}} f(x) = {sanitize_latex(cache['f_expr'])} \\ y = {g_latex_disp} \end{{cases}}")
    m_min_val, m_max_val, m_critical_num = cache['m_min_val'], cache['m_max_val'], cache['m_critical_num']

    col1, col2 = st.columns(2)
    with col1:
        if st.button("تشغيل المناقشة آلياً ▶", disabled=st.session_state.auto_play):
            st.session_state.auto_play = True
            st.session_state.m_anim = m_min_val
            st.rerun()
    with col2:
        if st.button("إيقاف ⏹", disabled=not st.session_state.auto_play):
            st.session_state.auto_play = False
            st.rerun()
    
    m_val_manual = st.slider("تحكم يدوي:", m_min_val, m_max_val, m_min_val, 0.05, format="%g", key="manual_m", disabled=st.session_state.auto_play)
    anim_placeholder = st.empty()

    st.markdown("<h3 style='color:#FFD700; text-align:center; direction:rtl; margin-top:15px; margin-bottom:5px;'>📌 المناقشة البيانية</h3>", unsafe_allow_html=True)
    st.info(fr"🔹 حلول المعادلة $f(x) = {g_latex_disp}$ هي فواصل نقط تقاطع منحنى الدالة $f$ مع المستقيم ذو المعادلة: $y = {g_latex_disp}$")

    table_placeholder = st.empty()

    def generate_st_markdown_table(current_m):
        md = "| عدد و إشارة حلول المعادلة | المجال / القيمة المضبوطة |\n| :---: | :---: |\n"
        active_idx = 0
        for idx, (m_latex, sol_text, L, H) in enumerate(cache['final_table']):
            if (L == H and abs(current_m - L) <= 0.04) or (L == float('-inf') and current_m <= H - 0.04) or (H == float('inf') and current_m >= L + 0.04) or (L + 0.04 <= current_m <= H - 0.04):
                active_idx = idx
        for idx, (m_latex, sol_text, L, H) in enumerate(cache['final_table']):
            c_text = get_sol_color_html(sol_text)
            if idx == active_idx:
                text_cell = f"<span style='display:inline-block; width:90%; background-color:#334155; border:2px solid #FFD700; padding:4px; border-radius:6px; color:{c_text}; font-weight:bold; font-size:17px;'>{sol_text}</span>"
                math_cell = f"<span style='display:inline-block; width:90%; background-color:#334155; border:2px solid #FFD700; padding:4px; border-radius:6px; white-space:nowrap; font-size:16px;'>**${m_latex}$**</span>"
            else:
                text_cell = f"<span style='color:{c_text}; font-weight:bold; font-size:17px;'>{sol_text}</span>"
                math_cell = f"<span style='white-space:nowrap; font-size:16px;'>${m_latex}$</span>"
            md += f"| {text_cell} | {math_cell} |\n"
        return md

    def draw_plot(m_val, mode='dark'):
        fig, ax = new_fig(figsize=(9.5, 6.0))
        x_lim_b = cache.get('plot_x_bound', 12.0)
        y_lim_b = cache.get('plot_y_bound', 8.0)
        major_step_x = 1 if x_lim_b <= 15 else (2 if x_lim_b <= 26 else 5)
        major_step_y = 1 if y_lim_b <= 12 else (2 if y_lim_b <= 22 else 5)

        if mode == 'dark':
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#0F172A')
            ax.tick_params(colors='#E2E8F0', labelsize=9)
            for spine in ax.spines.values():
                spine.set_edgecolor('#475569')
            ax.axhline(0, color='#E2E8F0', linewidth=2.5, zorder=3)
            ax.axvline(0, color='#E2E8F0', linewidth=2.5, zorder=3)
            ax.minorticks_on()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(major_step_x))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(major_step_y))
            ax.grid(True, which='major', color='#475569', linestyle='-', linewidth=1.2, zorder=1)
            ax.grid(True, which='minor', color='#1E293B', linestyle='-', linewidth=0.8, zorder=1)
            c_asym, c_cf, c_cg, c_pts, c_text, bg_leg, edge_leg = '#F472B6', '#00E5FF', '#FFD700', '#EF4444', '#E2E8F0', '#1E293B', '#475569'
        else:
            fig.patch.set_facecolor('#FFFFFF')
            ax.set_facecolor('#FFFFFF')
            ax.tick_params(colors='black', labelsize=9)
            for spine in ax.spines.values():
                spine.set_edgecolor('#A0A0A0')
            ax.axhline(0, color='black', linewidth=2, zorder=3)
            ax.axvline(0, color='black', linewidth=2, zorder=3)
            ax.minorticks_on()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(major_step_x))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(major_step_y))
            ax.grid(True, which='major', color='#D9DEE5', linestyle='-', linewidth=1.0, zorder=1)
            ax.grid(True, which='minor', color='#EEF1F5', linestyle='-', linewidth=0.6, zorder=1)
            c_asym, c_cf, c_cg, c_pts, c_text, bg_leg, edge_leg = '#9B2226', '#1F4E79', '#0F5E6B', '#B7791F', '#1F2937', '#FFFFFF', '#B8C0CC'

        for asym in cache['unique_asymptotes']:
            try:
                if asym['type'] == 'h':
                    ax.axhline(asym['val'], color=c_asym, linestyle='--', linewidth=2.0, zorder=4)
                    ax.text(-x_lim_b + 0.5, asym['val'] + 0.25, f"${asym['label']}$", color=c_asym, fontsize=13, fontweight='bold', ha='left')
                elif asym['type'] == 'v':
                    ax.axvline(asym['val'], color=c_asym, linestyle='--', linewidth=2.0, zorder=4)
                    ax.text(asym['val'] + 0.15, y_lim_b - 0.8, f"${asym['label']}$", color=c_asym, fontsize=13, fontweight='bold', va='top')
                elif asym['type'] == 'oblique':
                    x_ob = np.array([-x_lim_b, x_lim_b])
                    ax.plot(x_ob, asym['a'] * x_ob + asym['b'], color=c_asym, linestyle='-.', linewidth=2.0, zorder=4, label=f"$(\\Delta): {asym['label']}$")
            except Exception:
                pass
            
        for hole in cache['holes']:
            ax.plot(hole['val'], hole['lim'], marker='o', markerfacecolor=bg_leg, markeredgecolor=c_cf, markersize=8, markeredgewidth=2, zorder=6)
        ax.plot(cache['x_vals_plot'], cache['y_vals_plot'], color=c_cf, linewidth=3.3, label=r'$(C_f)$', zorder=5)
        
        if mode == 'dark':
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                y_g_plot = cache['g_func'](cache['x_vals_plot'], m_val)
            if np.isscalar(y_g_plot):
                y_g_plot = np.full_like(cache['x_vals_plot'], y_g_plot, dtype=float)
            m_val_str = str(int(m_val)) if int(m_val)==m_val else str(round(m_val, 2))
            m_eq_label = f"y = {m_val_str}" if current_g.strip() == 'm' else "y = " + current_g.replace('m', f"({m_val_str})" if m_val < 0 else m_val_str).replace('*', '')
            ax.plot(cache['x_vals_plot'], y_g_plot, color=c_cg, linestyle='--', linewidth=2.8, label=f"${m_eq_label}$", zorder=5)
            diff_plot = cache['y_vals_plot'] - y_g_plot
            intersect_x = []
            for i in range(len(diff_plot)-1):
                if np.isfinite(diff_plot[i]) and np.isfinite(diff_plot[i+1]):
                    if abs(diff_plot[i]) < 1e-7:
                        x_c = float(cache['x_vals_plot'][i])
                        if abs(x_c) <= x_lim_b:
                            intersect_x.append(x_c)
                    elif diff_plot[i] * diff_plot[i+1] < 0:
                        x_c = cache['x_vals_plot'][i] - diff_plot[i] * (cache['x_vals_plot'][i+1] - cache['x_vals_plot'][i]) / (diff_plot[i+1] - diff_plot[i])
                        if abs(x_c) <= x_lim_b and not any(abs(x_c - safe_float(a['val'])) < 1e-3 for a in cache['unique_asymptotes'] if a['type'] == 'v'):
                            if abs(cache['y_vals_plot'][i+1] - cache['y_vals_plot'][i]) > 1e-9 or abs(y_g_plot[i+1] - y_g_plot[i]) > 1e-9:
                                intersect_x.append(float(x_c))
            unique_ix = []
            for ix in intersect_x:
                if not any(abs(ix - u) < 0.12 for u in unique_ix):
                    unique_ix.append(ix)
            if unique_ix:
                iy = [m_val if current_g.strip() == 'm' else float(cache['g_func'](ix, m_val)) for ix in unique_ix]
                ax.scatter(unique_ix, iy, color=c_pts, s=125, zorder=6, edgecolor='white', linewidth=1.5, label=fix_arabic_mpl('نقاط التقاطع'))
            ax.text(x_lim_b * 0.33, m_val + 0.35, f"${m_eq_label}$", color=c_cg, fontsize=15, fontweight='bold', ha='center', va='bottom', zorder=6)
            
        ax.set_xlim(-x_lim_b, x_lim_b)
        ax.set_ylim(-y_lim_b, y_lim_b)
        try:
            legend = ax.legend(facecolor=bg_leg, edgecolor=edge_leg, loc='upper right', fontsize=12)
            for text in legend.get_texts():
                text.set_color(c_text)
            fig.tight_layout()
        except Exception:
            pass
        return fig, ax

    def get_img_height_mm(img_bytes, target_w_mm):
        if not img_bytes:
            return 0.0
        try:
            im = Image.open(io.BytesIO(img_bytes))
            w_px, h_px = im.size
            return (h_px / float(w_px)) * target_w_mm if w_px > 0 else 0.0
        except Exception:
            return 35.0

    def pdf_add_bytes_image(pdf, img_bytes, x, w):
        if not img_bytes:
            return
        h_mm = get_img_height_mm(img_bytes, w)
        if pdf.get_y() + h_mm > 280 and pdf.get_y() > 35:
            pdf.add_page()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
            tmp_img.write(img_bytes)
            tmp_path = tmp_img.name
        try:
            pdf.image(tmp_path, x=x, w=w)
        except Exception:
            pass
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    def pdf_section_title(pdf, title_text, size=15):
        pdf.set_font("Amiri", size=size)
        pdf.set_text_color(15, 94, 107)
        pdf.cell(0, 8, fix_arabic_pdf(title_text), ln=True, align='R')
        y_line = pdf.get_y()
        pdf.set_line_width(0.2)
        pdf.set_draw_color(203, 213, 225)
        pdf.line(15, y_line, 195, y_line)
        pdf.set_line_width(0.7)
        pdf.set_draw_color(15, 94, 107)
        pdf.line(150, y_line, 195, y_line)
        pdf.ln(2.5)

    def pdf_add_section_with_chunks(pdf, title_text, chunks_list, x, w):
        if not chunks_list:
            return
        first_h = get_img_height_mm(chunks_list[0], w)
        if pdf.get_y() + 10 + first_h > 280 and pdf.get_y() > 35:
            pdf.add_page()
        pdf_section_title(pdf, title_text)
        for chunk_b in chunks_list:
            pdf_add_bytes_image(pdf, chunk_b, x=x, w=w)
            pdf.ln(1)
        pdf.ln(2)

    @st.cache_data(show_spinner=False, max_entries=5)
    def get_cached_pdf_bytes(f_key, g_key, ver_key="v35"):
        if not PDF_ENABLED:
            return None
        try:
            class _StudyPDF(FPDF):
                def footer(self):
                    self.set_y(-13)
                    self.set_draw_color(203, 213, 225)
                    self.set_line_width(0.2)
                    self.line(15, self.get_y(), 195, self.get_y())
                    self.set_font("Amiri", size=11)
                    self.set_text_color(107, 114, 128)
                    self.set_x(15)
                    self.cell(90, 8, str(self.page_no()), align='L')
                    self.cell(90, 8, fix_arabic_pdf("الأستاذ سوايسية هشام"), align='R')

            pdf = _StudyPDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=18)
            font_path = "Amiri-Regular.ttf"
            if not os.path.exists(font_path) or os.path.getsize(font_path) < 10000:
                req = urllib.request.Request("https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(font_path, 'wb') as out_file:
                    out_file.write(response.read())
            pdf.add_font("Amiri", "", font_path, uni=True)
            pdf.add_page()
            pdf.set_font("Amiri", size=24)
            pdf.set_text_color(31, 58, 95)
            pdf.cell(0, 12, fix_arabic_pdf("المناقشة البيانية ودراسة تغيرات دالة"), ln=True, align='C')
            pdf.set_font("Amiri", size=15)
            pdf.set_text_color(107, 114, 128)
            pdf.cell(0, 8, fix_arabic_pdf("الأستاذ سوايسية هشام"), ln=True, align='C')
            y_t = pdf.get_y() + 1
            pdf.set_line_width(0.2)
            pdf.set_draw_color(203, 213, 225)
            pdf.line(15, y_t, 195, y_t)
            pdf.set_line_width(0.8)
            pdf.set_draw_color(15, 94, 107)
            pdf.line(85, y_t, 125, y_t)
            pdf.ln(5)
            try:
                fig_h, ax_h = new_fig(figsize=(9.5, 0.9))
                fig_h.patch.set_facecolor('white')
                ax_h.set_facecolor('white')
                ax_h.axis('off')
                ax_h.text(0.5, 0.5, "$f(x) = " + sanitize_latex(cache['f_expr']) + "$", fontsize=19, ha='center', va='center', color='#1F3A5F', transform=ax_h.transAxes)
                head_img = fig_to_bytes(fig_h)
                if head_img:
                    pdf_add_bytes_image(pdf, head_img, x=25, w=160)
            except Exception:
                pass
            pdf.ln(2)
            
            pdf_add_section_with_chunks(
                pdf,
                "1. حساب النهايات واستنتاج المقاربات العمودية والأفقية:",
                cache['limits_chunks_bytes'](),
                x=15, w=180
            )

            pdf_add_section_with_chunks(
                pdf,
                "2. حساب الدالة المشتقة:",
                cache['deriv_chunks_bytes'](),
                x=15, w=180
            )

            if cache.get('var_table_bytes'):
                pdf_add_section_with_chunks(
                    pdf,
                    "3. جدول التغيرات:",
                    [cache['var_table_bytes']],
                    x=10, w=190
                )

            has_oblique = bool(cache.get('rel_pos_tables_info'))
            if has_oblique:
                ob_chunks = [od['oblique_steps_bytes'] for od in cache['rel_pos_tables_info'] if od.get('oblique_steps_bytes')]
                pdf_add_section_with_chunks(
                    pdf,
                    "4. استنتاج معادلة المستقيم المقارب المائل وشرح طريقتها:",
                    ob_chunks,
                    x=15, w=180
                )
                rp_chunks = [od['rel_pos_bytes'] for od in cache['rel_pos_tables_info'] if od.get('rel_pos_bytes')]
                pdf_add_section_with_chunks(
                    pdf,
                    "5. جدول الوضع النسبي بين المقارب المائل والمنحنى (Cf):",
                    rp_chunks,
                    x=10, w=190
                )

            plot_sec_num = 6 if has_oblique else 4
            fig_light, _ = draw_plot(0, mode='light')
            light_bytes = fig_to_bytes(fig_light)
            plot_h = get_img_height_mm(light_bytes, 165)

            if pdf.get_y() + 10 + plot_h > 280 and pdf.get_y() > 35:
                pdf.add_page()
            pdf_section_title(pdf, f"{plot_sec_num}. التمثيل البياني للدالة (Cf):")
            pdf_add_bytes_image(pdf, light_bytes, x=22, w=165)
            pdf.ln(3)

            disc_sec_num = plot_sec_num + 1
            eq_img = cache['eq_bytes']()
            disc_img = cache['disc_table_bytes']()
            eq_h = get_img_height_mm(eq_img, 180)
            disc_h = get_img_height_mm(disc_img, 180)
            if pdf.get_y() + 10 + eq_h + disc_h > 282 and pdf.get_y() > 35:
                pdf.add_page()
            pdf_section_title(pdf, f"{disc_sec_num}. المناقشة البيانية:")
            if eq_img:
                pdf_add_bytes_image(pdf, eq_img, x=15, w=180)
                pdf.ln(1)
            if disc_img:
                pdf_add_bytes_image(pdf, disc_img, x=15, w=180)

            pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf_file.close()
            pdf.output(pdf_file.name)
            with open(pdf_file.name, "rb") as f_in:
                data_b = f_in.read()
            try:
                os.remove(pdf_file.name)
            except Exception:
                pass
            return data_b
        except Exception:
            return None

    if st.session_state.auto_play:
        m_val = st.session_state.m_anim
        stop_points = sorted(list(set(([0.0] if not m_critical_num else m_critical_num + [m_critical_num[0]-1.5, m_critical_num[-1]+1.5] + [(m_critical_num[i]+m_critical_num[i+1])/2.0 for i in range(len(m_critical_num)-1)]))))
        while m_val <= m_max_val and st.session_state.auto_play:
            fig_dark, _ = draw_plot(m_val, mode='dark')
            anim_placeholder.pyplot(fig_dark, use_container_width=True, clear_figure=True)
            table_placeholder.markdown(generate_st_markdown_table(m_val), unsafe_allow_html=True)
            plt.close(fig_dark)
            time.sleep(1.5 if any(abs(m_val - sp_val) < 1e-4 for sp_val in stop_points) else 0.02)
            next_m = m_val + 0.2
            for sp_val in stop_points:
                if m_val < sp_val - 1e-4 and next_m >= sp_val - 1e-4:
                    next_m = float(sp_val)
                    break
            m_val = next_m
        st.session_state.auto_play = False
        st.rerun()
    else:
        m_val = m_val_manual
        fig_dark, _ = draw_plot(m_val, mode='dark')
        anim_placeholder.pyplot(fig_dark, use_container_width=True, clear_figure=True)
        table_placeholder.markdown(generate_st_markdown_table(m_val), unsafe_allow_html=True)
        plt.close(fig_dark)
        
    with st.expander("📊 عرض دراسة الدالة الشاملة بالترتيب المنهجي", expanded=True):
        st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>1. حساب النهايات واستنتاج المقارب العمودي أو الأفقي:</h4>", unsafe_allow_html=True)
        st.latex(cache['domain_latex_st'])
        for lim_item in cache['limits_data_detailed']:
            st.latex(lim_item['main'])
            if lim_item['steps']:
                st.markdown("<div class='step-box-lim'>🔹 التعليل (خطوات الحساب):</div>", unsafe_allow_html=True)
                for stp in lim_item['steps']:
                    st.latex(fr"\color{{#C4B5FD}}{{{stp}}}")
                if lim_item.get('step_note'):
                    st.markdown(f"<div style='text-align:center; direction:rtl; color:#FDE047; font-size:15px; font-weight:bold;'>💡 ({lim_item['step_note']})</div>", unsafe_allow_html=True)
            if lim_item.get('geo_txt'):
                st.success(lim_item['geo_txt'])
                
        st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>2. حساب الدالة المشتقة:</h4>", unsafe_allow_html=True)
        for d_step in cache.get('deriv_steps_detailed', []):
            st.markdown(f"<div class='step-box-deriv'>🔸 {d_step['label']}</div>", unsafe_allow_html=True)
            for m_str in d_step['math_list']:
                st.latex(fr"\color{{#FDE68A}}{{{m_str}}}")
        st.markdown("<div class='step-box-final'>✅ العبارة النهائية للمشتقة:</div>", unsafe_allow_html=True)
        st.latex(fr"\color{{#4ADE80}}{{f'(x) = {cache['df_latex_str_safe']}}}")
        
        st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>3. جدول التغيرات:</h4>", unsafe_allow_html=True)
        if cache.get('var_table_bytes'):
            st.image(cache['var_table_bytes'], use_container_width=True)

        if cache.get('rel_pos_tables_info'):
            st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>4. استنتاج معادلة المستقيم المقارب المائل (Δ) وشرح طريقة استنتاجها:</h4>", unsafe_allow_html=True)
            for od in cache['rel_pos_tables_info']:
                st.info(fr"🔹 بما أن $\lim_{{x \to {od['target_latex']}}} f(x) = \pm\infty$، نبحث عن معامل التوجيه $a$ ثم $b$ بجوار ${od['target_latex']}$:")
                st.latex(fr"\color{{#FDE68A}}{{a = \lim_{{x \to {od['target_latex']}}} \frac{{f(x)}}{{x}} = {od['a_lat']}}}")
                st.latex(fr"\color{{#FDE68A}}{{b = \lim_{{x \to {od['target_latex']}}} [f(x) - ({od['a_lat']})x] = {od['b_lat']}}}")
                st.latex(fr"\color{{#34D399}}{{\lim_{{x \to {od['target_latex']}}} \left[ f(x) - ({od['line_lat']}) \right] = \lim_{{x \to {od['target_latex']}}} \left( {od['rem_lat']} \right) = 0}}")
                st.success(fr"📐 ومنه المنحنى $(C_f)$ يقبل مستقيماً مقارباً مائلاً $(\Delta)$ بجوار ${od['target_latex']}$ معادلته: $y = {od['line_lat']}$")

            st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>5. جدول الوضع النسبي بين المقارب المائل (Δ) والمنحنى (Cf):</h4>", unsafe_allow_html=True)
            for od in cache['rel_pos_tables_info']:
                st.markdown("<div class='step-box-deriv'>🔸 ندرس إشارة الفرق بين عبارة الدالة ومعادلة المستقيم المقارب المائل:</div>", unsafe_allow_html=True)
                st.latex(fr"\color{{#FDE68A}}{{f(x) - y = {od['rem_lat']}}}")
                if od.get('rel_pos_bytes'):
                    st.image(od['rel_pos_bytes'], use_container_width=True)

    if PDF_ENABLED and not st.session_state.auto_play:
        pdf_key = (current_f, current_g)
        if st.button("📄 تجهيز ملف PDF", use_container_width=True):
            with st.spinner("جاري إنشاء ملف الـ PDF..."):
                st.session_state.pdf_data = (pdf_key, get_cached_pdf_bytes(current_f, current_g, "v35"))
        _pd = st.session_state.get("pdf_data")
        pdf_bytes = _pd[1] if (_pd and _pd[0] == pdf_key) else None
        if pdf_bytes:
            st.download_button(
                label="📥 تحميل الحل والدراسة كملف PDF",
                data=pdf_bytes,
                file_name="monaqasha_souaissia.pdf",
                mime="application/pdf",
                disabled=st.session_state.auto_play
            )

st.markdown("""
<div class='footer-social'>
    <span class='footer-text'>رابط صفحتي في كل من الفايسبوك والانستغرام:</span>
    <div class='social-links-group'>
        <a href="https://www.facebook.com/share/1KHcAq6bVm/" target="_blank" class="social-btn fb-btn"><span>Facebook</span></a>
        <a href="https://www.instagram.com/prof_hicham_math?stkn=dzh0OWgxZ2ltb3Uw" target="_blank" class="social-btn ig-btn"><span>Instagram</span></a>
    </div>
</div>
""", unsafe_allow_html=True)
# ==================== نهاية الجزء (4/4) ====================
