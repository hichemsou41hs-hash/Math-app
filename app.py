# ==================== الجزء 1 من 4 ====================
import streamlit as st
import base64
import io
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sympy as sp
from scipy.signal import find_peaks
import time
import warnings
import re
import os
import urllib.request
import urllib.error
import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from PIL import Image, ImageOps, ImageEnhance
from sympy.parsing.sympy_parser import (
    parse_expr as _raw_parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)

# ---- طبقة أمان: قائمة بيضاء قبل تحليل أي عبارة (تمنع تنفيذ كود عشوائي) ----
_SAFE_TOKEN = re.compile(r'(?:x|m|e|E|pi|ln|log|exp|sqrt|abs|Abs|cos|sin|tan)+')

def parse_expr(s, *args, **kwargs):
    s = str(s)
    if len(s) > 200 or re.search(r'[^0-9A-Za-z+\-*/().\s]', s):
        raise ValueError("رمز غير مسموح في العبارة")
     # ==================== الجزء 2 من 4 ====================
def extract_math_from_image(image_file, api_key):
    try:
        image_file.seek(0)
    except Exception:
        pass

    orig_img = Image.open(image_file).convert("RGB")
    w, h = orig_img.size
    if w < 800 or h < 250:
        scale = max(2, int(900 / max(w, 1)))
        proc_img = orig_img.resize((w * scale, h * scale), Image.Resampling.LANCZOS)
    else:
        proc_img = orig_img.copy()
    proc_img = ImageOps.expand(proc_img, border=25, fill='white')
    proc_img = ImageEnhance.Contrast(proc_img).enhance(1.4)
    proc_img = ImageEnhance.Sharpness(proc_img).enhance(1.6)

    buf = io.BytesIO()
    proc_img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    prompt = (
        "You are a specialized mathematical OCR engine. Read the mathematical function from the image.\n"
        "Output ONLY the right-hand side expression in plain mathematical notation.\n"
        "Strict rules:\n"
        "- Do NOT include 'f(x) =' or 'y ='.\n"
        "- For exponentials, write e^(...) instead of exp(...). Example: x*e^x - e*x - 2 + e.\n"
        "- For fractions, wrap numerator and denominator in parentheses: (numerator)/(denominator).\n"
        "- For natural log, write ln(...). For square root, write sqrt(...). For |x|, write abs(x).\n"
        "- Output ONLY the single-line formula with no markdown, no backticks, and no extra words."
    )

    # المفتاح يُرسل في الترويسة وليس في الرابط 
 # ==================== الجزء 3 من 5 ====================
