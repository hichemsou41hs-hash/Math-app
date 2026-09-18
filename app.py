import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

# إعدادات الصفحة
st.set_page_config(page_title="المناقشة البيانية", page_icon="📈", layout="centered")

st.title("📈 تطبيق المناقشة البيانية للدوال")
st.write("أدخل الدوال بصيغة رياضية طبيعية (مثال: x^2 - 4 أو 2x+1).")

# تعريف المتغيرات الرمزية
x_sym, m_sym = sp.symbols('x m')

# خانات الإدخال
f_input = st.text_input("أدخل عبارة الدالة f(x):", value="x^2 - 4")
m_input = st.text_input("أدخل معادلة المناقشة (مثال: m, x+m, m*x):", value="m")

# معالجة المدخلات
try:
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    transformations = (standard_transformations + (implicit_multiplication_application,))
    
    f_expr_str = f_input.replace('^', '**')
    m_expr_str = m_input.replace('^', '**')

    f_expr = parse_expr(f_expr_str, transformations=transformations)
    m_expr = parse_expr(m_expr_str, transformations=transformations)
    
    # عرض العبارات بـ LaTeX
    st.write("العبارات التي تم التعرف عليها:")
    col1, col2 = st.columns(2)
    with col1:
        st.latex(rf"f(x) = {sp.latex(f_expr)}")
    with col2:
        st.latex(rf"y = {sp.latex(m_expr)}")
        
    valid_input = True
except Exception as e:
    st.error("⚠️ صيغة غير صالحة. يرجى التأكد من كتابة العبارات بشكل صحيح.")
    valid_input = False

if valid_input:
    # شريط تمرير (Slider) لقيمة الوسيط m
    st.write("---")
    st.write("### 🎛️ التحكم في المناقشة البيانية")
    m_val = st.slider("غيّر قيمة الوسيط (m):", min_value=-10.0, max_value=10.0, value=0.0, step=0.5)

    try:
        # تحويل الدالة f(x)
        f_func = sp.lambdify(x_sym, f_expr, 'numpy')
        
        # تعويض قيمة m في معادلة المناقشة لتصبح دالة في x فقط
        m_expr_sub = m_expr.subs(m_sym, m_val)
        m_func = sp.lambdify(x_sym, m_expr_sub, 'numpy')
        
        # إعداد مجال الحساب
        x_vals = np.linspace(-10, 10, 400)
        
        # حساب قيم y للدالة f(x)
        y_vals = f_func(x_vals)
        if np.isscalar(y_vals):
            y_vals = np.full_like(x_vals, y_vals)
            
        # حساب قيم y لمستقيم المناقشة
        y_m_vals = m_func(x_vals)
        if np.isscalar(y_m_vals):
            y_m_vals = np.full_like(x_vals, y_m_vals)
            
        # الرسم
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # رسم الدالة
        ax.plot(x_vals, y_vals, label=f'$f(x)$', color='#1f77b4', linewidth=2.5)
        
        # رسم مستقيم المناقشة باللون الأحمر المتقطع
        ax.plot(x_vals, y_m_vals, label=f'$y = {sp.latex(m_expr_sub)}$ (m={m_val})', color='red', linestyle='--', linewidth=2)
        
        # إعدادات المحاور
        ax.axhline(0, color='black', linewidth=1.5) 
        ax.axvline(0, color='black', linewidth=1.5) 
        
        # تقييد مجال الرؤية (y-axis) ليكون متناسقاً
        ax.set_ylim(-10, 15) 
        
        ax.grid(True, linestyle=':', alpha=0.7)
        ax.legend(fontsize=12)
        ax.set_xlabel('$x$')
        ax.set_ylabel('$y$')
        
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"⚠️ حدث خطأ أثناء الرسم: {e}")
