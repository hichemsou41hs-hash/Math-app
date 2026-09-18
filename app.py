import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import time

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(page_title="المناقشة البيانية", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #1A2F24; color: white; }
    h1, h2, h3, p, span { color: white !important; }
    .stTextInput > div > div > input { background-color: #2A4034; color: white; border: 1px solid #FFC000; font-size: 18px;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #FFC000 !important; font-size: 40px;'>الأستاذ سوايسية هشام</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: white !important; font-size: 30px;'>المناقشة البيانية</h2>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إدارة حالة الأنيميشن (لجعل الحركة أوتوماتيكية وسريعة)
# ---------------------------------------------------------
if 'auto_play' not in st.session_state:
    st.session_state.auto_play = False
if 'm_anim' not in st.session_state:
    st.session_state.m_anim = -5.0

# ---------------------------------------------------------
# 3. إدخال الدالة ومعادلة المناقشة (أفقية، مائلة، دورانية)
# ---------------------------------------------------------
x_sym, m_sym = sp.symbols('x m')

col1, col2 = st.columns(2)
with col1:
    f_input = st.text_input("أدخل الدالة f(x):", value="e^(-x+1)-x+1")
with col2:
    g_input = st.text_input("أدخل معادلة المستقيم y (مثال: m, x+m, m*x):", value="m")

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
    # عرض العبارات بـ LaTeX بشكل أنيق
    st.latex(rf"\begin{{cases}} f(x) = {sp.latex(f_expr)} \\ y = {sp.latex(g_expr)} \end{{cases}}")

    f_func = sp.lambdify(x_sym, f_expr, 'numpy')
    g_func = sp.lambdify((x_sym, m_sym), g_expr, 'numpy')
    
    x_vals = np.linspace(-8, 8, 2000)
    y_vals = f_func(x_vals)
    
    if np.iscomplexobj(y_vals):
        y_vals = np.where(np.isreal(y_vals), y_vals.real, np.nan)
    if np.isscalar(y_vals):
        y_vals = np.full_like(x_vals, y_vals, dtype=float)

    # ---------------------------------------------------------
    # 4. الحساب الدقيق للقيم الحدية لكل أنواع المناقشة وإشاراتها
    # ---------------------------------------------------------
    m_critical = []
    
    # 1. الذروات وتغير عدد الحلول (عن طريق حل المعادلة بالنسبة لـ m)
    try:
        m_sols = sp.solve(f_expr - g_expr, m_sym)
        if m_sols:
            H_expr = m_sols[0]
            H_func = sp.lambdify(x_sym, H_expr, 'numpy')
            H_vals = H_func(x_vals)
            if np.iscomplexobj(H_vals):
                H_vals = np.where(np.isreal(H_vals), H_vals.real, np.nan)
            
            dH = np.diff(H_vals)
            ext_idx = np.where(np.diff(np.sign(dH)) != 0)[0] + 1
            for idx in ext_idx:
                if abs(H_vals[idx] - H_vals[idx-1]) < 3.0: # لتفادي المقاربات العمودية
                    m_critical.append(round(float(H_vals[idx]), 1))
    except: pass
    
    # 2. نقطة تقاطع المنحنى مع محور التراتيب (تغير إشارة الحلول)
    try:
        m_0_sols = sp.solve(f_expr.subs(x_sym, 0) - g_expr.subs(x_sym, 0), m_sym)
        for m_sol in m_0_sols:
            m_critical.append(round(float(m_sol), 1))
    except: pass

    m_critical = [m for m in m_critical if np.isfinite(m) and abs(m) < 20]
    m_critical = np.unique(m_critical)
    m_critical = np.sort(m_critical)

    # خوارزمية ذكية جداً لاستنتاج عدد الحلول وإشارتها
    def get_roots_text(m_test, is_critical):
        y_g = g_func(x_vals, m_test)
        if np.isscalar(y_g):
            y_g = np.full_like(x_vals, y_g, dtype=float)
            
        diff = y_vals - y_g
        crossings = list(np.where(np.diff(np.sign(diff)))[0])
        tangents = []
        
        # التقاط الحلول المضاعفة بدقة
        if is_critical:
            abs_diff = np.abs(diff)
            minima = np.where((abs_diff[1:-1] < abs_diff[:-2]) & (abs_diff[1:-1] < abs_diff[2:]))[0] + 1
            for idx in minima:
                if abs_diff[idx] < 0.2:
                    if not any(abs(idx - c) < 20 for c in crossings):
                        tangents.append(idx)
                        
        all_roots = [(x_vals[c], "single") for c in crossings] + [(x_vals[t], "double") for t in tangents]
        
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
        
        if pos_s == 1 and neg_s == 1 and len(desc)==0:
            desc.append("حلان مختلفان في الإشارة")
        else:
            if pos_s == 1: desc.append("حل موجب")
            elif pos_s == 2: desc.append("حلان موجبان")
            elif pos_s > 2: desc.append(f"{pos_s} حلول موجبة")
            
            if neg_s == 1: desc.append("حل سالب")
            elif neg_s == 2: desc.append("حلان سالبان")
            elif neg_s > 2: desc.append(f"{neg_s} حلول سالبة")
            
            if zero_s == 1: desc.append("حل معدوم")
        
        return " و ".join(desc)

    # ---------------------------------------------------------
    # 5. بناء هيكل الجدول التفاعلي
    # ---------------------------------------------------------
    intervals = []
    if len(m_critical) > 0:
        intervals.append((float('-inf'), m_critical[0], f"m ∈ ]-∞, {m_critical[0]}[", get_roots_text(m_critical[0] - 1, False)))
        for i in range(len(m_critical)):
            intervals.append((m_critical[i], m_critical[i], f"m = {m_critical[i]}", get_roots_text(m_critical[i], True)))
            if i < len(m_critical) - 1:
                mid = (m_critical[i] + m_critical[i+1]) / 2.0
                intervals.append((m_critical[i], m_critical[i+1], f"m ∈ ]{m_critical[i]}, {m_critical[i+1]}[", get_roots_text(mid, False)))
        intervals.append((m_critical[-1], float('inf'), f"m ∈ ]{m_critical[-1]}, +∞[", get_roots_text(m_critical[-1] + 1, False)))
    else:
        intervals.append((float('-inf'), float('inf'), "m ∈ ℝ", get_roots_text(0, False)))

    def generate_html_table(current_m):
        html = "<table style='width:100%; border-collapse: collapse; text-align:center; font-size:18px; color:white; background-color:#111;'>"
        html += "<tr style='color:#FFC000; border-bottom:1px solid #444;'><th>الإشارة وعدد الحلول</th><th dir='ltr'>المجال / القيمة</th></tr>"
        
        for low, high, text, sol_text in intervals:
            is_active = False
            if low == high: 
                if abs(current_m - low) < 0.15: is_active = True
            else: 
                if low == float('-inf') and current_m < high - 0.15: is_active = True
                elif high == float('inf') and current_m > low + 0.15: is_active = True
                elif low + 0.15 <= current_m <= high - 0.15: is_active = True

            row_style = "border: 3px solid #FFC000; background-color: #2A4034; font-weight:bold;" if is_active else "border-bottom: 1px solid #333;"
            html += f"<tr style='{row_style} padding: 10px;'> <td style='padding:8px;'>{sol_text}</td> <td style='padding:8px;' dir='ltr'>{text}</td> </tr>"
        html += "</table>"
        return html

    # ---------------------------------------------------------
    # 6. أزرار التحكم والأنيميشن السريع
    # ---------------------------------------------------------
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
        m_val = st.slider("تحكم يدوي:", -8.0, 8.0, 0.0, 0.1)

    # ---------------------------------------------------------
    # 7. الرسم الفوري
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4.5))
    fig.patch.set_facecolor('#1A2F24')
    ax.set_facecolor('#1A2F24')
    ax.tick_params(colors='white')
    
    for spine in ax.spines.values(): spine.set_edgecolor('none')
    ax.axhline(0, color='white', linewidth=1.5) 
    ax.axvline(0, color='white', linewidth=1.5) 
    
    ax.plot(x_vals, y_vals, color='#00FFFF', linewidth=2.5, label='C_f')
    
    # رسم مستقيم المناقشة التفاعلي
    y_g_plot = g_func(x_vals, m_val)
    if np.isscalar(y_g_plot):
        y_g_plot = np.full_like(x_vals, y_g_plot, dtype=float)
    
    ax.plot(x_vals, y_g_plot, color='#FFC000', linestyle='--', linewidth=2.5, label=f'y = {m_val:.1f}' if g_input=='m' else 'y(m)')

    ax.set_ylim(-6, 8)
    ax.grid(True, color='#ffffff', linestyle='-', alpha=0.1)
    
    legend = ax.legend(facecolor='#111', edgecolor='#444', loc='upper right')
    for text in legend.get_texts(): text.set_color("white")
    
    st.pyplot(fig)
    st.markdown(generate_html_table(m_val), unsafe_allow_html=True)
    plt.close(fig)

    # ---------------------------------------------------------
    # 8. حلقة الأنيميشن (المحرك المسرع)
    # ---------------------------------------------------------
    if st.session_state.auto_play:
        time.sleep(0.05) # زمن انتظار أقل لحركة أسرع
        st.session_state.m_anim += 0.2 # قفزة أكبر في قيمة m
        if st.session_state.m_anim > 6.0:
            st.session_state.auto_play = False
        st.rerun()
