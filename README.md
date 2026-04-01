# This is prototyping repository
This repository is created to build most efficient way to represent and send data from backend

## Folder structure and content

```
├── 📁 assets
│   ├── 🖼️ geo-indexing.png
│   └── 🖼️ pagination-flow.png
├── 📁 data
│   ├── 📁 real_data
│   │   └── 📄 ....
│   ├── ⚙️ .gitignore
│   ├── 📄 ....
│   └── 📝 DATACARD.md
├── 📁 examples
│   └── 📄 Data_Spliter_Example.ipynb
├── 📁 modules
│   ├── 📁 streamlit
│   │   ├── 📄 __init__.py
│   │   └── 📄  app.py
│   ├── 📁 v1
│   │   ├── 📄 __init__.py
│   │   ├── 📄 data_merger.py
│   │   ├── 📄 data_splitter.py
│   │   ├── 📄 fetcher_functions.py
│   │   └── 📄 uploader_todb.py
│   └── 📄 __init__.py
├── ⚙️ .gitignore
├── 📝 README.md
├── 📄 requirements.txt
└── 📄 workspace.ipynb
```

---

- `version/` \
**Function, Class and Archtecture Design Result**

- `data/` \
**Data results folder with designed algorithm**

- `modules/streamlit/app.py` \
**Streamlit for data editor to generate and post data**

- `workspace.ipynb` \
**Ipynb Workspace to problem solving the real data and implementation of the created model architecture**

## Created Algorithm

### Data chunking via pagination
it takes to long to provide all the data from database, instead we chunk data by pagination. The algorithm of data pagination is shown below. The backend will only retrieved `number in pages` every pagination called.

![Pagination Flow](assets/pagination-flow.png)

Take an example let say user want to get page 3 so the backend will get only data from `index 3 * (number in pages) until (3+1) * (number in pages)`. And frontend will store every time the endpoint called and avoid to call the same page in pagination system so the page will be efficient.

### Geoindexing via lat long bins slicing
Instead search via compare all the data in database we do indexing by lat and long bins. And find all the candidate by range and compare to range. All the data selected will be choose and get it's statistic data.

![Pagination Flow](assets/geo-indexing.png)


### How to Use Streamlit

This project provides a web-based GUI built with **Streamlit** to manage the Hydrolab data processing pipeline, including data preparation, statistical processing, and database synchronization.

---

#### 1. Install Dependencies

Make sure you already have **Python 3.10+** installed.

Install all required packages:

```bash
pip install -r requirements.txt
```

---

#### 2. Setup Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add your MongoDB connection:

```env
DB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

---

#### 3. Project Structure (Important)

Make sure the directory structure is correct:

```
streamlit/
├── app.py
└── pages/
db/
├── metadata.json
├── pairingdata.json
├── statisticaldata.json
├── historical.json
├── infobins.json
├── infogrid.json
└── spliteddata.json
```

The `db/` folder is used as the intermediate storage for generated JSON datasets.

---

### 4. Run Streamlit App

From the project directory, run:

```bash
streamlit run modules/streamlit/app.py
```

Streamlit will start a local server:

```
Local URL: http://localhost:8501
```

Open it in your browser.

---

### 5. Application Workflow

Use the sidebar to navigate through the pipeline pages.

#### Step 1 — Metadata Processing

Generate and validate station metadata.

#### Step 2 — Statistical & Historical Processing

Upload pivot and additional datasets to generate:

* pairing data
* statistical data
* historical data

Output will be saved into the `db/` folder.

#### Step 3 — Upload to Database

Upload all generated JSON files into MongoDB.

> Upload will only be enabled if all required files exist.

---

#### 6. Required JSON Files

Before uploading to MongoDB, the following files must exist:

```
metadata.json
pairingdata.json
statisticaldata.json
historical.json
infobins.json
infogrid.json
spliteddata.json
```

If any file is missing, the upload process will be blocked automatically.

---

#### 7. Stop the Application

Press:

```
CTRL + C
```

inside the terminal.

---

#### Notes

* The Streamlit app acts as a **data pipeline controller**, not a production API.
* Generated files are deterministic and safe to regenerate.
* Always run the pipeline steps sequentially.