import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import time
import warnings

# تجاهل التحذيرات الرياضية
warnings.filterwarnings("ignore")

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم (الألوان المدروسة نفسياً)
# ---------------------------------------------------------
st.set_page_config(page_title="المناقشة البيانية", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    /* خلفية زرقاء داكنة جداً للتركيز (Midnight Blue) */
    .stApp { background-color: #0F172A; color: white; }
    h1, h2, h3, p, span { color: white !important; }
    
    /* تنسيق خانات الإدخال */
    .stTextInput > div > div > input { 
        background-color: #1E293B; 
        color: white; 
        border: 1px solid #00E5FF; 
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# عنوان الأستاذ في سطر واحد وبلون ذهبي مميز
st.markdown("<h1 style='text-align: center; color: #FFD700 !important; font-size: 32px; font-weight: bold; white-space: nowrap;'>الأستاذ سوايسية هشام</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #00E5FF !important; font-size: 26px; margin-top: -15px;'>المناقشة البيانية</h2>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إدارة حالة الأنيميشن
# ---------------------------------------------------------
if 'auto_play' not in st.session_state:
    st.session_state.auto_play = False
if 'm_anim' not in st.session_state:
    st.session_state.m_anim = -5.0

# ---------------------------------------------------------
# 3. إدخال الدالة ومعادلة المناقشة
# ---------------------------------------------------------
x_sym, m_sym = sp.symbols('x m')

col1, col2 = st.columns(2)
with col1:
    f_input = st.text_input("أدخل الدالة f(x):", value="ln(x+1)-x")
with col2:
    g_input = st.text_input("أدخل معادلة المستقيم y (مثال: m, x+m, m*x):", value="2*m+1")

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
    f_latex = sp.latex(f_expr).replace(r"\log", r"\ln")
    g_latex = sp.latex(g_expr).replace(r"\log", r"\ln")
    st.latex(rf"\begin{{cases}} f(x) = {f_latex} \\ y = {g_latex} \end{{cases}}")

    f_func = sp.lambdify(x_sym, f_expr, 'numpy')
    g_func = sp.lambdify((x_sym, m_sym), g_expr, 'numpy')
    
    x_vals = np.linspace(-8, 8, 2000)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        y_vals = f_func(x_vals)
    
    if np.iscomplexobj(y_vals):
        y_vals = np.where(np.isreal(y_vals), y_vals.real, np.nan)
    if np.isscalar(y_vals):
        y_vals = np.full_like(x_vals, y_vals, dtype=float)

    # ---------------------------------------------------------
    # 4. الحساب الدقيق للقيم الحدية
    # ---------------------------------------------------------
    m_critical = []
    
    try:
        m_sols = sp.solve(f_expr - g_expr, m_sym)
        if m_sols:
            H_expr = m_sols[0]
            H_func = sp.lambdify(x_sym, H_expr, 'numpy')
            with np.errstate(divide='ignore', invalid='ignore'):
                H_vals = H_func(x_vals)
            if np.iscomplexobj(H_vals):
                H_vals = np.where(np.isreal(H_vals), H_vals.real, np.nan)
            
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
        
        if is_critical:
            abs_diff = np.abs(diff)
            for i in range(1, len(abs_diff)-1):
                if np.isfinite(abs_diff[i-1]) and np.isfinite(abs_diff[i]) and np.isfinite(abs_diff[i+1]):
                    if abs_diff[i] < abs_diff[i-1] and abs_diff[i] < abs_diff[i+1]:
                        if abs_diff[i] < 0.2:
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
        html = "<table style='width:100%; border-collapse: collapse; text-align:center; font-size:18px; color:white; background-color:#1E293B;'>"
        html += "<tr style='color:#FFD700; border-bottom:1px solid #334155;'><th>الإشارة وعدد الحلول</th><th dir='ltr'>المجال / القيمة</th></tr>"
        
        for low, high, text, sol_text in intervals:
            is_active = False
            if low == high: 
                if abs(current_m - low) < 0.15: is_active = True
            else: 
                if low == float('-inf') and current_m < high - 0.15: is_active = True
                elif high == float('inf') and current_m > low + 0.15: is_active = True
                elif low + 0.15 <= current_m <= high - 0.15: is_active = True

            # تنسيق السطر المضيء بلون ذهبي
            row_style = "border: 3px solid #FFD700; background-color: #334155; font-weight:bold;" if is_active else "border-bottom: 1px solid #334155;"
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
    # 7. الرسم الفوري (تكبير حجم المنحنى)
    # ---------------------------------------------------------
    # تكبير أبعاد الرسم (figsize) ليكون أوضح على الشاشة
    fig, ax = plt.subplots(figsize=(10, 6.5))
    
    fig.patch.set_facecolor('#0F172A') # أزرق ليلي
    ax.set_facecolor('#0F172A')
    ax.tick_params(colors='white')
    
    for spine in ax.spines.values(): spine.set_edgecolor('none')
    ax.axhline(0, color='#9CA3AF', linewidth=1.5) 
    ax.axvline(0, color='#9CA3AF', linewidth=1.5) 
    
    # رسم المنحنى بلون سماوي مشع وسمك أكبر
    ax.plot(x_vals, y_vals, color='#00E5FF', linewidth=3, label='C_f')
    
    with np.errstate(divide='ignore', invalid='ignore'):
        y_g_plot = g_func(x_vals, m_val)
    if np.isscalar(y_g_plot):
        y_g_plot = np.full_like(x_vals, y_g_plot, dtype=float)
    
    # المستقيم المتحرك بلون ذهبي واضح
    ax.plot(x_vals, y_g_plot, color='#FFD700', linestyle='--', linewidth=3, label=f'y = {m_val:.1f}' if g_input=='m' else 'y(m)')

    ax.set_ylim(-6, 8)
    ax.grid(True, color='#ffffff', linestyle='-', alpha=0.1)
    
    legend = ax.legend(facecolor='#1E293B', edgecolor='#334155', loc='upper right')
    for text in legend.get_texts(): text.set_color("white")
    
    fig.tight_layout() # لتقليل الحواف البيضاء وجعل الرسم أكبر
    
    # عرض الرسم بعرض الشاشة الكامل (use_container_width=True)
    st.pyplot(fig, use_container_width=True)
    st.markdown(generate_html_table(m_val), unsafe_allow_html=True)
    plt.close(fig)

    # ---------------------------------------------------------
    # 8. حلقة الأنيميشن
    # ---------------------------------------------------------
    if st.session_state.auto_play:
        time.sleep(0.05) 
        st.session_state.m_anim += 0.2 
        if st.session_state.m_anim > 6.0:
            st.session_state.auto_play = False
        st.rerun()
