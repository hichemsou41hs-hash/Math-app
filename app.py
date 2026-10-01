import streamlit as st
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

import base64
b64_manifest = base64.b64encode(manifest_data.encode('utf-8')).decode('utf-8')

st.markdown(
    f'<link rel="manifest" href="data:application/manifest+json;base64,{b64_manifest}">',
    unsafe_allow_html=True
)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sympy as sp
from scipy.signal import find_peaks
import time
import warnings
import re
import os
import urllib.request
import tempfile
from PIL import Image, ImageOps, ImageEnhance
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

try:
    from fpdf import FPDF
    import arabic_reshaper
    from bidi.algorithm import get_display
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

warnings.filterwarnings("ignore")

st.set_page_config(page_title="المناقشة البيانية ودراسة تغيرات دالة", page_icon="📈", layout="centered")

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

# دالة تحويل رقمي محصنة ضد اللانهاية والأعداد المركبة ودالة لامبرت
def safe_float(expr):
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
        if val == sp.oo: return float('inf')
        if val == -sp.oo: return float('-inf')
        if val in [sp.zoo, sp.nan]: return np.nan
        im_part = float(sp.im(val))
        if abs(im_part) > 1e-6:
            return np.nan
        return float(sp.re(val))
    except Exception:
        try:
            c_val = complex(expr)
            if abs(c_val.imag) > 1e-6:
                return np.nan
            return float(c_val.real)
        except Exception:
            return np.nan

def fmt(val):
    if str(val) == 'oo' or val == float('inf'): return "+\infty"
    if str(val) == '-oo' or val == float('-inf'): return "-\infty"
    if str(val) == 'zoo': return "\pm\infty"
    try:
        f_val = safe_float(val)
        if not np.isfinite(f_val): return str(val)
        if abs(f_val) > 1e6: return str(f_val)
        if int(f_val) == f_val: return str(int(f_val))
        return str(round(f_val, 2))
    except:
        return str(val)

# مطهر ومترجم رياضي متطور يعالج كل مخرجات الـ OCR وصيغ exp و LaTeX
def clean_ocr_math(raw_str):
    if not raw_str:
        return ""
    s = str(raw_str).strip()
    s = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]', '', s)
    s = s.replace('`', '').replace('$', '').strip()
    
    lines = [line.strip() for line in s.splitlines() if line.strip()]
    if lines:
        for line in lines:
            if any(k in line.lower() for k in ['f(x)', 'x', 'ln', 'exp', 'e^', 'sqrt', '/']):
                s = line
                break
        else:
            s = lines[0]

    s = re.sub(r'^[fFgGhHyY]\s*(\(\s*[xX]\s*\))?\s*[:=]\s*', '', s)
    s = s.replace('X', 'x')

    replacements = {
        '−': '-', '–': '-', '—': '-', 'ｰ': '-',
        '×': '*', '÷': '/', '∕': '/', '⁄': '/', '⋅': '*', '·': '*',
        '（': '(', '）': ')', '［': '(', '］': ')', '[': '(', ']': ')',
        '²': '^2', '³': '^3', '⁴': '^4', '√': 'sqrt',
        '\\left': '', '\\right': '', '\\cdot': '*', '\\times': '*',
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
    s = s.replace('{', '(').replace('}', ')')
    s = s.replace('\\', '')
    s = re.sub(r'\|([^|]+)\|', r'abs(\1)', s)
    s = re.sub(r'\bexp\s*\(', 'e^(', s, flags=re.IGNORECASE)
    return s.strip()

def fix_implicit_mult(expr_str):
    expr_str = clean_ocr_math(expr_str)
    if "()" in expr_str:
        expr_str = expr_str.replace("()", "(1)")
    expr_str = expr_str.replace('^', '**')
    expr_str = re.sub(r'([xy0-9\)])\s*(exp|ln|log|cos|sin|tan|sqrt|abs|pi)\b', r'\1*\2', expr_str)
    expr_str = re.sub(r'([xy0-9\)])\s*(e)\b(?![a-zA-Z])', r'\1*\2', expr_str)
    expr_str = re.sub(r'\b(e|pi)\s*([xy0-9\(])', r'\1*\2', expr_str)
    expr_str = re.sub(r'(\))\s*(\()', r'\1*\2', expr_str)
    expr_str = re.sub(r'([0-9])\s*([xX\(])', r'\1*\2', expr_str)
    expr_str = re.sub(r'([xX\)])\s*([0-9])', r'\1*\2', expr_str)
    return expr_str

def validate_extracted_math(candidate_str):
    try:
        x_sym, m_sym = sp.symbols('x m', real=True)
        local_dict = {
            'x': x_sym, 'm': m_sym, 'e': sp.E, 'E': sp.E, 'pi': sp.pi,
            'ln': sp.log, 'log': sp.log, 'exp': sp.exp, 'sqrt': sp.sqrt,
            'abs': sp.Abs, 'Abs': sp.Abs, 'cos': sp.cos, 'sin': sp.sin, 'tan': sp.tan
        }
        transformations = (standard_transformations + (implicit_multiplication_application,))
        proc = fix_implicit_mult(candidate_str)
        if not proc:
            return None
        parsed = parse_expr(proc, local_dict=local_dict, transformations=transformations)
        unknown_syms = [s for s in parsed.free_symbols if s not in (x_sym, m_sym)]
        if unknown_syms:
            return None
        return clean_ocr_math(candidate_str)
    except Exception:
        return None

def extract_math_from_image(image_file, api_key):
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    orig_img = Image.open(image_file).convert("RGB")
    w, h = orig_img.size
    if w < 600 or h < 200:
        scale = max(2, int(800 / max(w, 1)))
        proc_img = orig_img.resize((w * scale, h * scale), Image.Resampling.LANCZOS)
    else:
        proc_img = orig_img.copy()
    proc_img = ImageEnhance.Contrast(proc_img).enhance(1.5)
    proc_img = ImageEnhance.Sharpness(proc_img).enhance(1.8)

    prompt = (
        "You are a specialized mathematical OCR engine. Read the mathematical function from the image.\n"
        "Output ONLY the right-hand side expression in plain mathematical notation.\n"
        "Strict rules:\n"
        "- Do NOT include 'f(x) =' or 'y ='.\n"
        "- For exponentials, write e^(...) instead of exp(...). Example: e^(x - 2).\n"
        "- For fractions, wrap numerator and denominator in parentheses: (numerator)/(denominator).\n"
        "- For natural log, write ln(...). For square root, write sqrt(...). For |x|, write abs(x).\n"
        "- Output ONLY the single-line formula with no markdown, no backticks, and no extra words."
    )

    candidate_models = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-3.8-flash',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]
    try:
        for m in genai.list_models():
            if 'generateContent' in getattr(m, 'supported_generation_methods', []):
                m_name = m.name.replace('models/', '')
                if m_name not in candidate_models:
                    candidate_models.append(m_name)
    except Exception:
        pass

    last_err = ""
    for model_name in candidate_models:
        for img_to_use in (proc_img, orig_img):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, img_to_use])
                if response and response.text:
                    valid_expr = validate_extracted_math(response.text)
                    if valid_expr:
                        return valid_expr, None
                    cleaned = clean_ocr_math(response.text)
                    if cleaned:
                        return cleaned, None
            except Exception as e:
                last_err = str(e)
                continue

    return None, last_err

def fix_arabic_pdf(text):
    return get_display(arabic_reshaper.reshape(text)) if PDF_ENABLED else text

def fix_arabic_mpl(text):
    return arabic_reshaper.reshape(text) if PDF_ENABLED else text

def sanitize_latex(expr):
    if hasattr(expr, 'has'):
        if expr.has(sp.LambertW) or (hasattr(sp, 'RootOf') and expr.has(sp.RootOf)):
            try:
                fl = safe_float(expr)
                if np.isfinite(fl):
                    if abs(fl - round(fl)) < 1e-5: return str(int(round(fl)))
                    return str(round(fl, 2))
            except: pass
    if not isinstance(expr, str): expr = sp.latex(expr)
    s = str(expr)
    s = s.replace('log', 'ln')
    s = s.replace(r'\left', '').replace(r'\right', '')
    s = s.replace(r'\operatorname', r'\mathrm')
    return s

def format_lim_val(lim_sym):
    if lim_sym == sp.oo or str(lim_sym) == 'oo': return r"+\infty"
    if lim_sym == -sp.oo or str(lim_sym) == '-oo': return r"-\infty"
    if lim_sym == sp.zoo or str(lim_sym) == 'zoo': return r"\pm\infty"
    return sanitize_latex(lim_sym)

def safe_solve_real(expr, x_sym):
    roots = []
    try:
        raw_sols = sp.solve(expr, x_sym)
        for r in raw_sols:
            if hasattr(r, 'has') and (r.has(sp.LambertW) or (hasattr(sp, 'RootOf') and r.has(sp.RootOf))):
                fl = safe_float(r)
                if np.isfinite(fl):
                    if abs(fl - round(fl)) < 1e-6:
                        roots.append(sp.Integer(int(round(fl))))
                    else:
                        roots.append(sp.nsimplify(round(fl, 4), tolerance=1e-3))
            else:
                fl = safe_float(r)
                if np.isfinite(fl):
                    if abs(fl - round(fl)) < 1e-6:
                        roots.append(sp.Integer(int(round(fl))))
                    else:
                        roots.append(sp.simplify(r))
    except Exception:
        pass
    
    try:
        f_num = sp.lambdify(x_sym, expr, 'numpy')
        xs = np.linspace(-15, 15, 3001)
        with np.errstate(all='ignore'):
            ys = f_num(xs)
        if np.iscomplexobj(ys):
            ys = np.where(np.isreal(ys), ys.real, np.nan)
        ys = np.array(ys, dtype=float)
        for i in range(len(ys) - 1):
            if np.isfinite(ys[i]) and np.isfinite(ys[i+1]):
                if ys[i] == 0 or ys[i] * ys[i+1] < 0:
                    guess = (xs[i] + xs[i+1]) / 2.0
                    try:
                        r_num = float(sp.nsolve(expr, x_sym, guess))
                        if np.isfinite(r_num) and not any(abs(safe_float(er) - r_num) < 1e-3 for er in roots):
                            if abs(r_num - round(r_num)) < 1e-5:
                                roots.append(sp.Integer(int(round(r_num))))
                            else:
                                roots.append(sp.nsimplify(round(r_num, 4), tolerance=1e-3))
                    except Exception:
                        pass
    except Exception:
        pass

    unique_roots = []
    for r in roots:
        fl = safe_float(r)
        if np.isfinite(fl) and not any(abs(safe_float(ur) - fl) < 1e-3 for ur in unique_roots):
            unique_roots.append(r)
    return unique_roots

