# This is prototyping repository
This repository is created to build most efficient way to represent and send data from backend

## Folder structure and content

```
├── 📁 data
│   ├── ⚙️ .gitignore
│   ├── ⚙️ all-data.json
│   ├── ⚙️ info-bins.json
│   ├── ⚙️ info-grid.json
│   ├── ⚙️ pairingdata.json
│   └── ⚙️ splited-data.json
├── 📁 version
│   ├── ⚙️ .env.example
│   ├── 📝 README.md
│   ├── 🐍 module.py
│   └── 📄 requrements.txt
├── ⚙️ .gitignore
├── 📝 README.md
├── 📄 data-lab.ipynb
├── 📄 data-merge.ipynb
├── 📄 data_processing.ipynb
├── 📄 final-test.ipynb
├── 📄 main.ipynb
└── 📄 requirements.txt
```

---
- `main.ipynb` \
**Jupyter notebook file to create efficient way to generate pivot points from database and Algorithm designing**

- `data-lab.ipynb` \
**Jupyter notebook file to implement to actual algorithm from main.ipynb**

- `data_processing.ipynb` \
**Jupyter notebook file to create create tools such as upload to database find method and implementation of data chunking**

- `data-merge.ipynb` \
**Main jupyter notebook to create data pairing for every stations to provide data statistics of stations**

- `version/` \
**Function Class and Archtecture Design Result**

- `data/` \
**Data results folder with designed algorithm**

## Created Algorithm

### Data chunking via pagination
it takes to long to provide all the data from database, instead we chunk data by pagination. The algorithm of data pagination is shown below. The backend will only retrieved `number in pages` every pagination called.

![Pagination Flow](assets/pagination-flow.png)

Take an example let say user want to get page 3 so the backend will get only data from `index 3 * (number in pages) until (3+1) * (number in pages)`. And frontend will store every time the endpoint called and avoid to call the same page in pagination system so the page will be efficient.

### Geoindexing via lat long bins slicing
Instead search via compare all the data in database we do indexing by lat and long bins. And find all the candidate by range and compare to range. All the data selected will be choose and get it's statistic data.

![Pagination Flow](assets/geo-indexing.png)