@st.cache_resource(max_entries=50, ttl=3600)
def build_math_context(f_str, g_str, version_tag="v29"):
    cache = {'valid': False, 'error': ''}
    try:
        if not f_str or not f_str.strip():
            cache['error'] = 'EMPTY'; return cache
        if not g_str or not g_str.strip(): g_str = "m"

        x_sym, m_sym = sp.symbols('x m', real=True)
        local_dict = {
            'x': x_sym, 'm': m_sym, 'e': sp.E, 'E': sp.E, 'pi': sp.pi,
            'ln': sp.log, 'log': sp.log, 'exp': sp.exp, 'sqrt': sp.sqrt,
            'abs': sp.Abs, 'Abs': sp.Abs, 'cos': sp.cos, 'sin': sp.sin, 'tan': sp.tan
        }
        transformations = (standard_transformations + (implicit_multiplication_application,))
        f_processed = fix_implicit_mult(f_str)
        g_processed = fix_implicit_mult(g_str) or "m"
        f_expr = elim_hyperbolic(parse_expr(f_processed, local_dict=local_dict, transformations=transformations))
        g_expr = elim_hyperbolic(parse_expr(g_processed, local_dict=local_dict, transformations=transformations))

        f_func = safe_lambdify(x_sym, f_expr)
        g_func = safe_lambdify((x_sym, m_sym), g_expr)

        candidate_v_asymptotes = []
        try:
            if not f_expr.has(sp.Abs):
                n_expr, d_expr = sp.fraction(sp.cancel(f_expr))
            else:
                n_expr, d_expr = sp.fraction(f_expr)
            if d_expr != 1:
                for r in safe_solve_real(d_expr, x_sym): candidate_v_asymptotes.append(r)
        except Exception: pass
        try:
        # ==================== الجزء 4 من 8 ====================
        def exactify_value(val_float, sym_val=None):
            if sym_val is not None:
                try:
                    sym_val = elim_hyperbolic(sp.simplify(sym_val))
                    if not any(bad in str(sym_val) for bad in ["LambertW", "RootOf", "Integral", "zoo", "I", "sinh", "cosh"]):
                        l_str = sanitize_latex(sym_val)
                        if len(l_str) < 30: return l_str
                except Exception: pass
            if abs(val_float - np.e) < 1e-3: return "e"
            if abs(val_float + np.e) < 1e-3: return "-e"
            if abs(val_float - 1/np.e) < 1e-3: return r"\frac{1}{e}"
            if abs(val_float + 1/np.e) < 1e-3: return r"-\frac{1}{e}"
            if abs(val_float - (np.e - 2)) < 1e-3: return "e - 2"
            if abs(val_float - (np.e - 2 - 1/np.e)) < 1e-3: return "e - 2 - e^{-1}"
            if abs(val_float - np.pi) < 1e-3: return r"\pi"
            if abs(val_float + np.pi) < 1e-3: return r"-\pi"
            if abs(val_float - np.e**2) < 1e-3: return "e^2"
            if abs(val_float + np.e**2) < 1e-3: return "-e^2"
            if abs(val_float - 2*np.e) < 1e-3: return "2e"
            if abs(val_float + 2*np.e) < 1e-3: return "-2e"
            if abs(val_float - int(round(val_float))) < 1e-3: return str(int(round(val_float)))
            return str(round(val_float, 2)).rstrip('0').rstrip('.') if '.' in str(round(val_float, 2)) else str(round(val_float, 2))

        def extract_sign_factors(rem_expr):
            try:
                if rem_expr.has(sp.Abs): return []
                fact_expr = elim_hyperbolic(sp.factor(sp.expand(rem_expr)))
                num_f, den_f = sp.fraction(sp.together(fact_expr))
                raw_factors = []
                if num_f.is_Mul: raw_factors.extend(list(num_f.args))
                elif num_f != 1: raw_factors.append(num_f)
                if den_f != 1:
                    if den_f.is_Mul: raw_factors.extend(list(den_f.args))  
