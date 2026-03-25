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
│   │   └── 📄  __init__.py
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

- `workspace.ipynb/` \
**Ipynb Workspace to problem solving the real data and implementation of the created model architecture**

## Created Algorithm

### Data chunking via pagination
it takes to long to provide all the data from database, instead we chunk data by pagination. The algorithm of data pagination is shown below. The backend will only retrieved `number in pages` every pagination called.

![Pagination Flow](assets/pagination-flow.png)

Take an example let say user want to get page 3 so the backend will get only data from `index 3 * (number in pages) until (3+1) * (number in pages)`. And frontend will store every time the endpoint called and avoid to call the same page in pagination system so the page will be efficient.

### Geoindexing via lat long bins slicing
Instead search via compare all the data in database we do indexing by lat and long bins. And find all the candidate by range and compare to range. All the data selected will be choose and get it's statistic data.

![Pagination Flow](assets/geo-indexing.png)
