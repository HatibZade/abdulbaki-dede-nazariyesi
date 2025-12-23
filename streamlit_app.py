import streamlit as st
import json
import os
import unicodedata
import re

st.set_page_config(page_title="Nasır Dede – Tedkîk u Tahkîk", layout="wide")

# ---------- Helpers ----------
def norm(s: str) -> str:
    if s is None:
        return ""
    s = str(s).lower()
    s = s.replace("ı","i").replace("İ","i").replace("I","i")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9 _-]+", "", s)
    return s.strip()

def find_dir_case_insensitive(target_name: str):
    target_lower = target_name.lower()
    for root, dirs, _files in os.walk(os.getcwd()):
        for d in dirs:
            if d.lower() == target_lower:
                return os.path.join(root, d)
    return None

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_json_files(folder: str):
    if not folder or not os.path.exists(folder) or not os.path.isdir(folder):
        return []
    return sorted([f for f in os.listdir(folder) if f.endswith(".json")])

def human_list(items):
    if items is None:
        return "—"
    if isinstance(items, str):
        return items if items.strip() else "—"
    if isinstance(items, list):
        cleaned = [str(x).strip() for x in items if str(x).strip() and str(x).strip() != "—"]
        return ", ".join(cleaned) if cleaned else "—"
    return str(items)

def render_makam(data: dict):
    st.markdown(f"## {data.get('Ad','')}")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Agaz")
        st.write(data.get("Agaz", "—") or "—")
        st.markdown("### Karar")
        st.write(data.get("Karar", "—") or "—")

    with col2:
        st.markdown("### Eski Adı")
        st.write(human_list(data.get("EskiAdi", ["—"])))
        st.markdown("### Not")
        st.write(data.get("Not", "—") or "—")

    st.markdown("### Nazari Seyir")
    ns = data.get("NazariSeyir", [])
    if isinstance(ns, list) and ns:
        st.write(" → ".join(ns))
    else:
        st.write("—")

    st.markdown("### Süsleyen Perdeler")
    st.write(human_list(data.get("SusleyenPerdeler", [])))

    with st.expander("Ham JSON (isteğe bağlı)"):
        st.json(data, expanded=False)

def render_terkib(data: dict):
    st.markdown(f"## {data.get('Ad','')}")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Agaze")
        st.write(data.get("Agaze", "—") or "—")
        st.markdown("### Agaz")
        st.write(data.get("Agaz", "—") or "—")
        st.markdown("### Karar")
        st.write(data.get("Karar", "—") or "—")

    with col2:
        st.markdown("### Eski Adı")
        st.write(data.get("EskiAdi", "—") or "—")
        st.markdown("### Not")
        st.write(data.get("Not", "—") or "—")

    st.markdown("### Nazari Seyir")
    st.write(data.get("NazariSeyir", "—") or "—")

    st.markdown("### Süsleme Kullanımı")
    st.write(data.get("SuslemeKullanimi", "—") or "—")

    with st.expander("Ham JSON (isteğe bağlı)"):
        st.json(data, expanded=False)

# ---------- Header ----------
st.title("Abdülbaki Nasır Dede – Tedkîk u Tahkîk")
st.caption("17’li sistem · Makam & Terkib veri seti")
st.markdown("Bu sayfa, veri setini **normal web sitesi gibi** (başlık başlık) görüntüler. Ham JSON yalnızca isteğe bağlı olarak açılır.")

# ---------- Sidebar (Advanced) ----------
auto_makam_dir = find_dir_case_insensitive("makam")
auto_terkib_dir = find_dir_case_insensitive("terkib")

with st.sidebar.expander("Gelişmiş · Veri yolu", expanded=False):
    makam_dir = st.text_input("Makam klasörü", value=auto_makam_dir or "data/makam", help="Örn: data/makam")
    terkib_dir = st.text_input("Terkib klasörü", value=auto_terkib_dir or "data/terkib", help="Örn: data/terkib")

# ---------- Tabs ----------
tab1, tab2 = st.tabs(["Makamlar", "Terkibler"])

with tab1:
    files = list_json_files(makam_dir)
    if not files:
        st.error("Makam dosyaları bulunamadı. (data/makam altında .json olmalı)")
    else:
        # Build display list by reading Ad from JSON (once per run)
        entries = []
        for fn in files:
            path = os.path.join(makam_dir, fn)
            try:
                d = load_json(path)
                ad = d.get("Ad", fn)
            except Exception:
                ad = fn
            entries.append({"label": f"{ad} ({fn})", "ad": ad, "fn": fn})

        q = st.text_input("Ara (makam adı):", value="")
        if q:
            nq = norm(q)
            filtered = [e for e in entries if nq in norm(e["ad"]) or nq in norm(e["fn"])]
        else:
            filtered = entries

        if not filtered:
            st.warning("Arama sonucu bulunamadı. Arama kutusunu temizleyip tekrar deneyin.")
        else:
            labels = [e["label"] for e in filtered]
            choice = st.selectbox("Makam seç:", labels, index=0)
            selected_fn = next(e["fn"] for e in filtered if e["label"] == choice)
            data = load_json(os.path.join(makam_dir, selected_fn))
            render_makam(data)

with tab2:
    files = list_json_files(terkib_dir)
    if not files:
        st.warning("Henüz terkip dosyası yok.")
    else:
        entries = []
        for fn in files:
            path = os.path.join(terkib_dir, fn)
            try:
                d = load_json(path)
                ad = d.get("Ad", fn)
            except Exception:
                ad = fn
            entries.append({"label": f"{ad} ({fn})", "ad": ad, "fn": fn})

        q = st.text_input("Ara (terkib adı):", value="", key="terkib_search")
        if q:
            nq = norm(q)
            filtered = [e for e in entries if nq in norm(e["ad"]) or nq in norm(e["fn"])]
        else:
            filtered = entries

        if not filtered:
            st.warning("Arama sonucu bulunamadı. Arama kutusunu temizleyip tekrar deneyin.")
        else:
            labels = [e["label"] for e in filtered]
            choice = st.selectbox("Terkib seç:", labels, index=0, key="terkib_select")
            selected_fn = next(e["fn"] for e in filtered if e["label"] == choice)
            data = load_json(os.path.join(terkib_dir, selected_fn))
            render_terkib(data)