# ==================== الجزء 5 من 8 ====================
        diff_fg = sp.together(f_expr - g_expr)
        A_m = elim_hyperbolic(sp.simplify(sp.diff(diff_fg, m_sym)))
        B_m = elim_hyperbolic(sp.simplify(diff_fg.subs(m_sym, 0)))

        pivot_roots = []
        pivot_x_floats = set()
        try:
            if A_m != 0 and A_m.has(x_sym):
                for r_piv in safe_solve_real(A_m, x_sym):
                    fl_piv = safe_float(r_piv)
                    if not np.isfinite(fl_piv): continue
                    if any(abs(fl_piv - safe_float(va)) < 1e-4 for va in true_v_asymptotes): continue
                    if any(abs(fl_piv - h['val']) < 1e-4 for h in holes): continue
                    b_val_piv = safe_float(B_m.subs(x_sym, r_piv))
                    f_val_piv = safe_float(f_expr.subs(x_sym, r_piv))
                    if np.isfinite(b_val_piv) and abs(b_val_piv) < 1e-6 and np.isfinite(f_val_piv):
                        if not any(abs(fl_piv - px) < 1e-4 for px in pivot_x_floats):
                            pivot_x_floats.add(fl_piv)
                            pivot_roots.append({
                                'x_val': fl_piv,
                                'sym': r_piv,
                                'sign': 'zero' if abs(fl_piv) < 1e-5 else ('pos' if fl_piv > 0 else 'neg')
                            })
        except Exception:
            pass

        try:
            if A_m != 0:
                m_expr = elim_hyperbolic(sp.simplify(-B_m / A_m))
            else:
                m_expr_list = sp.solve(diff_fg, m_sym)
                m_expr = elim_hyperbolic(sp.simplify(m_expr_list[0])) if m_expr_list else elim_hyperbolic(sp.simplify(f_expr))
        except Exception:
         # ==================== الجزء 6 من 8 ====================
        N = len(pts_var_exact)
        def generate_variation_table_bytes():
            if N < 2: return None
            n_int_v = max(1, N - 1)
            seg_w_v = 3.2; x_start_data = 2.0; x_max = x_start_data + n_int_v * seg_w_v

            def get_v_xc(idx_pt): return x_start_data + idx_pt * seg_w_v
            def get_v_label_x(idx_pt):
                if idx_pt == 0: return x_start_data + 0.50
                if idx_pt == N - 1: return x_max - 0.50
                return x_start_data + idx_pt * seg_w_v

            fig_v, ax_v = plt.subplots(figsize=(max(8.0, x_max * 0.85), 3.5))
            fig_v.patch.set_facecolor('white'); ax_v.set_facecolor('white'); ax_v.axis('off')
            for y_line, lw_v in [(6, 2), (5, 1.5), (3.8, 1.5), (0, 2)]: ax_v.plot([0, x_max], [y_line, y_line], 'k-', lw=lw_v)
            for x_line in [0, x_start_data, x_max]: ax_v.plot([x_line, x_line], [0, 6], 'k-', lw=2)
            ax_v.text(x_start_data / 2, 5.5, '$x$', ha='center', va='center', fontsize=18, color='#1E293B', fontweight='bold')
            ax_v.text(x_start_data / 2, 4.4, "$f'(x)$", ha='center', va='center', fontsize=18, color='#1E293B', fontweight='bold')
            ax_v.text(x_start_data / 2, 1.9, '$f(x)$', ha='center', va='center', fontsize=18, color='#1E293B', fontweight='bold')

            signs = []
            for i in range(N - 1):
                left, right = pts_var_exact[i]['val'], pts_var_exact[i+1]['val']
                mid = 0 if (left == -np.inf and right == np.inf) else (right - 1 if left == -np.inf else (left + 1 if right == np.inf else (left + right) / 2.0))
                try: signs.append(None if not np.isfinite(float(f_func(mid))) else ("+" if f_func(mid + 1e-5) > f_func(mid) else "-"))
                except Exception: signs.append(None)

            right_node, left_node = {}, {}
            for i in range(N):
                p = pts_var_exact[i]
                xc_line = get_v_xc(i); xc_lbl = get_v_label_x(i)
                ax_v.text(xc_lbl, 5.5, f"${p['latex_x']}$", ha='center', va='center', fontsize=16, fontweight='bold')
                if p['type'] == 'v_asym': 
             # ==================== الجزء 7 من 8 ====================
    def draw_plot(m_val, mode='dark'):
        fig, ax = plt.subplots(figsize=(10, 6.5))
        if mode == 'dark':
            fig.patch.set_facecolor('#0F172A'); ax.set_facecolor('#0F172A')
            ax.tick_params(colors='#E2E8F0', labelsize=9)
            for spine in ax.spines.values(): spine.set_edgecolor('#475569')
            ax.axhline(0, color='#E2E8F0', linewidth=2.5, zorder=3); ax.axvline(0, color='#E2E8F0', linewidth=2.5, zorder=3)
            ax.minorticks_on()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1)); ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
            ax.grid(True, which='major', color='#475569', linestyle='-', linewidth=1.2, zorder=1)
            ax.grid(True, which='minor', color='#1E293B', linestyle='-', linewidth=0.8, zorder=1)
            c_asym, c_cf, c_cg, c_pts, c_text, bg_leg, edge_leg = '#F472B6', '#00E5FF', '#FFD700', '#EF4444', '#E2E8F0', '#1E293B', '#475569'
        else:
            fig.patch.set_facecolor('#FFFFFF'); ax.set_facecolor('#FFFFFF')
            ax.tick_params(colors='black', labelsize=9)
            for spine in ax.spines.values(): spine.set_edgecolor('#A0A0A0')
            ax.axhline(0, color='black', linewidth=2, zorder=3); ax.axvline(0, color='black', linewidth=2, zorder=3)
            ax.minorticks_on()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1)); ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
            ax.grid(True, which='major', color='#CCCCCC', linestyle='-', linewidth=1.2, zorder=1)
            ax.grid(True, which='minor', color='#EBEBEB', linestyle='-', linewidth=0.6, zorder=1)
            c_asym, c_cf, c_cg, c_pts, c_text, bg_leg, edge_leg = '#D32F2F', '#2E7D32', '#1565C0', '#FF8C00', 'black', '#FFFFFF', '#A0A0A0'

        for asym in cache['unique_asymptotes']:
            try:
                if asym['type'] == 'h':
                    ax.axhline(asym['val'], color=c_asym, linestyle='--', linewidth=2.0, zorder=4)
                    ax.text(-11.5, asym['val'] + 0.25, f"${asym['label']}$", color=c_asym, fontsize=13, fontweight='bold', ha='left')
                elif asym['type'] == 'v':
                    ax.axvline(asym['val'], color=c_asym, linestyle='--', linewidth=2.0, zorder=4)
                    ax.text(asym['val'] + 0.15, 7.2, f"${asym['label']}$", color=c_asym, fontsize=13, fontweight='bold', va='top')
                elif asym['type'] == 'oblique':
                    x_ob = np.array([-12.0, 12.0]) 
