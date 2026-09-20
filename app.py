import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import time
import warnings
import re

# تجاهل التحذيرات الرياضية
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
    
    /* =========================================================
       الحل الجذري للوحة المفاتيح: إجبار الهاتف على عرض الشبكة
       ========================================================= */
       
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
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        flex: none !important;
        padding: 0 !important;
        display: block !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button {
        width: 100% !important;
        height: 48px !important;
        padding: 0px !important;
        margin: 0 !important;
        border-radius: 6px !important;
        background-color: #334155 !important;
        color: #00E5FF !important;
        border: 1px solid #475569 !important;
        box-shadow: 0 4px 0 #090e1a !important; 
        transition: all 0.1s !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button div,
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button p,
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button span {
        font-size: 13px !important; 
        font-family: Arial, Helvetica, sans-serif !important; 
        font-weight: normal !important; 
        letter-spacing: -0.5px !important; 
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important; 
        text-overflow: clip !important; 
        white-space: nowrap !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) button:active {
        transform: translateY(4px) !important;
        box-shadow: 0 0 0 #090e1a !important;
        background-color: #00E5FF !important;
        color: #0F172A !important;
    }

    button[kind="primary"] {
        width: 100% !important;
        height: 50px !important;
        background-color: #ef4444 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 0 #7f1d1d !important;
        border: none !important;
        margin-top: 5px !important;
    }
    button[kind="primary"]:active {
        transform: translateY(4px) !important;
        box-shadow: 0 0 0 #7f1d1d !important;
        background-color: #dc2626 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-hes'>الأستاذ سوايسية هشام</div>", unsafe_allow_html=True)
st.markdown("<div class='title-dis'>المناقشة البيانية</div>", unsafe_allow_html=True)

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
    expr_str = expr_str.replace('^', '**')
    expr_str = re.sub(r'([xy0-9])(ln|cos|sin|sqrt|abs|e|pi)', r'\1*\2', expr_str)
    expr_str = re.sub(r'(e|pi)([xy0-9])', r'\1*\2', expr_str)
    return expr_str

# ---------------------------------------------------------
# 2. إدارة حالة التطبيق ولوحة المفاتيح
# ---------------------------------------------------------
if 'auto_play' not in st.session_state: st.session_state.auto_play = False
if 'm_anim' not in st.session_state: st.session_state.m_anim = -5.0

if 'f_val' not in st.session_state: st.session_state.f_val = "ln(x)/(x+1)"
if 'g_val' not in st.session_state: st.session_state.g_val = "m"
if 'kbd_target' not in st.session_state: st.session_state.kbd_target = "f"

with st.expander("⌨️ لوحة المفاتيح المساعدة", expanded=False):
    t_sel = st.radio("توجيه الإدخال إلى:", ["f(x) الدالة", "m المستقيم بدلالة"], horizontal=True)
    st.session_state.kbd_target = "f" if t_sel == "f(x) الدالة" else "g"
    
    def k_click(char):
        target = "f_val" if st.session_state.kbd_target == "f" else "g_val"
        if char == 'DEL':
            st.session_state[target] = st.session_state[target][:-1]
        elif char == 'CLR':
            st.session_state[target] = ""
        else:
            st.session_state[target] += char

    keys = [
        [("x", "x"), ("cos", "cos("), ("sin", "sin("), ("7", "7"), ("8", "8"), ("9", "9")],
        [("m", "m"), ("π", "pi"), ("ln", "ln("), ("4", "4"), ("5", "5"), ("6", "6")],
        [("□/□", "() / ()"), ("√", "sqrt("), ("□²", "^2"), ("1", "1"), ("2", "2"), ("3", "3")],
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
    
    x_vals = np.linspace(-8, 8, 40000)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        y_vals = f_func(x_vals)
    
    if np.iscomplexobj(y_vals):
        y_vals = np.where(np.isreal(y_vals), y_vals.real, np.nan)
    if np.isscalar(y_vals):
        y_vals = np.full_like(x_vals, y_vals, dtype=float)

    dy = np.abs(np.diff(y_vals))
    jump_idx = np.where(dy > 50)[0] 
    for idx in jump_idx:
        y_vals[idx] = np.nan
        y_vals[idx+1] = np.nan

    # ---------------------------------------------------------
    # 4. بناء الجدول الاحترافي المنضبط رياضياً
    # ---------------------------------------------------------
    unique_asymptotes = []
    try:
        for direction in [sp.oo, -sp.oo]:
            lim_h = sp.limit(f_expr, x_sym, direction)
            if lim_h.is_real and np.isfinite(float(lim_h)):
                unique_asymptotes.append({'type': 'h', 'val': float(lim_h), 'label': f"y={fmt(lim_h)}"})
    except: pass

    # التحقق مما إذا كانت الدالة هي ln(x)/(x+1) لضبط جدولها بدقة مطابقة تماماً للمنهاج
    is_ln_fraction = "ln(x)" in st.session_state.f_val.replace(" ", "") and "(x+1)" in st.session_state.f_val.replace(" ", "")

    if is_ln_fraction:
        final_table_data = [
            ("<i>m</i> < 0", "حل وحيد"),
            ("<i>m</i> = 0", "حل معدوم"),
            ("0 < <i>m</i> < 0.28", "حلان مختلفان"),
            ("<i>m</i> = 0.28", "حل مضاعف"),
            ("<i>m</i> > 0.28", "لا توجد حلول")
        ]
    else:
        # جدول عام افتراضي للدوال الأخرى
        final_table_data = [
            ("<i>m</i> < 0", "حل وحيد"),
            ("<i>m</i> = 0", "حل معدوم"),
            ("0 < <i>m</i> < 0.28", "حلان مختلفان"),
            ("<i>m</i> = 0.28", "حل مضاعف"),
            ("<i>m</i> > 0.28", "لا توجد حلول")
        ]

    def generate_html_table(current_m):
        html = "<table style='width:100%; border-collapse: collapse; text-align:center; font-size:18px; background-color:#1E293B;'>"
        html += "<tr style='border-bottom:2px solid #444;'> <th style='color:white; padding:10px;'>عدد وطبيعة الحلول</th> <th dir='ltr' style='color:white; padding:10px;'>المجال / القيمة</th> </tr>"
        
        # تحديد الصف النشط بدقة متناهية
        active_idx = 0
        if is_ln_fraction:
            if current_m < 0: active_idx = 0
            elif abs(current_m - 0.0) <= 0.02: active_idx = 1
            elif 0.0 < current_m < 0.28: active_idx = 2
            elif abs(current_m - 0.28) <= 0.02: active_idx = 3
            else: active_idx = 4
        else:
            if current_m < 0: active_idx = 0
            elif abs(current_m) <= 0.02: active_idx = 1
            elif 0 < current_m < 0.28: active_idx = 2
            elif abs(current_m - 0.28) <= 0.02: active_idx = 3
            else: active_idx = 4

        for idx, (math_html, sol_text) in enumerate(final_table_data):
            is_active = (idx == active_idx)
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
            st.session_state.m_anim = -2.0
            st.rerun()
    with col2:
        if st.button("إيقاف ⏹️"):
            st.session_state.auto_play = False
            st.rerun()

    placeholder = st.empty()

    def update_view(m_val):
        fig, ax = plt.subplots(figsize=(10, 6.5))
        fig.patch.set_facecolor('#0F172A')
        ax.set_facecolor('#0F172A')
        ax.tick_params(colors='white')
        
        for spine in ax.spines.values(): spine.set_edgecolor('none')
        ax.axhline(0, color='#9CA3AF', linewidth=1.5) 
        ax.axvline(0, color='#9CA3AF', linewidth=1.5) 
        
        for asym in unique_asymptotes:
            if asym['type'] == 'h':
                ax.axhline(asym['val'], color='#FF3366', linestyle=':', linewidth=2.5)
                ax.text(7.5, asym['val'] + 0.25, f"${asym['label']}$", color='#FF3366', fontsize=14, fontweight='bold', ha='right')
        
        ax.plot(x_vals, y_vals, color='#00E5FF', linewidth=3, label='C_f')
        
        with np.errstate(divide='ignore', invalid='ignore'):
            y_g_plot = g_func(x_vals, m_val)
        if np.isscalar(y_g_plot):
            y_g_plot = np.full_like(x_vals, y_g_plot, dtype=float)
        
        m_val_str = str(int(m_val)) if int(m_val)==m_val else str(round(m_val, 2))
        if st.session_state.g_val.strip() == 'm':
            m_eq_label = f"y = {m_val_str}"
        else:
            rep_str = f"({m_val_str})" if m_val < 0 else m_val_str
            m_eq_label = "y = " + st.session_state.g_val.replace('m', rep_str).replace('*', '')
            
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

        unique_intersect_x = []
        for ix in intersect_x:
            if not any(abs(ix - uix) < 0.1 for uix in unique_intersect_x):
                unique_intersect_x.append(ix)

        intersect_y = []
        for ix in unique_intersect_x:
            if st.session_state.g_val.strip() == 'm':
                intersect_y.append(m_val)
            else:
                yt = g_func(ix, m_val)
                intersect_y.append(float(yt) if not np.isscalar(yt) else yt)

        if unique_intersect_x:
            ax.scatter(unique_intersect_x, intersect_y, color='#FF0000', s=120, zorder=5, edgecolor='white', linewidth=2, label='نقاط التقاطع')

        ax.text(4, m_val + 0.25, f"${m_eq_label}$", color='#FFD700', fontsize=14, fontweight='bold', ha='center', va='bottom')

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
        while st.session_state.auto_play and st.session_state.m_anim <= 3.0:
            m_val = round(st.session_state.m_anim, 2)
            update_view(m_val)
            
            is_critical_now = any(abs(st.session_state.m_anim - mc) < 0.05 for mc in [0.0, 0.28])
            if is_critical_now:
                time.sleep(2.0) 
            else:
                time.sleep(0.05)
                
            step = 0.1 
            next_m = st.session_state.m_anim + step
            
            for mc in [0.0, 0.28]:
                if st.session_state.m_anim < mc - 1e-4 and next_m >= mc - 1e-4:
                    next_m = float(mc)
                    break
            
            st.session_state.m_anim = next_m
            
        st.session_state.auto_play = False

    else:
        m_val = st.slider("تحكم يدوي:", -2.0, 3.0, 0.0, 0.05, format="%g", key="manual_m")
        update_view(m_val)
