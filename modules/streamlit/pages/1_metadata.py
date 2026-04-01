import streamlit as st
from pathlib import Path
from collections import defaultdict
import math
import pandas as pd
import json
import uuid

class DataSplitter:

    def __init__(self, data_json=None, data_frame=None):

        if data_json is not None:
            self.data = data_json
            self.data_type = "json"

        elif data_frame is not None:
            self.data = data_frame.to_dict("records")
            self.data_type = "data_frame"

        else:
            raise ValueError("Data tidak boleh kosong")

    def calculate_haversine(self, coord1, coord2):

        R = 6371  # km

        lat1, lon1 = coord1
        lat2, lon2 = coord2

        lat1, lon1 = map(math.radians, (lat1, lon1))
        lat2, lon2 = map(math.radians, (lat2, lon2))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.asin(math.sqrt(a))

        return R * c

    def process_boundaries(self, lat_name="latitude", lon_name="longitude"):

        if not self.data:
            raise ValueError("Data kosong")


        max_lat = max(self.data, key=lambda x: x[lat_name])[lat_name]
        min_lat = min(self.data, key=lambda x: x[lat_name])[lat_name]
        max_lon = max(self.data, key=lambda x: x[lon_name])[lon_name]
        min_lon = min(self.data, key=lambda x: x[lon_name])[lon_name]

        print (
            f"min-latitude: {min_lat}", "\n"
            f"max-latitude: {max_lat}", "\n"
            f"min-longitude: {min_lon}", "\n"
            f"max-longitude: {max_lon}", "\n"
        )

        return {
            "min-latitude": min_lat,
            "max-latitude": max_lat,
            "min-longitude": min_lon,
            "max-longitude": max_lon,
        }

    def create_bins_from_boundaries(
        self,
        lat_range,   # [start, end]
        lon_range,   # [start, end]
        range_lat=20,    # km
        range_lon=50     # km
    ):

        start_lat, end_lat = lat_range
        start_lon, end_lon = lon_range

        # latitude
        KM_PER_DEG_LAT = 111.32

        lat_step = range_lat / KM_PER_DEG_LAT

        lat_bins = self._generate_bins(
            start_lat, end_lat, lat_step
        )

        # longitude
        mid_lat = (start_lat + end_lat) / 2

        KM_PER_DEG_LON = 111.32 * math.cos(math.radians(mid_lat))

        if KM_PER_DEG_LON < 1e-6:
            raise ValueError("Terlalu dekat kutub")

        lon_step = range_lon / KM_PER_DEG_LON

        lon_bins = self._generate_bins(
            start_lon, end_lon, lon_step
        )

        print(
            f"There are {len(lat_bins)} latitude bins", "\n",
            f"There are {len(lon_bins)} longitude bins", "\n",
        )

        return {
            "lat_bins": lat_bins,
            "lon_bins": lon_bins
        }

    def _generate_bins(self, start, end, step):

        bins = []

        val = start

        while val <= end:
            bins.append(round(val, 6))
            val += step

        return bins

    def build_grid_index(self, lat_bins, lon_bins):

        if len(lat_bins) < 2 or len(lon_bins) < 2:
            raise ValueError("Bins tidak valid")

        lat_step = lat_bins[1] - lat_bins[0]
        lon_step = lon_bins[1] - lon_bins[0]

        grid_meta = {
            "lat_start": lat_bins[0],
            "lon_start": lon_bins[0],

            "lat_step": lat_step,
            "lon_step": lon_step,

            "lat_count": len(lat_bins) - 1,
            "lon_count": len(lon_bins) - 1,
        }

        return grid_meta


    def find_grid_fast(self, lat, lon, grid_meta):

        lat_start = grid_meta["lat_start"]
        lon_start = grid_meta["lon_start"]

        lat_step = grid_meta["lat_step"]
        lon_step = grid_meta["lon_step"]

        lat_count = grid_meta["lat_count"]
        lon_count = grid_meta["lon_count"]

        # Hitung index baris & kolom
        row = int((lat - lat_start) / lat_step)
        col = int((lon - lon_start) / lon_step)

        # Cek out of bounds
        if (
            row < 0 or row >= lat_count
            or
            col < 0 or col >= lon_count
        ):
            return None

        # Konversi ke area id
        area_id = row * lon_count + col + 1

        return f"Area_{area_id}"


    def splitdata(self, data_list, grid, lat_name = "latitude", lon_name = "longitude"):
        data_container = defaultdict(list)

        for data in data_list:
            lat = data[lat_name]
            lon = data[lon_name]
            area = self.find_grid_fast(lat, lon, grid)

            if area:
                data_container[area].append(data)
            else:
                data_container["OOB"].append(data)

        print(dict(data_container))
        return dict(data_container)

    def convert2JSON(self, data, name):
        try:
            with open(name, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                print(f"JSON in FILE {name} created!!")
        except Exception as E:
            print(f"Error happened {str(E)}")

def create_uuid(row):
    return str(uuid.uuid4())

BASE_STREAMLIT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_STREAMLIT_DIR / "db"

DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Process Metadata")

st.title("Metadata processing page")
st.write(
    "Halaman ini digunakan untuk menghasilkan "
    "infobins.json, infogrid.json, metadata.json dan spliteddata.json"
)

defaults = {
    "ready_df": None,
    "lat_option": None,
    "lon_option": None,
    "metadata_loaded": False,
    "boundaries": None,
    "bins": None,
    "grid": None,
    "splitted": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

uploaded_metadata_file = st.file_uploader(
    "Pilih Meta Data File (.csv)",
    type=["csv"]
)

if uploaded_metadata_file:

    df = pd.read_csv(uploaded_metadata_file)

    st.subheader("Preview Data")
    st.dataframe(df, width="stretch")

    cols = df.columns.tolist()

    if "latitude" not in cols:
        st.session_state.lat_option = st.selectbox(
            "Pilih kolom latitude",
            cols,
            key="lat_select",
        )
    else:
        st.session_state.lat_option = "latitude"

    if "longitude" not in cols:
        st.session_state.lon_option = st.selectbox(
            "Pilih kolom longitude",
            cols,
            key="lon_select",
        )
    else:
        st.session_state.lon_option = "longitude"

    if st.button("Review DataFrame", width="stretch"):

        df["latitude"] = df[st.session_state.lat_option]
        df["longitude"] = df[st.session_state.lon_option]
        df["_id"] = df.apply(create_uuid, axis=1)

        st.session_state.ready_df = df.copy()

        st.success("DataFrame siap digunakan")

if st.session_state.ready_df is not None:

    st.divider()
    st.subheader("Reviewed Data")
    ready_df = st.session_state.ready_df

    st.dataframe(ready_df, width="stretch")

    metadata_path = DATA_DIR / "metadata.json"

    overwrite_warning = False

    if metadata_path.exists():
        overwrite_warning = True
        st.warning(
            "metadata.json sudah ada. "
            "Generate ulang akan MENIMPA file lama."
        )

    if st.button("Generate metadata json", width="stretch"):

        ready_df.to_json(
            metadata_path,
            orient="records",
            indent=4,
        )

        st.session_state.metadata_loaded = True

        st.success(f"metadata.json dibuat di:\n{metadata_path}")


if (DATA_DIR / "metadata.json").exists():

    with open(DATA_DIR / "metadata.json") as f:
        datafile = json.load(f)

    dataSplitter = DataSplitter(datafile)

    st.divider()
    st.header("Geo Indexing Pipeline")

    if st.button("Process Boundaries", width="stretch"):

        boundaries = dataSplitter.process_boundaries()

        st.session_state.boundaries = boundaries

        st.success("Boundaries calculated")

    if st.session_state.boundaries:
        st.json(st.session_state.boundaries)

        b = st.session_state.boundaries

        st.subheader("Grid Configuration")

        range_lat = st.number_input(
            "Latitude bin size (km)",
            value=20.0,
        )

        range_lon = st.number_input(
            "Longitude bin size (km)",
            value=50.0,
        )

        if st.button("Create Bins", width="stretch"):

            bins = dataSplitter.create_bins_from_boundaries(
                lat_range=[b["min-latitude"], b["max-latitude"]],
                lon_range=[b["min-longitude"], b["max-longitude"]],
                range_lat=range_lat,
                range_lon=range_lon,
            )

            st.session_state.bins = bins

            dataSplitter.convert2JSON(
                bins,
                DATA_DIR / "infobins.json",
            )

            st.success("Bins created")

    if st.session_state.bins:

        if st.button("Build Grid", width="stretch"):

            grid = dataSplitter.build_grid_index(
                st.session_state.bins["lat_bins"],
                st.session_state.bins["lon_bins"],
            )

            st.session_state.grid = grid

            dataSplitter.convert2JSON(
                grid,
                DATA_DIR / "infogrid.json",
            )

            st.success("Grid created")

        st.json(st.session_state.grid)

    if st.session_state.grid:

        if st.button("Split Data", width="stretch"):

            result = dataSplitter.splitdata(
                datafile,
                st.session_state.grid,
            )

            st.session_state.splitted = result

            dataSplitter.convert2JSON(
                result,
                DATA_DIR / "spliteddata.json",
            )

            st.success("Data splitted")

    if st.session_state.splitted:
        st.subheader("Sample Output (2 data pertama)")
        st.json(
            dict(list(st.session_state.splitted.items())[:2])
        )