import streamlit as st
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
    button[kind="primary"] { width: 100% !important; height: 50px !important; background-color: #ef4444 !important; color: white !important; font-size: 18px !important; font-weight: bold !important; border-radius: 8px !important; box-shadow: 0 4px 0 #7f1d1d !important; border: none !important; margin-top: 5px !important; }
    button[kind="primary"]:active { transform: translateY(4px) !important; box-shadow: 0 0 0 #7f1d1d !important; background-color: #dc2626 !important; }
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

def fix_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

def clean_latex_to_text(l_str):
    s = str(l_str).replace(" ", "")
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"\1/\2", s)
    s = s.replace(r"\infty", "∞").replace(r"\ln", "ln")
    s = s.replace("{", "").replace("}", "").replace("\\", "")
    return s

if 'auto_play' not in st.session_state: st.session_state.auto_play = False
if 'm_anim' not in st.session_state: st.session_state.m_anim = -5.0
if 'f_val' not in st.session_state: st.session_state.f_val = "x*ln(x)"
if 'g_val' not in st.session_state: st.session_state.g_val = "m"
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
        [("□/□", "/"), ("√", "sqrt("), ("□²", "^2"), ("1", "1"), ("2", "2"), ("3", "3")],
        [("e^□", "e^("), ("|□|", "abs("), ("=", "="), ("0", "0"), (".", "."), ("⌫", "DEL")],
        [("(", "("), (")", ")"), ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/")]
    ]
    for r_idx, row in enumerate(keys):
        cols = st.columns(6) 
        for c_idx, (label, val) in enumerate(row):
            cols[c_idx].button(label, key=f"kb_{r_idx}_{c_idx}", on_click=k_click, args=(val,))
    st.button("مسح الكل (Clear)", on_click=k_click, args=("CLR",), use_container_width=True, type="primary")

x_sym, m_sym = sp.symbols('x m')
col1, col2 = st.columns(2)
with col1: st.text_input("أدخل عبارة الدالة f(x):", key="f_val")
with col2: st.text_input("أدخل معادلة المستقيم بدلالة m:", key="g_val")

try:
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    transformations = (standard_transformations + (implicit_multiplication_application,))
    local_dict = {'e': sp.E, 'pi': sp.pi, 'ln': sp.log, 'sqrt': sp.sqrt, 'abs': sp.Abs, 'cos': sp.cos, 'sin': sp.sin}
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
    st.latex(rf"\color{{#FFD700}} \begin{{cases}} f(x) = {sp.latex(f_expr).replace('log', 'ln')} \\ y = {sp.latex(g_expr).replace('log', 'ln')} \end{{cases}}")

    f_func = sp.lambdify(x_sym, f_expr, 'numpy')
    g_func = sp.lambdify((x_sym, m_sym), g_expr, 'numpy')
    
    x_vals_plot = np.linspace(-8, 8, 40001)
    x_vals_roots = np.concatenate([np.linspace(-500, -8, 5000, endpoint=False), np.linspace(-8, 8, 40001), np.linspace(8, 500, 5000)])
    
    def process_y_vals(x_arr):
        with np.errstate(divide='ignore', invalid='ignore'): y_arr = f_func(x_arr)
        if np.iscomplexobj(y_arr): y_arr = np.where(np.isreal(y_arr), y_arr.real, np.nan)
        if np.isscalar(y_arr): y_arr = np.full_like(x_arr, y_arr, dtype=float)
        dy = np.abs(np.diff(y_arr))
        for idx in np.where(dy > 30)[0]: y_arr[idx] = np.nan; y_arr[idx+1] = np.nan
        return y_arr

    y_vals_plot = process_y_vals(x_vals_plot)
    y_vals_roots = process_y_vals(x_vals_roots)

    # ---------------------------------------------------------
    # المحرك الجبري: استخراج القيم المظبوطة (Exact Symbolic Engine)
    # ---------------------------------------------------------
    sym_m_critical = []
    unique_asymptotes = []
    
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
    
    for r in candidate_v_asymptotes:
        unique_asymptotes.append({'type': 'v', 'val': float(sp.N(r)), 'label': f"x={sp.latex(r).replace('log', 'ln')}"})

    sym_extrema = []
    try:
        df_expr = sp.diff(f_expr, x_sym)
        for r in sp.solve(df_expr, x_sym):
            if r.is_real is not False and sp.im(sp.N(r)) == 0:
                sym_extrema.append(r)
                sym_m_critical.append(sp.simplify(f_expr.subs(x_sym, r)))
    except: pass
    sym_extrema = list(set(sym_extrema))

    pts_var_exact = []
    pts_var_exact.append({'val': -np.inf, 'sym': -sp.oo, 'latex_x': r"-\infty", 'type': 'inf'})
    
    for r in candidate_v_asymptotes:
        pts_var_exact.append({'val': float(sp.N(r)), 'sym': r, 'latex_x': sp.latex(r).replace('log', 'ln'), 'type': 'v_asym'})
        
    for r in sym_extrema:
        val = float(sp.N(r))
        if not any(abs(p['val'] - val) < 1e-4 for p in pts_var_exact):
            pts_var_exact.append({'val': val, 'sym': r, 'latex_x': sp.latex(r).replace('log', 'ln'), 'type': 'extrema'})
            
    pts_var_exact.append({'val': np.inf, 'sym': sp.oo, 'latex_x': r"+\infty", 'type': 'inf'})
    pts_var_exact.sort(key=lambda p: p['val'])

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
    for i in range(len(valid_intervals)):
        if valid_intervals[i]:
            l_b = "-\infty" if pts_var_exact[i]['val'] == -np.inf else pts_var_exact[i]['latex_x']
            r_b = "+\infty" if pts_var_exact[i+1]['val'] == np.inf else pts_var_exact[i+1]['latex_x']
            domain_intervals_str.append(fr"]{l_b}; {r_b}[")
            
    domain_latex = r"D_f = \color{#FFD700}{" + r" \cup ".join(domain_intervals_str) + r"}" if domain_intervals_str else r"D_f = \emptyset"

    # إضافة كل النهايات إلى القيم الحرجة (لكي يُقطع مجال المناقشة بدقة مثل الصفر)
    try:
        for direction in [sp.oo, -sp.oo]:
            lim = sp.limit(f_expr, x_sym, direction)
            if lim.is_real: sym_m_critical.append(lim)
    except: pass

    for p in pts_var_exact:
        if p['type'] == 'v_asym':
            idx = pts_var_exact.index(p)
            if idx > 0 and valid_intervals[idx-1]:
                try: 
                    lim = sp.limit(f_expr, x_sym, p['sym'], dir='-')
                    if lim.is_real: sym_m_critical.append(lim)
                except: pass
            if idx < len(valid_intervals) and valid_intervals[idx]:
                try: 
                    lim = sp.limit(f_expr, x_sym, p['sym'], dir='+')
                    if lim.is_real: sym_m_critical.append(lim)
                except: pass
    
    sym_m_critical = list(set(sym_m_critical))

    # ---------------------------------------------------------
    # شرح وحساب النهايات رياضياً (القيم المضبوطة)
    # ---------------------------------------------------------
    limits_data_detailed = []
    limits_mpl_list = []

    def get_limit_explanation(val_sym):
        if val_sym == sp.oo or val_sym == -sp.oo:
            return "نعتمد على الحد الأعلى درجة (للدوال الناطقة) أو نطبق مبرهنات التزايد المقارن للدوال الأسية واللوغاريتمية."
        return "إذا واجهنا حالة عدم تعيين بعد التعويض المباشر، نستخدم طرق الاختزال، التحليل، أو المبرهنات الشهيرة."

    def add_limit(val_sym, dir_sympy, dir_latex, ar_desc):
        try:
            lim = sp.limit(f_expr, x_sym, val_sym, dir=dir_sympy)
            lim_latex = sp.latex(lim).replace('log', 'ln')
            expr_latex = sp.latex(f_expr).replace('log', 'ln')
            
            explanation = get_limit_explanation(val_sym)
            latex_streamlit = fr"\lim_{{x \to {dir_latex}}} \left( {expr_latex} \right) = \mathbf{{\color{{#EF4444}}{{{lim_latex}}}}}"
            limits_data_detailed.append({'desc': ar_desc, 'explanation': explanation, 'latex': latex_streamlit})
            
            mpl_str = fr"\lim_{{x \to {dir_latex}}} f(x) = {lim_latex}"
            limits_mpl_list.append((ar_desc, mpl_str))
        except: pass

    if len(pts_var_exact) > 0:
        if pts_var_exact[0]['sym'] == -sp.oo: add_limit(-sp.oo, '+', r"-\infty", "النهاية عند الأطراف غير المنتهية:")
        if pts_var_exact[-1]['sym'] == sp.oo: add_limit(sp.oo, '-', r"+\infty", "النهاية عند الأطراف غير المنتهية:")

        for p in pts_var_exact:
            if p['type'] == 'v_asym':
                idx = pts_var_exact.index(p)
                v_latex = p['latex_x']
                if idx > 0 and valid_intervals[idx-1]:
                    add_limit(p['sym'], '-', fr"{v_latex}^-", f"النهاية بجوار القيمة الممنوعة ${v_latex}$ بقيم صغرى :")
                if idx < len(valid_intervals) and valid_intervals[idx]:
                    add_limit(p['sym'], '+', fr"{v_latex}^+", f"النهاية بجوار القيمة الممنوعة ${v_latex}$ بقيم كبرى :")

    def generate_limits_image():
        if not limits_mpl_list: return None
        n_lim = len(limits_mpl_list)
        fig_l, ax_l = plt.subplots(figsize=(6, max(1, n_lim * 0.8)))
        ax_l.axis('off')
        for i, (ar_desc, math_str) in enumerate(limits_mpl_list):
            y_pos = 1.0 - (i + 0.5) / n_lim
            clean_ar_desc = ar_desc.replace("$", "") 
            ax_l.text(0.95, y_pos, fix_arabic(clean_ar_desc), fontsize=14, ha='right', va='center', color='#1E3A8A', fontweight='bold')
            ax_l.text(0.4, y_pos, f"${math_str}$", fontsize=18, ha='right', va='center', color='#D32F2F')
        fig_l.tight_layout(pad=0)
        tmp_l = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig_l.savefig(tmp_l.name, bbox_inches='tight', dpi=300)
        plt.close(fig_l)
        return tmp_l.name

    limits_image_path = generate_limits_image()

    # ---------------------------------------------------------
    # بناء جدول التغيرات الاحترافي (Vector Graphic باستخدام Matplotlib)
    # ---------------------------------------------------------
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
                ax_v.plot([x_c, x_c], [0, 4], 'k:', lw=1, alpha=0.5, zorder=2)

            if i < N - 1:
                x_ic = x_c + (col_w / 2.0)
                if not valid_intervals[i]:
                    rect = plt.Rectangle((x_c, 0), col_w, 5, facecolor='#EF4444', alpha=0.7, zorder=1)
                    ax_v.add_patch(rect)
                else:
                    ax_v.text(x_ic, 4.5, f"${signs[i]}$", ha='center', va='center', fontsize=26, color='#D32F2F' if signs[i]=='-' else '#2E7D32')
            
            if p['type'] == 'inf':
                lim = sp.limit(f_expr, x_sym, p['sym'])
                dx = 0.5 if x_val == -np.inf else -0.5
                nodes.append((x_c+dx, float(sp.N(lim)) if lim.is_real else float('inf') if lim==sp.oo else float('-inf'), sp.latex(lim).replace('log','ln')))
            elif p['type'] == 'v_asym':
                if i > 0 and valid_intervals[i-1]:
                    lim_l = sp.limit(f_expr, x_sym, p['sym'], dir='-')
                    nodes.append((x_c-0.4, float(sp.N(lim_l)) if lim_l.is_real else float('inf') if lim_l==sp.oo else float('-inf'), sp.latex(lim_l).replace('log','ln')))
                if i < N-1 and valid_intervals[i]:
                    lim_r = sp.limit(f_expr, x_sym, p['sym'], dir='+')
                    nodes.append((x_c+0.4, float(sp.N(lim_r)) if lim_r.is_real else float('inf') if lim_r==sp.oo else float('-inf'), sp.latex(lim_r).replace('log','ln')))
            elif p['type'] == 'extrema':
                sym_y = sp.simplify(f_expr.subs(x_sym, p['sym']))
                nodes.append((x_c, float(sp.N(sym_y)), sp.latex(sym_y).replace('log','ln')))

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
                    
                    ax_v.text(l_node[0], y_l, f"${l_node[2]}$", ha='center', va='center', fontsize=16, color='#D32F2F', fontweight='bold')
                    ax_v.text(r_node[0], y_r, f"${r_node[2]}$", ha='center', va='center', fontsize=16, color='#D32F2F', fontweight='bold')
                    
                    pad_x, pad_y = 0.35, 0.4
                    start_x, end_x = l_node[0] + pad_x, r_node[0] - pad_x
                    start_y = y_l + (pad_y if signs[i]=="+" else -pad_y)
                    end_y = y_r + (-pad_y if signs[i]=="+" else pad_y)
                    if y_l == y_r: start_y = end_y = y_l
                    
                    ax_v.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=2.5))
        
        ax_v.set_xlim(0, x_max); ax_v.set_ylim(0, 6)
        fig_v.tight_layout(pad=0.2)
        tmp_v = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig_v.savefig(tmp_v.name, bbox_inches='tight', dpi=300)
        plt.close(fig_v)
        return tmp_v.name

    var_table_image_path = generate_variation_table_image()

    # ---------------------------------------------------------
    # المناقشة البيانية (استعمال القيم المضبوطة والمجالات الحقيقية)
    # ---------------------------------------------------------
    m_critical_num = []
    for sm in sym_m_critical:
        fl_m = float(sp.N(sm))
        if np.isfinite(fl_m) and abs(fl_m) < 50: m_critical_num.append(round(fl_m, 2))
        
    is_valid_plot = ~np.isnan(y_vals_plot)
    edges = np.diff(is_valid_plot.astype(int))
    starts = np.where(edges == 1)[0] + 1
    if is_valid_plot[0]: starts = np.insert(starts, 0, 0)
    ends = np.where(edges == -1)[0]
    if is_valid_plot[-1]: ends = np.append(ends, len(y_vals_plot) - 1)

    for s, e in zip(starts, ends):
        segment = y_vals_plot[s:e+1]
        if len(segment) > 10:
            peaks, _ = find_peaks(segment, prominence=0.05)
            valleys, _ = find_peaks(-segment, prominence=0.05)
            for p in peaks: m_critical_num.append(round(float(segment[p]), 2))
            for v in valleys: m_critical_num.append(round(float(segment[v]), 2))
            
    m_critical_num = sorted(list(set([round(m, 2) for m in m_critical_num if np.isfinite(m) and abs(m) < 50])))

    def get_exact_m(val_float):
        for sm in sym_m_critical:
            if abs(float(sp.N(sm)) - val_float) < 1e-2:
                return sp.latex(sm).replace('log', 'ln')
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
                if diff[i] * diff[i+1] < 0: crossings.append(x_vals_roots[i])
                elif diff[i] == 0: crossings.append(x_vals_roots[i])
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
            for i in range(1, len(abs_diff)-1):
                if np.isfinite(abs_diff[i-1]) and np.isfinite(abs_diff[i]) and np.isfinite(abs_diff[i+1]):
                    if abs_diff[i] < abs_diff[i-1] and abs_diff[i] < abs_diff[i+1] and abs_diff[i] < 0.1:
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

    final_table_data = []
    final_table_plain = [] 
    
    for L, H, sol_text in merged_intervals:
        L_inc = any(r[0] == L and r[1] == L and r[2] == sol_text for r in raw_intervals)
        H_inc = any(r[0] == H and r[1] == H and r[2] == sol_text for r in raw_intervals)
        
        L_latex = r"-\infty" if L == float('-inf') else get_exact_m(L)
        H_latex = r"+\infty" if H == float('inf') else get_exact_m(H)
        
        L_plain = "-∞" if L == float('-inf') else clean_latex_to_text(L_latex)
        H_plain = "+∞" if H == float('inf') else clean_latex_to_text(H_latex)
        
        # تصحيح الخطأ المطبعي H_latex بدلاً من L_latex في المجالات
        if L == float('-inf') and H == float('inf'):
            math_html = r"m \in \mathbb{R}"
            plain_m = "m ∈ R"
        elif L == float('-inf'):
            bracket_H = "]" if H_inc else "["
            math_html = fr"m \in ]-\infty ; {H_latex}{bracket_H}"
            plain_m = f"m ∈ ]-∞ ; {H_plain}{bracket_H}"
        elif H == float('inf'):
            bracket_L = "[" if L_inc else "]"
            math_html = fr"m \in {bracket_L}{L_latex} ; +\infty["
            plain_m = f"m ∈ {bracket_L}{L_plain} ; +∞["
        elif L == H:
            math_html = fr"m = {L_latex}"
            plain_m = f"m = {L_plain}"
        else:
            bracket_L = "[" if L_inc else "]"
            bracket_H = "]" if H_inc else "["
            math_html = fr"m \in {bracket_L}{L_latex} ; {H_latex}{bracket_H}"
            plain_m = f"m ∈ {bracket_L}{L_plain} ; {H_plain}{bracket_H}"
            
        final_table_data.append((f"${math_html}$", sol_text, L, H))
        final_table_plain.append((plain_m, sol_text))

    # ---------------------------------------------------------
    # دوال واجهة الويب وملف الـ PDF الملون
    # ---------------------------------------------------------
    def generate_html_table(current_m):
        html = "<table style='width:100%; border-collapse: collapse; text-align:center; font-size:18px; background-color:#1E293B;'>"
        html += "<tr style='border-bottom:2px solid #444;'> <th style='color:white; padding:10px;'>عدد وطبيعة الحلول</th> <th dir='ltr' style='color:white; padding:10px;'>المجال / القيمة</th> </tr>"
        active_idx = 0
        for idx, (math_html, sol_text, L, H) in enumerate(final_table_data):
            is_active = False
            if L == H and abs(current_m - L) <= 0.03: is_active = True
            elif L == float('-inf') and current_m <= H - 0.03: is_active = True
            elif H == float('inf') and current_m >= L + 0.03: is_active = True
            elif L + 0.03 <= current_m <= H - 0.03: is_active = True
            if is_active: active_idx = idx

        for idx, (math_html, sol_text, L, H) in enumerate(final_table_data):
            row_style = "border: 3px solid #FFD700; background-color: #334155; font-weight:bold;" if idx == active_idx else "border-bottom: 1px solid #334155;"
            html += f"<tr style='{row_style}'> <td style='padding:10px; color:{'#00E5FF' if idx == active_idx else '#A5F3FC'};'>{sol_text}</td> <td style='padding:10px; color:{'#FFD700' if idx == active_idx else '#FEF08A'}; font-family: Arial; font-size: 18px; white-space: nowrap;' dir='ltr'>{math_html}</td> </tr>"
        html += "</table>"
        return html

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
            
        pdf.add_page()
        pdf.add_font("Amiri", "", font_path, uni=True)
        pdf.set_font("Amiri", size=24)
        pdf.set_text_color(21, 101, 192)
        pdf.cell(0, 10, fix_arabic("الأستاذ سوايسية هشام - المناقشة البيانية"), ln=True, align='C')
        pdf.ln(5); pdf.image(fig_path, x=15, w=180); pdf.ln(5)
        
        pdf.set_font("Amiri", size=14)
        pdf.set_fill_color(30, 58, 138); pdf.set_text_color(255, 255, 255)
        pdf.cell(95, 12, fix_arabic("المجال / القيمة المضبوطة"), border=1, fill=True, align='C')
        pdf.cell(95, 12, fix_arabic("عدد وطبيعة الحلول"), border=1, ln=True, fill=True, align='C')
        
        for i, (m_str, text_str) in enumerate(final_table_plain):
            if i % 2 == 0:
                pdf.set_fill_color(241, 245, 249) 
            else:
                pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(95, 12, m_str, border=1, align='C', fill=True)
            pdf.cell(95, 12, fix_arabic(text_str), border=1, ln=True, align='C', fill=True)

        pdf.add_page()
        pdf.set_font("Amiri", size=20)
        pdf.set_text_color(21, 101, 192)
        pdf.cell(0, 15, fix_arabic("دراسة الدالة الشاملة (مستخرجة آلياً)"), ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Amiri", size=16)
        pdf.set_text_color(21, 101, 192)
        pdf.cell(0, 10, fix_arabic("1. استنتاج مجموعة التعريف وحساب النهايات:"), ln=True, align='R')
        pdf.ln(2)
        
        if limits_image_path:
            pdf.image(limits_image_path, x=20, w=170)
            pdf.ln(5)

        pdf.set_font("Amiri", size=16)
        pdf.set_text_color(21, 101, 192)
        pdf.cell(0, 10, fix_arabic("2. جدول التغيرات الرياضي بالقيم المضبوطة:"), ln=True, align='R')
        pdf.ln(5)
        
        if var_table_image_path:
            pdf.image(var_table_image_path, x=10, w=190)

        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(pdf_file.name)
        return pdf_file.name

    st.write("") 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("تشغيل المناقشة آلياً ▶️"):
            st.session_state.auto_play = True
            st.session_state.m_anim = -2.0
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
            if asym['type'] == 'h':
                ax.axhline(asym['val'], color='#D32F2F', linestyle='--', linewidth=2.2, zorder=4)
                ax.text(7.5, asym['val'] + 0.25, f"${asym['label']}$", color='#D32F2F', fontsize=14, fontweight='bold', ha='right')
            elif asym['type'] == 'v':
                ax.axvline(asym['val'], color='#D32F2F', linestyle='--', linewidth=2.2, zorder=4)
                ax.text(asym['val'] + 0.15, 6.5, f"${asym['label']}$", color='#D32F2F', fontsize=14, fontweight='bold', va='top')
        
        ax.plot(x_vals_plot, y_vals_plot, color='#2E7D32', linewidth=3.5, label='C_f', zorder=5)
        
        with np.errstate(divide='ignore', invalid='ignore'): y_g_plot = g_func(x_vals_plot, m_val)
        if np.isscalar(y_g_plot): y_g_plot = np.full_like(x_vals_plot, y_g_plot, dtype=float)
        
        m_val_str = str(int(m_val)) if int(m_val)==m_val else str(round(m_val, 2))
        m_eq_label = f"y = {m_val_str}" if st.session_state.g_val.strip() == 'm' else "y = " + st.session_state.g_val.replace('m', f"({m_val_str})" if m_val < 0 else m_val_str).replace('*', '')
            
        ax.plot(x_vals_plot, y_g_plot, color='#1565C0', linestyle='--', linewidth=3, label=f"${m_eq_label}$", zorder=5)
        
        diff_plot = y_vals_plot - y_g_plot
        intersect_x = []
        for i in range(len(diff_plot)-1):
            if np.isfinite(diff_plot[i]) and np.isfinite(diff_plot[i+1]):
                if diff_plot[i] * diff_plot[i+1] < 0:
                    denom = diff_plot[i+1] - diff_plot[i]
                    intersect_x.append(float(x_vals_plot[i] - diff_plot[i] * (x_vals_plot[i+1] - x_vals_plot[i]) / denom if denom != 0 else x_vals_plot[i]))
                elif diff_plot[i] == 0: intersect_x.append(float(x_vals_plot[i]))

        unique_intersect_x = []
        for ix in intersect_x:
            if not any(abs(ix - u) < 0.1 for u in unique_intersect_x): unique_intersect_x.append(ix)

        intersect_y = [m_val if st.session_state.g_val.strip() == 'm' else (float(g_func(ix, m_val)) if not np.isscalar(g_func(ix, m_val)) else g_func(ix, m_val)) for ix in unique_intersect_x]

        if unique_intersect_x: ax.scatter(unique_intersect_x, intersect_y, color='#FF8C00', s=130, zorder=6, edgecolor='black', linewidth=1.5, label='نقاط التقاطع')
        ax.text(4, m_val + 0.35, f"${m_eq_label}$", color='#1565C0', fontsize=15, fontweight='bold', ha='center', va='bottom', zorder=6)
        ax.set_ylim(-6, 8)
        legend = ax.legend(facecolor='#FFFFFF', edgecolor='#A0A0A0', loc='upper right', fontsize=12)
        for text in legend.get_texts(): text.set_color("black")
        fig.tight_layout()
        
        with placeholder.container():
            st.pyplot(fig, use_container_width=True)
            st.markdown(generate_html_table(m_val), unsafe_allow_html=True)
            
            with st.expander("📊 عرض دراسة الدالة الشاملة (مستخرجة آلياً)", expanded=False):
                st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>1. مجموعة التعريف والتبرير الرياضي للنهايات:</h4>", unsafe_allow_html=True)
                st.latex(domain_latex)
                
                for lim in limits_data_detailed:
                    st.markdown(f"<p style='color:#FFD700; text-align:right; direction:rtl; font-weight:normal; margin-bottom:5px;'>• {lim['desc']}<br><span style='color:#9CA3AF; font-size:14px;'>{lim['explanation']}</span></p>", unsafe_allow_html=True)
                    st.latex(lim['latex'])
                
                st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>2. جدول التغيرات الرياضي بالقيم المضبوطة:</h4>", unsafe_allow_html=True)
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
        while st.session_state.auto_play and st.session_state.m_anim <= 4.0:
            m_val = round(st.session_state.m_anim, 2)
            update_view(m_val)
            is_critical_now = any(abs(st.session_state.m_anim - mc) < 0.05 for mc in m_critical_num)
            if is_critical_now: time.sleep(2.0) 
            else: time.sleep(0.05)
            step = 0.1 
            next_m = st.session_state.m_anim + step
            for mc in m_critical_num:
                if st.session_state.m_anim < mc - 1e-4 and next_m >= mc - 1e-4:
                    next_m = float(mc); break
            st.session_state.m_anim = next_m
        st.session_state.auto_play = False
    else:
        m_val = st.slider("تحكم يدوي:", -2.0, 3.0, 0.0, 0.05, format="%g", key="manual_m")
        update_view(m_val)
