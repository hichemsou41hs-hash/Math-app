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

# استيراد مكتبات الـ PDF
try:
    from fpdf import FPDF
    import arabic_reshaper
    from bidi.algorithm import get_display
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

warnings.filterwarnings("ignore")

# 1. إعدادات الصفحة
st.set_page_config(page_title="المناقشة البيانية", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: white; }
    .title-hes { text-align: center; color: #FFFFFF !important; font-size: 36px; font-weight: bold; white-space: nowrap; margin-bottom: 0px;}
    .title-dis { text-align: center; color: #FFD700 !important; font-size: 28px; font-weight: bold; margin-top: -5px; margin-bottom: 30px;}
    
    label, p, div[data-testid="stRadio"] p, div[data-testid="stTextInput"] label p {
        font-weight: bold !important;
        font-size: 17px !important;
        color: #00E5FF !important;
    }

    .stTextInput label { direction: rtl !important; text-align: right !important; display: block;}
    .stTextInput > div > div > input { background-color: #1E293B; color: white; border: 1px solid #00E5FF; font-size: 18px; direction: ltr !important; }
    
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) {
        display: grid !important;
        grid-template-columns: repeat(6, 1fr) !important;
        gap: 5px !important;
        background-color: #1E293B !important; 
        padding: 5px !important;
        border-radius: 8px !important;
        margin-bottom: 2px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) > div[data-testid="column"] {
        width: 100% !important; min-width: 0 !important; max-width: 100% !important; flex: none !important; padding: 0 !important; display: block !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button {
        width: 100% !important; height: 48px !important; padding: 0px !important; margin: 0 !important; border-radius: 6px !important; background-color: #334155 !important; color: #00E5FF !important; border: 1px solid #475569 !important; box-shadow: 0 4px 0 #090e1a !important; transition: all 0.1s !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button div,
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button p,
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button span {
        font-size: 13px !important; font-family: Arial, Helvetica, sans-serif !important; font-weight: normal !important; letter-spacing: -0.5px !important; margin: 0 !important; padding: 0 !important; overflow: visible !important; text-overflow: clip !important; white-space: nowrap !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button:active {
        transform: translateY(4px) !important; box-shadow: 0 0 0 #090e1a !important; background-color: #00E5FF !important; color: #0F172A !important;
    }

    button[kind="primary"] {
        width: 100% !important; height: 50px !important; background-color: #ef4444 !important; color: white !important; font-size: 18px !important; font-weight: bold !important; border-radius: 8px !important; box-shadow: 0 4px 0 #7f1d1d !important; border: none !important; margin-top: 5px !important;
    }
    button[kind="primary"]:active {
        transform: translateY(4px) !important; box-shadow: 0 0 0 #7f1d1d !important; background-color: #dc2626 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-hes'>الأستاذ سوايسية هشام</div>", unsafe_allow_html=True)
st.markdown("<div class='title-dis'>المناقشة البيانية ودراسة الدالة</div>", unsafe_allow_html=True)

def fmt(val):
    if val == float('inf') or val == sp.oo: return "+∞"
    if val == float('-inf') or val == -sp.oo: return "-∞"
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
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# ---------------------------------------------------------
# 2. إدارة حالة التطبيق ولوحة المفاتيح
# ---------------------------------------------------------
if 'auto_play' not in st.session_state: st.session_state.auto_play = False
if 'm_anim' not in st.session_state: st.session_state.m_anim = -5.0
if 'f_val' not in st.session_state: st.session_state.f_val = "x*ln(x**2+x)"
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

# ---------------------------------------------------------
# 3. إدخال الدالة ومعادلة المناقشة
# ---------------------------------------------------------
x_sym, m_sym = sp.symbols('x m')

col1, col2 = st.columns(2)
with col1:
    st.text_input("أدخل عبارة الدالة f(x):", key="f_val")
with col2:
    st.text_input("أدخل معادلة المستقيم بدلالة m:", key="g_val")

manual_crit_input = st.text_input("🛡️ زر الأستاذ: أضف قيمة حرجة يدوياً (اختياري):", "")

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
    f_latex = sp.latex(f_expr).replace(r"\log", r"\ln")
    g_latex = sp.latex(g_expr).replace(r"\log", r"\ln")
    st.latex(rf"\color{{#FFD700}} \begin{{cases}} f(x) = {f_latex} \\ y = {g_latex} \end{{cases}}")

    f_func = sp.lambdify(x_sym, f_expr, 'numpy')
    g_func = sp.lambdify((x_sym, m_sym), g_expr, 'numpy')
    
    x_vals_plot = np.linspace(-8, 8, 40001)
    x_vals_roots = np.concatenate([
        np.linspace(-500, -8, 5000, endpoint=False),
        np.linspace(-8, 8, 40001),
        np.linspace(8, 500, 5000)
    ])
    
    def process_y_vals(x_arr):
        with np.errstate(divide='ignore', invalid='ignore'):
            y_arr = f_func(x_arr)
        if np.iscomplexobj(y_arr):
            y_arr = np.where(np.isreal(y_arr), y_arr.real, np.nan)
        if np.isscalar(y_arr):
            y_arr = np.full_like(x_arr, y_arr, dtype=float)
        dy = np.abs(np.diff(y_arr))
        jump_idx = np.where(dy > 30)[0] 
        for idx in jump_idx:
            y_arr[idx] = np.nan
            y_arr[idx+1] = np.nan
        return y_arr

    y_vals_plot = process_y_vals(x_vals_plot)
    y_vals_roots = process_y_vals(x_vals_roots)

    # ---------------------------------------------------------
    # 4. الرادار الذكي لاستخراج القيم الحرجة ودراسة الدالة
    # ---------------------------------------------------------
    unique_asymptotes = []
    m_critical = []
    x_extrema = [] 
    
    try:
        for direction in [sp.oo, -sp.oo]:
            lim_h = sp.limit(f_expr, x_sym, direction)
            if lim_h.is_real and np.isfinite(float(lim_h)):
                unique_asymptotes.append({'type': 'h', 'val': float(lim_h), 'label': f"y={fmt(lim_h)}"})
                m_critical.append(round(float(lim_h), 2))
    except: pass

    candidate_v_asymptotes = []
    try:
        n_expr, d_expr = sp.fraction(sp.cancel(f_expr))
        if d_expr != 1:
            roots = sp.solve(d_expr, x_sym)
            for r in roots:
                if r.is_real: candidate_v_asymptotes.append(float(r))
    except: pass
    try:
        for log_expr in f_expr.atoms(sp.log):
            arg = log_expr.args[0]
            roots = sp.solve(arg, x_sym)
            for r in roots:
                if r.is_real: candidate_v_asymptotes.append(float(r))
    except: pass

    for r in set(candidate_v_asymptotes):
        r_str = str(int(r)) if int(r)==r else str(float(r))
        unique_asymptotes.append({'type': 'v', 'val': float(r), 'label': f"x={r_str}"})
        try:
            lim_r = sp.limit(f_expr, x_sym, r, dir='+')
            if lim_r.is_real and np.isfinite(float(lim_r)): m_critical.append(round(float(lim_r), 2))
            lim_l = sp.limit(f_expr, x_sym, r, dir='-')
            if lim_l.is_real and np.isfinite(float(lim_l)): m_critical.append(round(float(lim_l), 2))
        except: pass

    seen_labels = set()
    final_asyms = []
    for asym in unique_asymptotes:
        if asym['label'] not in seen_labels:
            seen_labels.add(asym['label'])
            final_asyms.append(asym)
    unique_asymptotes = final_asyms

    is_valid = ~np.isnan(y_vals_plot)
    edges = np.diff(is_valid.astype(int))
    starts = np.where(edges == 1)[0] + 1
    if is_valid[0]: starts = np.insert(starts, 0, 0)
    ends = np.where(edges == -1)[0]
    if is_valid[-1]: ends = np.append(ends, len(y_vals_plot) - 1)
    
    for s, e in zip(starts, ends):
        segment = y_vals_plot[s:e+1]
        seg_x = x_vals_plot[s:e+1]
        if len(segment) > 10:
            peaks, _ = find_peaks(segment, prominence=0.05)
            valleys, _ = find_peaks(-segment, prominence=0.05)
            for p in peaks: 
                m_critical.append(round(float(segment[p]), 2))
                x_extrema.append(float(seg_x[p]))
            for v in valleys: 
                m_critical.append(round(float(segment[v]), 2))
                x_extrema.append(float(seg_x[v]))

    if manual_crit_input:
        try: m_critical.append(round(float(manual_crit_input.strip()), 2))
        except: pass

    m_critical = [round(m, 2) for m in m_critical if np.isfinite(m) and abs(m) < 50]
    m_critical.sort()
    merged_m_crit = []
    for m in m_critical:
        if not merged_m_crit: merged_m_crit.append(m)
        else:
            if abs(m - merged_m_crit[-1]) > 0.05: merged_m_crit.append(m)
    m_critical = merged_m_crit

    x_roots = []
    with np.errstate(divide='ignore', invalid='ignore'):
        diff_0 = y_vals_roots - 0
    for i in range(len(diff_0)-1):
        if np.isfinite(diff_0[i]) and np.isfinite(diff_0[i+1]):
            if diff_0[i] * diff_0[i+1] < 0: x_roots.append(float(x_vals_roots[i]))
            elif diff_0[i] == 0: x_roots.append(float(x_vals_roots[i]))
    
    unique_x_roots = []
    for ix in x_roots:
        if not any(abs(ix - u) < 0.1 for u in unique_x_roots):
            unique_x_roots.append(ix)

    # ---------------------------------------------------------
    # 5. بناء جداول (إتجاه التغير + الوضع النسبي + النهايات)
    # ---------------------------------------------------------
    v_asym_x = [v['val'] for v in unique_asymptotes if v['type'] == 'v']
    
    critical_x_var = sorted(list(set(x_extrema + v_asym_x)))
    var_table_data = []
    pts_var = [-np.inf] + critical_x_var + [np.inf]
    for i in range(len(pts_var)-1):
        left, right = pts_var[i], pts_var[i+1]
        if abs(right - left) < 1e-3: continue
        mid = 0 if (left == -np.inf and right == np.inf) else (right - 1 if left == -np.inf else (left + 1 if right == np.inf else (left + right) / 2))
        y_mid = f_func(mid)
        if not np.isfinite(y_mid): continue
        y_mid_plus = f_func(mid + 1e-5)
        state = "متزايدة تماما (+)" if y_mid_plus > y_mid else "متناقصة تماما (-)"
        var_table_data.append((left, right, state))

    critical_x_pos = sorted(list(set(unique_x_roots + v_asym_x)))
    pos_table_data = []
    pts_pos = [-np.inf] + critical_x_pos + [np.inf]
    for i in range(len(pts_pos)-1):
        left, right = pts_pos[i], pts_pos[i+1]
        if abs(right - left) < 1e-3: continue
        mid = 0 if (left == -np.inf and right == np.inf) else (right - 1 if left == -np.inf else (left + 1 if right == np.inf else (left + right) / 2))
        y_mid = f_func(mid)
        if not np.isfinite(y_mid): continue
        state = "فوق محور الفواصل (+)" if y_mid > 0 else "تحت محور الفواصل (-)"
        pos_table_data.append((left, right, state))

    limits_data = []
    for asym in unique_asymptotes:
        if asym['type'] == 'h': limits_data.append((f"y = {asym['val']}", "مقارب أفقي عند المالانهاية"))
        elif asym['type'] == 'v': limits_data.append((f"x = {asym['val']}", "مقارب عمودي (النهاية ±∞)"))
    if not limits_data: limits_data.append(("±∞", "تؤول النهايات إلى المالانهاية عند أطراف مجموعة التعريف"))

    # ---------------------------------------------------------
    # 6. تصنيف الحلول الصارم للمناقشة البيانية 
    # ---------------------------------------------------------
    def get_roots_text(m_test):
        is_critical = any(abs(m_test - mc) < 1e-2 for mc in m_critical)
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
                if skip:
                    skip = False; continue
                if i < len(crossings)-1 and abs(crossings[i+1] - crossings[i]) < 0.5:
                    tangents.append((crossings[i] + crossings[i+1])/2.0)
                    skip = True
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
    if len(m_critical) > 0:
        raw_intervals.append((float('-inf'), m_critical[0], get_roots_text(m_critical[0] - 0.5)))
        for i in range(len(m_critical)):
            raw_intervals.append((m_critical[i], m_critical[i], get_roots_text(m_critical[i])))
            if i < len(m_critical) - 1:
                mid = (m_critical[i] + m_critical[i+1]) / 2.0
                raw_intervals.append((m_critical[i], m_critical[i+1], get_roots_text(mid)))
        raw_intervals.append((m_critical[-1], float('inf'), get_roots_text(m_critical[-1] + 0.5)))
    else: raw_intervals.append((float('-inf'), float('inf'), get_roots_text(0.0)))

    merged_intervals = []
    if raw_intervals:
        cur_L, cur_H, cur_text = raw_intervals[0][0], raw_intervals[0][1], raw_intervals[0][2]
        for item in raw_intervals[1:]:
            l, h, txt = item[0], item[1], item[2]
            if txt == cur_text: cur_H = h
            else:
                merged_intervals.append((cur_L, cur_H, cur_text))
                cur_L, cur_H, cur_text = l, h, txt
        merged_intervals.append((cur_L, cur_H, cur_text))

    final_table_data = []
    final_table_plain = [] 
    
    for L, H, sol_text in merged_intervals:
        L_inc = any(r[0] == L and r[1] == L and r[2] == sol_text for r in raw_intervals)
        H_inc = any(r[0] == H and r[1] == H and r[2] == sol_text for r in raw_intervals)
        
        if L == float('-inf') and H == float('inf'):
            math_html = "<i>m</i> ∈ ℝ"
            plain_m = "m ∈ R"
        elif L == float('-inf'):
            math_html = f"<i>m</i> ≤ {fmt(H)}" if H_inc else f"<i>m</i> < {fmt(H)}"
            plain_m = f"m <= {fmt(H)}" if H_inc else f"m < {fmt(H)}"
        elif H == float('inf'):
            math_html = f"<i>m</i> ≥ {fmt(L)}" if L_inc else f"<i>m</i> > {fmt(L)}"
            plain_m = f"m >= {fmt(L)}" if L_inc else f"m > {fmt(L)}"
        elif L == H:
            math_html = f"<i>m</i> = {fmt(L)}"
            plain_m = f"m = {fmt(L)}"
        else:
            ls = "≤" if L_inc else "<"
            rs = "≤" if H_inc else "<"
            math_html = f"{fmt(L)} {ls} <i>m</i> {rs} {fmt(H)}"
            ls_p = "<=" if L_inc else "<"
            rs_p = "<=" if H_inc else "<"
            plain_m = f"{fmt(L)} {ls_p} m {rs_p} {fmt(H)}"
            
        final_table_data.append((math_html, sol_text, L, H))
        final_table_plain.append((plain_m, sol_text))

    # ---------------------------------------------------------
    # 7. دوال واجهة الويب وملف الـ PDF الآمن
    # ---------------------------------------------------------
    def generate_html_table(current_m):
        html = "<table style='width:100%; border-collapse: collapse; text-align:center; font-size:18px; background-color:#1E293B;'>"
        html += "<tr style='border-bottom:2px solid #444;'> <th style='color:white; padding:10px;'>عدد وطبيعة الحلول</th> <th dir='ltr' style='color:white; padding:10px;'>المجال / القيمة</th> </tr>"
        active_idx = 0
        for idx, (math_html, sol_text, L, H) in enumerate(final_table_data):
            is_active = False
            if L == H:
                if abs(current_m - L) <= 0.03: is_active = True
            elif L == float('-inf'):
                if current_m <= H - 0.03: is_active = True
            elif H == float('inf'):
                if current_m >= L + 0.03: is_active = True
            else:
                if L + 0.03 <= current_m <= H - 0.03: is_active = True
            if is_active: active_idx = idx

        for idx, (math_html, sol_text, L, H) in enumerate(final_table_data):
            is_active = (idx == active_idx)
            row_style = "border: 3px solid #FFD700; background-color: #334155; font-weight:bold;" if is_active else "border-bottom: 1px solid #334155;"
            text_color_sol = "#00E5FF" if is_active else "#A5F3FC"  
            text_color_m = "#FFD700" if is_active else "#FEF08A"    
            html += f"<tr style='{row_style}'> <td style='padding:10px; color:{text_color_sol};'>{sol_text}</td> <td style='padding:10px; color:{text_color_m}; font-family: \"Times New Roman\", Times, serif; font-size: 18px; white-space: nowrap;' dir='ltr'>{math_html}</td> </tr>"
        html += "</table>"
        return html

    def generate_study_html():
        html = "<div style='background-color:#1E293B; padding:15px; border-radius:10px; margin-top:10px;'>"
        html += "<h4 style='color:#00E5FF; text-align:right;'>1. النهايات والمقاربات:</h4><ul style='text-align:right; direction:rtl; color:white;'>"
        for math_str, ar_str in limits_data:
            html += f"<li>{ar_str} : <b style='color:#FFD700;' dir='ltr'>{math_str}</b></li>"
        html += "</ul>"
        
        html += "<h4 style='color:#00E5FF; text-align:right;'>2. جدول إتجاه التغير:</h4>"
        html += "<table style='width:100%; text-align:center; background-color:#0F172A; border-collapse: collapse;' dir='rtl'>"
        html += "<tr style='background-color:#334155; color:white;'><th style='padding:8px; border:1px solid #444;'>المجال</th><th style='padding:8px; border:1px solid #444;'>إتجاه التغير</th></tr>"
        for L, R, state in var_table_data:
            L_str = "-∞" if L == -np.inf else fmt(L)
            R_str = "+∞" if R == np.inf else fmt(R)
            html += f"<tr><td dir='ltr' style='padding:8px; border:1px solid #444; color:#FFD700;'>] {L_str} , {R_str} [</td><td style='padding:8px; border:1px solid #444; color:white;'>{state}</td></tr>"
        html += "</table><br>"
        
        html += "<h4 style='color:#00E5FF; text-align:right;'>3. جدول الوضع النسبي (مع محور الفواصل):</h4>"
        html += "<table style='width:100%; text-align:center; background-color:#0F172A; border-collapse: collapse;' dir='rtl'>"
        html += "<tr style='background-color:#334155; color:white;'><th style='padding:8px; border:1px solid #444;'>المجال</th><th style='padding:8px; border:1px solid #444;'>الوضع النسبي</th></tr>"
        for L, R, state in pos_table_data:
            L_str = "-∞" if L == -np.inf else fmt(L)
            R_str = "+∞" if R == np.inf else fmt(R)
            html += f"<tr><td dir='ltr' style='padding:8px; border:1px solid #444; color:#FFD700;'>] {L_str} , {R_str} [</td><td style='padding:8px; border:1px solid #444; color:white;'>{state}</td></tr>"
        html += "</table></div>"
        return html

    def generate_pdf(fig_path):
        if not PDF_ENABLED: return None
        
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        font_path = "Amiri-Regular.ttf"
        
        # تحميل آمن للخط لتجاوز حظر GitHub
        if not os.path.exists(font_path) or os.path.getsize(font_path) < 10000:
            try:
                req = urllib.request.Request(
                    "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf",
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req) as response, open(font_path, 'wb') as out_file:
                    out_file.write(response.read())
            except: pass
            
        if not os.path.exists(font_path) or os.path.getsize(font_path) < 10000:
            st.error("⚠️ خطأ في تحميل الخط العربي. يرجى التأكد من اتصال خوادم المنصة.")
            return None
            
        pdf.add_page()
        pdf.add_font("Amiri", "", font_path, uni=True)
        pdf.set_font("Amiri", size=24)
            
        pdf.set_text_color(21, 101, 192)
        title = fix_arabic("الأستاذ سوايسية هشام - المناقشة البيانية")
        pdf.cell(0, 10, title, ln=True, align='C')
        pdf.ln(5)
        
        pdf.image(fig_path, x=15, w=180)
        pdf.ln(5)
        
        # استخدام خط Amiri للجدول لحل مشكلة الترميز
        pdf.set_font("Amiri", size=14)
        pdf.set_fill_color(30, 58, 138) 
        pdf.set_text_color(255, 255, 255)
        pdf.cell(95, 12, fix_arabic("المجال / القيمة"), border=1, fill=True, align='C')
        pdf.cell(95, 12, fix_arabic("عدد وطبيعة الحلول"), border=1, ln=True, fill=True, align='C')
        
        for i, (m_str, text_str) in enumerate(final_table_plain):
            pdf.set_fill_color(241, 245, 249) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(95, 12, m_str, border=1, align='C', fill=True)
            pdf.cell(95, 12, fix_arabic(text_str), border=1, ln=True, align='C', fill=True)

        # الصفحة الثانية
        pdf.add_page()
        pdf.set_font("Amiri", size=20)
        pdf.set_text_color(21, 101, 192)
        pdf.cell(0, 15, fix_arabic("دراسة الدالة الشاملة (مستخرجة آلياً)"), ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Amiri", size=16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, fix_arabic("1. النهايات والمقاربات:"), ln=True, align='R')
        
        # تصحيح خطأ الترميز: إجبار استخدام Amiri في جميع أنحاء المستند
        pdf.set_font("Amiri", size=14)
        for math_str, ar_str in limits_data:
            text_line = math_str + "  :  " + fix_arabic(ar_str)
            pdf.cell(0, 8, text_line, ln=True, align='R')
        pdf.ln(5)

        def draw_study_table(title, headers, data_rows):
            pdf.set_font("Amiri", size=16)
            pdf.set_text_color(21, 101, 192)
            pdf.cell(0, 10, fix_arabic(title), ln=True, align='R')
            
            pdf.set_font("Amiri", size=14)
            pdf.set_fill_color(30, 58, 138)
            pdf.set_text_color(255, 255, 255)
            
            col_width = 190 / len(headers)
            pdf.cell(col_width, 10, fix_arabic(headers[0]), border=1, fill=True, align='C')
            pdf.cell(col_width, 10, fix_arabic(headers[1]), border=1, ln=True, fill=True, align='C')
            
            pdf.set_text_color(15, 23, 42)
            for i, row in enumerate(data_rows):
                pdf.set_fill_color(241, 245, 249) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
                L, R, state = row
                L_str = "-∞" if L == -np.inf else fmt(L)
                R_str = "+∞" if R == np.inf else fmt(R)
                domain_str = f"] {L_str} , {R_str} ["
                
                pdf.cell(col_width, 10, fix_arabic(state), border=1, fill=True, align='C')
                pdf.cell(col_width, 10, domain_str, border=1, ln=True, fill=True, align='C')
            pdf.ln(5)

        draw_study_table("2. جدول إتجاه التغير:", ["إتجاه التغير", "المجال"], var_table_data)
        draw_study_table("3. جدول الوضع النسبي (مع محور الفواصل):", ["الوضع النسبي", "المجال"], pos_table_data)

        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(pdf_file.name)
        return pdf_file.name

    # ---------------------------------------------------------
    # 8. عرض التطبيق
    # ---------------------------------------------------------
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
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')
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
        
        with np.errstate(divide='ignore', invalid='ignore'):
            y_g_plot = g_func(x_vals_plot, m_val)
        if np.isscalar(y_g_plot): y_g_plot = np.full_like(x_vals_plot, y_g_plot, dtype=float)
        
        m_val_str = str(int(m_val)) if int(m_val)==m_val else str(round(m_val, 2))
        if st.session_state.g_val.strip() == 'm': m_eq_label = f"y = {m_val_str}"
        else:
            rep_str = f"({m_val_str})" if m_val < 0 else m_val_str
            m_eq_label = "y = " + st.session_state.g_val.replace('m', rep_str).replace('*', '')
            
        ax.plot(x_vals_plot, y_g_plot, color='#1565C0', linestyle='--', linewidth=3, label=f"${m_eq_label}$", zorder=5)
        
        diff_plot = y_vals_plot - y_g_plot
        intersect_x = []
        for i in range(len(diff_plot)-1):
            if np.isfinite(diff_plot[i]) and np.isfinite(diff_plot[i+1]):
                if diff_plot[i] * diff_plot[i+1] < 0:
                    denom = diff_plot[i+1] - diff_plot[i]
                    xi = x_vals_plot[i] - diff_plot[i] * (x_vals_plot[i+1] - x_vals_plot[i]) / denom if denom != 0 else x_vals_plot[i]
                    intersect_x.append(float(xi))
                elif diff_plot[i] == 0: intersect_x.append(float(x_vals_plot[i]))

        unique_intersect_x = []
        for ix in intersect_x:
            if not any(abs(ix - uix) < 0.1 for uix in unique_intersect_x): unique_intersect_x.append(ix)

        intersect_y = []
        for ix in unique_intersect_x:
            if st.session_state.g_val.strip() == 'm': intersect_y.append(m_val)
            else:
                yt = g_func(ix, m_val)
                intersect_y.append(float(yt) if not np.isscalar(yt) else yt)

        if unique_intersect_x:
            ax.scatter(unique_intersect_x, intersect_y, color='#FF8C00', s=130, zorder=6, edgecolor='black', linewidth=1.5, label='نقاط التقاطع')

        ax.text(4, m_val + 0.35, f"${m_eq_label}$", color='#1565C0', fontsize=15, fontweight='bold', ha='center', va='bottom', zorder=6)

        ax.set_ylim(-6, 8)
        legend = ax.legend(facecolor='#FFFFFF', edgecolor='#A0A0A0', loc='upper right', fontsize=12)
        for text in legend.get_texts(): text.set_color("black")
        fig.tight_layout()
        
        with placeholder.container():
            st.pyplot(fig, use_container_width=True)
            st.markdown(generate_html_table(m_val), unsafe_allow_html=True)
            
            with st.expander("📊 عرض دراسة الدالة الشاملة (مستخرجة آلياً)", expanded=False):
                st.markdown(generate_study_html(), unsafe_allow_html=True)
            
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
            is_critical_now = any(abs(st.session_state.m_anim - mc) < 0.05 for mc in m_critical)
            if is_critical_now: time.sleep(2.0) 
            else: time.sleep(0.05)
            step = 0.1 
            next_m = st.session_state.m_anim + step
            for mc in m_critical:
                if st.session_state.m_anim < mc - 1e-4 and next_m >= mc - 1e-4:
                    next_m = float(mc)
                    break
            st.session_state.m_anim = next_m
        st.session_state.auto_play = False
    else:
        m_val = st.slider("تحكم يدوي:", -2.0, 3.0, 0.0, 0.05, format="%g", key="manual_m")
        update_view(m_val)
