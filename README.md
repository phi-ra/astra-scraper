# ASTRA scraper

Contains a simple scraper for the ASTRA webpage. Basically just grabs everything it can find on the webpage itself and on linked feldex data fields 

## How to use it

Set up your virtual environment and run

```
pip install -r ./requirements.txt
python crawly.py --write_dir='path_to_your_write_dir'
```
and the optional arguments

### What it does
1. Scrapes pages in sequential manner (not really efficient, but for one base page it suffices)
2. Stores the following filetypes
	* .pdf
	* .html
	* .xml
	* legal documents
	* .zip
	* excel (xlsx, xls)
	* word (docx, doc, dotx)
	* powerpoint (pptx, ppt)
	* images (jpg, png, mpg)
	* CAD tools (dxf, dwg)
3. html and legal texts are stored as Beautifulsoup objects
4. Keeps a Python _"knowledge"_ dictionary, a dict that containts entries like:

	```
	url: {
	  "storage_location": path_where_file_is_stored_on_machine,
	  "hash": a hash of the content (makes it easier to keep track of changes),
	  "neighbours": [a list of all urls of neighbours]
	}
	```
5. For legal documents, there is an additional crawler that uses the [Fedlex SPARQL Endpoint](https://lindas.admin.ch/data-usage/fedlex/) to collect the full set of legal texts and also collect the dependencies specified by the JoLux model. 


### Get the docs

Docs can be recreated with `sphinx` using the docsource (if need be)
```
cd ./docs
sphinx-build -b html source build
```

## Overview
The doctree of the repo is outlined below
```
.
├── README.md
├── crawly.py
├── requirements.txt
└── src
    ├── __init__.py
    ├── legal
    │   ├── __init__.py
    │   ├── helpers.py
    │   └── sparqlqueries.py
    ├── scraper.py
    └── utils
        ├── __init__.py
        └── adminlink.py
```