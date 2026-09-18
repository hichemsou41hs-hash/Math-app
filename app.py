import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import time

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(page_title="المناقشة البيانية التفاعلية", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #1A2F24; color: white; }
    h1, h2, h3, p, span { color: white !important; }
    .stTextInput > div > div > input { background-color: #2A4034; color: white; border: 1px solid #FFC000; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #FFC000 !important;'>الأستاذ هشام: المناقشة الأفقية</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إدارة حالة الأنيميشن (السر الحقيقي للحركة السلسة)
# ---------------------------------------------------------
if 'auto_play' not in st.session_state:
    st.session_state.auto_play = False
if 'm_anim' not in st.session_state:
    st.session_state.m_anim = -4.0

# ---------------------------------------------------------
# 3. إدخال الدالة
# ---------------------------------------------------------
x_sym = sp.Symbol('x')
f_input = st.text_input("أدخل الدالة f(x):", value="2*x^2 / (x^2 + 1)")

try:
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    transformations = (standard_transformations + (implicit_multiplication_application,))
    local_dict = {'e': sp.E, 'pi': sp.pi, 'ln': sp.log}
    f_expr = parse_expr(f_input.replace('^', '**'), local_dict=local_dict, transformations=transformations)
    valid_input = True
except:
    st.error("⚠️ صيغة غير صالحة.")
    valid_input = False

if valid_input:
    f_func = sp.lambdify(x_sym, f_expr, 'numpy')
    x_vals = np.linspace(-6, 6, 1000)
    y_vals = f_func(x_vals)
    
    if np.iscomplexobj(y_vals):
        y_vals = np.where(np.isreal(y_vals), y_vals.real, np.nan)
    if np.isscalar(y_vals):
        y_vals = np.full_like(x_vals, y_vals, dtype=float)

    # ---------------------------------------------------------
    # 4. الحساب الدقيق للقيم الحدية (الذروات والمقاربات)
    # ---------------------------------------------------------
    m_critical = []
    
    # المقاربات (الأطراف)
    try:
        lim_inf = round(float(f_func(-100)), 1)
        lim_sup = round(float(f_func(100)), 1)
        if abs(lim_inf) < 50: m_critical.append(lim_inf)
        if abs(lim_sup) < 50: m_critical.append(lim_sup)
    except: pass

    # الذروات (النقاط الحدية)
    dy = np.diff(y_vals)
    extrema_indices = np.where(np.diff(np.sign(dy)) != 0)[0] + 1
    for idx in extrema_indices:
        val = round(y_vals[idx], 1)
        if np.isfinite(val): m_critical.append(val)

    m_critical = np.unique(m_critical)
    m_critical = np.sort(m_critical)

    # خوارزمية ذكية لعد الحلول بدقة
    def get_roots_count(m_test):
        roots = 0
        segment_boundaries = [0] + list(extrema_indices) + [len(y_vals)-1]
        for i in range(len(segment_boundaries)-1):
            start, end = segment_boundaries[i], segment_boundaries[i+1]
            min_y, max_y = min(y_vals[start], y_vals[end]), max(y_vals[start], y_vals[end])
            
            if min_y < m_test < max_y:
                roots += 1
            elif abs(m_test - y_vals[start]) < 1e-4:
                roots += 1
        
        if abs(m_test - y_vals[-1]) < 1e-4:
            roots += 1
        return roots

    # ---------------------------------------------------------
    # 5. بناء هيكل الجدول التفاعلي
    # ---------------------------------------------------------
    intervals = []
    if len(m_critical) > 0:
        intervals.append((float('-inf'), m_critical[0], f"m ∈ ]-∞, {m_critical[0]}[", get_roots_count(m_critical[0] - 1)))
        for i in range(len(m_critical)):
            intervals.append((m_critical[i], m_critical[i], f"m = {m_critical[i]}", get_roots_count(m_critical[i])))
            if i < len(m_critical) - 1:
                mid = (m_critical[i] + m_critical[i+1]) / 2.0
                intervals.append((m_critical[i], m_critical[i+1], f"m ∈ ]{m_critical[i]}, {m_critical[i+1]}[", get_roots_count(mid)))
        intervals.append((m_critical[-1], float('inf'), f"m ∈ ]{m_critical[-1]}, +∞[", get_roots_count(m_critical[-1] + 1)))
    else:
        intervals.append((float('-inf'), float('inf'), "m ∈ ℝ", get_roots_count(0)))

    def generate_html_table(current_m):
        html = "<table style='width:100%; border-collapse: collapse; text-align:center; font-size:18px; color:white; background-color:#111;'>"
        html += "<tr style='color:#FFC000; border-bottom:1px solid #444;'><th>عدد الحلول</th><th dir='ltr'>المجال / القيمة</th></tr>"
        
        for low, high, text, roots in intervals:
            is_active = False
            # دقة الإضاءة للسطر الصحيح فقط
            if low == high: 
                if abs(current_m - low) < 0.05: is_active = True
            else: 
                if low == float('-inf') and current_m < high - 0.05: is_active = True
                elif high == float('inf') and current_m > low + 0.05: is_active = True
                elif low + 0.05 < current_m < high - 0.05: is_active = True

            row_style = "border: 3px solid #FFC000; background-color: #2A4034; font-weight:bold;" if is_active else "border-bottom: 1px solid #333;"
            sol_text = f"يوجد {roots} حلول" if roots > 0 else "لا توجد حلول"
            if roots == 1: sol_text = "حل وحيد"
            if roots == 2: sol_text = "حلان"

            html += f"<tr style='{row_style} padding: 10px;'> <td style='padding:8px;'>{sol_text}</td> <td style='padding:8px;' dir='ltr'>{text}</td> </tr>"
        html += "</table>"
        return html

    # ---------------------------------------------------------
    # 6. أزرار التحكم
    # ---------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        if st.button("تشغيل المناقشة آلياً ▶️"):
            st.session_state.auto_play = True
            st.session_state.m_anim = -4.0
            st.rerun() # تحديث فوري
    with col2:
        if st.button("إيقاف ⏹️"):
            st.session_state.auto_play = False
            st.rerun()

    # تحديد قيمة m (من الأنيميشن أو يدوياً)
    if st.session_state.auto_play:
        m_val = st.session_state.m_anim
    else:
        m_val = st.slider("تحكم يدوي:", -5.0, 5.0, 0.0, 0.1)

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
    ax.axhline(m_val, color='#FFC000', linestyle='--', linewidth=2.5, label=f'y = {m_val:.1f}')
    
    for mc in m_critical:
        ax.axhline(mc, color='#FF6666', linestyle=':', linewidth=1.2, alpha=0.5)

    ax.set_ylim(-4, 6)
    ax.grid(True, color='#ffffff', linestyle='-', alpha=0.1)
    
    legend = ax.legend(facecolor='#111', edgecolor='#444', loc='upper right')
    for text in legend.get_texts(): text.set_color("white")
    
    # عرض الرسم والجدول
    st.pyplot(fig)
    st.markdown(generate_html_table(m_val), unsafe_allow_html=True)
    plt.close(fig)

    # ---------------------------------------------------------
    # 8. حلقة الأنيميشن (المحرك)
    # ---------------------------------------------------------
    if st.session_state.auto_play:
        time.sleep(0.15) # سرعة حركة المستقيم (كلما صغر الرقم زادت السرعة)
        st.session_state.m_anim += 0.1
        if st.session_state.m_anim > 5.0:
            st.session_state.auto_play = False # إيقاف تلقائي عند القمة
        st.rerun() # السطر السحري الذي يصنع الفيديو!
