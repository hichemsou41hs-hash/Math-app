import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="المناقشة البيانية الشاملة", page_icon="📈", layout="centered")

st.title("📈 تطبيق المناقشة البيانية الشاملة")
st.write("أدخل الدالة، وسيقوم التطبيق برسمها واستنتاج جدول المناقشة الأفقية f(x) = m أوتوماتيكياً!")

# تعريف المتغيرات الرمزية
x_sym = sp.Symbol('x')

# خانة الإدخال
f_input = st.text_input("أدخل عبارة الدالة f(x) (مثال: e^x - x + 1 أو x^2 - 4):", value="e^x - x + 1")

# معالجة المدخلات
try:
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    transformations = (standard_transformations + (implicit_multiplication_application,))
    local_dict = {'e': sp.E, 'pi': sp.pi, 'ln': sp.log}
    
    f_expr_str = f_input.replace('^', '**')
    f_expr = parse_expr(f_expr_str, local_dict=local_dict, transformations=transformations)
    
    st.write("الدالة المدروسة:")
    st.latex(rf"f(x) = {sp.latex(f_expr)}")
    valid_input = True
except Exception as e:
    st.error("⚠️ صيغة غير صالحة. يرجى التأكد من الكتابة.")
    valid_input = False

if valid_input:
    # تحويل الدالة للرسم والحساب
    f_func = sp.lambdify(x_sym, f_expr, 'numpy')
    x_vals = np.linspace(-10, 10, 2000)
    y_vals = f_func(x_vals)
    
    # تنظيف القيم المركبة إن وجدت
    if np.iscomplexobj(y_vals):
        y_vals = np.where(np.isreal(y_vals), y_vals.real, np.nan)
    if np.isscalar(y_vals):
        y_vals = np.full_like(x_vals, y_vals, dtype=float)

    # ---------------------------------------------------------
    # خوارزمية استنتاج جدول المناقشة البيانية (النقاط الحدية)
    # ---------------------------------------------------------
    m_critical = []
    
    # 1. إيجاد f(0) الفاصل بين الحلول الموجبة والسالبة
    try:
        y_at_0 = float(f_func(0.0))
        if np.isfinite(y_at_0):
            m_critical.append(np.round(y_at_0, 2))
    except:
        pass

    # 2. إيجاد القيم الحدية (الذروات حيث تنعدم المشتقة تقريبياً)
    dy = np.diff(y_vals)
    extrema_indices = np.where(np.diff(np.sign(dy)))[0] + 1
    for idx in extrema_indices:
        val = np.round(y_vals[idx], 2)
        if np.isfinite(val):
            m_critical.append(val)

    # ترتيب وحذف القيم المكررة
    m_critical = np.unique(m_critical)
    m_critical = np.sort(m_critical)

    # دالة لحساب عدد الحلول وإشارتها عند قيمة m معينة
    def get_roots_info(m_test, is_critical):
        y_shifted = y_vals - m_test
        crossings = np.where(np.diff(np.sign(y_shifted)))[0]
        roots = [x_vals[c] for c in crossings]
        
        # التقاط الحل المضاعف عند القيم الحدية
        if is_critical:
            abs_y = np.abs(y_shifted)
            minima = np.where((abs_y[1:-1] < abs_y[:-2]) & (abs_y[1:-1] < abs_y[2:]))[0] + 1
            for idx in minima:
                if abs_y[idx] < 0.15:
                    if not any(abs(x_vals[idx] - r) < 0.2 for r in roots):
                        roots.append(x_vals[idx])
                        
        pos = sum(1 for r in roots if r > 0.05)
        neg = sum(1 for r in roots if r < -0.05)
        zero = sum(1 for r in roots if abs(r) <= 0.05)
        
        total = pos + neg + zero
        if total == 0: return "لا توجد حلول"
        if is_critical and total == 1:
            if pos == 1: return "حل مضاعف موجب"
            if neg == 1: return "حل مضاعف سالب"
            if zero == 1: return "حل مضاعف معدوم"
            
        if pos == 1 and neg == 0 and zero == 0: return "حل وحيد موجب"
        if pos == 0 and neg == 1 and zero == 0: return "حل وحيد سالب"
        if pos == 0 and neg == 0 and zero == 1: return "حل وحيد معدوم"
        if pos == 2 and neg == 0 and zero == 0: return "حلان موجبان"
        if pos == 0 and neg == 2 and zero == 0: return "حلان سالبان"
        if pos == 1 and neg == 1 and zero == 0: return "حلان مختلفان في الإشارة"
        
        desc = f"يوجد {total} حلول"
        if pos>0 or neg>0: desc += f" ({pos} موجب، {neg} سالب)"
        return desc

    # بناء مجالات الجدول
    table_data = []
    if len(m_critical) > 0:
        table_data.append({"المجال (قيم m)": f"m ∈ ] -∞ , {m_critical[0]} [", "الإشارة وعدد الحلول": get_roots_info(m_critical[0] - 1, False)})
        
        for i in range(len(m_critical)):
            table_data.append({"المجال (قيم m)": f"m = {m_critical[i]}", "الإشارة وعدد الحلول": get_roots_info(m_critical[i], True)})
            if i < len(m_critical) - 1:
                mid = (m_critical[i] + m_critical[i+1]) / 2.0
                table_data.append({"المجال (قيم m)": f"m ∈ ] {m_critical[i]} , {m_critical[i+1]} [", "الإشارة وعدد الحلول": get_roots_info(mid, False)})
                
        table_data.append({"المجال (قيم m)": f"m ∈ ] {m_critical[-1]} , +∞ [", "الإشارة وعدد الحلول": get_roots_info(m_critical[-1] + 1, False)})
    else:
        table_data.append({"المجال (قيم m)": "m ∈ ] -∞ , +∞ [", "الإشارة وعدد الحلول": get_roots_info(0, False)})

    # ---------------------------------------------------------
    # عرض الجدول والرسم
    # ---------------------------------------------------------
    st.write("---")
    st.markdown("<h3 style='text-align: center; color: #f39c12;'>جدول المناقشة البيانية الأفقية</h3>", unsafe_allow_html=True)
    
    # عرض الجدول بتنسيق أنيق
    df = pd.DataFrame(table_data)
    st.table(df.style.set_properties(**{'text-align': 'center', 'font-size': '16px', 'background-color': '#2e2e2e', 'color': 'white'}))

    # شريط التحكم التفاعلي
    st.write("---")
    st.write("### 🎛️ جرب المناقشة بنفسك للتحقق")
    m_val = st.slider("حرك المستقيم (m):", min_value=-10.0, max_value=15.0, value=0.0, step=0.25)

    # الرسم البياني
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x_vals, y_vals, label=f'$f(x)$', color='#1f77b4', linewidth=2.5)
    ax.axhline(m_val, label=f'$y = m$ (m={m_val})', color='red', linestyle='--', linewidth=2)
    
    ax.axhline(0, color='black', linewidth=1.5) 
    ax.axvline(0, color='black', linewidth=1.5) 
    ax.set_ylim(-10, 15) 
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.legend(fontsize=12)
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    
    st.pyplot(fig)
