"""«تمارين الدوال في البكالوريا»: year -> stream -> subject -> statement pages (images, watermarked)."""
import io
import json
import os

import streamlit as st

DIR = os.path.join(os.path.dirname(__file__), "bac_dawal")
STREAMS = [("SE", "علوم تجريبية"), ("TM", "تقني رياضي (هندسة)"), ("M", "رياضيات"), ("GE", "تسيير واقتصاد")]
SESS = {"b": " (الدورة الثانية)", "x": " (الدورة الاستثنائية)"}
SUBJ = {"1": "الموضوع الأول", "2": "الموضوع الثاني"}
WHATSAPP = "https://wa.me/213699928024"
FACEBOOK = "https://www.facebook.com/share/1KHcAq6bVm/"
INSTAGRAM = "https://www.instagram.com/prof_hicham_math"

CSS = """<style>
.bac-card { direction: rtl; text-align: right; background: #1E293B; border: 1px solid #38BDF8; border-radius: 12px;
            padding: 14px 16px; margin: 10px 0 14px 0; color: #F8FAFC; font-size: 16px; line-height: 1.9; }
.bac-card b { color: #FFD700; }
.bac-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 8px; direction: ltr; justify-content: center; }
.bac-links a { padding: 7px 15px; border-radius: 30px; color: white !important; text-decoration: none !important; font-weight: bold; }
.bac-wa { background: #16A34A; } .bac-fb { background: #1877F2; }
.bac-ig { background: linear-gradient(45deg, #f09433, #dc2743, #bc1888); }
</style>"""


@st.cache_data
def _index():
    try:
        with open(os.path.join(DIR, "index.json"), encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {}


@st.cache_data
def _pdf(pages):
    from PIL import Image
    imgs = [Image.open(os.path.join(DIR, p)).convert("RGB") for p in pages]
    buf = io.BytesIO()
    imgs[0].save(buf, "PDF", save_all=True, append_images=imgs[1:], resolution=110)
    return buf.getvalue()


def _year_label(key):
    return key[:4] + SESS.get(key[4:], "")


def contact_card():
    st.markdown(
        "<div class='bac-card'>🔒 <b>الحلول المفصّلة</b> موجودة في <b>الملف الشامل</b>.<br>"
        "للحصول عليه تواصل مع الأستاذ سوايسية هشام:"
        "<div class='bac-links'>"
        f"<a class='bac-wa' href='{WHATSAPP}' target='_blank'>WhatsApp</a>"
        f"<a class='bac-fb' href='{FACEBOOK}' target='_blank'>Facebook</a>"
        f"<a class='bac-ig' href='{INSTAGRAM}' target='_blank'>Instagram</a>"
        "</div></div>", unsafe_allow_html=True)


def render():
    index = _index()
    if not index:
        return
    st.markdown(CSS, unsafe_allow_html=True)
    with st.expander("📚 تمارين الدوال في البكالوريا", expanded=False):
        years = sorted(index, key=lambda k: (k[:4], k[4:]), reverse=True)
        year = st.selectbox("اختر السنة:", years, index=None, format_func=_year_label,
                            placeholder="السنة", key="bac_year")
        if not year:
            return
        streams = [(c, n) for c, n in STREAMS if c in index[year]]
        stream = st.radio("اختر الشعبة:", [c for c, _ in streams], index=None, horizontal=True,
                          format_func=dict(streams).get, key=f"bac_stream_{year}")
        if not stream:
            return
        subjects = index[year][stream]
        subj = st.radio("اختر الموضوع:", sorted(subjects), index=None, horizontal=True,
                        format_func=SUBJ.get, key=f"bac_subj_{year}_{stream}")
        if not subj:
            return
        pages = tuple(subjects[subj]["pages"])
        contact_card()
        for p in pages:
            st.image(os.path.join(DIR, p), width="stretch")
        name = f"bac_{_year_label(year)}_{dict(STREAMS)[stream]}_{SUBJ[subj]}.pdf".replace(" ", "_")
        st.download_button("⬇️ تحميل الموضوع (PDF)", _pdf(pages), file_name=name, mime="application/pdf",
                           key=f"bac_dl_{year}_{stream}_{subj}")
        contact_card()
