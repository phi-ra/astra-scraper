# ASTRA scraper

Contains a simple scraper for the ASTRA webpage.

### What it does
1. Scrapes pages in sequential manner (not really efficient, but for one page it suffices)
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

Currently supports 