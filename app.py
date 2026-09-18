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
    .title-hes { text-align: center; color: #FFFFFF !important; font-size: 36px; font-weight: bold; white-space: nowrap; margin-bottom: 0px;}
    .title-dis { text-align: center; color: #FFD700 !important; font-size: 28px; font-weight: bold; margin-top: -5px; margin-bottom: 30px;}
    .stTextInput label { color: #00E5FF !important; font-size: 18px !important; font-weight: bold !important; direction: rtl !important; text-align: right !important; display: block;}
    .stTextInput > div > div > input { background-color: #1E293B; color: white; border: 1px solid #00E5FF; font-size: 18px; direction: ltr !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-hes'>الأستاذ سوايسية هشام</div>", unsafe_allow_html=True)
st.markdown("<div class='title-dis'>المناقشة البيانية</div>", unsafe_allow_html=True)

def fmt(val):
    if val == float('inf'): return "+∞"
    if val == float('-inf'): return "-∞"
    if int(val) == val: return str(int(val))
    return str(val)

if 'auto_play' not in st.session_state:
    st.session_state.auto_play = False
if 'm_anim' not in st.session_state:
    st.session_state.m_anim = -5.0

x_sym, m_sym = sp.symbols('x m')

col1, col2 = st.columns(2)
with col1:
    f_input = st.text_input("أدخل عبارة الدالة f(x):", value="x+1+e^(-x)")
with col2:
    g_input = st.text_input("أدخل معادلة المستقيم بدلالة m:", value="m*x+1")

try:
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    transformations = (standard_transformations + (implicit_multiplication_application,))
    local_dict = {'e': sp.E, 'pi': sp.pi, 'ln': sp.log}
    f_expr = parse_expr(f_input.replace('^', '**'), local_dict=local_dict, transformations=transformations)
    g_expr = parse_expr(g_input.replace('^', '**'), local_dict=local_dict, transformations=transformations)
    valid_input = True
except:
    st.error("⚠️ صيغة غير صالحة.")
    valid_input = False

if valid_input:
    f_latex = sp.latex(f_expr).replace(r"\log", r"\ln")
    g_latex = sp.latex(g_expr).replace(r"\log", r"\ln")
    st.latex(rf"\color{{#FFD700}} \begin{{cases}} f(x) = {f_latex} \\ y = {g_latex} \end{{cases}}")

    f_func = sp.lambdify(x_sym, f_expr, 'numpy')
    g_func = sp.lambdify((x_sym, m_sym), g_expr, 'numpy')
    
    x_vals = np.linspace(-8, 8, 3000)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        y_vals = f_func(x_vals)
    
    if np.iscomplexobj(y_vals):
        y_vals = np.where(np.isreal(y_vals), y_vals.real, np.nan)
    if np.isscalar(y_vals):
        y_vals = np.full_like(x_vals, y_vals, dtype=float)

    dy = np.abs(np.diff(y_vals))
    jump_idx = np.where(dy > 10)[0]
    for idx in jump_idx:
        y_vals[idx] = np.nan
        y_vals[idx+1] = np.nan

    # المقاربات
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
                    if b_val == 0:
                        eq = f"y={sign_a}{a_str}x"
                    else:
                        sign_b = "+" if b_val > 0 else "-"
                        b_str = str(int(abs(b_val))) if int(abs(b_val))==abs(b_val) else str(abs(b_val))
                        eq = f"y={sign_a}{a_str}x {sign_b} {b_str}"
                    asymptotes.append({'type': 'o', 'a': a_val, 'b': b_val, 'label': eq})
        except: pass
        
    try:
        n_expr, d_expr = sp.fraction(sp.cancel(f_expr))
        if d_expr != 1:
            roots = sp.solve(d_expr, x_sym)
            for r in roots:
                if r.is_real:
                    r_str = str(int(r)) if int(r)==r else str(float(r))
                    asymptotes.append({'type': 'v', 'val': float(r), 'label': f"x={r_str}"})
    except: pass
    
    try:
        for log_expr in f_expr.atoms(sp.log):
            arg = log_expr.args[0]
            roots = sp.solve(arg, x_sym)
            for r in roots:
                if r.is_real:
                    r_str = str(int(r)) if int(r)==r else str(float(r))
                    asymptotes.append({'type': 'v', 'val': float(r), 'label': f"x={r_str}"})
    except: pass

    unique_asymptotes = []
    seen_labels = set()
    for asym in asymptotes:
        if asym['label'] not in seen_labels:
            seen_labels.add(asym['label'])
            unique_asymptotes.append(asym)

    m_critical = []
    try:
        pivot_x_sols = sp.solve(sp.diff(g_expr, m_sym), x_sym)
        for px in pivot_x_sols:
            if np.isreal(complex(px)):
                px_val = float(px)
                df = sp.diff(f_expr, x_sym)
                dg = sp.diff(g_expr, x_sym)
                m_pivot = sp.solve(df.subs(x_sym, px) - dg.subs(x_sym, px), m_sym)
                for m_sol in m_pivot:
                    m_critical.append(round(float(m_sol), 2))
    except: pass
    
    try:
        m_sols = sp.solve(f_expr - g_expr, m_sym)
        if m_sols:
            H_expr = m_sols[0]
            H_func = sp.lambdify(x_sym, H_expr, 'numpy')
            with np.errstate(divide='ignore', invalid='ignore'):
                H_vals = H_func(x_vals)
            try:
                m_critical.append(round(float(H_func(-1000)), 1))
                m_critical.append(round(float(H_func(1000)), 1))
            except: pass
            if not np.isscalar(H_vals):
                dH = np.diff(H_vals)
                ext_idx = np.where(np.diff(np.sign(dH)) != 0)[0] + 1
                for idx in ext_idx:
                    if np.isfinite(H_vals[idx]) and np.isfinite(H_vals[idx-1]):
                        if abs(H_vals[idx] - H_vals[idx-1]) < 3.0: 
                            m_critical.append(round(float(H_vals[idx]), 2))
    except: pass
    
    try:
        m_0_sols = sp.solve(f_expr.subs(x_sym, 0) - g_expr.subs(x_sym, 0), m_sym)
        for m_sol in m_0_sols:
            m_critical.append(round(float(m_sol), 2))
    except: pass

    m_critical = [m for m in m_critical if np.isfinite(m) and abs(m) < 20]
    m_critical = np.unique(m_critical)
    m_critical = np.sort(m_critical)

    def get_roots_text(m_test, is_critical):
        with np.errstate(divide='ignore', invalid='ignore'):
            y_g = g_func(x_vals, m_test)
            if np.isscalar(y_g):
                y_g = np.full_like(x_vals, y_g, dtype=float)
            diff = y_vals - y_g
            
        crossings = []
        tangents = []
        for i in range(len(diff)-1):
            if np.isfinite(diff[i]) and np.isfinite(diff[i+1]):
                if diff[i] * diff[i+1] < 0:
                    crossings.append(i)
                elif diff[i] == 0:
                    crossings.append(i)
        if np.isfinite(diff[-1]) and diff[-1] == 0:
            crossings.append(len(diff)-1)
        
        abs_diff = np.abs(diff)
        for i in range(1, len(abs_diff)-1):
            if np.isfinite(abs_diff[i-1]) and np.isfinite(abs_diff[i]) and np.isfinite(abs_diff[i+1]):
                if abs_diff[i] < abs_diff[i-1] and abs_diff[i] < abs_diff[i+1]:
                    if abs_diff[i] < 0.1: 
                        if not any(abs(i - c) < 20 for c in crossings):
                            tangents.append(i)
                                
        raw_roots = [(x_vals[c], "single") for c in crossings] + [(x_vals[t], "double") for t in tangents]
        all_roots = []
        for r, t in raw_roots:
            if not any(abs(r - fr) < 0.15 for fr, ft in all_roots):
                all_roots.append((r, t))
        
        if len(all_roots) == 0: return "لا توجد حلول"
        
        desc = []
        pos_s = sum(1 for r, t in all_roots if r > 0.05 and t == "single")
        neg_s = sum(1 for r, t in all_roots if r < -0.05 and t == "single")
        zero_s = sum(1 for r, t in all_roots if abs(r) <= 0.05 and t == "single")
        pos_d = sum(1 for r, t in all_roots if r > 0.05 and t == "double")
        neg_d = sum(1 for r, t in all_roots if r < -0.05 and t == "double")
        zero_d = sum(1 for r, t in all_roots if abs(r) <= 0.05 and t == "double")
        
        if pos_d == 1: desc.append("حل مضاعف موجب")
        if neg_d == 1: desc.append("حل مضاعف سالب")
        if zero_d == 1: desc.append("حل مضاعف معدوم")
        if pos_s == 1: desc.append("حل موجب")
        elif pos_s == 2: desc.append("حلان موجبان")
        elif pos_s > 2: desc.append(f"{pos_s} حلول موجبة")
        if neg_s == 1: desc.append("حل سالب")
        elif neg_s == 2: desc.append("حلان سالبان")
        elif neg_s > 2: desc.append(f"{neg_s} حلول سالبة")
        if zero_s == 1: desc.append("حل معدوم")
        
        if pos_s == 1 and neg_s == 1 and len(desc) == 2:
            return "حلان مختلفان في الإشارة"
        return " و ".join(desc)

    raw_intervals = []
    if len(m_critical) > 0:
        raw_intervals.append((float('-inf'), m_critical[0], get_roots_text(m_critical[0] - 1, False)))
        for i in range(len(m_critical)):
            raw_intervals.append((m_critical[i], m_critical[i], get_roots_text(m_critical[i], True)))
            if i < len(m_critical) - 1:
                mid = (m_critical[i] + m_critical[i+1]) / 2.0
                raw_intervals.append((m_critical[i], m_critical[i+1], get_roots_text(mid, False)))
        raw_intervals.append((m_critical[-1], float('inf'), get_roots_text(m_critical[-1] + 1, False)))
    else:
        raw_intervals.append((float('-inf'), float('inf'), get_roots_text(0, False)))

    merged_intervals = []
    if raw_intervals:
        current_group = [raw_intervals[0]]
        for item in raw_intervals[1:]:
            if item[2] == current_group[-1][2]: 
                current_group.append(item)
            else:
                merged_intervals.append(current_group)
                current_group = [item]
        merged_intervals.append(current_group)

    final_table_data = []
    for g in merged_intervals:
        sol_text = g[0][2]
        L = g[0][0]
        H = g[-1][1]
        include_L = (g[0][0] == g[0][1]) 
        include_H = (g[-1][0] == g[-1][1]) 

        if L == float('-inf') and H == float('inf'):
            math_html = "<i>m</i> ∈ ℝ"
        elif L == H:
            math_html = f"<i>m</i> = {fmt(L)}"
        else:
            left_bracket = "[" if include_L else "]"
            right_bracket = "]" if include_H else "["
            math_html = f"<i>m</i> ∈ {left_bracket}{fmt(L)}; {fmt(H)}{right_bracket}"
        final_table_data.append((math_html, sol_text, g)) 

    def generate_html_table(current_m):
        html = "<table style='width:100%; border-collapse: collapse; text-align:center; font-size:18px; background-color:#1E293B;'>"
        html += "<tr style='border-bottom:2px solid #444;'> <th style='color:white; padding:10px;'>الإشارة وعدد الحلول</th> <th dir='ltr' style='color:white; padding:10px;'>المجال / القيمة</th> </tr>"
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
            text_color_sol = "#00E5FF" if is_active else "#A5F3FC"  
            text_color_m = "#FFD700" if is_active else "#FEF08A"    
            html += f"<tr style='{row_style}'> <td style='padding:10px; color:{text_color_sol};'>{sol_text}</td> <td style='padding:10px; color:{text_color_m}; font-family: \"Times New Roman\", Times, serif; font-size: 18px; white-space: nowrap;' dir='ltr'>{math_html}</td> </tr>"
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

    if st.session_state.auto_play:
        m_val = round(st.session_state.m_anim, 2)
    else:
        m_val = st.slider("تحكم يدوي:", -8.0, 8.0, 0.0, 0.1, format="%g")

    # الرسم
    fig, ax = plt.subplots(figsize=(10, 6.5))
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')
    ax.tick_params(colors='white')
    
    for spine in ax.spines.values(): spine.set_edgecolor('none')
    ax.axhline(0, color='#9CA3AF', linewidth=1.5) 
    ax.axvline(0, color='#9CA3AF', linewidth=1.5) 
    
    for asym in unique_asymptotes:
        if asym['type'] == 'v':
            ax.axvline(asym['val'], color='#FF3366', linestyle=':', linewidth=2.5)
            ax.text(asym['val'] + 0.15, 6.5, f"${asym['label']}$", color='#FF3366', fontsize=14, fontweight='bold', va='top')
        elif asym['type'] == 'h':
            ax.axhline(asym['val'], color='#FF3366', linestyle=':', linewidth=2.5)
            ax.text(7.5, asym['val'] + 0.25, f"${asym['label']}$", color='#FF3366', fontsize=14, fontweight='bold', ha='right')
        elif asym['type'] == 'o':
            y_asym = asym['a'] * x_vals + asym['b']
            ax.plot(x_vals, y_asym, color='#FF3366', linestyle=':', linewidth=2.5)
            x_text = 5
            y_text = asym['a'] * x_text + asym['b']
            if y_text > 7 or y_text < -5.5:
                x_text = -5
                y_text = asym['a'] * x_text + asym['b']
            ax.text(x_text, y_text + 0.5, f"${asym['label']}$", color='#FF3366', fontsize=14, fontweight='bold', ha='center', va='bottom', rotation=np.degrees(np.arctan(asym['a'])) * 0.6)
    
    ax.plot(x_vals, y_vals, color='#00E5FF', linewidth=3, label='C_f')
    
    with np.errstate(divide='ignore', invalid='ignore'):
        y_g_plot = g_func(x_vals, m_val)
    if np.isscalar(y_g_plot):
        y_g_plot = np.full_like(x_vals, y_g_plot, dtype=float)
    
    m_val_str = str(int(m_val)) if int(m_val)==m_val else str(round(m_val, 2))
    if g_input.strip() == 'm':
        m_eq_label = f"y = {m_val_str}"
    else:
        rep_str = f"({m_val_str})" if m_val < 0 else m_val_str
        m_eq_label = "y = " + g_input.replace('m', rep_str).replace('*', '')
        
    ax.plot(x_vals, y_g_plot, color='#FFD700', linestyle='--', linewidth=3, label=f"${m_eq_label}$")
    
    diff_plot = y_vals - y_g_plot
    intersect_x = []
    for i in range(len(diff_plot)-1):
        if np.isfinite(diff_plot[i]) and np.isfinite(diff_plot[i+1]):
            if diff_plot[i] * diff_plot[i+1] < 0:
                denom = diff_plot[i+1] - diff_plot[i]
                xi = x_vals[i] - diff_plot[i] * (x_vals[i+1] - x_vals[i]) / denom if denom != 0 else x_vals[i]
                intersect_x.append(float(xi))
            elif diff_plot[i] == 0:
                intersect_x.append(float(x_vals[i]))
                
    abs_diff = np.abs(diff_plot)
    for i in range(1, len(abs_diff)-1):
        if np.isfinite(abs_diff[i-1]) and np.isfinite(abs_diff[i]) and np.isfinite(abs_diff[i+1]):
            if abs_diff[i] < abs_diff[i-1] and abs_diff[i] < abs_diff[i+1]:
                if abs_diff[i] < 0.15: 
                    intersect_x.append(float(x_vals[i]))

    unique_intersect_x = []
    for ix in intersect_x:
        if not any(abs(ix - uix) < 0.1 for uix in unique_intersect_x):
            unique_intersect_x.append(ix)

    intersect_y = []
    for ix in unique_intersect_x:
        if g_input.strip() == 'm':
            intersect_y.append(m_val)
        else:
            yt = g_func(ix, m_val)
            intersect_y.append(float(yt) if not np.isscalar(yt) else yt)

    if unique_intersect_x:
        ax.scatter(unique_intersect_x, intersect_y, color='#FF0000', s=120, zorder=5, edgecolor='white', linewidth=2, label='نقاط التقاطع')

    if g_input.strip() == 'm':
        ax.text(-7.5, m_val + 0.25, f"${m_eq_label}$", color='#FFD700', fontsize=14, fontweight='bold', ha='left', va='bottom')
    else:
        y_text_m = g_func(4, m_val)
        if -5.5 <= y_text_m <= 7:
            ax.text(4, y_text_m + 0.5, f"${m_eq_label}$", color='#FFD700', fontsize=14, fontweight='bold', ha='center', va='bottom')
        else:
            y_text_m2 = g_func(-4, m_val)
            if -5.5 <= y_text_m2 <= 7:
                 ax.text(-4, y_text_m2 + 0.5, f"${m_eq_label}$", color='#FFD700', fontsize=14, fontweight='bold', ha='center', va='bottom')

    ax.set_ylim(-6, 8)
    ax.grid(True, color='#ffffff', linestyle='-', alpha=0.1)
    legend = ax.legend(facecolor='#1E293B', edgecolor='#334155', loc='upper right', fontsize=12)
    for text in legend.get_texts(): text.set_color("white")
    fig.tight_layout()
    
    st.pyplot(fig, use_container_width=True)
    st.markdown(generate_html_table(m_val), unsafe_allow_html=True)
    plt.close(fig)

    if st.session_state.auto_play:
        is_critical_now = any(abs(st.session_state.m_anim - mc) < 1e-4 for mc in m_critical)
        if is_critical_now:
            time.sleep(1.5) 
        else:
            time.sleep(0.05) 
        step = 0.15 
        next_m = st.session_state.m_anim + step
        for mc in m_critical:
            if st.session_state.m_anim < mc - 1e-4 and next_m >= mc - 1e-4:
                next_m = float(mc)
                break
        st.session_state.m_anim = next_m
        if st.session_state.m_anim > 8.0:
            st.session_state.auto_play = False
        st.rerun()
