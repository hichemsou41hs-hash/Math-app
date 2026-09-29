import streamlit as st
st.markdown(
    """
    <link rel="manifest" href="manifest.json">
    """,
    unsafe_allow_html=True,
)

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from scipy.signal import find_peaks
import time
import warnings
import re
import os
import urllib.request
import tempfile

try:
    from fpdf import FPDF
    import arabic_reshaper
    from bidi.algorithm import get_display
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

warnings.filterwarnings("ignore")

st.set_page_config(page_title="المناقشة البيانية", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: white; }
    .title-hes { text-align: center; color: #FFFFFF !important; font-size: 36px; font-weight: bold; white-space: nowrap; margin-bottom: 0px;}
    .title-dis { text-align: center; color: #FFD700 !important; font-size: 28px; font-weight: bold; margin-top: -5px; margin-bottom: 30px;}
    label, p, div[data-testid="stRadio"] p, div[data-testid="stTextInput"] label p { font-weight: bold !important; font-size: 17px !important; color: #00E5FF !important; }
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

st.markdown("<div class='title-hes'>الأستاذ سوايسية هشام</div>", unsafe_allow_html=True)
st.markdown("<div class='title-dis'>المناقشة البيانية ودراسة الدالة</div>", unsafe_allow_html=True)

def fmt(val):
    if str(val) == 'oo' or val == float('inf'): return "+\infty"
    if str(val) == '-oo' or val == float('-inf'): return "-\infty"
    if str(val) == 'zoo': return "\pm\infty"
    try:
        f_val = float(val)
        if not np.isfinite(f_val): return str(val)
        if abs(f_val) > 1e6: return str(f_val)
        if int(f_val) == f_val: return str(int(f_val))
        return str(round(f_val, 2))
    except:
        return str(val)

def fix_implicit_mult(expr_str):
    if "()" in expr_str: expr_str = expr_str.replace("()", "(1)")
    expr_str = expr_str.replace('^', '**')
    expr_str = re.sub(r'([xy0-9])(ln|cos|sin|sqrt|abs|e|pi)', r'\1*\2', expr_str)
    expr_str = re.sub(r'(e|pi)([xy0-9])', r'\1*\2', expr_str)
    return expr_str

def fix_arabic_pdf(text):
    return get_display(arabic_reshaper.reshape(text))

def fix_arabic_mpl(text):
    return arabic_reshaper.reshape(text)

def sanitize_latex(expr):
    if hasattr(expr, 'has'):
        if expr.has(sp.LambertW) or (hasattr(sp, 'RootOf') and expr.has(sp.RootOf)):
            try:
                fl = float(sp.N(expr))
                if int(fl) == fl: return str(int(fl))
                return str(round(fl, 2))
            except: pass
    elif isinstance(expr, str) and ("LambertW" in expr or "RootOf" in expr or "W(" in expr):
        try:
            fl = float(sp.N(sp.sympify(expr)))
            if int(fl) == fl: return str(int(fl))
            return str(round(fl, 2))
        except: pass

    if not isinstance(expr, str): expr = sp.latex(expr)
    s = str(expr)
    s = s.replace('log', 'ln')
    s = s.replace(r'\left', '').replace(r'\right', '')
    s = s.replace(r'\operatorname', r'\mathrm')
    return s

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
if 'm_anim' not in st.session_state: st.session_state.m_anim = -6.0
if 'f_val' not in st.session_state: st.session_state.f_val = "(x+e^x+2)/(e^x+1)"
if 'g_val' not in st.session_state: st.session_state.g_val = "m+x"
if 'kbd_target' not in st.session_state: st.session_state.kbd_target = "f"

with st.expander("⌨️ لوحة المفاتيح المساعدة", expanded=False):
    t_sel = st.radio("توجيه الإدخال إلى:", ["f(x) الدالة", "m المستقيم بدلالة"], horizontal=True)
    st.session_state.kbd_target = "f" if t_sel == "f(x) الدالة" else "g"
    
    def k_click(char):
        target = "f_val" if st.session_state.kbd_target == "f" else "g_val"
        if char == 'DEL': st.session_state[target] = st.session_state[target][:-1]
        elif char == 'CLR': st.session_state[target] = ""
        else: st.session_state[target] += char

    keys = [
        [("x", "x"), ("cos", "cos("), ("sin", "sin("), ("7", "7"), ("8", "8"), ("9", "9")],
        [("m", "m"), ("π", "pi"), ("ln", "ln("), ("4", "4"), ("5", "5"), ("6", "6")],
        [("■/■", "/"), ("√", "sqrt("), ("x²", "^2"), ("1", "1"), ("2", "2"), ("3", "3")],
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
except:
    pass 

col_text, col_img = st.columns(2)

with col_img:
    img_file = st.file_uploader("🖼️ ارفع صورة الدالة لاستخراجها آلياً:", type=['png', 'jpg', 'jpeg'])
    st.markdown("<p style='font-size:14px; color:#94A3B8; text-align:right; direction:rtl; margin-top:-10px;'>💡 <b>ملاحظة:</b> في حال وجود ضغط على خادم الذكاء الاصطناعي وفشل قراءة الصورة، يرجى كتابة الدالة يدوياً في الخانة المجاورة.</p>", unsafe_allow_html=True)
    
    if img_file:
        if not api_key:
            st.error("⚠️ خاصية الذكاء الاصطناعي غير مفعلة (ينقص مفتاح API).")
        else:
            if st.button("استخراج الدالة 🤖", use_container_width=True):
                with st.spinner("جاري قراءة الصورة..."):
                    try:
                        import google.generativeai as genai
                        from PIL import Image
                        genai.configure(api_key=api_key)
                        
                        img = Image.open(img_file)
                        model = genai.GenerativeModel('gemini-3.8-flash')
                        prompt = "Extract ONLY the mathematical function expression from this image. Convert it to a simple string compatible with Python/SymPy (use ** for powers, * for multiplication, sqrt() for roots, abs() for absolute value, ln() for natural log). DO NOT output any markdown, LaTeX, or explanatory text. Just the raw math string."
                        response = model.generate_content([prompt, img])
                        
                        extracted_text = response.text.strip().replace('`', '').replace('\n', '')
                        st.session_state.f_val = extracted_text
                        st.success("✅ تم الاستخراج بنجاح!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ خطأ تقني: {str(e)}")

with col_text:
    st.text_input("أدخل عبارة الدالة f(x):", key="f_val")
    st.text_input("أدخل معادلة المستقيم بدلالة m:", key="g_val")

x_sym, m_sym = sp.symbols('x m', real=True)
local_dict = {'x': x_sym, 'm': m_sym, 'e': sp.E, 'pi': sp.pi, 'ln': sp.log, 'sqrt': sp.sqrt, 'abs': sp.Abs, 'cos': sp.cos, 'sin': sp.sin}

try:
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    transformations = (standard_transformations + (implicit_multiplication_application,))
    f_processed = fix_implicit_mult(st.session_state.f_val)
    g_processed = fix_implicit_mult(st.session_state.g_val)
    with sp.evaluate(False):
        f_expr = parse_expr(f_processed, local_dict=local_dict, transformations=transformations, evaluate=False)
        g_expr = parse_expr(g_processed, local_dict=local_dict, transformations=transformations, evaluate=False)
    valid_input = True
except:
    st.error("⚠️ صيغة غير صالحة أو الخانة فارغة.")
    valid_input = False

if valid_input:
    st.latex(rf"\color{{#FFD700}} \begin{{cases}} f(x) = {sanitize_latex(f_expr)} \\ y = {sanitize_latex(g_expr)} \end{{cases}}")

    f_func = sp.lambdify(x_sym, f_expr, 'numpy')
    g_func = sp.lambdify((x_sym, m_sym), g_expr, 'numpy')
    
    x_vals_plot = np.linspace(-15, 15, 60001)
    x_vals_roots = np.concatenate([np.linspace(-500, -15, 5000, endpoint=False), np.linspace(-15, 15, 60001), np.linspace(15, 500, 5000)])
    
    def process_y_vals(x_arr):
        with np.errstate(divide='ignore', invalid='ignore'): y_arr = f_func(x_arr)
        if np.iscomplexobj(y_arr): y_arr = np.where(np.isreal(y_arr), y_arr.real, np.nan)
        if np.isscalar(y_arr): y_arr = np.full_like(x_arr, y_arr, dtype=float)
        dy = np.abs(np.diff(y_arr))
        for idx in np.where(dy > 30)[0]: y_arr[idx] = np.nan; y_arr[idx+1] = np.nan
        return y_arr

    y_vals_plot = process_y_vals(x_vals_plot)
    y_vals_roots = process_y_vals(x_vals_roots)

    candidate_v_asymptotes = []
    try:
        n_expr, d_expr = sp.fraction(sp.cancel(f_expr))
        if d_expr != 1:
            for r in sp.solve(d_expr, x_sym):
                if r.is_real is not False and sp.im(sp.N(r)) == 0: candidate_v_asymptotes.append(r)
    except: pass
    try:
        for log_expr in f_expr.atoms(sp.log):
            for r in sp.solve(log_expr.args[0], x_sym):
                if r.is_real is not False and sp.im(sp.N(r)) == 0: candidate_v_asymptotes.append(r)
    except: pass
    candidate_v_asymptotes = list(set(candidate_v_asymptotes))
    
    unique_asymptotes = []
    for r in candidate_v_asymptotes:
        unique_asymptotes.append({'type': 'v', 'val': float(sp.N(r)), 'label': f"x={sanitize_latex(r)}"})

    df_expr = sp.diff(f_expr, x_sym)
    
    df_clean = df_expr.replace(sp.sign, lambda arg: arg / sp.Abs(arg))
    df_simp = sp.simplify(df_clean)
    if df_simp.has(sp.Piecewise): df_simp = df_clean 
    df_latex_str_safe = sanitize_latex(df_simp)
    
    sym_extrema = []
    try:
        for r in sp.solve(df_expr, x_sym):
            if r.is_real is not False and sp.im(sp.N(r)) == 0:
                sym_extrema.append(r)
    except: pass
    sym_extrema = list(set(sym_extrema))

    pts_var_exact = []
    pts_var_exact.append({'val': -np.inf, 'sym': -sp.oo, 'latex_x': r"-\infty", 'type': 'inf'})
    for r in candidate_v_asymptotes:
        pts_var_exact.append({'val': float(sp.N(r)), 'sym': r, 'latex_x': sanitize_latex(r), 'type': 'v_asym'})
    for r in sym_extrema:
        val = float(sp.N(r))
        if not any(abs(p['val'] - val) < 1e-4 for p in pts_var_exact):
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
                y_val = sp.simplify(f_expr.subs(x_sym, sym_nx))
                if y_val.is_real:
                    pts_var_exact.append({'val': float(sp.N(sym_nx)), 'sym': sym_nx, 'latex_x': sanitize_latex(sym_nx), 'type': 'extrema'})
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
            if not np.isfinite(df_val) or abs(df_near_plus) > 20 or abs(df_near_minus) > 20:
                p['type'] = 'corner'

    valid_intervals = []
    for i in range(len(pts_var_exact) - 1):
        left, right = pts_var_exact[i]['val'], pts_var_exact[i+1]['val']
        mid = 0 if (left == -np.inf and right == np.inf) else (right - 1 if left == -np.inf else (left + 1 if right == np.inf else (left + right) / 2.0))
        valid_intervals.append(np.isfinite(f_func(mid)))
        
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
    domain_latex_mpl = r"D_f =" + (r" \cup ".join(domain_intervals_str) if domain_intervals_str else r"\emptyset")

    sym_m_critical = []
    try:
        m_expr_list = sp.solve(f_expr - g_expr, m_sym)
        m_expr = m_expr_list[0] if m_expr_list else f_expr
    except:
        m_expr = f_expr

    try:
        for direction in [sp.oo, -sp.oo]:
            lim = sp.limit(m_expr, x_sym, direction)
            if lim.is_real: sym_m_critical.append(lim)
    except: pass

    try:
        val_0 = sp.simplify(m_expr.subs(x_sym, 0))
        if val_0.is_real: sym_m_critical.append(val_0)
        else:
            lim_0 = sp.limit(m_expr, x_sym, 0)
            if lim_0.is_real: sym_m_critical.append(lim_0)
    except: pass
    
    try:
        for r in sym_extrema:
            sym_m_val = sp.simplify(m_expr.subs(x_sym, r))
            if sym_m_val.is_real: sym_m_critical.append(sym_m_val)
    except: pass

    try:
        dm_expr = sp.diff(m_expr, x_sym)
        for r in sp.solve(dm_expr, x_sym):
            if r.is_real is not False and sp.im(sp.N(r)) == 0:
                sym_m_val = sp.simplify(m_expr.subs(x_sym, r))
                if sym_m_val.is_real: sym_m_critical.append(sym_m_val)
    except: pass

    m_critical_num = []
    for sm in sym_m_critical:
        fl_m = float(sp.N(sm))
        if np.isfinite(fl_m) and abs(fl_m) < 100: m_critical_num.append(round(fl_m, 2))

    try:
        m_func_eval = sp.lambdify(x_sym, m_expr, 'numpy')
        x_test_m = np.linspace(-25, 25, 100001)
        with np.errstate(divide='ignore', invalid='ignore'):
            y_test_m = m_func_eval(x_test_m)
            if np.iscomplexobj(y_test_m): y_test_m = np.where(np.isreal(y_test_m), y_test_m.real, np.nan)
            
        is_val_m = ~np.isnan(y_test_m)
        edges_m = np.diff(is_val_m.astype(int))
        starts_m = np.where(edges_m == 1)[0] + 1
        if is_val_m[0]: starts_m = np.insert(starts_m, 0, 0)
        ends_m = np.where(edges_m == -1)[0]
        if is_val_m[-1]: ends_m = np.append(ends_m, len(y_test_m) - 1)

        for s, e in zip(starts_m, ends_m):
            segment = y_test_m[s:e+1]
            if len(segment) > 0:
                if s > 0 and np.isfinite(y_test_m[s]): m_critical_num.append(round(float(y_test_m[s]), 2))
                if e < len(x_test_m) - 1 and np.isfinite(y_test_m[e]): m_critical_num.append(round(float(y_test_m[e]), 2))
                
                if len(segment) > 10:
                    peaks, _ = find_peaks(segment, prominence=0.05)
                    valleys, _ = find_peaks(-segment, prominence=0.05)
                    for p in peaks: m_critical_num.append(round(float(segment[p]), 2))
                    for v in valleys: m_critical_num.append(round(float(segment[v]), 2))
    except: pass
    
    m_critical_num = sorted(list(set([round(m, 2) for m in m_critical_num if np.isfinite(m) and abs(m) < 100])))

    # حساب حدود حركة الوسيط m لينطلق دائماً من الأسفل صعوداً للأعلى
    m_min_val = -6.0
    m_max_val = 6.0
    if m_critical_num:
        if m_critical_num[0] - 1.5 < m_min_val:
            m_min_val = float(np.floor(m_critical_num[0] - 1.5))
        if m_critical_num[-1] + 1.5 > m_max_val:
            m_max_val = float(np.ceil(m_critical_num[-1] + 1.5))
    m_min_val = float(max(-25.0, m_min_val))
    m_max_val = float(min(25.0, m_max_val))

    def get_exact_m(val_float):
        for sm in sym_m_critical:
            if abs(float(sp.N(sm)) - val_float) < 1e-2:
                s_str = str(sm)
                if "LambertW" in s_str or "RootOf" in s_str or "Integral" in s_str or "zoo" in s_str:
                    return fmt(val_float)
                latex_str = sanitize_latex(sm)
                if len(latex_str) > 25:
                    return fmt(val_float)
                return latex_str
        return fmt(val_float)

    def get_roots_text(m_test):
        is_critical = any(abs(m_test - mc) < 1e-2 for mc in m_critical_num)
        with np.errstate(divide='ignore', invalid='ignore'):
            y_g = g_func(x_vals_roots, m_test)
            if np.isscalar(y_g): y_g = np.full_like(x_vals_roots, y_g, dtype=float)
            diff = y_vals_roots - y_g
        crossings = []
        for i in range(len(diff)-1):
            if np.isfinite(diff[i]) and np.isfinite(diff[i+1]):
                if diff[i] * diff[i+1] < 0:
                    denom = diff[i+1] - diff[i]
                    x_c = x_vals_roots[i] - diff[i] * (x_vals_roots[i+1] - x_vals_roots[i]) / denom
                    crossings.append(float(x_c))
                elif diff[i] == 0:
                    if i == 0 or diff[i-1] != 0:
                        j = i
                        while j < len(diff) and diff[j] == 0: j += 1
                        if j - i < 5: 
                            crossings.append(float(x_vals_roots[i]))
        if len(diff) > 0 and diff[-1] == 0 and diff[-2] != 0:
            crossings.append(float(x_vals_roots[-1]))
            
        tangents = []
        cleaned_crossings = []
        if is_critical:
            skip = False
            for i in range(len(crossings)):
                if skip: skip = False; continue
                if i < len(crossings)-1 and abs(crossings[i+1] - crossings[i]) < 0.5:
                    tangents.append((crossings[i] + crossings[i+1])/2.0); skip = True
                else: cleaned_crossings.append(crossings[i])
            
            abs_diff = np.abs(diff)
            abs_diff_r = np.round(abs_diff, 5)
            for i in range(1, len(abs_diff_r)-1):
                if np.isfinite(abs_diff_r[i-1]) and np.isfinite(abs_diff_r[i]) and np.isfinite(abs_diff_r[i+1]):
                    if abs_diff_r[i] < abs_diff_r[i-1] - 1e-9 and abs_diff_r[i] < abs_diff_r[i+1] - 1e-9 and abs_diff_r[i] < 0.05:
                        if not any(abs(x_vals_roots[i] - c) < 0.6 for c in cleaned_crossings) and not any(abs(x_vals_roots[i] - t) < 0.6 for t in tangents):
                            tangents.append(x_vals_roots[i])
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

    merged_intervals = []
    if raw_intervals:
        cur_L, cur_H, cur_text = raw_intervals[0][0], raw_intervals[0][1], raw_intervals[0][2]
        for item in raw_intervals[1:]:
            if item[2] == cur_text: cur_H = item[1]
            else:
                merged_intervals.append((cur_L, cur_H, cur_text))
                cur_L, cur_H, cur_text = item[0], item[1], item[2]
        merged_intervals.append((cur_L, cur_H, cur_text))

    final_table = [] 
    for L, H, sol_text in merged_intervals:
        L_inc = any(r[0] == L and r[1] == L and r[2] == sol_text for r in raw_intervals)
        H_inc = any(r[0] == H and r[1] == H and r[2] == sol_text for r in raw_intervals)
        
        L_latex = r"-\infty" if L == float('-inf') else get_exact_m(L)
        H_latex = r"+\infty" if H == float('inf') else get_exact_m(H)
        
        if L == float('-inf') and H == float('inf'):
            m_latex = r"m \in \mathbb{R}"
        elif L == float('-inf'):
            bracket_H = "]" if H_inc else "["
            m_latex = fr"m \in ]-\infty ; {H_latex}{bracket_H}"
        elif H == float('inf'):
            bracket_L = "[" if L_inc else "]"
            m_latex = fr"m \in {bracket_L}{L_latex} ; +\infty["
        elif L == H:
            m_latex = fr"m = {L_latex}"
        else:
            bracket_L = "[" if L_inc else "]"
            bracket_H = "]" if H_inc else "["
            m_latex = fr"m \in {bracket_L}{L_latex} ; {H_latex}{bracket_H}"
            
        final_table.append((m_latex, sol_text, L, H))

    # تعديل عنوان العمود في التطبيق إلى "عدد و إشارة حلول المعادلة"
    def generate_st_markdown_table(current_m):
        md = "| عدد و إشارة حلول المعادلة | المجال / القيمة المضبوطة |\n"
        md += "| :---: | :---: |\n"
        
        active_idx = 0
        for idx, (m_latex, sol_text, L, H) in enumerate(final_table):
            is_active = False
            if L == H and abs(current_m - L) <= 0.03: is_active = True
            elif L == float('-inf') and current_m <= H - 0.03: is_active = True
            elif H == float('inf') and current_m >= L + 0.03: is_active = True
            elif L + 0.03 <= current_m <= H - 0.03: is_active = True
            if is_active: active_idx = idx

        for idx, (m_latex, sol_text, L, H) in enumerate(final_table):
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

    # تعديل عنوان العمود في جدول الـ PDF إلى "عدد و إشارة حلول المعادلة"
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
            try: fig_dt.tight_layout(pad=0)
            except: pass
            
        tmp_dt = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig_dt.savefig(tmp_dt.name, bbox_inches='tight', dpi=300)
        plt.close(fig_dt)
        return tmp_dt.name

    # توليد صورة أنيقة لمعادلة المناقشة البيانية لوضعها فوق جدول الـ PDF
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
            ax_e.text(0.5, 0.5, f"f(x) = {st.session_state.g_val}", fontsize=18, ha='center', va='center', color='#1E3A8A')
            try: fig_e.tight_layout(pad=0)
            except: pass
        tmp_e = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig_e.savefig(tmp_e.name, bbox_inches='tight', dpi=300)
        plt.close(fig_e)
        return tmp_e.name

    limits_data_detailed = []
    limits_mpl_list = []
    
    def add_limit(val_sym, dir_sympy, dir_latex):
        try:
            lim = sp.limit(f_expr, x_sym, val_sym, dir=dir_sympy)
            lim_latex = "+\infty" if lim == sp.oo else sanitize_latex(lim)
            expr_latex = sanitize_latex(f_expr)
            
            latex_streamlit = fr"\lim_{{x \to {dir_latex}}} \left( {expr_latex} \right) = \mathbf{{\color{{#EF4444}}{{{lim_latex}}}}}"
            limits_data_detailed.append(latex_streamlit)
            
            lhs_mpl = fr"\lim_{{x \to {dir_latex}}} f(x) = \lim_{{x \to {dir_latex}}} \left( {expr_latex} \right) ="
            rhs_mpl = fr"{lim_latex}"
            limits_mpl_list.append((lhs_mpl, rhs_mpl))
        except: pass

    if len(pts_var_exact) > 0:
        if valid_intervals and valid_intervals[0]:
            if pts_var_exact[0]['sym'] == -sp.oo: add_limit(-sp.oo, '+', r"-\infty")
        if valid_intervals and valid_intervals[-1]:
            if pts_var_exact[-1]['sym'] == sp.oo: add_limit(sp.oo, '-', r"+\infty")

        for i, p in enumerate(pts_var_exact):
            if p['type'] == 'v_asym':
                v_latex = p['latex_x']
                if i > 0 and valid_intervals[i-1]: add_limit(p['sym'], '-', fr"{v_latex}^-")
                if i < len(valid_intervals) and valid_intervals[i]: add_limit(p['sym'], '+', fr"{v_latex}^+")

    def generate_limits_image():
        all_lines = [(domain_latex_mpl, "")] + limits_mpl_list
        n_lines = len(all_lines)
        fig_l, ax_l = plt.subplots(figsize=(8, max(1.5, n_lines * 0.9)))
        ax_l.axis('off')
        
        try:
            for i, (lhs, rhs) in enumerate(all_lines):
                y_pos = 1.0 - (i + 0.5) / n_lines
                if i == 0: 
                    ax_l.text(0.5, y_pos, f"${lhs}$", fontsize=22, ha='center', va='center', color='#1E3A8A')
                else: 
                    ax_l.text(0.70, y_pos, f"${lhs}$", fontsize=22, ha='right', va='center', color='#1E3A8A')
                    ax_l.text(0.72, y_pos, f"${rhs}$", fontsize=24, ha='left', va='center', color='#D32F2F', fontweight='bold')
            fig_l.canvas.draw()
            fig_l.tight_layout(pad=0)
        except:
            ax_l.clear()
            ax_l.axis('off')
            ax_l.text(0.5, 0.5, "خطأ في رسم المعادلات", fontsize=18, ha='center', va='center', color='#D32F2F')
            
        tmp_l = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig_l.savefig(tmp_l.name, bbox_inches='tight', dpi=300)
        plt.close(fig_l)
        return tmp_l.name

    limits_image_path = generate_limits_image()

    def generate_deriv_image():
        math_str = fr"f'(x) = {df_latex_str_safe}"
        fig_d, ax_d = plt.subplots(figsize=(8, 1.5))
        ax_d.axis('off')
        try:
            ax_d.text(0.5, 0.5, f"${math_str}$", fontsize=24, ha='center', va='center', color='#1E3A8A')
            fig_d.canvas.draw()
            fig_d.tight_layout(pad=0)
        except:
            ax_d.clear()
            ax_d.axis('off')
            safe_str = str(df_simp).replace('**', '^')
            ax_d.text(0.5, 0.5, f"f'(x) = {safe_str}", fontsize=18, ha='center', va='center', color='#1E3A8A', family='serif')
            try: fig_d.tight_layout(pad=0)
            except: pass
            
        tmp_d = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig_d.savefig(tmp_d.name, bbox_inches='tight', dpi=300)
        plt.close(fig_d)
        return tmp_d.name
        
    deriv_image_path = generate_deriv_image()

    N = len(pts_var_exact)
    def generate_variation_table_image():
        if N < 2: return None
        col_w = 2.8 
        x_start_data = 2.0 
        x_max = x_start_data + N * col_w
        
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
            if not np.isfinite(f_func(mid)): signs.append(None)
            else: signs.append("+" if f_func(mid + 1e-5) > f_func(mid) else "-")
                
        nodes = []
        for i in range(N):
            p = pts_var_exact[i]
            x_val = p['val']
            x_c = x_start_data + (col_w / 2.0) + i * col_w 
            
            ax_v.text(x_c, 5.5, f"${p['latex_x']}$", ha='center', va='center', fontsize=18)
            
            if p['type'] == 'v_asym':
                ax_v.plot([x_c-0.05, x_c-0.05], [0, 5], 'k-', lw=1.5, zorder=2)
                ax_v.plot([x_c+0.05, x_c+0.05], [0, 5], 'k-', lw=1.5, zorder=2)
            elif p['type'] == 'extrema':
                ax_v.plot([x_c, x_c], [4, 5], 'k-', lw=1.2, zorder=2)
                ax_v.text(x_c, 4.5, '0', ha='center', va='center', fontsize=16)
                # تم إلغاء إسقاط الخط المتقطع في خانة الدالة f(x) كما طلبت
            elif p['type'] == 'corner': 
                ax_v.plot([x_c-0.03, x_c-0.03], [4, 5], 'k-', lw=1.5, color='#D32F2F', zorder=2)
                ax_v.plot([x_c+0.03, x_c+0.03], [4, 5], 'k-', lw=1.5, color='#D32F2F', zorder=2)
                # تم إلغاء إسقاط الخط المتقطع في خانة الدالة f(x) كما طلبت

            if i < N - 1:
                x_ic = x_c + (col_w / 2.0)
                if not valid_intervals[i]:
                    rect = plt.Rectangle((x_c, 0), col_w, 5, facecolor='#EF4444', alpha=0.7, zorder=1)
                    ax_v.add_patch(rect)
                else:
                    ax_v.text(x_ic, 4.5, f"${signs[i]}$", ha='center', va='center', fontsize=26, color='#D32F2F' if signs[i]=='-' else '#2E7D32')
            
            def get_lim_latex_for_table(l_sym):
                return "+\infty" if l_sym == sp.oo else sanitize_latex(l_sym)

            if p['type'] == 'inf':
                lim = sp.limit(f_expr, x_sym, p['sym'])
                dx = 0.5 if x_val == -np.inf else -0.5
                nodes.append((x_c+dx, float(sp.N(lim)) if lim.is_real else float('inf') if lim==sp.oo else float('-inf'), get_lim_latex_for_table(lim)))
            elif p['type'] == 'v_asym':
                if i > 0 and valid_intervals[i-1]:
                    lim_l = sp.limit(f_expr, x_sym, p['sym'], dir='-')
                    nodes.append((x_c-0.4, float(sp.N(lim_l)) if lim_l.is_real else float('inf') if lim_l==sp.oo else float('-inf'), get_lim_latex_for_table(lim_l)))
                if i < N-1 and valid_intervals[i]:
                    lim_r = sp.limit(f_expr, x_sym, p['sym'], dir='+')
                    nodes.append((x_c+0.4, float(sp.N(lim_r)) if lim_r.is_real else float('inf') if lim_r==sp.oo else float('-inf'), get_lim_latex_for_table(lim_r)))
            elif p['type'] in ['extrema', 'corner']:
                sym_y = sp.simplify(f_expr.subs(x_sym, p['sym']))
                nodes.append((x_c, float(sp.N(sym_y)), sanitize_latex(sym_y)))

        for i in range(N - 1):
            if valid_intervals[i]:
                x_c_left = x_start_data + (col_w / 2.0) + i * col_w
                x_c_right = x_start_data + (col_w / 2.0) + (i+1) * col_w
                
                l_node = next((n for n in nodes if n[0] >= x_c_left and n[0] <= x_c_left + 0.7), None)
                r_node = next((n for n in nodes if n[0] >= x_c_right - 0.7 and n[0] <= x_c_right), None)
                
                if l_node and r_node:
                    y_l = 0.8 if signs[i] == "+" else 3.2
                    y_r = 3.2 if signs[i] == "+" else 0.8
                    if y_l == y_r: y_l = 2.0; y_r = 2.0
                    
                    try:
                        ax_v.text(l_node[0], y_l, f"${l_node[2]}$", ha='center', va='center', fontsize=18, color='#D32F2F', fontweight='bold')
                    except: pass
                    try:
                        ax_v.text(r_node[0], y_r, f"${r_node[2]}$", ha='center', va='center', fontsize=18, color='#D32F2F', fontweight='bold')
                    except: pass
                    
                    pad_x, pad_y = 0.35, 0.4
                    start_x, end_x = l_node[0] + pad_x, r_node[0] - pad_x
                    start_y = y_l + (pad_y if signs[i]=="+" else -pad_y)
                    end_y = y_r + (-pad_y if signs[i]=="+" else pad_y)
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

    # ترتيب ملف PDF بالتسلسل البيداغوجي وإضافة معادلة المناقشة البيانية فوق الجدول
    def generate_pdf(fig_path):
        if not PDF_ENABLED: return None
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        font_path = "Amiri-Regular.ttf"
        
        if not os.path.exists(font_path) or os.path.getsize(font_path) < 10000:
            try:
                req = urllib.request.Request("https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(font_path, 'wb') as out_file: out_file.write(response.read())
            except: pass
        if not os.path.exists(font_path) or os.path.getsize(font_path) < 10000: return None
            
        pdf.add_font("Amiri", "", font_path, uni=True)
        
        # --- الصفحة الأولى: دراسة تغيرات الدالة بالتسلسل المنطقي ---
        pdf.add_page()
        pdf.set_font("Amiri", size=22)
        pdf.set_text_color(21, 101, 192)
        pdf.cell(0, 12, fix_arabic_pdf("الأستاذ سوايسية هشام - دراسة الدالة والمناقشة البيانية"), ln=True, align='C')
        pdf.ln(3)
        
        pdf.set_font("Amiri", size=15)
        pdf.set_text_color(194, 24, 91) 
        pdf.cell(0, 8, fix_arabic_pdf("1. استنتاج مجموعة التعريف وحساب النهايات:"), ln=True, align='R')
        pdf.ln(1)
        if limits_image_path:
            pdf.image(limits_image_path, x=20, w=170)
            pdf.ln(4)

        pdf.set_font("Amiri", size=15)
        pdf.set_text_color(194, 24, 91) 
        pdf.cell(0, 8, fix_arabic_pdf("2. حساب الدالة المشتقة:"), ln=True, align='R')
        pdf.ln(1)
        if deriv_image_path:
            pdf.image(deriv_image_path, x=45, w=120)
            pdf.ln(4)

        pdf.set_font("Amiri", size=15)
        pdf.set_text_color(194, 24, 91) 
        pdf.cell(0, 8, fix_arabic_pdf("3. جدول التغيرات:"), ln=True, align='R')
        pdf.ln(3)
        if var_table_image_path:
            pdf.image(var_table_image_path, x=10, w=190)

        # --- الصفحة الثانية: المنحنى البياني يليه معادلة وجدول المناقشة البيانية ---
        pdf.add_page()
        pdf.set_font("Amiri", size=17)
        pdf.set_text_color(21, 101, 192)
        pdf.cell(0, 9, fix_arabic_pdf("4. التمثيل البياني للدالة ومستقيم المناقشة:"), ln=True, align='R')
        pdf.ln(1)
        pdf.image(fig_path, x=20, w=170)
        pdf.ln(4)
        
        pdf.set_font("Amiri", size=17)
        pdf.set_text_color(194, 24, 91)
        pdf.cell(0, 9, fix_arabic_pdf("5. جدول نتائج المناقشة البيانية لحلول المعادلة:"), ln=True, align='R')
        pdf.ln(1)
        
        # إدراج معادلة المناقشة البيانية بصيغة رياضية أنيقة فوق الجدول
        eq_image_path = generate_eq_image()
        if eq_image_path:
            pdf.image(eq_image_path, x=60, w=90)
            pdf.ln(2)

        disc_table_img = generate_pdf_discussion_table()
        if disc_table_img:
            pdf.image(disc_table_img, x=15, w=180)

        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(pdf_file.name)
        return pdf_file.name

    st.write("") 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("تشغيل المناقشة آلياً ▶️"):
            st.session_state.auto_play = True
            st.session_state.m_anim = m_min_val
            st.rerun()
    with col2:
        if st.button("إيقاف ⏹️"):
            st.session_state.auto_play = False
            st.rerun()

    placeholder = st.empty()

    def update_view(m_val):
        fig, ax = plt.subplots(figsize=(10, 6.5))
        fig.patch.set_facecolor('#FFFFFF'); ax.set_facecolor('#FFFFFF')
        ax.tick_params(colors='black', labelsize=11)
        for spine in ax.spines.values(): spine.set_edgecolor('#A0A0A0')
        ax.axhline(0, color='black', linewidth=2, zorder=3)
        ax.axvline(0, color='black', linewidth=2, zorder=3)
        ax.minorticks_on()
        ax.grid(True, which='major', color='#CCCCCC', linestyle='-', linewidth=1.2, zorder=1)
        ax.grid(True, which='minor', color='#EBEBEB', linestyle='-', linewidth=0.6, zorder=1)
        
        for asym in unique_asymptotes:
            try:
                if asym['type'] == 'h':
                    ax.axhline(asym['val'], color='#D32F2F', linestyle='--', linewidth=2.2, zorder=4)
                    ax.text(7.5, asym['val'] + 0.25, f"${asym['label']}$", color='#D32F2F', fontsize=14, fontweight='bold', ha='right')
                elif asym['type'] == 'v':
                    ax.axvline(asym['val'], color='#D32F2F', linestyle='--', linewidth=2.2, zorder=4)
                    ax.text(asym['val'] + 0.15, 6.5, f"${asym['label']}$", color='#D32F2F', fontsize=14, fontweight='bold', va='top')
            except: pass
        
        try:
            ax.plot(x_vals_plot, y_vals_plot, color='#2E7D32', linewidth=3.5, label=r'$C_f$', zorder=5)
        except:
            ax.plot(x_vals_plot, y_vals_plot, color='#2E7D32', linewidth=3.5, label='C_f', zorder=5)
        
        with np.errstate(divide='ignore', invalid='ignore'): y_g_plot = g_func(x_vals_plot, m_val)
        if np.isscalar(y_g_plot): y_g_plot = np.full_like(x_vals_plot, y_g_plot, dtype=float)
        
        m_val_str = str(int(m_val)) if int(m_val)==m_val else str(round(m_val, 2))
        m_eq_label = f"y = {m_val_str}" if st.session_state.g_val.strip() == 'm' else "y = " + st.session_state.g_val.replace('m', f"({m_val_str})" if m_val < 0 else m_val_str).replace('*', '')
            
        try:
            ax.plot(x_vals_plot, y_g_plot, color='#1565C0', linestyle='--', linewidth=3, label=f"${m_eq_label}$", zorder=5)
        except:
            ax.plot(x_vals_plot, y_g_plot, color='#1565C0', linestyle='--', linewidth=3, label=m_eq_label, zorder=5)
            
        diff_plot = y_vals_plot - y_g_plot
        intersect_x = []
        for i in range(len(diff_plot)-1):
            if np.isfinite(diff_plot[i]) and np.isfinite(diff_plot[i+1]):
                if diff_plot[i] * diff_plot[i+1] < 0:
                    denom = diff_plot[i+1] - diff_plot[i]
                    x_c = x_vals_plot[i] - diff_plot[i] * (x_vals_plot[i+1] - x_vals_plot[i]) / denom
                    intersect_x.append(float(x_c))
                elif diff_plot[i] == 0:
                    if i == 0 or diff_plot[i-1] != 0:
                        j = i
                        while j < len(diff) and diff[j] == 0: j += 1
                        if j - i < 5: 
                            intersect_x.append(float(x_vals_plot[i]))
        if len(diff_plot) > 0 and diff_plot[-1] == 0 and diff_plot[-2] != 0:
            intersect_x.append(float(x_vals_plot[-1]))

        unique_intersect_x = []
        for ix in intersect_x:
            if not any(abs(ix - u) < 0.1 for u in unique_intersect_x): unique_intersect_x.append(ix)

        intersect_y = [m_val if st.session_state.g_val.strip() == 'm' else (float(g_func(ix, m_val)) if not np.isscalar(g_func(ix, m_val)) else g_func(ix, m_val)) for ix in unique_intersect_x]

        if unique_intersect_x:
            try:
                ax.scatter(unique_intersect_x, intersect_y, color='#FF8C00', s=130, zorder=6, edgecolor='black', linewidth=1.5, label=fix_arabic_mpl('نقاط التقاطع'))
            except: pass
                
        try:
            ax.text(4, m_val + 0.35, f"${m_eq_label}$", color='#1565C0', fontsize=15, fontweight='bold', ha='center', va='bottom', zorder=6)
        except: pass
            
        ax.set_ylim(-6, 8)
        try:
            legend = ax.legend(facecolor='#FFFFFF', edgecolor='#A0A0A0', loc='upper right', fontsize=12)
            for text in legend.get_texts(): text.set_color("black")
        except: pass
            
        try:
            fig.tight_layout()
        except: pass
        
        with placeholder.container():
            st.pyplot(fig, use_container_width=True)
            st.markdown(generate_st_markdown_table(m_val), unsafe_allow_html=True)
            
            with st.expander("📊 عرض دراسة الدالة الشاملة (مستخرجة آلياً)", expanded=False):
                st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>1. استنتاج مجموعة التعريف وحساب النهايات:</h4>", unsafe_allow_html=True)
                st.latex(domain_latex_st)
                
                for lim in limits_data_detailed:
                    st.latex(lim)
                    
                st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>2. حساب الدالة المشتقة:</h4>", unsafe_allow_html=True)
                st.latex(fr"f'(x) = {df_latex_str_safe}")
                
                st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>3. جدول التغيرات:</h4>", unsafe_allow_html=True)
                if var_table_image_path:
                    st.image(var_table_image_path, use_container_width=True)
            
            if PDF_ENABLED and not st.session_state.auto_play:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    fig.savefig(tmpfile.name, facecolor='#FFFFFF')
                    pdf_path = generate_pdf(tmpfile.name)
                    if pdf_path:
                        with open(pdf_path, "rb") as pdf_file: pdf_bytes = pdf_file.read()
                        st.download_button(label="📥 تحميل الحل والدراسة كملف PDF", data=pdf_bytes, file_name="monaqasha_souaissia.pdf", mime="application/pdf")
        plt.close(fig)

    if st.session_state.auto_play:
        while st.session_state.auto_play and st.session_state.m_anim <= m_max_val:
            m_val = round(st.session_state.m_anim, 2)
            update_view(m_val)
            is_critical_now = any(abs(st.session_state.m_anim - mc) < 0.05 for mc in m_critical_num)
            if is_critical_now: time.sleep(1.8) 
            else: time.sleep(0.04)
            step = 0.1 
            next_m = st.session_state.m_anim + step
            for mc in m_critical_num:
                if st.session_state.m_anim < mc - 1e-4 and next_m >= mc - 1e-4:
                    next_m = float(mc); break
            st.session_state.m_anim = next_m
        st.session_state.auto_play = False
    else:
        if 'manual_m' in st.session_state:
            if st.session_state.manual_m < m_min_val or st.session_state.manual_m > m_max_val:
                st.session_state.manual_m = m_min_val
        m_val = st.slider("تحكم يدوي:", m_min_val, m_max_val, m_min_val, 0.05, format="%g", key="manual_m")
        update_view(m_val)
