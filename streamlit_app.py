import streamlit as st
import json
import os

st.set_page_config(page_title="Nasır Dede – Makam & Terkib", layout="wide")

st.title("Abdülbaki Nasır Dede – Tedkîk u Tahkîk")
st.caption("17’li sistem · Makam & Terkib veri seti")

def find_dir(target):
    """Search for target directory starting from repo root."""
    for root, dirs, files in os.walk(os.getcwd()):
        if target in dirs:
            return os.path.join(root, target)
    return None

MAKAM_DIR = find_dir("makam")
TERKIB_DIR = find_dir("terkib")

tab1, tab2 = st.tabs(["Makamlar", "Terkibler"])

with tab1:
    st.subheader("Makamlar")
    if not MAKAM_DIR:
        st.error("makam klasörü bulunamadı (repo içinde aranamadı).")
    else:
        files = sorted([f for f in os.listdir(MAKAM_DIR) if f.endswith(".json")])
        if not files:
            st.warning("Henüz makam dosyası yok.")
        else:
            selected = st.selectbox("Makam seç:", files)
            with open(os.path.join(MAKAM_DIR, selected), "r", encoding="utf-8") as f:
                data = json.load(f)
            st.markdown(f"### {data.get('Ad','')}")
            st.json(data, expanded=True)

with tab2:
    st.subheader("Terkibler")
    if not TERKIB_DIR:
        st.error("terkib klasörü bulunamadı (repo içinde aranamadı).")
    else:
        files = sorted([f for f in os.listdir(TERKIB_DIR) if f.endswith(".json")])
        if not files:
            st.warning("Henüz terkip dosyası yok.")
        else:
            selected = st.selectbox("Terkib seç:", files)
            with open(os.path.join(TERKIB_DIR, selected), "r", encoding="utf-8") as f:
                data = json.load(f)
            st.markdown(f"### {data.get('Ad','')}")
            st.json(data, expanded=True)
