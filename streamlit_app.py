import streamlit as st
import json
import os
from pathlib import Path

st.set_page_config(page_title="Nasır Dede – Makam & Terkib", layout="wide")
st.title("Abdülbaki Nasır Dede – Tedkîk u Tahkîk")
st.caption("17’li sistem · Makam & Terkib veri seti")

# --- Diagnostics ------------------------------------------------------------
with st.expander("Tanılama (repo dizini ve dosya ağacı)", expanded=False):
    cwd = Path.cwd()
    st.write("Çalışma dizini:", str(cwd))

    # Show first 2 levels of tree (avoid huge output)
    def tree(root: Path, max_depth: int = 2):
        lines = []
        root = root.resolve()
        for p in sorted(root.rglob("*")):
            try:
                rel = p.relative_to(root)
            except Exception:
                continue
            depth = len(rel.parts)
            if depth <= max_depth:
                lines.append(f"{'  '*(depth-1)}- {rel.as_posix()}{'/' if p.is_dir() else ''}")
        return "\n".join(lines) if lines else "(boş)"
    st.code(tree(cwd, max_depth=3), language="text")

# --- Helpers ----------------------------------------------------------------
def find_dir_case_insensitive(target_name: str):
    target_lower = target_name.lower()
    for root, dirs, _files in os.walk(os.getcwd()):
        for d in dirs:
            if d.lower() == target_lower:
                return os.path.join(root, d)
    return None

auto_makam_dir = find_dir_case_insensitive("makam")
auto_terkib_dir = find_dir_case_insensitive("terkib")

st.sidebar.header("Veri yolu")
makam_dir = st.sidebar.text_input(
    "Makam klasörü (elle girilebilir)",
    value=auto_makam_dir or "",
    placeholder="Örn: data/makam"
)
terkib_dir = st.sidebar.text_input(
    "Terkib klasörü (elle girilebilir)",
    value=auto_terkib_dir or "",
    placeholder="Örn: data/terkib"
)

def load_json_files(folder: str):
    if not folder or not os.path.exists(folder) or not os.path.isdir(folder):
        return [], None
    files = sorted([f for f in os.listdir(folder) if f.endswith(".json")])
    return files, folder

tab1, tab2 = st.tabs(["Makamlar", "Terkibler"])

with tab1:
    st.subheader("Makamlar")
    files, resolved = load_json_files(makam_dir)
    if not resolved:
        st.error("Makam klasörü bulunamadı. Tanılama bölümünden repo ağacını kontrol edip klasör yolunu soldan gir.")
    elif not files:
        st.warning(f"Makam klasörü var ama .json yok: {resolved}")
    else:
        selected = st.selectbox("Makam seç:", files)
        with open(os.path.join(resolved, selected), "r", encoding="utf-8") as f:
            data = json.load(f)
        st.markdown(f"### {data.get('Ad','')}")
        st.json(data, expanded=True)

with tab2:
    st.subheader("Terkibler")
    files, resolved = load_json_files(terkib_dir)
    if not resolved:
        st.error("Terkib klasörü bulunamadı. Tanılama bölümünden repo ağacını kontrol edip klasör yolunu soldan gir.")
    elif not files:
        st.warning(f"Terkib klasörü var ama .json yok: {resolved}")
    else:
        selected = st.selectbox("Terkib seç:", files)
        with open(os.path.join(resolved, selected), "r", encoding="utf-8") as f:
            data = json.load(f)
        st.markdown(f"### {data.get('Ad','')}")
        st.json(data, expanded=True)
