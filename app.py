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
       الحل الجذري للوحة المفاتيح
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
    if "()" in expr_str:
        expr_str = expr_str.replace("()", "(1)")
    expr_str = expr_str.replace('^', '**')
    expr_str = re.sub(r'([xy0-9])(ln|cos|sin|sqrt|abs|e|pi)', r'\1*\2', expr_str)
    expr_str = re.sub(r'(e|pi)([xy0-9])', r'\1*\2', expr_str)
    return expr_str

# ---------------------------------------------------------
# 2. إدارة حالة التطبيق ولوحة المفاتيح
# ---------------------------------------------------------
if 'auto_play' not in st.session_state: st.session_state.auto_play = False
if 'm_anim' not in st.session_state: st.session_state.m_anim = -5.0

if 'f_val' not in st.session_state: st.session_state.f_val = "ln(x**2+x)/x"
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
        [("□/□", "/"), ("√", "sqrt("), ("□²", "^2"), ("1", "1"), ("2", "2"), ("3", "3")],
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
    
    x_vals = np.linspace(-8, 8, 40001)
    
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
    # 4. الرادار الذكي الشامل (التحليلي + العددي) لتعويض عجز SymPy
    # ---------------------------------------------------------
    unique_asymptotes = []
    m_critical = []
    
    # أ. المقاربات الأفقية
    try:
        for direction in [sp.oo, -sp.oo]:
            lim_h = sp.limit(f_expr, x_sym, direction)
            if lim_h.is_real and np.isfinite(float(lim_h)):
                unique_asymptotes.append({'type': 'h', 'val': float(lim_h), 'label': f"y={fmt(lim_h)}"})
                m_critical.append(round(float(lim_h), 2))
    except: pass

    # المقاربات العمودية
    candidate_v_asymptotes = []
    try:
        n_expr, d_expr = sp.fraction(sp.cancel(f_expr))
        if d_expr != 1:
            roots = sp.solve(d_expr, x_sym)
            for r in roots:
                if r.is_real: candidate_v_asymptotes.append(float(r))
    except: pass
    
    try:
        for log_expr in f_expr.atoms(sp.log):
            arg = log_expr.args[0]
            roots = sp.solve(arg, x_sym)
            for r in roots:
                if r.is_real: candidate_v_asymptotes.append(float(r))
    except: pass

    for r in set(candidate_v_asymptotes):
        r_str = str(int(r)) if int(r)==r else str(float(r))
        unique_asymptotes.append({'type': 'v', 'val': float(r), 'label': f"x={r_str}"})

    seen_labels = set()
    final_asyms = []
    for asym in unique_asymptotes:
        if asym['label'] not in seen_labels:
            seen_labels.add(asym['label'])
            final_asyms.append(asym)
    unique_asymptotes = final_asyms

    # ب. استخراج القيم الحرجة (تقاطع مع المحاور والمشتقة جبرياً إن أمكن)
    try:
        val_0 = float(f_expr.subs(x_sym, 0))
        if np.isfinite(val_0): m_critical.append(round(val_0, 2))
    except: pass

    try:
        df_expr = sp.diff(f_expr, x_sym)
        crit_pts = sp.solve(df_expr, x_sym)
        for cp in crit_pts:
            if cp.is_real:
                val_cp = float(f_expr.subs(x_sym, cp))
                if np.isfinite(val_cp): m_critical.append(round(val_cp, 2))
    except: pass

    # ج. الإضافة العبقرية: رصد القيم الحدية (الذروات) عددياً لسد عجز SymPy
    with np.errstate(divide='ignore', invalid='ignore'):
        dy_num = np.diff(y_vals)
        for i in range(1, len(dy_num)):
            dy_prev = dy_num[i-1]
            dy_curr = dy_num[i]
            if np.isfinite(dy_prev) and np.isfinite(dy_curr):
                # إذا تغيرت الإشارة من موجب إلى سالب (أو العكس)، فهذه ذروة حقيقية
                if dy_prev * dy_curr <= 0 and (dy_prev != 0 or dy_curr != 0):
                    idx = i
                    if np.isfinite(y_vals[idx]) and np.isfinite(y_vals[idx-1]) and np.isfinite(y_vals[idx+1]):
                        # فلترة لضمان أنها قمة وليست قفزة مقارب عمودي
                        if abs(y_vals[idx] - y_vals[idx-1]) < 0.5:
                            m_critical.append(round(float(y_vals[idx]), 2))

    # فلترة وترتيب ودمج القيم الحرجة المتقاربة (لمنع التكرار)
    m_critical = [round(m, 2) for m in m_critical if np.isfinite(m) and abs(m) < 50]
    m_critical.sort()
    merged_m_crit = []
    for m in m_critical:
        if not merged_m_crit:
            merged_m_crit.append(m)
        else:
            # دمج القيم الحرجة المتقاربة جداً
            if abs(m - merged_m_crit[-1]) > 0.05:
                merged_m_crit.append(m)
    m_critical = merged_m_crit

    # ---------------------------------------------------------
    # 5. تصنيف الحلول بناءً على التقاطع وقنص التماس
    # ---------------------------------------------------------
    def get_roots_text(m_test):
        # التحقق إن كانت القيمة m تعتبر قيمة حرجة (ذروة)
        is_critical = any(abs(m_test - mc) < 1e-3 for mc in m_critical)
        
        with np.errstate(divide='ignore', invalid='ignore'):
            y_g = g_func(x_vals, m_test)
            if np.isscalar(y_g):
                y_g = np.full_like(x_vals, y_g, dtype=float)
            diff = y_vals - y_g
            
        crossings = []
        for i in range(len(diff)-1):
            if np.isfinite(diff[i]) and np.isfinite(diff[i+1]):
                if diff[i] * diff[i+1] < 0:
                    crossings.append(x_vals[i])
                elif diff[i] == 0:
                    crossings.append(x_vals[i])
                    
        tangents = []
        cleaned_crossings = []
        
        # هندسة قنص التماس: دمج نقطتي تقاطع متقاربتين جداً في نقطة مماس واحدة
        if is_critical:
            skip = False
            for i in range(len(crossings)):
                if skip:
                    skip = False
                    continue
                if i < len(crossings)-1 and abs(crossings[i+1] - crossings[i]) < 0.4:
                    tangents.append((crossings[i] + crossings[i+1])/2.0)
                    skip = True
                else:
                    cleaned_crossings.append(crossings[i])
            
            # قنص التماس الخفي (في حال مر المستقيم فوق الذروة بمسافة مجهرية)
            abs_diff = np.abs(diff)
            for i in range(1, len(abs_diff)-1):
                if np.isfinite(abs_diff[i-1]) and np.isfinite(abs_diff[i]) and np.isfinite(abs_diff[i+1]):
                    if abs_diff[i] < abs_diff[i-1] and abs_diff[i] < abs_diff[i+1]:
                        if abs_diff[i] < 0.08:
                            if not any(abs(x_vals[i] - c) < 0.5 for c in cleaned_crossings) and not any(abs(x_vals[i] - t) < 0.5 for t in tangents):
                                tangents.append(x_vals[i])
        else:
            cleaned_crossings = crossings
            
        all_roots = [(c, "single") for c in cleaned_crossings] + [(t, "double") for t in tangents]
        
        final_roots = []
        for r, t in all_roots:
            if not any(abs(r - fr[0]) < 0.1 for fr in final_roots):
                final_roots.append((r, t))
        
        count = len(final_roots)
        if count == 0: return "لا توجد حلول"
        
        desc = []
        pos_s = sum(1 for r, t in final_roots if r > 0.05 and t == "single")
        neg_s = sum(1 for r, t in final_roots if r < -0.05 and t == "single")
        zero_s = sum(1 for r, t in final_roots if abs(r) <= 0.05 and t == "single")
        pos_d = sum(1 for r, t in final_roots if r > 0.05 and t == "double")
        neg_d = sum(1 for r, t in final_roots if r < -0.05 and t == "double")
        zero_d = sum(1 for r, t in final_roots if abs(r) <= 0.05 and t == "double")

        if pos_d == 1: desc.append("حل مضاعف موجب")
        elif pos_d > 1: desc.append(f"{pos_d} حلول مضاعفة موجبة")
        if neg_d == 1: desc.append("حل مضاعف سالب")
        elif neg_d > 1: desc.append(f"{neg_d} حلول مضاعفة سالبة")
        if zero_d == 1: desc.append("حل مضاعف معدوم")

        if pos_s == 1: desc.append("حل وحيد موجب")
        elif pos_s == 2: desc.append("حلان موجبان")
        elif pos_s > 2: desc.append(f"{pos_s} حلول موجبة")

        if neg_s == 1: desc.append("حل وحيد سالب")
        elif neg_s == 2: desc.append("حلان سالبان")
        elif neg_s > 2: desc.append(f"{neg_s} حلول سالبة")

        if zero_s == 1: desc.append("حل معدوم")

        if pos_s == 1 and neg_s == 1 and len(desc) == 2:
            return "حلان مختلفان في الإشارة"
        elif pos_s == 2 and neg_s == 1 and pos_d == 0 and len(desc) == 2:
            return "حلان موجبان وحل سالب"
        elif pos_s == 1 and neg_s == 2 and pos_d == 0 and len(desc) == 2:
            return "حلان سالبان وحل موجب"
        elif pos_s == 1 and zero_s == 1 and len(desc) == 2:
            return "حل معدوم و حل موجب"
        elif neg_s == 1 and zero_s == 1 and len(desc) == 2:
            return "حل معدوم و حل سالب"

        if len(desc) == 0: return f"{count} حلول"
        return " و ".join(desc)

    raw_intervals = []
    if len(m_critical) > 0:
        raw_intervals.append((float('-inf'), m_critical[0], get_roots_text(m_critical[0] - 1.0)))
        for i in range(len(m_critical)):
            raw_intervals.append((m_critical[i], m_critical[i], get_roots_text(m_critical[i])))
            if i < len(m_critical) - 1:
                mid = (m_critical[i] + m_critical[i+1]) / 2.0
                raw_intervals.append((m_critical[i], m_critical[i+1], get_roots_text(mid)))
        raw_intervals.append((m_critical[-1], float('inf'), get_roots_text(m_critical[-1] + 1.0)))
    else:
        raw_intervals.append((float('-inf'), float('inf'), get_roots_text(0.0)))

    # دمج المجالات المتشابهة تلقائياً
    merged_intervals = []
    if raw_intervals:
        cur_L, cur_H, cur_text = raw_intervals[0][0], raw_intervals[0][1], raw_intervals[0][2]
        for item in raw_intervals[1:]:
            l, h, txt = item[0], item[1], item[2]
            if txt == cur_text:
                cur_H = h
            else:
                merged_intervals.append((cur_L, cur_H, cur_text))
                cur_L, cur_H, cur_text = l, h, txt
        merged_intervals.append((cur_L, cur_H, cur_text))

    final_table_data = []
    for L, H, sol_text in merged_intervals:
        if L == float('-inf') and H == float('inf'):
            math_html = "<i>m</i> ∈ ℝ"
        elif L == float('-inf'):
            math_html = f"<i>m</i> < {fmt(H)}"
        elif H == float('inf'):
            math_html = f"<i>m</i> > {fmt(L)}"
        elif L == H:
            math_html = f"<i>m</i> = {fmt(L)}"
        else:
            math_html = f"{fmt(L)} < <i>m</i> < {fmt(H)}"
        final_table_data.append((math_html, sol_text, L, H))

    def generate_html_table(current_m):
        html = "<table style='width:100%; border-collapse: collapse; text-align:center; font-size:18px; background-color:#1E293B;'>"
        html += "<tr style='border-bottom:2px solid #444;'> <th style='color:white; padding:10px;'>عدد وطبيعة الحلول</th> <th dir='ltr' style='color:white; padding:10px;'>المجال / القيمة</th> </tr>"
        
        active_idx = 0
        for idx, (math_html, sol_text, L, H) in enumerate(final_table_data):
            is_active = False
            if L == H:
                if abs(current_m - L) <= 0.03: is_active = True
            elif L == float('-inf'):
                if current_m <= H - 0.03: is_active = True
            elif H == float('inf'):
                if current_m >= L + 0.03: is_active = True
            else:
                if L + 0.03 <= current_m <= H - 0.03: is_active = True
            if is_active:
                active_idx = idx

        for idx, (math_html, sol_text, L, H) in enumerate(final_table_data):
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
            st.session_state.m_anim = -3.0
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
            elif asym['type'] == 'v':
                ax.axvline(asym['val'], color='#FF3366', linestyle=':', linewidth=2.5)
                ax.text(asym['val'] + 0.15, 6.5, f"${asym['label']}$", color='#FF3366', fontsize=14, fontweight='bold', va='top')
        
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
        while st.session_state.auto_play and st.session_state.m_anim <= 4.0:
            m_val = round(st.session_state.m_anim, 2)
            update_view(m_val)
            
            is_critical_now = any(abs(st.session_state.m_anim - mc) < 0.05 for mc in m_critical)
            if is_critical_now:
                time.sleep(2.0) 
            else:
                time.sleep(0.05)
                
            step = 0.1 
            next_m = st.session_state.m_anim + step
            
            for mc in m_critical:
                if st.session_state.m_anim < mc - 1e-4 and next_m >= mc - 1e-4:
                    next_m = float(mc)
                    break
            
            st.session_state.m_anim = next_m
            
        st.session_state.auto_play = False

    else:
        m_val = st.slider("تحكم يدوي:", -3.0, 4.0, 0.0, 0.05, format="%g", key="manual_m")
        update_view(m_val)
