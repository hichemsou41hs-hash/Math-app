import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# إعدادات الصفحة
st.set_page_config(page_title="المناقشة البيانية", page_icon="📈", layout="centered")

# عنوان التطبيق
st.title("📈 تطبيق المناقشة البيانية للدوال")
st.write("أهلاً بك أستاذ هشام! هذا التطبيق مخصص لرسم الدوال والمناقشة البيانية.")

# خانات الإدخال
f_str = st.text_input("أدخل عبارة الدالة f(x) (مثال: x**2 - 4):", value="x**2 - 4")
m_str = st.text_input("أدخل معادلة المناقشة (مثال: m أو x+m):", value="m")

# زر التنفيذ
if st.button("رسم المنحنى والمناقشة"):
    try:
        # إعداد مجال الحساب
        x = np.linspace(-10, 10, 400)
        eval_str = f_str.replace('^', '**')
        
        # حساب الدالة
        y = eval(eval_str, {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "exp": np.exp, "abs": np.abs})
        
        # إعداد الرسم البياني
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(x, y, label=f'f(x) = {f_str}', color='#1f77b4', linewidth=2.5)
        ax.axhline(0, color='black', linewidth=1.5) # محور الفواصل
        ax.axvline(0, color='black', linewidth=1.5) # محور التراتيب
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(fontsize=12)
        
        # عرض الرسم في التطبيق
        st.pyplot(fig)
        
        # عرض النتائج
        st.success("✅ تم رسم منحنى الدالة بنجاح!")
        st.info(f"🔍 المناقشة البيانية المطلوبة: {m_str}")
        
    except Exception as e:
        st.error(f"⚠️ يوجد خطأ في كتابة عبارة الدالة، يرجى التأكد منها. (الخطأ: {e})")