def get_sol_color_pdf(sol_text):
    if "لا توجد" in sol_text: return "#D32F2F"      
    if "مضاعف" in sol_text: return "#D97706"       
    if "حل وحيد" in sol_text or "معدوم" in sol_text: return "#2E7D32" 
    if "حلان" in sol_text or "مختلفان" in sol_text: return "#0284C7"  
    if "ثلاثة" in sol_text: return "#C2185B"
    if "أربعة" in sol_text: return "#00796B"
    return "#6D28D9"                               

def get_sol_color_html(sol_text):
    if "لا توجد" in sol_text: return "#EF4444"
    if "مضاعف" in sol_text: return "#F59E0B"
    if "حل وحيد" in sol_text or "معدوم" in sol_text: return "#4ADE80"
    if "حلان" in sol_text or "مختلفان" in sol_text: return "#38BDF8"
    if "ثلاثة" in sol_text: return "#F472B6"
    if "أربعة" in sol_text: return "#2DD4BF"
    return "#A78BFA"

if 'auto_play' not in st.session_state: st.session_state.auto_play = False
if 'f_val' not in st.session_state: st.session_state.f_val = "x - 1 + x / exp(x - 2)"
if 'g_val' not in st.session_state: st.session_state.g_val = "m"
if 'kbd_target' not in st.session_state: st.session_state.kbd_target = "f"

with st.expander("⌨️ لوحة المفاتيح المساعدة", expanded=False):
    t_sel = st.radio("🎯 تحديد خانة الكتابة:", ["f(x) الدالة", "m المستقيم بدلالة"], horizontal=True, key="kbd_radio")
    st.session_state.kbd_target = "f" if t_sel == "f(x) الدالة" else "g"
    
    def k_click(char):
        target = "f_val" if st.session_state.kbd_target == "f" else "g_val"
        if char == 'DEL': st.session_state[target] = st.session_state[target][:-1]
        elif char == 'CLR': st.session_state[target] = ""
        else: st.session_state[target] += char

    # استبدال x² بالحالة العامة xⁿ التي تكتب رمز الأس ^
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
except: pass 

col_text, col_img = st.columns(2)
with col_img:
    img_file = st.file_uploader("🖼 ارفع صورة الدالة لاستخراجها آلياً:", type=['png', 'jpg', 'jpeg', 'webp'])
    st.markdown("<div style='font-size:14px; color:#94A3B8; text-align:right; direction:rtl; margin-top:-10px; margin-bottom:10px;'>💡 <b>ملاحظة:</b> في حال وجود ضغط على خادم الذكاء الاصطناعي وفشل قراءة الصورة، يرجى كتابة الدالة يدوياً في الخانة المجاورة.</div>", unsafe_allow_html=True)
    if img_file:
        if not api_key:
            st.error("⚠️ خاصية الذكاء الاصطناعي غير مفعلة (ينقص مفتاح API).")
        else:
            if st.button("استخراج الدالة 🤖", use_container_width=True):
                with st.spinner("جاري قراءة الصورة..."):
                    extracted_text, err_msg = extract_math_from_image(img_file, api_key)
                    if extracted_text:
                        st.session_state.f_val = extracted_text
                        st.success(f"✅ تم الاستخراج بنجاح: {extracted_text}")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"❌ تعذر استخراج الدالة حالياً: {err_msg}")

with col_text:
    st.text_input("أدخل عبارة الدالة f(x):", key="f_val")
    st.text_input("أدخل معادلة المستقيم بدلالة m:", key="g_val")

current_f = st.session_state.f_val
current_g = st.session_state.g_val

