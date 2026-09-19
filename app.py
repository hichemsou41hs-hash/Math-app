import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import time
import warnings

# تجاهل التحذيرات الرياضية
warnings.filterwarnings("ignore")

# 1. إعدادات الصفحة
st.set_page_config(page_title="المناقشة البيانية", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: white; }
    .title-hes { text-align: center; color: #FFFFFF !important; font-size: 34px; font-weight: bold; margin-bottom: 0px;}
    .title-dis { text-align: center; color: #FFD700 !important; font-size: 26px; font-weight: bold; margin-top: -5px; margin-bottom: 20px;}
    .stTextInput label { color: #00E5FF !important; font-size: 18px !important; font-weight: bold !important; direction: rtl !important; text-align: right !important; display: block;}
    .stTextInput > div > div > input { background-color: #1E293B; color: white; border: 1px solid #00E5FF; font-size: 18px; direction: ltr !important; }
    
    /* تحسين مظهر أزرار لوحة المفاتيح لتكون مريحة بالهاتف */
    .stButton > button {
        width: 100% !important;
        height: 45px !important;
        border-radius: 8px !important;
        background-color: #334155 !important;
        color: #A5F3FC !important;
        font-size: 17px !important;
        font-weight: bold !important;
        border: 1px solid #475569 !important;
    }
    .stButton > button:active {
        background-color: #00E5FF !important;
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-hes'>الأستاذ سوايسية هشام</div>", unsafe_allow_html=True)
st.markdown("<div class='title-dis'>المناقشة البيانية</div>", unsafe_allow_html=True)

def fmt(val):
    if val == float('inf'): return "+∞"
    if val == float('-inf'): return "-∞"
    if int(val) == val: return str(int(val))
    return str(val)

# ---------------------------------------------------------
# 2. إدارة حالة التطبيق
# ---------------------------------------------------------
if 'auto_play' not in st.session_state: st.session_state.auto_play = False
if 'm_anim' not in st.session_state: st.session_state.m_anim = -5.0
if 'f_val' not in st.session_state: st.session_state.f_val = "ln(x)-ln(x+1)"
if 'g_val' not in st.session_state: st.session_state.g_val = "m*x+1"
if 'kbd_target' not in st.session_state: st.session_state.kbd_target = "f"

def add_to_input(val):
    target = "f_val" if st.session_state.kbd_target == "فقط f(x)" else "g_val"
    if val == 'DEL':
        st.session_state[target] = st.session_state[target][:-1]
    elif val == 'CLR':
        st.session_state[target] = ""
    else:
        st.session_state[target] += val

with st.expander("⌨️ لوحة المفاتيح الرياضية السريعة", expanded=False):
    st.session_state.kbd_target = st.radio("إضافة إلى:", ["فقط f(x)", "معادلة المستقيم m"], horizontal=True)
    
    # صفوف أزرار منظمة لا تتكسر في الهاتف
    r1 = [("𝑥", "x"), ("𝑦", "y"), ("𝑒", "e"), ("ln", "ln("), ("+", "+"), ("-", "-")]
    r2 = [("𝑚", "m"), ("𝜋", "pi"), ("√", "sqrt("), ("^2", "^2"), ("×", "*"), ("÷", "/")]
    r3 = [("(", "("), (")", ")"), ("<", "<"), (">", ">"), ("=", "="), (".", ".")]
    r4 = [("7", "7"), ("8", "8"), ("9", "9"), ("4", "4"), ("5", "5"), ("6", "6")]
    r5 = [("1", "1"), ("2", "2"), ("3", "3"), ("0", "0"), ("⌫ حذف", "DEL"), ("🧹 مسح", "CLR")]

    for row in [r1, r2, r3, r4, r5]:
        cols = st.columns(len(row))
        for idx, (lbl, val) in enumerate(row):
            cols[idx].button(lbl, key=f"btn_{val}_{idx}", on_click=add_to_input, args=(val,))

# ---------------------------------------------------------
# 3. إدخال الدوال
# ---------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    st.text_input("الدالة f(x):", key="f_val")
with col2:
    st.text_input("المستقيم g(x):", key="g_val")

try:
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    transformations = (standard_transformations + (implicit_multiplication_application,))
    local_dict = {'e': sp.E, 'pi': sp.pi, 'ln': sp.log, 'sqrt': sp.sqrt, 'abs': sp.Abs}
    f_expr = parse_expr(st.session_state.f_val.replace('^', '**'), local_dict=local_dict, transformations=transformations)
    g_expr = parse_expr(st.session_state.g_val.replace('^', '**'), local_dict=local_dict, transformations=transformations)
    valid_input = True
except:
    st.error("⚠️ صيغة غير صالحة أو الخانة فارغة.")
    valid_input = False

if valid_input:
    f_latex = sp.latex(f_expr).replace(r"\log", r"\ln")
    g_latex = sp.latex(g_expr).replace(r"\log", r"\ln")
    st.latex(rf"\color{{#FFD700}} \begin{{cases}} f(x) = {f_latex} \\ y = {g_latex} \end{{cases}}")

    f_func = sp.lambdify(x_sym := sp.symbols('x'), f_expr, 'numpy')
    g_func = sp.lambdify((x_sym, m_sym := sp.symbols('m')), g_expr, 'numpy')
    
    x_vals = np.linspace(-8, 8, 3000)
    with np.errstate(divide='ignore', invalid='ignore'):
        y_vals = f_func(x_vals)
    
    if np.iscomplexobj(y_vals): y_vals = np.where(np.isreal(y_vals), y_vals.real, np.nan)
    if np.isscalar(y_vals): y_vals = np.full_like(x_vals, y_vals, dtype=float)

    dy = np.abs(np.diff(y_vals))
    jump_idx = np.where(dy > 10)[0]
    for idx in jump_idx:
        y_vals[idx] = np.nan
        y_vals[idx+1] = np.nan

    # ---------------------------------------------------------
    # 4. حساب المقاربات والقيّم المميزة
    # ---------------------------------------------------------
    asymptotes = []
    for direction in [sp.oo, -sp.oo]:
        try:
            lim_h = sp.limit(f_expr, x_sym, direction)
            if lim_h.is_real and np.isfinite(float(lim_h)):
                val_str = "+∞" if lim_h == sp.oo else ("-∞" if lim_h == -sp.oo else str(int(lim_h) if int(lim_h)==lim_h else float(lim_h)))
                asymptotes.append({'type': 'h', 'val': float(lim_h), 'label': f"y={val_str}"})
                continue
            a_lim = sp.limit(f_expr / x_sym, x_sym, direction)
            if a_lim.is_real and a_lim != 0 and np.isfinite(float(a_lim)):
                b_lim = sp.limit(f_expr - a_lim * x_sym, x_sym, direction)
                if b_lim.is_real and np.isfinite(float(b_lim)):
                    a_val, b_val = float(a_lim), float(b_lim)
                    a_str = str(int(abs(a_val))) if int(abs(a_val))==abs(a_val) else str(abs(a_val))
                    if a_str == "1": a_str = ""
                    sign_a = "-" if a_val < 0 else ""
                    b_str = f" {('+' if b_val>0 else '-')} {str(int(abs(b_val))) if int(abs(b_val))==abs(b_val) else str(abs(b_val))}" if b_val != 0 else ""
                    asymptotes.append({'type': 'o', 'a': a_val, 'b': b_val, 'label': f"y={sign_a}{a_str}x{b_str}"})
        except: pass
        
    candidate_v_asymptotes = []
    try:
        n_expr, d_expr = sp.fraction(sp.cancel(f_expr))
        if d_expr != 1:
            for r in sp.solve(d_expr, x_sym):
                if r.is_real: candidate_v_asymptotes.append(float(r))
    except: pass
    
    try:
        for log_expr in f_expr.atoms(sp.log):
            for r in sp.solve(log_expr.args[0], x_sym):
                if r.is_real: candidate_v_asymptotes.append(float(r))
    except: pass

    for r in set(candidate_v_asymptotes):
        is_valid = False
        for test_pt in [r + 1e-5, r - 1e-5]:
            try:
                val = complex(f_func(test_pt))
                if val.imag == 0 and not np.isnan(val.real): is_valid = True; break
            except: pass
        if is_valid:
            asymptotes.append({'type': 'v', 'val': float(r), 'label': f"x={fmt(r)}"})

    unique_asymptotes, seen_labels = [], set()
    for asym in asymptotes:
        if asym['label'] not in seen_labels:
            seen_labels.add(asym['label'])
            unique_asymptotes.append(asym)

    m_critical = []
    try:
        for px in sp.solve(sp.diff(g_expr, m_sym), x_sym):
            if np.isreal(complex(px)):
                for m_sol in sp.solve(sp.diff(f_expr, x_sym).subs(x_sym, px) - sp.diff(g_expr, x_sym).subs(x_sym, px), m_sym):
                    m_critical.append(round(float(m_sol), 2))
    except: pass
    
    try:
        m_sols = sp.solve(f_expr - g_expr, m_sym)
        if m_sols:
            H_func = sp.lambdify(x_sym, m_sols[0], 'numpy')
            m_critical.extend([round(float(H_func(-1000)), 1), round(float(H_func(1000)), 1)])
    except: pass

    m_critical = np.unique([m for m in m_critical if np.isfinite(m) and abs(m) < 20])
    m_critical.sort()

    def get_roots_text(m_test):
        with np.errstate(divide='ignore', invalid='ignore'):
            y_g = g_func(x_vals, m_test)
            if np.isscalar(y_g): y_g = np.full_like(x_vals, y_g, dtype=float)
            diff = y_vals - y_g
            
        crossings, tangents = [], []
        for i in range(len(diff)-1):
            if np.isfinite(diff[i]) and np.isfinite(diff[i+1]):
                if diff[i] * diff[i+1] < 0: crossings.append(i)
                elif diff[i] == 0: crossings.append(i)
        
        abs_diff = np.abs(diff)
        for i in range(1, len(abs_diff)-1):
            if np.isfinite(abs_diff[i-1]) and np.isfinite(abs_diff[i]) and np.isfinite(abs_diff[i+1]):
                if abs_diff[i] < abs_diff[i-1] and abs_diff[i] < abs_diff[i+1] and abs_diff[i] < 0.1:
                    if not any(abs(i - c) < 20 for c in crossings): tangents.append(i)
                                
        raw_roots = [(x_vals[c], "single") for c in crossings] + [(x_vals[t], "double") for t in tangents]
        all_roots = []
        for r, t in raw_roots:
            if not any(abs(r - fr) < 0.15 for fr, ft in all_roots): all_roots.append((r, t))
        
        if len(all_roots) == 0: return "لا توجد حلول"
        
        pos_s = sum(1 for r, t in all_roots if r > 0.05 and t == "single")
        neg_s = sum(1 for r, t in all_roots if r < -0.05 and t == "single")
        zero_s = sum(1 for r, t in all_roots if abs(r) <= 0.05 and t == "single")
        pos_d = sum(1 for r, t in all_roots if r > 0.05 and t == "double")
        neg_d = sum(1 for r, t in all_roots if r < -0.05 and t == "double")
        
        desc = []
        if pos_d == 1: desc.append("حل مضاعف موجب")
        if neg_d == 1: desc.append("حل مضاعف سالب")
        if pos_s == 1: desc.append("حل موجب")
        elif pos_s == 2: desc.append("حلان موجبان")
        elif pos_s > 2: desc.append(f"{pos_s} حلول موجبة")
        if neg_s == 1: desc.append("حل سالب")
        elif neg_s == 2: desc.append("حلان سالبان")
        elif neg_s > 2: desc.append(f"{neg_s} حلول سالبة")
        if zero_s == 1: desc.append("حل معدوم")
        
        if pos_s == 1 and neg_s == 1 and len(desc) == 2: return "حلان مختلفان في الإشارة"
        return " و ".join(desc)

    raw_intervals = []
    if len(m_critical) > 0:
        raw_intervals.append((float('-inf'), m_critical[0], get_roots_text(m_critical[0] - 1)))
        for i in range(len(m_critical)):
            raw_intervals.append((m_critical[i], m_critical[i], get_roots_text(m_critical[i])))
            if i < len(m_critical) - 1:
                raw_intervals.append((m_critical[i], m_critical[i+1], get_roots_text((m_critical[i] + m_critical[i+1]) / 2.0)))
        raw_intervals.append((m_critical[-1], float('inf'), get_roots_text(m_critical[-1] + 1)))
    else:
        raw_intervals.append((float('-inf'), float('inf'), get_roots_text(0)))

    merged_intervals = []
    if raw_intervals:
        current_group = [raw_intervals[0]]
        for item in raw_intervals[1:]:
            if item[2] == current_group[-1][2]: current_group.append(item)
            else: merged_intervals.append(current_group); current_group = [item]
        merged_intervals.append(current_group)

    final_table_data = []
    for g in merged_intervals:
        sol_text, L, H = g[0][2], g[0][0], g[-1][1]
        include_L, include_H = (g[0][0] == g[0][1]), (g[-1][0] == g[-1][1]) 

        if L == float('-inf') and H == float('inf'): math_html = "<i>m</i> ∈ ℝ"
        elif L == H: math_html = f"<i>m</i> = {fmt(L)}"
        else:
            math_html = f"<i>m</i> ∈ {('[' if include_L else ']')}{fmt(L)}; {fmt(H)}{(']' if include_H else '[')}"
        final_table_data.append((math_html, sol_text, g)) 

    def generate_html_table(current_m):
        html = "<table style='width:100%; border-collapse: collapse; text-align:center; font-size:17px; background-color:#1E293B;'>"
        html += "<tr style='border-bottom:2px solid #444;'> <th style='color:white; padding:8px;'>الإشارة وعدد الحلول</th> <th dir='ltr' style='color:white; padding:8px;'>المجال / القيمة</th> </tr>"
        for math_html, sol_text, g in final_table_data:
            is_active = False
            for low, high, _ in g:
                if low == high:
                    if abs(current_m - low) < 0.15: is_active = True
                else:
                    if low == float('-inf') and current_m < high - 0.15: is_active = True
                    elif high == float('inf') and current_m > low + 0.15: is_active = True
                    elif low + 0.15 <= current_m <= high - 0.15: is_active = True

            row_style = "border: 3px solid #FFD700; background-color: #334155; font-weight:bold;" if is_active else "border-bottom: 1px solid #334155;"
            html += f"<tr style='{row_style}'> <td style='padding:8px; color:{('#00E5FF' if is_active else '#A5F3FC')};'>{sol_text}</td> <td style='padding:8px; color:{('#FFD700' if is_active else '#FEF08A')};' dir='ltr'>{math_html}</td> </tr>"
        html += "</table>"
        return html

    st.write("") 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("تشغيل المناقشة آلياً ▶️"):
            st.session_state.auto_play = True
            st.session_state.m_anim = -6.0
            st.rerun()
    with col2:
        if st.button("إيقاف ⏹️"):
            st.session_state.auto_play = False
            st.rerun()

    placeholder = st.empty()

    def update_view(m_val):
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#0F172A')
        ax.set_facecolor('#0F172A')
        ax.tick_params(colors='white')
        
        for spine in ax.spines.values(): spine.set_edgecolor('none')
        ax.axhline(0, color='#9CA3AF', linewidth=1.5) 
        ax.axvline(0, color='#9CA3AF', linewidth=1.5) 
        
        for asym in unique_asymptotes:
            if asym['type'] == 'v':
                ax.axvline(asym['val'], color='#FF3366', linestyle=':', linewidth=2.5)
            elif asym['type'] == 'h':
                ax.axhline(asym['val'], color='#FF3366', linestyle=':', linewidth=2.5)
            elif asym['type'] == 'o':
                ax.plot(x_vals, asym['a'] * x_vals + asym['b'], color='#FF3366', linestyle=':', linewidth=2.5)
        
        ax.plot(x_vals, y_vals, color='#00E5FF', linewidth=3, label='C_f')
        
        with np.errstate(divide='ignore', invalid='ignore'):
            y_g_plot = g_func(x_vals, m_val)
        if np.isscalar(y_g_plot): y_g_plot = np.full_like(x_vals, y_g_plot, dtype=float)
        
        m_val_str = str(int(m_val)) if int(m_val)==m_val else str(round(m_val, 2))
        m_eq_label = f"y = {m_val_str}" if st.session_state.g_val.strip() == 'm' else "y = " + st.session_state.g_val.replace('m', f"({m_val_str})" if m_val < 0 else m_val_str).replace('*', '')
        
        ax.plot(x_vals, y_g_plot, color='#FFD700', linestyle='--', linewidth=3, label=f"${m_eq_label}$")
        
        diff_plot = y_vals - y_g_plot
        intersect_x = []
        for i in range(len(diff_plot)-1):
            if np.isfinite(diff_plot[i]) and np.isfinite(diff_plot[i+1]) and diff_plot[i] * diff_plot[i+1] < 0:
                denom = diff_plot[i+1] - diff_plot[i]
                xi = x_vals[i] - diff_plot[i] * (x_vals[i+1] - x_vals[i]) / denom if denom != 0 else x_vals[i]
                intersect_x.append(float(xi))
        
        unique_intersect_x = []
        for ix in intersect_x:
            if not any(abs(ix - uix) < 0.1 for uix in unique_intersect_x): unique_intersect_x.append(ix)

        if unique_intersect_x:
            intersect_y = [m_val if st.session_state.g_val.strip() == 'm' else float(g_func(ix, m_val)) for ix in unique_intersect_x]
            ax.scatter(unique_intersect_x, intersect_y, color='#FF0000', s=120, zorder=5, edgecolor='white', linewidth=2)

        ax.set_ylim(-6, 8)
        ax.grid(True, color='#ffffff', linestyle='-', alpha=0.1)
        legend = ax.legend(facecolor='#1E293B', edgecolor='#334155', loc='upper right', fontsize=12)
        for text in legend.get_texts(): text.set_color("white")
        fig.tight_layout()
        
        with placeholder.container():
            st.pyplot(fig, use_container_width=True)
            st.markdown(generate_html_table(m_val), unsafe_allow_html=True)
        plt.close(fig)

    if st.session_state.auto_play:
        while st.session_state.auto_play and st.session_state.m_anim <= 8.0:
            update_view(round(st.session_state.m_anim, 2))
            is_crit = any(abs(st.session_state.m_anim - mc) < 1e-4 for mc in m_critical)
            time.sleep(1.5 if is_crit else 0.05)
            
            next_m = st.session_state.m_anim + 0.15
            for mc in m_critical:
                if st.session_state.m_anim < mc - 1e-4 and next_m >= mc - 1e-4:
                    next_m = float(mc); break
            st.session_state.m_anim = next_m
        st.session_state.auto_play = False
    else:
        update_view(st.slider("تحكم يدوي بميل المستقيم m:", -8.0, 8.0, 0.0, 0.1, format="%g", key="manual_m"))
