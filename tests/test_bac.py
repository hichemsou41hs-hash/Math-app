"""«تمارين الدوال في البكالوريا»: every subject listed in the index has its pages, and the app opens one."""
import json
import os

from streamlit.testing.v1 import AppTest

ROOT = os.path.join(os.path.dirname(__file__), "..")
DIR = os.path.join(ROOT, "bac_dawal")


def test_index_pages_exist():
    index = json.load(open(os.path.join(DIR, "index.json"), encoding="utf-8"))
    assert len(index) >= 20
    for year, streams in index.items():
        for stream, subjects in streams.items():
            assert stream in {"SE", "TM", "M", "GE"}
            for s, info in subjects.items():
                assert s in {"1", "2"} and info["pages"], (year, stream, s)
                for p in info["pages"]:
                    assert os.path.isfile(os.path.join(DIR, p)), p


def test_open_subject_in_app():
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=120)
    at.run()
    at.selectbox(key="bac_year").set_value("2024")
    at.run()
    at.radio(key="bac_stream_2024").set_value("SE")
    at.run()
    at.radio(key="bac_subj_2024_SE").set_value("1")
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert any("الملف الشامل" in m.value for m in at.markdown)
