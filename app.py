import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import time

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم (الألوان المستوحاة من الفيديو)
# ---------------------------------------------------------
st.set_page_config(page_title="المناقشة البيانية التفاعلية", page_icon="📈", layout="centered")

# تغيير لون خلفية التطبيق باستخدام CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #1A2F24; /* لون أخضر داكن يشبه السبورة */
        color: white;
    }
    h1, h2, h3, p, span {
        color: white !important;
    }
    .stTextInput > div > div > input {
        background-color: #2A4034;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #FFC000 !important;'>الأستاذ هشام: المناقشة الأفقية</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إدخال الدالة ومعالجتها
# ---------------------------------------------------------
x_sym = sp.Symbol('x')
f_input = st.text_input("أدخل الدالة f(x) (مثال: x^3 - 3*x أو e^x - x):", value="2*x^2 / (x^2 + 1)")

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
    # 3. استخراج القيم الحدية والمقاربات الأفقية (للمناقشة)
    # ---------------------------------------------------------
    m_critical = []
    
    # حساب النهايات التقريبية عند + و - مالانهاية (المقاربات الأفقية)
    try:
        lim_inf = round(float(f_func(-100)), 1)
        lim_sup = round(float(f_func(100)), 1)
        if abs(lim_inf) < 50: m_critical.append(lim_inf)
        if abs(lim_sup) < 50: m_critical.append(lim_sup)
    except: pass

    # حساب القيم الحدية (الذروات)
    dy = np.diff(y_vals)
    extrema_indices = np.where(np.diff(np.sign(dy)))[0] + 1
    for idx in extrema_indices:
        val = round(y_vals[idx], 1)
        if np.isfinite(val): m_critical.append(val)

    m_critical = np.unique(m_critical)
    m_critical = np.sort(m_critical)

    # دالة لتحديد عدد الحلول لإدراجها في الجدول
    def get_roots_count(m_test):
        y_shifted = y_vals - m_test
        crossings = np.where(np.diff(np.sign(y_shifted)))[0]
        return len(crossings)

    # ---------------------------------------------------------
    # 4. بناء هيكل الجدول التفاعلي
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
        html += "<tr style='color:#FFC000; border-bottom:1px solid #444;'><th>عدد الحلول</th><th>المجال / القيمة</th></tr>"
        
        for low, high, text, roots in intervals:
            # تحديد هل هذا هو السطر "النشط" حالياً لإضاءته
            is_active = False
            if low == high: # قيمة مضبوطة
                if abs(current_m - low) < 0.05: is_active = True
            else: # مجال
                if low < current_m < high: is_active = True
                if low == float('-inf') and current_m < high: is_active = True
                if high == float('inf') and current_m > low: is_active = True

            # تنسيق السطر النشط
            row_style = "border: 3px solid #FFC000; background-color: #2A4034; font-weight:bold;" if is_active else "border-bottom: 1px solid #333;"
            sol_text = f"يوجد {roots} حلول" if roots > 0 else "لا توجد حلول"
            if roots == 1: sol_text = "حل وحيد"
            if roots == 2: sol_text = "حلان"

            html += f"<tr style='{row_style} padding: 10px;'> <td style='padding:8px;'>{sol_text}</td> <td style='padding:8px;' dir='ltr'>{text}</td> </tr>"
        html += "</table>"
        return html

    # ---------------------------------------------------------
    # 5. عرض الواجهة (الرسم والأنيميشن)
    # ---------------------------------------------------------
    col1, col2 = st.columns([1, 1])
    with col1:
        auto_play = st.button("تشغيل المناقشة آلياً ▶️")
    with col2:
        m_manual = st.slider("تحكم يدوي:", -5.0, 5.0, 0.0, 0.1)

    # مساحات العرض التي سيتم تحديثها
    plot_placeholder = st.empty()
    table_placeholder = st.empty()

    def draw_frame(m_val):
        fig, ax = plt.subplots(figsize=(7, 5))
        # ألوان الفيديو
        fig.patch.set_facecolor('#1A2F24')
        ax.set_facecolor('#1A2F24')
        ax.tick_params(colors='white')
        
        for spine in ax.spines.values(): spine.set_edgecolor('none')
        ax.axhline(0, color='white', linewidth=1.5) # محور الفواصل
        ax.axvline(0, color='white', linewidth=1.5) # محور التراتيب
        
        # المنحنى بلون سماوي
        ax.plot(x_vals, y_vals, color='#00FFFF', linewidth=2.5, label='C_f')
        
        # مستقيم المناقشة بلون أصفر/برتقالي متقطع
        ax.axhline(m_val, color='#FFC000', linestyle='--', linewidth=2.5, label=f'y = {m_val:.1f}')
        
        # المقاربات (إن وجدت)
        for mc in m_critical:
            ax.axhline(mc, color='#FF6666', linestyle=':', linewidth=1.5, alpha=0.5)

        ax.set_ylim(-4, 6)
        ax.grid(True, color='#ffffff', linestyle='-', alpha=0.1)
        
        legend = ax.legend(facecolor='#111', edgecolor='#444', loc='upper right')
        for text in legend.get_texts(): text.set_color("white")
        
        return fig

    # منطق التشغيل الآلي
    if auto_play:
        start_m = -4.0
        end_m = 4.0
        for m_anim in np.arange(start_m, end_m + 0.1, 0.15):
            fig = draw_frame(m_anim)
            plot_placeholder.pyplot(fig)
            table_placeholder.markdown(generate_html_table(m_anim), unsafe_allow_html=True)
            plt.close(fig) # لتفادي استهلاك الذاكرة
            time.sleep(0.1) # سرعة الأنيميشن
    else:
        # الوضع اليدوي
        fig = draw_frame(m_manual)
        plot_placeholder.pyplot(fig)
        table_placeholder.markdown(generate_html_table(m_manual), unsafe_allow_html=True)
        plt.close(fig)
