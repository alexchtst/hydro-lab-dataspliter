import json
from collections import defaultdict
import math
import pandas as pd
import pymongo

# constant and value
LAT_BINS = [(-90, -30), (-30, 30), (30, 90)]
LON_BINS = [
    (-180, -120), (-120, -60), (-60, 0),
    (0, 60), (60, 120), (120, 180)
]

# functions


def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1) * math.cos(lat2) *
         math.sin(dlon / 2) ** 2)

    c = 2 * math.asin(math.sqrt(a))

    return R * c


def build_grid_index(lat_bins, lon_bins):
    grid = []

    area_id = 1

    for lat_min, lat_max in lat_bins:
        for lon_min, lon_max in lon_bins:
            grid.append({
                "index": f"Area_{area_id}",
                "minimum-latitude": lat_min,
                "maximum-latitude": lat_max,
                "minimum-longitude": lon_min,
                "maximum-longitude": lon_max,
            })
            area_id += 1

    return grid


def find_grid(lat, lon, grid):
    for area in grid:
        if (
            (
                area["minimum-latitude"] <= lat
                and
                lat < area["maximum-latitude"]
            )
            and
            (
                area["minimum-longitude"] <= lon
                and
                lon < area["maximum-longitude"]
            )
        ):
            return area["index"]
    else:
        return None


def data_splitter(data_list, grid):
    data_container = defaultdict(list)

    for data in data_list:

        lat = data["latitude"]
        lon = data["longitude"]

        area = find_grid(lat, lon, grid)   # FIX

        if area:
            data_container[area].append(data)
        else:
            data_container["OOB"].append(data)

    return dict(data_container)



def convert(data, name):
    try:
        with open(name, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            print(f"JSON in FILE {name} created!!")
    except Exception as E:
        print(f"Error happened {str(E)}")


def convert_all_data_container(data_splited):
    for k, item in data_splited.items():
        convert(item, name=f"./data/{k}.json")

# class
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
            
    def UploadToDatabase(
        self, 
        DB_URI, DB_NAME, 
        COLLECTION_NAME, data_list
    ):
        try:
            client = pymongo.MongoClient(DB_URI)

            db = client[DB_NAME]

            collection = db[COLLECTION_NAME]

            collection.insert_many(data_list)

            print(
                f"Data stored in DB: {DB_NAME}, Collection: {COLLECTION_NAME}"
            )

        except Exception as E:
            print(f"Error happened: {str(E)}")
            
    def UploadData(self, DB_URI, DB_NAME):
        res_temp = []
        for k, item in self.dataSplited.items():
            self.UploadToDatabase(DB_URI, DB_NAME, k, item)
            res_temp.append({"DB_NAME": DB_NAME, "COL_NAME": k})
    