import streamlit as st
from pathlib import Path
import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv


st.set_page_config(page_title="DB Upload")

st.title("Upload to DB")
st.write(
    "Halaman ini digunakan untuk mengupload data json ke database "
    "supaya backend dan frontend dapat sinkron satu sama lain"
)

BASE_STREAMLIT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_STREAMLIT_DIR / "db"

if not DATA_DIR.exists():
    st.error("Folder db tidak ditemukan")
    st.stop()


REQUIRED_FILES = {
    "infobins.json": ("bins", "one"),
    "infogrid.json": ("grid", "one"),
    "spliteddata.json": ("splitted", "one"),
    "metadata.json": ("stations", "many"),
    "pairingdata.json": ("pairings", "many"),
    "statisticaldata.json": ("statistics", "many"),
}

existing_files = {
    file.name: file
    for file in DATA_DIR.glob("*.json")
}

st.subheader("Status File JSON")

missing_files = []

for filename in REQUIRED_FILES.keys():

    if filename in existing_files:
        st.write(f"{filename} : OK")
    else:
        st.write(f"{filename} : MISSING")
        missing_files.append(filename)


if missing_files:
    st.error("Upload diblokir. File berikut belum tersedia:")
    for f in missing_files:
        st.write(f"- {f}")
    st.stop()


st.success("Semua file terdeteksi. Siap upload.")


load_dotenv()

DB_URI = os.getenv("DB_URI")
DB_NAME = "hydrolab-database-v0"

if not DB_URI:
    st.error("DB_URI tidak ditemukan di .env")
    st.stop()


def load_file_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Gagal membaca {path.name}: {e}")
        return None


if st.button("Upload All JSON to MongoDB", type="primary"):

    with st.spinner("Uploading data to MongoDB..."):

        try:
            client = MongoClient(DB_URI)
            db = client[DB_NAME]

            progress = st.progress(0)
            total = len(REQUIRED_FILES)

            for i, (filename, config) in enumerate(REQUIRED_FILES.items()):

                collection_name, mode = config
                file_path = existing_files[filename]

                data = load_file_json(file_path)

                if data is None:
                    st.stop()

                collection = db[collection_name]

                collection.delete_many({})

                if mode == "one":
                    collection.insert_one(data)
                else:
                    collection.insert_many(data)

                progress.progress((i + 1) / total)

            client.close()

            st.success("Semua data berhasil diupload ke MongoDB")

        except Exception as e:
            st.error(f"Upload gagal: {e}")