@st.cache_resource
def build_math_context(f_str, g_str, version_tag="v8"):
    cache = {'valid': False, 'error': ''}
    try:
        x_sym, m_sym = sp.symbols('x m', real=True)
        local_dict = {
            'x': x_sym, 'm': m_sym, 'e': sp.E, 'E': sp.E, 'pi': sp.pi,
            'ln': sp.log, 'log': sp.log, 'exp': sp.exp, 'sqrt': sp.sqrt,
            'abs': sp.Abs, 'Abs': sp.Abs, 'cos': sp.cos, 'sin': sp.sin, 'tan': sp.tan
        }
        transformations = (standard_transformations + (implicit_multiplication_application,))
        f_processed = fix_implicit_mult(f_str)
        g_processed = fix_implicit_mult(g_str)
        f_expr = parse_expr(f_processed, local_dict=local_dict, transformations=transformations)
        g_expr = parse_expr(g_processed, local_dict=local_dict, transformations=transformations)
        
        f_func = sp.lambdify(x_sym, f_expr, 'numpy')
        g_func = sp.lambdify((x_sym, m_sym), g_expr, 'numpy')
        
        candidate_v_asymptotes = []
        try:
            n_expr, d_expr = sp.fraction(sp.cancel(f_expr))
            if d_expr != 1:
                for r in safe_solve_real(d_expr, x_sym):
                    candidate_v_asymptotes.append(r)
        except: pass
        try:
            for log_expr in f_expr.atoms(sp.log):
                for r in safe_solve_real(log_expr.args[0], x_sym):
                    candidate_v_asymptotes.append(r)
        except: pass
        
        unique_cands = []
        for r in candidate_v_asymptotes:
            fl = safe_float(r)
            if np.isfinite(fl) and not any(abs(safe_float(uc) - fl) < 1e-4 for uc in unique_cands):
                unique_cands.append(r)
        candidate_v_asymptotes = unique_cands
        
        true_v_asymptotes = []
        holes = []
        for r in candidate_v_asymptotes:
            try:
                lim_p = sp.limit(f_expr, x_sym, r, dir='+')
                lim_m = sp.limit(f_expr, x_sym, r, dir='-')
                if lim_p in [sp.oo, -sp.oo, sp.zoo] or lim_m in [sp.oo, -sp.oo, sp.zoo]:
                    true_v_asymptotes.append(r)
                else:
                    val_p = safe_float(lim_p)
                    if np.isfinite(val_p):
                        holes.append({'sym': r, 'val': safe_float(r), 'lim': val_p})
            except:
                true_v_asymptotes.append(r)

        unique_asymptotes = []
        for r in true_v_asymptotes:
            unique_asymptotes.append({'type': 'v', 'val': safe_float(r), 'label': f"x={sanitize_latex(r)}"})

        x_base = np.linspace(-15, 15, 6001)
        x_roots_base = np.concatenate([np.linspace(-500, -15, 2000, endpoint=False), np.linspace(-15, 15, 6001), np.linspace(15, 500, 2000)])
        
        extra_x = []
        for a in candidate_v_asymptotes:
            val = safe_float(a)
            if np.isfinite(val) and -16 <= val <= 16:
                for delta in [1e-3, 1e-4, 1e-5, 1e-6]:
                    extra_x.append(val - delta)
                    extra_x.append(val + delta)
                    
        if extra_x:
            x_vals_plot = np.sort(np.concatenate([x_base, extra_x]))
            x_vals_roots = np.sort(np.concatenate([x_roots_base, extra_x]))
        else:
            x_vals_plot = x_base
            x_vals_roots = x_roots_base

        def process_y_vals(x_arr):
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'): y_arr = f_func(x_arr)
            if np.iscomplexobj(y_arr): y_arr = np.where(np.isreal(y_arr), y_arr.real, np.nan)
            if np.isscalar(y_arr): y_arr = np.full_like(x_arr, y_arr, dtype=float)
            y_arr = np.array(y_arr, dtype=float)
            y_arr[~np.isfinite(y_arr)] = np.nan
            dy = np.abs(np.diff(y_arr))
            for idx in np.where(dy > 30)[0]: y_arr[idx] = np.nan; y_arr[idx+1] = np.nan
            return y_arr

        y_vals_plot = process_y_vals(x_vals_plot)
        y_vals_roots = process_y_vals(x_vals_roots)

        df_expr = sp.diff(f_expr, x_sym)
        df_clean = df_expr.replace(sp.sign, lambda arg: arg / sp.Abs(arg))
        df_simp = sp.simplify(df_clean)
        if df_simp.has(sp.Piecewise): df_simp = df_clean 
        try:
            df_together = sp.together(df_simp)
            if not df_together.has(sp.Piecewise):
                df_simp = df_together
        except: pass
        df_latex_str_safe = sanitize_latex(df_simp)

        def build_derivative_steps():
            steps = []
            try:
                num, den = sp.fraction(f_expr)
                if den != 1 and den.has(x_sym):
                    du = sp.simplify(sp.diff(num, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                    dv = sp.simplify(sp.diff(den, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                    u_l, v_l = sanitize_latex(num), sanitize_latex(den)
                    du_l, dv_l = sanitize_latex(du), sanitize_latex(dv)
                    steps.append({
                        'label': 'قانون مشتق حاصل قسمة:',
                        'math': r"f'(x) = \frac{u'(x) \cdot v(x) - v'(x) \cdot u(x)}{(v(x))^2}"
                    })
                    steps.append({
                        'label': 'حساب مشتق البسط والمقام:',
                        'math': fr"u(x) = {u_l} \Rightarrow u'(x) = {du_l} \quad , \quad v(x) = {v_l} \Rightarrow v'(x) = {dv_l}"
                    })
                    steps.append({
                        'label': 'بالتعويض في القانون:',
                        'math': fr"f'(x) = \frac{{({du_l})({v_l}) - ({dv_l})({u_l})}}{{({v_l})^2}}"
                    })
                elif f_expr.is_Add:
                    term_derivs = []
                    sub_rules = []
                    for arg in f_expr.args:
                        d_arg = sp.simplify(sp.diff(arg, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                        if arg.is_number:
                            sub_rules.append(fr"({sanitize_latex(arg)})' = 0")
                        else:
                            num_a, den_a = sp.fraction(arg)
                            if den_a != 1 and den_a.has(x_sym):
                                du_a = sp.simplify(sp.diff(num_a, x_sym))
                                dv_a = sp.simplify(sp.diff(den_a, x_sym))
                                sub_rules.append(fr"\left({sanitize_latex(arg)}\right)' = \frac{{({sanitize_latex(du_a)})({sanitize_latex(den_a)}) - ({sanitize_latex(dv_a)})({sanitize_latex(num_a)})}}{{({sanitize_latex(den_a)})^2}} = {sanitize_latex(d_arg)}")
                            else:
                                x_factors = [f for f in arg.as_ordered_factors() if f.has(x_sym)] if arg.is_Mul else []
                                if len(x_factors) >= 2:
                                    u_part = x_factors[0]
                                    v_part = sp.Mul(*x_factors[1:])
                                    c_part = sp.Mul(*[f for f in arg.as_ordered_factors() if not f.has(x_sym)])
                                    du_p = sp.simplify(sp.diff(u_part, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                                    dv_p = sp.simplify(sp.diff(v_part, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                                    c_str = "" if c_part == 1 else ("-" if c_part == -1 else sanitize_latex(c_part))
                                    sub_rules.append(fr"\left({sanitize_latex(arg)}\right)' = {c_str}\left[({sanitize_latex(du_p)})({sanitize_latex(v_part)}) + ({sanitize_latex(dv_p)})({sanitize_latex(u_part)})\right] = {sanitize_latex(d_arg)}")
                                else:
                                    sub_rules.append(fr"\left({sanitize_latex(arg)}\right)' = {sanitize_latex(d_arg)}")
                        if d_arg != 0:
                            term_derivs.append(d_arg)
                    
                    for idx_s, rule_str in enumerate(sub_rules):
                        steps.append({
                            'label': f'مشتق الحد ({idx_s + 1}):',
                            'math': rule_str
                        })
                    raw_sum = sp.Add(*term_derivs) if term_derivs else sp.Integer(0)
                    if sanitize_latex(raw_sum) != df_latex_str_safe:
                        steps.append({
                            'label': 'بجمع المشتقات الجزئية وتوحيد المقامات:',
                            'math': fr"f'(x) = {sanitize_latex(raw_sum)}"
                        })
                elif f_expr.is_Mul:
                    x_factors = [f for f in f_expr.as_ordered_factors() if f.has(x_sym)]
                    c_factors = [f for f in f_expr.as_ordered_factors() if not f.has(x_sym)]
                    if len(x_factors) >= 2:
                        u_p = x_factors[0] * sp.Mul(*c_factors)
                        v_p = sp.Mul(*x_factors[1:])
                        du_p = sp.simplify(sp.diff(u_p, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                        dv_p = sp.simplify(sp.diff(v_p, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                        steps.append({
                            'label': 'قانون مشتق جداء:',
                            'math': r"f'(x) = u'(x) \cdot v(x) + v'(x) \cdot u(x)"
                        })
                        steps.append({
                            'label': 'حساب المشتقات الجزئية:',
                            'math': fr"u(x) = {sanitize_latex(u_p)} \Rightarrow u'(x) = {sanitize_latex(du_p)} \quad , \quad v(x) = {sanitize_latex(v_p)} \Rightarrow v'(x) = {sanitize_latex(dv_p)}"
                        })
                        steps.append({
                            'label': 'بالتعويض في القانون:',
                            'math': fr"f'(x) = ({sanitize_latex(du_p)})({sanitize_latex(v_p)}) + ({sanitize_latex(dv_p)})({sanitize_latex(u_p)})"
                        })
                elif f_expr.func == sp.log and len(f_expr.args) > 0:
                    inner = f_expr.args[0]
                    d_in = sp.simplify(sp.diff(inner, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                    steps.append({
                        'label': 'قانون مشتق اللوغاريتم:',
                        'math': fr"f'(x) = \frac{{u'(x)}}{{u(x)}} = \frac{{({sanitize_latex(inner)})'}}{{{sanitize_latex(inner)}}} = \frac{{{sanitize_latex(d_in)}}}{{{sanitize_latex(inner)}}}"
                    })
                elif f_expr.func == sp.exp and len(f_expr.args) > 0:
                    inner = f_expr.args[0]
                    d_in = sp.simplify(sp.diff(inner, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                    steps.append({
                        'label': 'قانون مشتق الأسية:',
                        'math': fr"f'(x) = u'(x) \cdot e^{{u(x)}} = ({sanitize_latex(d_in)}) \cdot e^{{{sanitize_latex(inner)}}}"
                    })
                elif f_expr.func == sp.sqrt and len(f_expr.args) > 0:
                    inner = f_expr.args[0]
                    d_in = sp.simplify(sp.diff(inner, x_sym).replace(sp.sign, lambda a: a/sp.Abs(a)))
                    steps.append({
                        'label': 'قانون مشتق الجذر:',
                        'math': fr"f'(x) = \frac{{u'(x)}}{{2\sqrt{{u(x)}}}} = \frac{{{sanitize_latex(d_in)}}}{{2\sqrt{{{sanitize_latex(inner)}}}}}"
                    })
            except: pass
            return steps

        deriv_steps_detailed = build_derivative_steps()
        
        sym_extrema = []
        try:
            for r_simp in safe_solve_real(df_expr, x_sym):
                val_y_check = safe_float(f_expr.subs(x_sym, r_simp))
                if np.isfinite(val_y_check):
                    sym_extrema.append(r_simp)
        except: pass

        pts_var_exact = []
        pts_var_exact.append({'val': -np.inf, 'sym': -sp.oo, 'latex_x': r"-\infty", 'type': 'inf'})
        for r in candidate_v_asymptotes:
            pts_var_exact.append({'val': safe_float(r), 'sym': r, 'latex_x': sanitize_latex(r), 'type': 'v_asym'})
        for r in sym_extrema:
            val = safe_float(r)
            if np.isfinite(val) and not any(abs(p['val'] - val) < 1e-4 for p in pts_var_exact):
                pts_var_exact.append({'val': val, 'sym': r, 'latex_x': sanitize_latex(r), 'type': 'extrema'})

        is_valid_plot = ~np.isnan(y_vals_plot)
        edges = np.diff(is_valid_plot.astype(int))
        starts = np.where(edges == 1)[0] + 1
        if is_valid_plot[0]: starts = np.insert(starts, 0, 0)
        ends = np.where(edges == -1)[0]
        if is_valid_plot[-1]: ends = np.append(ends, len(y_vals_plot) - 1)

        numeric_extrema_x = []
        for s, e in zip(starts, ends):
            segment = y_vals_plot[s:e+1]
            seg_x = x_vals_plot[s:e+1]
            if len(segment) > 10:
                peaks, _ = find_peaks(segment, prominence=0.02)
                valleys, _ = find_peaks(-segment, prominence=0.02)
                for p in peaks: numeric_extrema_x.append(float(seg_x[p]))
                for v in valleys: numeric_extrema_x.append(float(seg_x[v]))
                
        for nx in numeric_extrema_x:
            if not any(abs(p['val'] - nx) < 0.1 for p in pts_var_exact):
                try:
                    sym_nx = sp.nsimplify(nx, tolerance=0.05)
                    y_val_fl = safe_float(f_expr.subs(x_sym, sym_nx))
                    if np.isfinite(y_val_fl):
                        pts_var_exact.append({'val': safe_float(sym_nx), 'sym': sym_nx, 'latex_x': sanitize_latex(sym_nx), 'type': 'extrema'})
                except: pass
                
        pts_var_exact.append({'val': np.inf, 'sym': sp.oo, 'latex_x': r"+\infty", 'type': 'inf'})
        pts_var_exact.sort(key=lambda p: p['val'])

        df_func_test = sp.lambdify(x_sym, df_expr, 'numpy')
        for p in pts_var_exact:
            if p['type'] == 'extrema':
                v_test = p['val']
                with np.errstate(all='ignore'):
                    df_val = df_func_test(v_test)
                    df_near_plus = df_func_test(v_test + 1e-4)
                    df_near_minus = df_func_test(v_test - 1e-4)
                diff_lr = abs(df_near_plus - df_near_minus) if (np.isfinite(df_near_plus) and np.isfinite(df_near_minus)) else 999.0
                if not np.isfinite(df_val) or abs(df_near_plus) > 20 or abs(df_near_minus) > 20 or diff_lr > 0.05:
                    p['type'] = 'corner'

        valid_intervals = []
        for i in range(len(pts_var_exact) - 1):
            left, right = pts_var_exact[i]['val'], pts_var_exact[i+1]['val']
            mid = 0 if (left == -np.inf and right == np.inf) else (right - 1 if left == -np.inf else (left + 1 if right == np.inf else (left + right) / 2.0))
            try:
                v_mid = f_func(mid)
                valid_intervals.append(not np.iscomplexobj(v_mid) and np.isfinite(float(v_mid)))
            except:
                valid_intervals.append(False)
            
        while len(valid_intervals) > 0 and not valid_intervals[0]:
            valid_intervals.pop(0); pts_var_exact.pop(0)
        while len(valid_intervals) > 0 and not valid_intervals[-1]:
            valid_intervals.pop(-1); pts_var_exact.pop(-1)

        domain_intervals_str = []
        i = 0
        while i < len(valid_intervals):
            if valid_intervals[i]:
                start_idx = i
                while i < len(valid_intervals) - 1 and valid_intervals[i+1] and pts_var_exact[i+1]['type'] != 'v_asym':
                    i += 1
                end_idx = i
                l_b = "-\infty" if pts_var_exact[start_idx]['val'] == -np.inf else pts_var_exact[start_idx]['latex_x']
                r_b = "+\infty" if pts_var_exact[end_idx+1]['val'] == np.inf else pts_var_exact[end_idx+1]['latex_x']
                domain_intervals_str.append(fr"]{l_b}; {r_b}[")
            i += 1
                
        domain_latex_st = r"D_f = \color{#FFD700}{" + (r" \cup ".join(domain_intervals_str) if domain_intervals_str else r"\emptyset") + r"}"
        domain_latex_mpl = r"D_f = " + (r" \cup ".join(domain_intervals_str) if domain_intervals_str else r"\emptyset")

        try:
            m_expr_list = sp.solve(f_expr - g_expr, m_sym)
            m_expr = m_expr_list[0] if m_expr_list else f_expr
        except:
            m_expr = f_expr

        m_critical_num = []
        sym_m_critical = []
        m_candidate_boundaries = list(candidate_v_asymptotes)
        try:
            n_expr, d_expr = sp.fraction(sp.cancel(m_expr))
            if d_expr != 1:
                for r in safe_solve_real(d_expr, x_sym):
                    if not any(abs(safe_float(r) - safe_float(b)) < 1e-4 for b in m_candidate_boundaries):
                        m_candidate_boundaries.append(r)
        except: pass

        try:
            for direction in [sp.oo, -sp.oo]:
                lim = sp.limit(m_expr, x_sym, direction)
                lim_fl = safe_float(lim)
                if np.isfinite(lim_fl):
                    m_critical_num.append(lim_fl)
                    sym_m_critical.append(sp.simplify(lim))
        except: pass

        exact_tangent_points = []
        for boundary in m_candidate_boundaries:
            for dir in ['+', '-']:
                try:
                    lim = sp.limit(m_expr, x_sym, boundary, dir=dir)
                    val_m = safe_float(lim)
                    if np.isfinite(val_m):
                        m_critical_num.append(val_m)
                        sym_m_critical.append(sp.simplify(lim))
                        try:
                            b_fl = safe_float(boundary)
                            val_f = f_func(b_fl)
                            if not np.iscomplexobj(val_f) and np.isfinite(float(val_f)):
                                exact_tangent_points.append({'x': b_fl, 'm_req': val_m})
                        except: pass
                except: pass

        try:
            val_0_sym = sp.simplify(m_expr.subs(x_sym, 0))
            val_0 = safe_float(val_0_sym)
            if np.isfinite(val_0):
                m_critical_num.append(val_0)
                sym_m_critical.append(val_0_sym)
        except: pass
        
        try:
            lim_0 = sp.limit(m_expr, x_sym, 0)
            lim_0_fl = safe_float(lim_0)
            if np.isfinite(lim_0_fl):
                m_critical_num.append(lim_0_fl)
                sym_m_critical.append(sp.simplify(lim_0))
        except: pass

        try:
            dm_expr = sp.diff(m_expr, x_sym)
            for r_simp in safe_solve_real(dm_expr, x_sym):
                try:
                    val_x = safe_float(r_simp)
                    val_f = f_func(val_x)
                    if np.isfinite(val_x) and not np.iscomplexobj(val_f) and np.isfinite(float(val_f)):
                        m_sub = sp.simplify(m_expr.subs(x_sym, r_simp))
                        val_m = safe_float(m_sub)
                        if np.isfinite(val_m):
                            exact_tangent_points.append({'x': val_x, 'm_req': val_m})
                            m_critical_num.append(val_m)
                            sym_m_critical.append(m_sub)
                except: pass
        except: pass

        try:
            m_func_eval = sp.lambdify(x_sym, m_expr, 'numpy')
            x_test_m = np.linspace(-25, 25, 10001)
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                y_test_m = m_func_eval(x_test_m)
                if np.iscomplexobj(y_test_m): y_test_m = np.where(np.isreal(y_test_m), y_test_m.real, np.nan)
                
            is_val_m = np.isfinite(y_test_m)
            edges_m = np.diff(is_val_m.astype(int))
            starts_m = np.where(edges_m == 1)[0] + 1
            if is_val_m[0]: starts_m = np.insert(starts_m, 0, 0)
            ends_m = np.where(edges_m == -1)[0]
            if is_val_m[-1]: ends_m = np.append(ends_m, len(y_test_m) - 1)

            for s, e in zip(starts_m, ends_m):
                segment = y_test_m[s:e+1]
                seg_x = x_test_m[s:e+1]
                if len(segment) > 10:
                    peaks, _ = find_peaks(segment, prominence=0.05)
                    valleys, _ = find_peaks(-segment, prominence=0.05)
                    for p in peaks:
                        val_x = float(seg_x[p])
                        val_m = float(segment[p])
                        if not any(abs(val_x - tp['x']) < 0.1 for tp in exact_tangent_points):
                            exact_tangent_points.append({'x': val_x, 'm_req': val_m})
                        m_critical_num.append(val_m)
                    for v in valleys:
                        val_x = float(seg_x[v])
                        val_m = float(segment[v])
                        if not any(abs(val_x - tp['x']) < 0.1 for tp in exact_tangent_points):
                            exact_tangent_points.append({'x': val_x, 'm_req': val_m})
                        m_critical_num.append(val_m)
        except: pass

        for asym in unique_asymptotes:
            if asym['type'] == 'h': m_critical_num.append(asym['val'])

        m_critical_num = sorted(list(set([round(m, 3) for m in m_critical_num if np.isfinite(m) and abs(m) < 100])))
        
        m_min_val, m_max_val = -6.0, 6.0
        if m_critical_num:
            if m_critical_num[0] - 1.5 < m_min_val: m_min_val = float(np.floor(m_critical_num[0] - 1.5))
            if m_critical_num[-1] + 1.5 > m_max_val: m_max_val = float(np.ceil(m_critical_num[-1] + 1.5))
        m_min_val = float(max(-25.0, m_min_val))
        m_max_val = float(min(25.0, m_max_val))

        def exactify_value(val_float, sym_val=None):
            if sym_val is not None:
                try:
                    sym_val = sp.simplify(sym_val)
                    s_str = str(sym_val)
                    if not any(bad in s_str for bad in ["LambertW", "RootOf", "Integral", "zoo", "I"]):
                        l_str = sanitize_latex(sym_val)
                        if len(l_str) < 25: return l_str
                except: pass
            if abs(val_float - np.e) < 1e-2: return "e"
            if abs(val_float + np.e) < 1e-2: return "-e"
            if abs(val_float - 1/np.e) < 1e-2: return r"\frac{1}{e}"
            if abs(val_float + 1/np.e) < 1e-2: return r"-\frac{1}{e}"
            if abs(val_float - np.pi) < 1e-2: return r"\pi"
            if abs(val_float + np.pi) < 1e-2: return r"-\pi"
            if abs(val_float - np.e**2) < 1e-2: return "e^2"
            if abs(val_float + np.e**2) < 1e-2: return "-e^2"
            if abs(val_float - 2*np.e) < 1e-2: return "2e"
            if abs(val_float + 2*np.e) < 1e-2: return "-2e"
            if abs(val_float - int(round(val_float))) < 1e-2: return str(int(round(val_float)))
            return str(round(val_float, 2)).rstrip('0').rstrip('.') if '.' in str(round(val_float, 2)) else str(round(val_float, 2))

        def get_exact_m(val_float):
            for sm in sym_m_critical:
                try:
                    sm_fl = safe_float(sm)
                    if np.isfinite(sm_fl) and abs(sm_fl - val_float) < 1e-2:
                        res = exactify_value(val_float, sm)
                        if not re.match(r'^-?\d+(\.\d+)?$', res): return res
                except: pass
            return exactify_value(val_float)

        def is_valid_root(x_val):
            if any(abs(x_val - safe_float(a['val'])) < 1e-3 for a in unique_asymptotes if a['type'] == 'v'): return False
            if any(abs(x_val - h['val']) < 1e-3 for h in holes): return False
            try:
                with np.errstate(all='ignore'): v = f_func(x_val)
                if isinstance(v, complex) or np.iscomplexobj(v): return False
                if not np.isfinite(float(v)): return False
                return True
            except: return False

        def get_roots_text(m_test):
            is_critical = any(abs(m_test - mc) < 1e-2 for mc in m_critical_num)
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                y_g = g_func(x_vals_roots, m_test)
                if np.isscalar(y_g): y_g = np.full_like(x_vals_roots, y_g, dtype=float)
                diff = y_vals_roots - y_g
                
            crossings = []
            for i in range(len(diff)-1):
                if np.isfinite(diff[i]) and np.isfinite(diff[i+1]):
                    if diff[i] * diff[i+1] < 0:
                        denom = diff[i+1] - diff[i]
                        x_c = x_vals_roots[i] - diff[i] * (x_vals_roots[i+1] - x_vals_roots[i]) / denom
                        if is_valid_root(x_c): crossings.append(float(x_c))
                    elif diff[i] == 0:
                        if i == 0 or diff[i-1] != 0:
                            j = i
                            while j < len(diff) and diff[j] == 0: j += 1
                            if j - i < 5: 
                                x_c = x_vals_roots[i]
                                if is_valid_root(x_c): crossings.append(float(x_c))
            if len(diff) > 0 and diff[-1] == 0 and diff[-2] != 0:
                x_c = x_vals_roots[-1]
                if is_valid_root(x_c): crossings.append(float(x_c))
                
            tangents = []
            cleaned_crossings = []
            if is_critical:
                skip = False
                for i in range(len(crossings)):
                    if skip: skip = False; continue
                    if i < len(crossings)-1 and abs(crossings[i+1] - crossings[i]) < 0.5:
                        tangents.append((crossings[i] + crossings[i+1])/2.0); skip = True
                    else: cleaned_crossings.append(crossings[i])
                for tp in exact_tangent_points:
                    if abs(tp['m_req'] - m_test) < 0.05:
                        if is_valid_root(tp['x']):
                            if not any(abs(tp['x'] - c) < 0.6 for c in cleaned_crossings) and not any(abs(tp['x'] - t) < 0.6 for t in tangents):
                                tangents.append(tp['x'])
            else: cleaned_crossings = crossings
                
            all_roots = [(c, "single") for c in cleaned_crossings] + [(t, "double") for t in tangents]
            final_roots = []
            for r, t in all_roots:
                if not any(abs(r - fr[0]) < 0.1 for fr in final_roots): final_roots.append((r, t))
            
            count = len(final_roots)
            if count == 0: return "لا توجد حلول"
            
            desc = []
            pos_s = sum(1 for r, t in final_roots if r > 0.01 and t == "single")
            neg_s = sum(1 for r, t in final_roots if r < -0.01 and t == "single")
            zero_s = sum(1 for r, t in final_roots if abs(r) <= 0.01 and t == "single")
            pos_d = sum(1 for r, t in final_roots if r > 0.01 and t == "double")
            neg_d = sum(1 for r, t in final_roots if r < -0.01 and t == "double")
            zero_d = sum(1 for r, t in final_roots if abs(r) <= 0.01 and t == "double")

            if pos_d == 1 and neg_d == 1: desc.append("حلان مضاعفان (أحدهما موجب والآخر سالب)")
            else:
                if pos_d == 1: desc.append("حل مضاعف موجب")
                elif pos_d > 1: desc.append(f"{pos_d} حلول مضاعفة موجبة")
                if neg_d == 1: desc.append("حل مضاعف سالب")
                elif neg_d > 1: desc.append(f"{neg_d} حلول مضاعفة سالبة")
                if zero_d == 1: desc.append("حل مضاعف معدوم")
                
            if pos_s == 1: desc.append("حل وحيد موجب")
            elif pos_s == 2: desc.append("حلان موجبان")
            elif pos_s > 2: desc.append(f"{pos_s} حلول موجبة")
            if neg_s == 1: desc.append("حل وحيد سالب")
            elif neg_s == 2: desc.append("حلان سالبان")
            elif neg_s > 2: desc.append(f"{neg_s} حلول سالبة")
            if zero_s == 1: desc.append("حل معدوم")

            if pos_s == 1 and neg_s == 1 and len(desc) == 2: return "حلان مختلفان في الإشارة"
            if pos_s == 2 and neg_s == 1 and pos_d == 0 and len(desc) == 2: return "ثلاثة حلول: حل سالب وحلان موجبان"
            if pos_s == 1 and neg_s == 2 and pos_d == 0 and len(desc) == 2: return "ثلاثة حلول: حل موجب وحلان سالبان"
            if pos_s == 1 and zero_s == 1 and len(desc) == 2: return "حل معدوم و حل موجب"
            if neg_s == 1 and zero_s == 1 and len(desc) == 2: return "حل معدوم و حل سالب"
            if len(desc) == 0: return f"{count} حلول"
            return " و ".join(desc)

        raw_intervals = []
        if len(m_critical_num) > 0:
            raw_intervals.append((float('-inf'), m_critical_num[0], get_roots_text(m_critical_num[0] - 0.5)))
            for i in range(len(m_critical_num)):
                raw_intervals.append((m_critical_num[i], m_critical_num[i], get_roots_text(m_critical_num[i])))
                if i < len(m_critical_num) - 1:
                    raw_intervals.append((m_critical_num[i], m_critical_num[i+1], get_roots_text((m_critical_num[i] + m_critical_num[i+1]) / 2.0)))
            raw_intervals.append((m_critical_num[-1], float('inf'), get_roots_text(m_critical_num[-1] + 0.5)))
        else: raw_intervals.append((float('-inf'), float('inf'), get_roots_text(0.0)))

        final_table = [] 
        for L, H, sol_text in raw_intervals:
            L_latex = r"-\infty" if L == float('-inf') else get_exact_m(L)
            H_latex = r"+\infty" if H == float('inf') else get_exact_m(H)
            if L == float('-inf') and H == float('inf'): m_latex = r"m \in \mathbb{R}"
            elif L == float('-inf'): m_latex = fr"m \in ]-\infty ; {H_latex}["
            elif H == float('inf'): m_latex = fr"m \in ]{L_latex} ; +\infty["
            elif L == H: m_latex = fr"m = {L_latex}"
            else: m_latex = fr"m \in ]{L_latex} ; {H_latex}["
            final_table.append((m_latex, sol_text, L, H))

        N = len(pts_var_exact)
        def generate_variation_table_image():
            if N < 2: return None
            col_w = 2.8; x_start_data = 2.0; x_max = x_start_data + N * col_w
            fig_v, ax_v = plt.subplots(figsize=(max(8, N*2.5), 3.5))
            ax_v.axis('off')
            ax_v.plot([0, x_max], [6, 6], 'k-', lw=2, zorder=2)
            ax_v.plot([0, x_max], [5, 5], 'k-', lw=1.5, zorder=2)
            ax_v.plot([0, x_max], [4, 4], 'k-', lw=1.5, zorder=2)
            ax_v.plot([0, x_max], [0, 0], 'k-', lw=2, zorder=2)
            ax_v.plot([0, 0], [0, 6], 'k-', lw=2, zorder=2)
            ax_v.plot([x_start_data, x_start_data], [0, 6], 'k-', lw=2, zorder=2)
            ax_v.plot([x_max, x_max], [0, 6], 'k-', lw=2, zorder=2)
            ax_v.text(x_start_data / 2, 5.5, '$x$', ha='center', va='center', fontsize=20, color='#1565C0', fontweight='bold')
            ax_v.text(x_start_data / 2, 4.5, "$f'(x)$", ha='center', va='center', fontsize=20, color='#1565C0', fontweight='bold')
            ax_v.text(x_start_data / 2, 2.0, '$f(x)$', ha='center', va='center', fontsize=20, color='#1565C0', fontweight='bold')
            
            signs = []
            for i in range(N - 1):
                left, right = pts_var_exact[i]['val'], pts_var_exact[i+1]['val']
                mid = 0 if (left == -np.inf and right == np.inf) else (right - 1 if left == -np.inf else (left + 1 if right == np.inf else (left + right) / 2.0))
                try:
                    if not np.isfinite(float(f_func(mid))): signs.append(None)
                    else: signs.append("+" if f_func(mid + 1e-5) > f_func(mid) else "-")
                except: signs.append(None)
                    
            nodes = []
            for i in range(N):
                p = pts_var_exact[i]
                x_c = x_start_data + (col_w / 2.0) + i * col_w 
                ax_v.text(x_c, 5.5, f"${p['latex_x']}$", ha='center', va='center', fontsize=18)
                if p['type'] == 'v_asym':
                    ax_v.plot([x_c-0.05, x_c-0.05], [0, 5], 'k-', lw=1.5, zorder=2)
                    ax_v.plot([x_c+0.05, x_c+0.05], [0, 5], 'k-', lw=1.5, zorder=2)
                elif p['type'] == 'extrema':
                    ax_v.plot([x_c, x_c], [4, 5], 'k-', lw=1.2, zorder=2)
                    ax_v.text(x_c, 4.5, '0', ha='center', va='center', fontsize=16)
                elif p['type'] == 'corner': 
                    ax_v.plot([x_c-0.04, x_c-0.04], [4, 5], 'k-', lw=1.5, zorder=2)
                    ax_v.plot([x_c+0.04, x_c+0.04], [4, 5], 'k-', lw=1.5, zorder=2)
                if i < N - 1:
                    x_ic = x_c + (col_w / 2.0)
                    if not valid_intervals[i]:
                        rect = plt.Rectangle((x_c, 0), col_w, 5, facecolor='#EF4444', alpha=0.7, zorder=1)
                        ax_v.add_patch(rect)
                    else:
                        ax_v.text(x_ic, 4.5, f"${signs[i]}$", ha='center', va='center', fontsize=26, color='#D32F2F' if signs[i]=='-' else '#2E7D32')
                if p['type'] == 'inf':
                    try:
                        lim = sp.limit(f_expr, x_sym, p['sym'])
                        dx = 0.5 if p['val'] == -np.inf else -0.5
                        nodes.append((x_c+dx, safe_float(lim), format_lim_val(lim)))
                    except: pass
                elif p['type'] == 'v_asym':
                    if i > 0 and valid_intervals[i-1]:
                        try:
                            lim_l = sp.limit(f_expr, x_sym, p['sym'], dir='-')
                            nodes.append((x_c-0.4, safe_float(lim_l), format_lim_val(lim_l)))
                        except: pass
                    if i < N-1 and valid_intervals[i]:
                        try:
                            lim_r = sp.limit(f_expr, x_sym, p['sym'], dir='+')
                            nodes.append((x_c+0.4, safe_float(lim_r), format_lim_val(lim_r)))
                        except: pass
                elif p['type'] in ['extrema', 'corner']:
                    try:
                        sym_y = sp.simplify(f_expr.subs(x_sym, p['sym']))
                        val_y = safe_float(sym_y)
                        nodes.append((x_c, val_y, exactify_value(val_y, sym_y)))
                    except: pass

            drawn_nodes = set()
            for i in range(N - 1):
                if valid_intervals[i]:
                    x_c_left = x_start_data + (col_w / 2.0) + i * col_w
                    x_c_right = x_start_data + (col_w / 2.0) + (i+1) * col_w
                    l_node = next((n for n in nodes if n[0] >= x_c_left and n[0] <= x_c_left + 0.7), None)
                    r_node = next((n for n in nodes if n[0] >= x_c_right - 0.7 and n[0] <= x_c_right), None)
                    if l_node and r_node:
                        is_left_inflection = (i > 0 and valid_intervals[i-1] and signs[i-1] == signs[i] and pts_var_exact[i]['type'] == 'extrema')
                        is_right_inflection = (i < N - 2 and valid_intervals[i+1] and signs[i] == signs[i+1] and pts_var_exact[i+1]['type'] == 'extrema')
                        
                        y_l = 2.0 if is_left_inflection else (0.8 if signs[i] == "+" else 3.2)
                        y_r = 2.0 if is_right_inflection else (3.2 if signs[i] == "+" else 0.8)
                        
                        if l_node[0] not in drawn_nodes:
                            try:
                                ax_v.text(l_node[0], y_l, f"${l_node[2]}$", ha='center', va='center', fontsize=18, color='#D32F2F', fontweight='bold')
                                drawn_nodes.add(l_node[0])
                            except: pass
                        if r_node[0] not in drawn_nodes:
                            try:
                                ax_v.text(r_node[0], y_r, f"${r_node[2]}$", ha='center', va='center', fontsize=18, color='#D32F2F', fontweight='bold')
                                drawn_nodes.add(r_node[0])
                            except: pass
                        
                        pad_x, pad_y = 0.35, 0.35
                        start_x, end_x = l_node[0] + pad_x, r_node[0] - pad_x
                        slope_up = (y_r > y_l)
                        start_y = y_l + (pad_y if slope_up else -pad_y)
                        end_y = y_r + (-pad_y if slope_up else pad_y)
                        if y_l == y_r: start_y = end_y = y_l
                        ax_v.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=2.5))
            ax_v.set_xlim(0, x_max); ax_v.set_ylim(0, 6)
            try:
                fig_v.tight_layout(pad=0.2)
                tmp_v = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                fig_v.savefig(tmp_v.name, bbox_inches='tight', dpi=300)
                plt.close(fig_v)
                return tmp_v.name
            except Exception as e:
                plt.close(fig_v)
                return None

        var_table_image_path = generate_variation_table_image()
        
        limits_data_detailed = []
        limits_mpl_items = [{'type': 'domain', 'latex': domain_latex_mpl}]

        def build_limit_steps(val_sym, dir_sympy, target_latex, arrow_latex):
            steps_math = []
            try:
                num, den = sp.fraction(f_expr)
                if den != 1 and not den.is_number:
                    l_num = sp.limit(num, x_sym, val_sym, dir=dir_sympy)
                    l_den = sp.limit(den, x_sym, val_sym, dir=dir_sympy)
                    l_num_s = format_lim_val(l_num)
                    l_den_s = format_lim_val(l_den)
                    if l_den == 0 and val_sym not in [sp.oo, -sp.oo]:
                        try:
                            eps = 1e-5 if dir_sympy == '+' else -1e-5
                            d_val = safe_float(den.subs(x_sym, safe_float(val_sym) + eps))
                            l_den_s = "0^+" if d_val > 0 else "0^-"
                        except: pass
                    steps_math.append(fr"\lim_{{x {arrow_latex} {target_latex}}} \left({sanitize_latex(num)}\right) = {l_num_s} \quad , \quad \lim_{{x {arrow_latex} {target_latex}}} \left({sanitize_latex(den)}\right) = {l_den_s}")
                
                elif f_expr.is_Add:
                    sub_parts = []
                    has_pos_inf, has_neg_inf = False, False
                    for arg in f_expr.args:
                        if not arg.is_number:
                            l_p = sp.limit(arg, x_sym, val_sym, dir=dir_sympy)
                            if l_p == sp.oo: has_pos_inf = True
                            if l_p == -sp.oo: has_neg_inf = True
                            sub_parts.append(fr"\lim_{{x {arrow_latex} {target_latex}}} \left({sanitize_latex(arg)}\right) = {format_lim_val(l_p)}")
                    if has_pos_inf and has_neg_inf:
                        try:
                            fact = sp.factor(f_expr)
                            if fact != f_expr:
                                l_tot = format_lim_val(sp.limit(f_expr, x_sym, val_sym, dir=dir_sympy))
                                steps_math.append(fr"\lim_{{x {arrow_latex} {target_latex}}} \left({sanitize_latex(fact)}\right) = {l_tot}")
                        except: pass
                    if sub_parts:
                        steps_math.append(r" \quad , \quad ".join(sub_parts[:3]))

                elif f_expr.func in [sp.log, sp.exp, sp.sqrt] and len(f_expr.args) > 0:
                    inner = f_expr.args[0]
                    l_in = sp.limit(inner, x_sym, val_sym, dir=dir_sympy)
                    l_in_s = "0^+" if (l_in == 0 and f_expr.func == sp.log) else format_lim_val(l_in)
                    steps_math.append(fr"\lim_{{x {arrow_latex} {target_latex}}} \left({sanitize_latex(inner)}\right) = {l_in_s}")

                elif f_expr.is_Mul:
                    sub_parts = []
                    for arg in f_expr.args:
                        if not arg.is_number:
                            l_p = sp.limit(arg, x_sym, val_sym, dir=dir_sympy)
                            sub_parts.append(fr"\lim_{{x {arrow_latex} {target_latex}}} \left({sanitize_latex(arg)}\right) = {format_lim_val(l_p)}")
                    if sub_parts:
                        steps_math.append(r" \quad , \quad ".join(sub_parts[:3]))
            except: pass
            return steps_math

        def add_limit(val_sym, dir_sympy, target_latex, arrow_latex=r"\to"):
            try:
                lim = sp.limit(f_expr, x_sym, val_sym, dir=dir_sympy)
                lim_latex = format_lim_val(lim)
                expr_latex = sanitize_latex(f_expr)
                
                steps_list = build_limit_steps(val_sym, dir_sympy, target_latex, arrow_latex)
                
                latex_streamlit = fr"\lim_{{x {arrow_latex} {target_latex}}} f(x) = \lim_{{x {arrow_latex} {target_latex}}} \left( {expr_latex} \right) = \mathbf{{\color{{#EF4444}}{{{lim_latex}}}}}"
                limits_data_detailed.append({'main': latex_streamlit, 'steps': steps_list})
                
                lhs_mpl = fr"\lim_{{x {arrow_latex} {target_latex}}} f(x) = \lim_{{x {arrow_latex} {target_latex}}} \left( {expr_latex} \right) ="
                rhs_mpl = fr"{lim_latex}"
                limits_mpl_items.append({'type': 'main', 'lhs': lhs_mpl, 'rhs': rhs_mpl})
                
                for stp in steps_list:
                    limits_mpl_items.append({'type': 'step', 'math': stp})
            except: pass

        if len(pts_var_exact) > 0:
            if valid_intervals and valid_intervals[0]:
                if pts_var_exact[0]['sym'] == -sp.oo: add_limit(-sp.oo, '+', r"-\infty", r"\to")
            if valid_intervals and valid_intervals[-1]:
                if pts_var_exact[-1]['sym'] == sp.oo: add_limit(sp.oo, '-', r"+\infty", r"\to")
            for i, p in enumerate(pts_var_exact):
                if p['type'] == 'v_asym':
                    v_latex = p['latex_x']
                    if i > 0 and valid_intervals[i-1]: add_limit(p['sym'], '-', v_latex, r"\overset{<}{\to}")
                    if i < len(valid_intervals) and valid_intervals[i]: add_limit(p['sym'], '+', v_latex, r"\overset{>}{\to}")

        def generate_limits_image():
            n_lines = len(limits_mpl_items)
            fig_l, ax_l = plt.subplots(figsize=(9, max(2.0, n_lines * 0.75)))
            ax_l.axis('off')
            ax_l.set_xlim(0, 10)
            ax_l.set_ylim(0, n_lines)
            
            for i, item in enumerate(limits_mpl_items):
                y_pos = n_lines - i - 0.5
                try:
                    if item['type'] == 'domain':
                        ax_l.text(5.0, y_pos, f"${item['latex']}$", fontsize=20, ha='center', va='center', color='#1E3A8A', fontweight='bold')
                    elif item['type'] == 'main':
                        ax_l.text(7.2, y_pos, f"${item['lhs']}$", fontsize=18, ha='right', va='center', color='#1E3A8A')
                        ax_l.text(7.4, y_pos, f"${item['rhs']}$", fontsize=20, ha='left', va='center', color='#D32F2F', fontweight='bold')
                    elif item['type'] == 'step':
                        ax_l.text(9.6, y_pos, fix_arabic_mpl("لأن:"), fontsize=14, ha='right', va='center', color='#D97706', fontweight='bold')
                        ax_l.text(8.8, y_pos, f"$({item['math']})$", fontsize=14, ha='right', va='center', color='#6D28D9')
                except:
                    pass
            
            try:
                fig_l.tight_layout(pad=0.2)
            except: pass
            tmp_l = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig_l.savefig(tmp_l.name, bbox_inches='tight', dpi=300)
            plt.close(fig_l)
            return tmp_l.name

        limits_image_path = generate_limits_image()

        def generate_deriv_image():
            n_lines = len(deriv_steps_detailed) + 1
            fig_d, ax_d = plt.subplots(figsize=(9, max(1.6, n_lines * 0.8)))
            ax_d.axis('off')
            ax_d.set_xlim(0, 10)
            ax_d.set_ylim(0, n_lines)
            
            for i, stp in enumerate(deriv_steps_detailed):
                y_pos = n_lines - i - 0.5
                try:
                    ax_d.text(9.7, y_pos, fix_arabic_mpl(stp['label']), fontsize=13, ha='right', va='center', color='#D97706', fontweight='bold')
                    ax_d.text(7.1, y_pos, f"${stp['math']}$", fontsize=14, ha='right', va='center', color='#0F766E')
                except:
                    pass
            
            y_final = 0.5
            math_str = fr"f'(x) = {df_latex_str_safe}"
            try:
                ax_d.text(9.7, y_final, fix_arabic_mpl("العبارة النهائية:"), fontsize=14, ha='right', va='center', color='#2E7D32', fontweight='bold')
                ax_d.text(7.1, y_final, f"${math_str}$", fontsize=18, ha='right', va='center', color='#15803D', fontweight='bold')
            except:
                safe_str = str(df_simp).replace('**', '^')
                ax_d.text(5.0, y_final, f"f'(x) = {safe_str}", fontsize=16, ha='center', va='center', color='#15803D', family='serif')
                
            try:
                fig_d.tight_layout(pad=0.2)
            except: pass
            tmp_d = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig_d.savefig(tmp_d.name, bbox_inches='tight', dpi=300)
            plt.close(fig_d)
            return tmp_d.name
            
        deriv_image_path = generate_deriv_image()
        
        def generate_eq_image():
            math_str = fr"f(x) = {sanitize_latex(g_expr)}"
            fig_e, ax_e = plt.subplots(figsize=(8, 0.7))
            fig_e.patch.set_facecolor('#FFFFFF')
            ax_e.set_facecolor('#FFFFFF')
            ax_e.axis('off')
            try:
                ax_e.text(0.5, 0.5, f"${math_str}$", fontsize=22, ha='center', va='center', color='#1E3A8A', fontweight='bold')
                fig_e.canvas.draw()
                fig_e.tight_layout(pad=0)
            except:
                ax_e.clear()
                ax_e.axis('off')
                ax_e.text(0.5, 0.5, f"f(x) = {current_g}", fontsize=18, ha='center', va='center', color='#1E3A8A')
                try: fig_e.tight_layout(pad=0)
                except: pass
            tmp_e = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig_e.savefig(tmp_e.name, bbox_inches='tight', dpi=300)
            plt.close(fig_e)
            return tmp_e.name
            
        eq_image_path = generate_eq_image()

        def generate_pdf_discussion_table():
            nrows = len(final_table)
            fig_dt, ax_dt = plt.subplots(figsize=(10, nrows * 0.7 + 0.8))
            def draw_table(use_math=True):
                ax_dt.clear()
                ax_dt.axis('off')
                ax_dt.set_xlim(-0.05, 10.05)
                ax_dt.set_ylim(-0.05, nrows * 0.7 + 0.75)
                for i in range(nrows + 1):
                    y = i * 0.7
                    ax_dt.plot([0, 10], [y, y], 'k-', lw=1 if 0 < i < nrows else 2)
                ax_dt.plot([0, 0], [0, nrows * 0.7], 'k-', lw=2)
                ax_dt.plot([6, 6], [0, nrows * 0.7], 'k-', lw=1) 
                ax_dt.plot([10, 10], [0, nrows * 0.7], 'k-', lw=2)
                ax_dt.plot([0, 10], [nrows * 0.7, nrows * 0.7], 'k-', lw=2)
                ax_dt.plot([0, 10], [nrows * 0.7 + 0.7, nrows * 0.7 + 0.7], 'k-', lw=2)
                ax_dt.plot([0, 0], [nrows * 0.7, nrows * 0.7 + 0.7], 'k-', lw=2)
                ax_dt.plot([6, 6], [nrows * 0.7, nrows * 0.7 + 0.7], 'k-', lw=2)
                ax_dt.plot([10, 10], [nrows * 0.7, nrows * 0.7 + 0.7], 'k-', lw=2)
                
                rect1 = plt.Rectangle((0, nrows * 0.7), 6, 0.7, facecolor='#1E3A8A')
                rect2 = plt.Rectangle((6, nrows * 0.7), 4, 0.7, facecolor='#1E3A8A')
                ax_dt.add_patch(rect1)
                ax_dt.add_patch(rect2)
                ax_dt.text(3, nrows * 0.7 + 0.35, fix_arabic_mpl("عدد و إشارة حلول المعادلة"), color='white', fontsize=15, fontweight='bold', ha='center', va='center')
                ax_dt.text(8, nrows * 0.7 + 0.35, fix_arabic_mpl("المجال / القيمة المضبوطة"), color='white', fontsize=16, fontweight='bold', ha='center', va='center')
                for i, (m_latex, sol_text, L, H) in enumerate(final_table):
                    y_center = (nrows - i - 1) * 0.7 + 0.35
                    c_pdf = get_sol_color_pdf(sol_text)
                    f_size = 14 if len(sol_text) > 35 else 16 
                    ax_dt.text(3, y_center, fix_arabic_mpl(sol_text), fontsize=f_size, ha='center', va='center', color=c_pdf, fontweight='bold')
                    if use_math:
                        ax_dt.text(8, y_center, f"${m_latex}$", fontsize=16, ha='center', va='center', color='#1E3A8A')
                    else:
                        plain_text = m_latex.replace(r'\infty', 'oo').replace(r'\in', ' in ').replace(r'\\', '')
                        plain_text = plain_text.replace('{', '').replace('}', '')
                        ax_dt.text(8, y_center, plain_text, fontsize=14, ha='center', va='center', color='#1E3A8A', family='serif')

            try:
                draw_table(use_math=True)
                fig_dt.canvas.draw()
                fig_dt.tight_layout(pad=0)
            except:
                draw_table(use_math=False)
                try: 
                    fig_dt.tight_layout(pad=0)
                except: 
                    pass
            tmp_dt = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig_dt.savefig(tmp_dt.name, bbox_inches='tight', dpi=300)
            plt.close(fig_dt)
            return tmp_dt.name
            
        disc_table_img_path = generate_pdf_discussion_table()

        cache.update({
            'valid': True,
            'f_func': f_func,
            'g_func': g_func,
            'x_vals_plot': x_vals_plot,
            'y_vals_plot': y_vals_plot,
            'unique_asymptotes': unique_asymptotes,
            'holes': holes,
            'm_critical_num': m_critical_num,
            'final_table': final_table,
            'domain_latex_st': domain_latex_st,
            'limits_data_detailed': limits_data_detailed,
            'deriv_steps_detailed': deriv_steps_detailed,
            'df_latex_str_safe': df_latex_str_safe,
            'var_table_image_path': var_table_image_path,
            'limits_image_path': limits_image_path,
            'deriv_image_path': deriv_image_path,
            'eq_image_path': eq_image_path,
            'disc_table_img_path': disc_table_img_path,
            'm_min_val': m_min_val,
            'm_max_val': m_max_val,
            'f_expr': f_expr,
            'g_expr': g_expr,
        })
    except Exception as e:
        cache['error'] = str(e)
    return cache

if 'math_cache' not in st.session_state or st.session_state.get('last_f') != current_f or st.session_state.get('last_g') != current_g or st.session_state.get('cache_ver') != "v8":
    with st.spinner("جاري التحليل الرياضي الدقيق (تتم هذه العملية مرة واحدة لتسريع حركة المناقشة الآلية)..."):
        st.session_state.math_cache = build_math_context(current_f, current_g, "v8")
        st.session_state.last_f = current_f
        st.session_state.last_g = current_g
        st.session_state.cache_ver = "v8"

cache = st.session_state.math_cache

if not cache.get('valid'):
    st.error(f"⚠️ صيغة غير صالحة أو الخانة فارغة. حاول كتابة الدالة بصيغة رياضية صحيحة.")
else:
    st.latex(rf"\color{{#FFD700}} \begin{{cases}} f(x) = {sanitize_latex(cache['f_expr'])} \\ y = {sanitize_latex(cache['g_expr'])} \end{{cases}}")

    m_min_val = cache['m_min_val']
    m_max_val = cache['m_max_val']
    m_critical_num = cache['m_critical_num']

    st.write("") 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("تشغيل المناقشة آلياً ▶️", disabled=st.session_state.auto_play):
            st.session_state.auto_play = True
            st.session_state.m_anim = m_min_val
            st.rerun()
    with col2:
        if st.button("إيقاف ⏹", disabled=not st.session_state.auto_play):
            st.session_state.auto_play = False
            st.rerun()
    
    m_val_manual = st.slider("تحكم يدوي:", m_min_val, m_max_val, m_min_val, 0.05, format="%g", key="manual_m", disabled=st.session_state.auto_play)

    anim_placeholder = st.empty()
    table_placeholder = st.empty()

    def generate_st_markdown_table(current_m):
        md = "| عدد و إشارة حلول المعادلة | المجال / القيمة المضبوطة |\n"
        md += "| :---: | :---: |\n"
        active_idx = 0
        for idx, (m_latex, sol_text, L, H) in enumerate(cache['final_table']):
            is_active = False
            if L == H and abs(current_m - L) <= 0.03: is_active = True
            elif L == float('-inf') and current_m <= H - 0.03: is_active = True
            elif H == float('inf') and current_m >= L + 0.03: is_active = True
            elif L + 0.03 <= current_m <= H - 0.03: is_active = True
            if is_active: active_idx = idx

        for idx, (m_latex, sol_text, L, H) in enumerate(cache['final_table']):
            is_active = (idx == active_idx)
            c_text = get_sol_color_html(sol_text)
            if is_active:
                text_cell = f"<span style='display:inline-block; width:90%; background-color:#334155; border:2px solid #FFD700; padding:4px; border-radius:6px; color:{c_text}; font-weight:bold; font-size:17px;'>{sol_text}</span>"
                math_cell = f"<span style='display:inline-block; width:90%; background-color:#334155; border:2px solid #FFD700; padding:4px; border-radius:6px; white-space:nowrap; font-size:16px;'>**${m_latex}$**</span>"
            else:
                text_cell = f"<span style='color:{c_text}; font-weight:bold; font-size:17px;'>{sol_text}</span>"
                math_cell = f"<span style='white-space:nowrap; font-size:16px;'>${m_latex}$</span>"
            md += f"| {text_cell} | {math_cell} |\n"
        return md

    def draw_plot(m_val, mode='dark'):
        fig, ax = plt.subplots(figsize=(10, 6.5))
        if mode == 'dark':
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#0F172A')
            ax.tick_params(colors='#E2E8F0', labelsize=9)
            for spine in ax.spines.values(): spine.set_edgecolor('#475569')
            ax.axhline(0, color='#E2E8F0', linewidth=2.5, zorder=3)
            ax.axvline(0, color='#E2E8F0', linewidth=2.5, zorder=3)
            ax.minorticks_on()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
            ax.grid(True, which='major', color='#475569', linestyle='-', linewidth=1.2, zorder=1)
            ax.grid(True, which='minor', color='#1E293B', linestyle='-', linewidth=0.8, zorder=1)
            c_asym, c_cf, c_cg, c_pts, c_text, bg_leg, edge_leg = '#F472B6', '#00E5FF', '#FFD700', '#EF4444', '#E2E8F0', '#1E293B', '#475569'
        else:
            fig.patch.set_facecolor('#FFFFFF')
            ax.set_facecolor('#FFFFFF')
            ax.tick_params(colors='black', labelsize=9)
            for spine in ax.spines.values(): spine.set_edgecolor('#A0A0A0')
            ax.axhline(0, color='black', linewidth=2, zorder=3)
            ax.axvline(0, color='black', linewidth=2, zorder=3)
            ax.minorticks_on()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
            ax.grid(True, which='major', color='#CCCCCC', linestyle='-', linewidth=1.2, zorder=1)
            ax.grid(True, which='minor', color='#EBEBEB', linestyle='-', linewidth=0.6, zorder=1)
            c_asym, c_cf, c_cg, c_pts, c_text, bg_leg, edge_leg = '#D32F2F', '#2E7D32', '#1565C0', '#FF8C00', 'black', '#FFFFFF', '#A0A0A0'

        for asym in cache['unique_asymptotes']:
            try:
                if asym['type'] == 'h':
                    ax.axhline(asym['val'], color=c_asym, linestyle='--', linewidth=2.2, zorder=4)
                    ax.text(ax.get_xlim()[1]-0.5, asym['val'] + 0.25, f"${asym['label']}$", color=c_asym, fontsize=14, fontweight='bold', ha='right')
                elif asym['type'] == 'v':
                    ax.axvline(asym['val'], color=c_asym, linestyle='--', linewidth=2.2, zorder=4)
                    ax.text(asym['val'] + 0.15, ax.get_ylim()[1]-1.5, f"${asym['label']}$", color=c_asym, fontsize=14, fontweight='bold', va='top')
            except: pass
            
        for hole in cache['holes']:
            ax.plot(hole['val'], hole['lim'], marker='o', markerfacecolor=bg_leg, markeredgecolor=c_cf, markersize=8, markeredgewidth=2, zorder=6)
        
        try: ax.plot(cache['x_vals_plot'], cache['y_vals_plot'], color=c_cf, linewidth=3.5, label=r'$C_f$', zorder=5)
        except: ax.plot(cache['x_vals_plot'], cache['y_vals_plot'], color=c_cf, linewidth=3.5, label='C_f', zorder=5)
        
        if mode == 'dark':
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'): y_g_plot = cache['g_func'](cache['x_vals_plot'], m_val)
            if np.isscalar(y_g_plot): y_g_plot = np.full_like(cache['x_vals_plot'], y_g_plot, dtype=float)
            
            m_val_str = str(int(m_val)) if int(m_val)==m_val else str(round(m_val, 2))
            m_eq_label = f"y = {m_val_str}" if current_g.strip() == 'm' else "y = " + current_g.replace('m', f"({m_val_str})" if m_val < 0 else m_val_str).replace('*', '')
                
            try: ax.plot(cache['x_vals_plot'], y_g_plot, color=c_cg, linestyle='--', linewidth=3, label=f"${m_eq_label}$", zorder=5)
            except: ax.plot(cache['x_vals_plot'], y_g_plot, color=c_cg, linestyle='--', linewidth=3, label=m_eq_label, zorder=5)
                
            diff_plot = cache['y_vals_plot'] - y_g_plot
            intersect_x = []
            
            for i in range(len(diff_plot)-1):
                if np.isfinite(diff_plot[i]) and np.isfinite(diff_plot[i+1]):
                    if diff_plot[i] * diff_plot[i+1] < 0:
                        denom = diff_plot[i+1] - diff_plot[i]
                        x_c = cache['x_vals_plot'][i] - diff_plot[i] * (cache['x_vals_plot'][i+1] - cache['x_vals_plot'][i]) / denom
                        if not any(abs(x_c - safe_float(a['val'])) < 1e-3 for a in cache['unique_asymptotes'] if a['type'] == 'v'):
                            intersect_x.append(float(x_c))
                    elif diff_plot[i] == 0:
                        if i == 0 or diff_plot[i-1] != 0:
                            j = i
                            while j < len(diff_plot) and diff_plot[j] == 0: j += 1
                            if j - i < 5: 
                                x_c = cache['x_vals_plot'][i]
                                if not any(abs(x_c - safe_float(a['val'])) < 1e-3 for a in cache['unique_asymptotes'] if a['type'] == 'v'):
                                    intersect_x.append(float(x_c))
                                    
            if len(diff_plot) > 0 and diff_plot[-1] == 0 and diff_plot[-2] != 0:
                x_c = cache['x_vals_plot'][-1]
                if not any(abs(x_c - safe_float(a['val'])) < 1e-3 for a in cache['unique_asymptotes'] if a['type'] == 'v'):
                    intersect_x.append(float(x_c))

            unique_intersect_x = []
            for ix in intersect_x:
                if not any(abs(ix - u) < 0.1 for u in unique_intersect_x): unique_intersect_x.append(ix)

            intersect_y = []
            for ix in unique_intersect_x:
                if current_g.strip() == 'm': intersect_y.append(m_val)
                else:
                    try:
                        v_eval = cache['g_func'](ix, m_val)
                        if isinstance(v_eval, complex) or np.iscomplexobj(v_eval): intersect_y.append(np.nan)
                        else: intersect_y.append(float(v_eval))
                    except: intersect_y.append(np.nan)

            if unique_intersect_x:
                try: ax.scatter(unique_intersect_x, intersect_y, color=c_pts, s=130, zorder=6, edgecolor='white', linewidth=1.5, label=fix_arabic_mpl('نقاط التقاطع'))
                except: pass
                    
            try: ax.text(4, m_val + 0.35, f"${m_eq_label}$", color=c_cg, fontsize=15, fontweight='bold', ha='center', va='bottom', zorder=6)
            except: pass
            
        ax.set_xlim(-12, 12)
        ax.set_ylim(-8, 8)
        
        try:
            legend = ax.legend(facecolor=bg_leg, edgecolor=edge_leg, loc='upper right', fontsize=12)
            for text in legend.get_texts(): text.set_color(c_text)
        except: pass
        try: fig.tight_layout()
        except: pass
        return fig, ax

    def generate_pdf():
        if not PDF_ENABLED: return None
        try:
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            font_path = "Amiri-Regular.ttf"
            if not os.path.exists(font_path) or os.path.getsize(font_path) < 10000:
                req = urllib.request.Request("https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(font_path, 'wb') as out_file: out_file.write(response.read())
                
            pdf.add_font("Amiri", "", font_path, uni=True)
            pdf.add_page()
            pdf.set_font("Amiri", size=22)
            pdf.set_text_color(21, 101, 192)
            pdf.cell(0, 10, fix_arabic_pdf("المناقشة البيانية ودراسة تغيرات دالة"), ln=True, align='C')
            pdf.set_font("Amiri", size=17)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 8, fix_arabic_pdf("الأستاذ سوايسية هشام"), ln=True, align='C')
            pdf.ln(3)
            
            pdf.set_font("Amiri", size=15)
            pdf.set_text_color(194, 24, 91) 
            pdf.cell(0, 8, fix_arabic_pdf("1. استنتاج مجموعة التعريف وحساب النهايات:"), ln=True, align='R')
            pdf.ln(1)
            if cache['limits_image_path']:
                pdf.image(cache['limits_image_path'], x=15, w=180)
                pdf.ln(4)

            pdf.set_font("Amiri", size=15)
            pdf.set_text_color(194, 24, 91) 
            pdf.cell(0, 8, fix_arabic_pdf("2. حساب الدالة المشتقة:"), ln=True, align='R')
            pdf.ln(1)
            if cache['deriv_image_path']:
                pdf.image(cache['deriv_image_path'], x=15, w=180)
                pdf.ln(4)

            pdf.set_font("Amiri", size=15)
            pdf.set_text_color(194, 24, 91) 
            pdf.cell(0, 8, fix_arabic_pdf("3. جدول التغيرات:"), ln=True, align='R')
            pdf.ln(3)
            if cache['var_table_image_path']:
                pdf.image(cache['var_table_image_path'], x=10, w=190)

            pdf.add_page()
            pdf.set_font("Amiri", size=17)
            pdf.set_text_color(21, 101, 192)
            pdf.cell(0, 9, fix_arabic_pdf("4. التمثيل البياني للدالة (Cf):"), ln=True, align='R')
            pdf.ln(1)
            
            fig_light, ax_light = draw_plot(0, mode='light')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                fig_light.savefig(tmpfile.name, facecolor='#FFFFFF')
                pdf.image(tmpfile.name, x=20, w=170)
            plt.close(fig_light)
            pdf.ln(4)
            
            pdf.set_font("Amiri", size=17)
            pdf.set_text_color(194, 24, 91)
            pdf.cell(0, 9, fix_arabic_pdf("5. جدول نتائج المناقشة البيانية لحلول المعادلة:"), ln=True, align='R')
            pdf.ln(1)
            
            if cache['eq_image_path']:
                pdf.image(cache['eq_image_path'], x=60, w=90)
                pdf.ln(2)

            if cache['disc_table_img_path']:
                pdf.image(cache['disc_table_img_path'], x=15, w=180)

            pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf.output(pdf_file.name)
            return pdf_file.name
        except Exception as e:
            return None

    if st.session_state.auto_play:
        m_val = st.session_state.m_anim
        
        stop_points = []
        if len(m_critical_num) == 0:
            stop_points.append(0.0)
        else:
            stop_points.extend(m_critical_num)
            stop_points.append(m_critical_num[0] - 1.5) 
            for i in range(len(m_critical_num) - 1):
                stop_points.append((m_critical_num[i] + m_critical_num[i+1]) / 2.0) 
            stop_points.append(m_critical_num[-1] + 1.5) 
        stop_points = sorted(list(set(stop_points)))

        while m_val <= m_max_val and st.session_state.auto_play:
            fig_dark, ax_dark = draw_plot(m_val, mode='dark')
            anim_placeholder.pyplot(fig_dark, use_container_width=True, clear_figure=True)
            table_placeholder.markdown(generate_st_markdown_table(m_val), unsafe_allow_html=True)
            plt.close(fig_dark)
            
            is_stop_now = any(abs(m_val - sp_val) < 1e-4 for sp_val in stop_points)
            time.sleep(1.5 if is_stop_now else 0.02) 
            
            step = 0.2
            next_m = m_val + step
            
            for sp_val in stop_points:
                if m_val < sp_val - 1e-4 and next_m >= sp_val - 1e-4:
                    next_m = float(sp_val)
                    break
            
            m_val = next_m
            
        st.session_state.auto_play = False
        st.rerun()
    else:
        m_val = m_val_manual
        fig_dark, ax_dark = draw_plot(m_val, mode='dark')
        anim_placeholder.pyplot(fig_dark, use_container_width=True, clear_figure=True)
        table_placeholder.markdown(generate_st_markdown_table(m_val), unsafe_allow_html=True)
        plt.close(fig_dark)
        
    with st.expander("📊 عرض دراسة الدالة الشاملة (مستخرجة آلياً)", expanded=False):
        st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>1. استنتاج مجموعة التعريف وحساب النهايات:</h4>", unsafe_allow_html=True)
        st.latex(cache['domain_latex_st'])
        for lim_item in cache['limits_data_detailed']:
            st.latex(lim_item['main'])
            for stp in lim_item['steps']:
                st.markdown("<div class='step-box-lim'>🔹 التعليل (خطوات الحساب):</div>", unsafe_allow_html=True)
                st.latex(fr"\color{{#C4B5FD}}{{{stp}}}")
                
        st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>2. حساب الدالة المشتقة:</h4>", unsafe_allow_html=True)
        for d_step in cache.get('deriv_steps_detailed', []):
            st.markdown(f"<div class='step-box-deriv'>🔸 {d_step['label']}</div>", unsafe_allow_html=True)
            st.latex(fr"\color{{#FDE68A}}{{{d_step['math']}}}")
        st.markdown("<div class='step-box-final'>✅ العبارة النهائية للمشتقة:</div>", unsafe_allow_html=True)
        st.latex(fr"\color{{#4ADE80}}{{f'(x) = {cache['df_latex_str_safe']}}}")
        
        st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>3. جدول التغيرات:</h4>", unsafe_allow_html=True)
        if cache['var_table_image_path']:
            st.image(cache['var_table_image_path'], use_container_width=True)

    if PDF_ENABLED:
        if not st.session_state.auto_play:
            st.session_state.cached_pdf = generate_pdf()
        if st.session_state.get('cached_pdf'):
            with open(st.session_state.cached_pdf, "rb") as pdf_file: 
                pdf_bytes = pdf_file.read()
            st.download_button(label="📥 تحميل الحل والدراسة كملف PDF", data=pdf_bytes, file_name="monaqasha_souaissia.pdf", mime="application/pdf", disabled=st.session_state.auto_play)

st.markdown("""
<div class='footer-social'>
    <span class='footer-text'>رابط صفحتي في كل من الفايسبوك والانستغرام:</span>
    <div class='social-links-group'>
        <a href="https://www.facebook.com/share/1KHcAq6bVm/" target="_blank" class="social-btn fb-btn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M22.675 0h-21.35c-.732 0-1.325.593-1.325 1.325v21.351c0 .731.593 1.324 1.325 1.324h11.495v-9.294h-3.128v-3.622h3.128v-2.671c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.795.143v3.24l-1.918.001c-1.504 0-1.795.715-1.795 1.763v2.313h3.587l-.467 3.622h-3.12v9.293h6.116c.73 0 1.323-.593 1.323-1.325v-21.35c0-.732-.593-1.325-1.325-1.325z"/></svg>
            <span>Facebook</span>
        </a>
        <a href="https://www.instagram.com/prof_hicham_math?stkn=dzh0OWgxZ2ltb3Uw" target="_blank" class="social-btn ig-btn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            <span>Instagram</span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)
