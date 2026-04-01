import streamlit as st
from pathlib import Path
import pandas as pd
import json
import uuid

def create_uuid(_=None):
    return str(uuid.uuid4())

def convert2JSON(data, name):
    try:
        with open(name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return f"JSON created at {name}"

    except Exception as e:
        return f"Error happened {str(e)}"

def create_template_historical(id, station_name, data):
    return {
        "_id": create_uuid(),
        "Station_ID": id,
        "station_name": station_name,
        "data": data,
    }

BASE_STREAMLIT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_STREAMLIT_DIR / "db"
DATA_DIR.mkdir(exist_ok=True)


st.set_page_config(
    page_title="Statistic Data",
    layout="wide"
)

st.title("Statistical and Historical Processing Page")


defaults = {
    "merged_pivot_non_null_df": None,
    "metadata_json": None,
    "additional_hist_data": None,
    "unincluded_col": [],
    "pairing_data": None,
    "additional_hist_json": None,
}

for k, v in defaults.items():
    st.session_state.setdefault(k, v)


metadata_path = DATA_DIR / "metadata.json"

if not metadata_path.exists():
    st.error("Proses metadata.json terlebih dahulu di section metadata")
    st.stop()

with open(metadata_path) as f:
    metadata = json.load(f)

st.success("metadata.json terdeteksi")
st.json(metadata[:2])

st.session_state.metadata_json = metadata


uploaded_mergedpivot_file = st.file_uploader(
    "Pilih Merged Pivot Data File (.csv)",
    type=["csv"]
)

if uploaded_mergedpivot_file:
    piv_df = pd.read_csv(uploaded_mergedpivot_file)

    st.session_state.merged_pivot_non_null_df = piv_df.fillna(0)

    st.subheader("Preview Pivot Data")
    st.dataframe(
        st.session_state.merged_pivot_non_null_df,
        width="stretch"
    )


uploaded_additional_file = st.file_uploader(
    "Pilih Additional Statistical Data (.xlsx)",
    type=["xlsx"]
)

if uploaded_additional_file:

    additional_df = pd.read_excel(uploaded_additional_file)

    st.subheader("Preview Additional Data (Raw)")
    st.dataframe(additional_df, width="stretch")

    columns = additional_df.columns.tolist()

    if "Station_ID" not in columns:

        st.warning("Column 'Station_ID' tidak ditemukan.")

        suggestion = None
        for col in columns:
            if col.lower() in ["station_id", "stationid", "station"]:
                suggestion = col
                break

        selected_col = st.selectbox(
            "Pilih kolom yang merepresentasikan Station_ID:",
            options=columns,
            index=columns.index(suggestion) if suggestion else 0
        )

        additional_df["Station_ID"] = additional_df[selected_col]

        st.success(
            f"Station_ID dibuat dari kolom '{selected_col}'"
        )

    else:
        st.success("Column Station_ID ditemukan")

    st.session_state.additional_hist_data = additional_df

    st.session_state.unincluded_col = st.multiselect(
        "Kolom yang tidak disertakan",
        additional_df.columns.tolist(),
    )

    st.write(
        "Kolom tidak disertakan:",
        st.session_state.unincluded_col
    )


if st.button("Start Process Historical Data", type="primary"):

    if st.session_state.merged_pivot_non_null_df is None:
        st.warning("Upload pivot data terlebih dahulu")
        st.stop()

    if st.session_state.additional_hist_data is None:
        st.warning("Upload additional data terlebih dahulu")
        st.stop()

    with st.spinner("Processing data... please wait"):

        metadata_json = st.session_state.metadata_json
        piv_data = st.session_state.merged_pivot_non_null_df

        pairing_data = []

        progress = st.progress(0)

        for i, data in enumerate(metadata_json):

            station_id = data["Station_ID"]
            station_name = data["Station_Name"]

            try:
                series = piv_data[str(station_id)].to_list()

                pairing_data.append(
                    create_template_historical(
                        id=station_id,
                        station_name=station_name,
                        data=series
                    )
                )

            except Exception:
                continue

            progress.progress((i + 1) / len(metadata_json))

        additional_hist_data = (
            st.session_state.additional_hist_data
            .drop(columns=st.session_state.unincluded_col, errors="ignore")
            .copy()
        )

        additional_hist_data["_id"] = additional_hist_data.apply(
            create_uuid,
            axis=1
        )

        additional_hist_json = additional_hist_data.to_dict("records")

        st.session_state.pairing_data = pairing_data
        st.session_state.additional_hist_json = additional_hist_json

    st.success("Processing selesai!")


if st.session_state.pairing_data is not None:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pairing Preview")
        st.json(st.session_state.pairing_data[:2])

        pairing_path = DATA_DIR / "pairingdata.json"

        if st.button("Generate pairing data json", width="stretch"):

            msg = convert2JSON(
                st.session_state.pairing_data,
                pairing_path
            )

            st.success(msg)

    with col2:
        st.subheader("Statistical Preview")
        st.json(st.session_state.additional_hist_json[:2])

        statistical_path = DATA_DIR / "statisticaldata.json"

        if st.button("Generate statistical data json", width="stretch"):

            msg = convert2JSON(
                st.session_state.additional_hist_json,
                statistical_path
            )

            st.success(msg)