# ==================== الجزء 8 من 8 ====================
    if st.session_state.auto_play:
        m_val = st.session_state.m_anim
        stop_points = sorted(list(set(([0.0] if not m_critical_num else m_critical_num + [m_critical_num[0]-1.5, m_critical_num[-1]+1.5] + [(m_critical_num[i]+m_critical_num[i+1])/2.0 for i in range(len(m_critical_num)-1)]))))
        while m_val <= m_max_val and st.session_state.auto_play:
            fig_dark, _ = draw_plot(m_val, mode='dark')
            anim_placeholder.pyplot(fig_dark, use_container_width=True, clear_figure=True)
            table_placeholder.markdown(generate_st_markdown_table(m_val), unsafe_allow_html=True)
            plt.close(fig_dark)
            time.sleep(1.5 if any(abs(m_val - sp_val) < 1e-4 for sp_val in stop_points) else 0.02)
            next_m = m_val + 0.2
            for sp_val in stop_points:
                if m_val < sp_val - 1e-4 and next_m >= sp_val - 1e-4: next_m = float(sp_val); break
            m_val = next_m
        st.session_state.auto_play = False; st.rerun()
    else:
        m_val = m_val_manual
        fig_dark, _ = draw_plot(m_val, mode='dark')
        anim_placeholder.pyplot(fig_dark, use_container_width=True, clear_figure=True)
        table_placeholder.markdown(generate_st_markdown_table(m_val), unsafe_allow_html=True)
        plt.close(fig_dark)

    with st.expander("📊 عرض دراسة الدالة الشاملة بالترتيب المنهجي", expanded=True):
        st.markdown("<h4 style='color:#00E5FF; text-align:right; direction:rtl;'>1. حساب النهايات واستنتاج المقارب العمودي أو الأفقي:</h4>", unsafe_allow_html=True)
        st.latex(cache['domain_latex_st'])
        for lim_item in cache['limits_data_detailed']:
            st.latex(lim_item['main'])
            if lim_item['steps']:
                st.markdown("<div class='step-box-lim'>🔹 التعليل (خطوات الحساب):</div>", unsafe_allow_html=True)
                for stp in lim_item['steps']: st.latex(fr"\color{{#C4B5FD}}{{{stp}}}")
                if lim_item.get('step_note'):
                    st.markdown(f"<div style='text-align:center; direction:rtl; color:#FDE047; font-size:15px; font-weight:bold;'>💡 ({lim_item['step_note']})</div>", unsafe_allow_html=True)
            if lim_item.get('geo_txt'):
                st.success(lim_item['geo_txt'])
