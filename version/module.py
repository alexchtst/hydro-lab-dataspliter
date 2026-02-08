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


# class from the ./version/module.py
class DataSplitter:
    def __init__(
        self,
    ):
        # may be this is not nescesary at all
        self.dataSplited = None

        self.LAT_BINS = [(-90, -30), (-30, 30), (30, 90)]
        self.LON_BINS = [
            (-180, -120), (-120, -60), (-60, 0),
            (0, 60), (60, 120), (120, 180)
        ]

        self.GRID = self.build_grid_index(self.LAT_BINS, self.LON_BINS)

    def build_grid_index(self, lat_bins, lon_bins):
        grid = []

        area_id = 1

        for lat_min, lat_max in lat_bins:
            for lon_min, lon_max in lon_bins:
                grid.append({
                    "index": f"Area_{area_id}",
                    "minimum_latitude": lat_min,
                    "maximum_latitude": lat_max,
                    "minimum_longitude": lon_min,
                    "maximum_longitude": lon_max,
                })
                area_id += 1

        return grid

    def find_grid(self, lat, lon, grid):
        for area in grid:
            if (
                (
                    area["minimum_latitude"] <= lat
                    and
                    lat < area["maximum_latitude"]
                )
                and
                (
                    area["minimum_longitude"] <= lon
                    and
                    lon < area["maximum_longitude"]
                )
            ):
                return area["index"]
        else:
            return None

    def data_splitter(self, data_list, grid):
        data_container = defaultdict(list)

        for data in data_list:
            lat = data["latitude"]
            lon = data["longitude"]
            area = self.find_grid(lat, lon, grid)

            if area:
                data_container[area].append(data)
            else:
                data_container["OOB"].append(data)

        return dict(data_container)

    def convert(self, data, name):
        try:
            with open(name, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                print(f"JSON in FILE {name} created!!")
        except Exception as E:
            print(f"Error happened {str(E)}")

    def convert_all_data_container(self, data_splited):
        for k, item in data_splited.items():
            self.convert(item, name=f"./data/{k}.json")

    # incase the data loaded as the pandas dataframe
    def CSV2JSON_Convert(self, dataframe):
        json_data = dataframe.to_json(orientation="records", indent=4)
        json_data = json.loads(json_data)
        return json_data

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


    def runSplit(self, dataJSON):
        grid = self.GRID
        data_splited = self.data_splitter(dataJSON, grid)
        self.result_files = self.convert_all_data_container(data_splited)
        self.dataSplited = data_splited
    
    def UploadData(self, DB_URI, DB_NAME):
        res_temp = []
        for k, item in self.dataSplited.items():
            self.UploadToDatabase(DB_URI, DB_NAME, k, item)
            res_temp.append({"DB_NAME": DB_NAME, "COL_NAME": k})
            
    