import os
import time
import pickle

import requests
import hashlib
from urllib.parse import unquote

import re
from bs4 import BeautifulSoup

from typing import Optional, Callable

from .utils.adminlink import isolate_simple
from .utils.adminlink import detect_javascript
from legal.helpers import isolate_legal_xml
from legal.sparqlqueries import fetch_full_fedlex, fetch_citing_art, fetch_cited_by_art

class AstraScraper:
    """
    Scraper to get public data from ASTRA
    """
    def __init__(self) -> None:
        self.knowledge_base = {}
        self.error_iterator = 0

    def crawl_page(self, 
                   write_dir, 
                   initial_url='https://www.astra.admin.ch/astra/de/home.html',
                   domain_url='https://www.astra.admin.ch',
                   predefined=False, 
                   write=False,
                   verbose=True,
                   begin=True,
                   retries=1,
                   **kwargs,
                   ):
        if begin:
            # set write dir
            self.write_dir = write_dir
            # Initialize if not predefined
            if not predefined:
                self._setup_crawling()
            else:
                if not hasattr(self, 'link_dict'):
                    raise AttributeError('A link dictionary needs to be\
                                        defined if using predefined=True')
                
            # Start crawling        
            self._process_page(url=initial_url, 
                            write_status=write, 
                            verbose=verbose, 
                            **kwargs)
        
        while len(self.todo_links) > 0:
            current_try=0
            current_url = next(iter(self.todo_links))

            if not domain_url in current_url and not 'classified-compilation' in current_url and not 'fedlex' in current_url:
                pull_url = domain_url + current_url
            else:
                pull_url = current_url

            try:
                self._process_page(url=pull_url, 
                                write_status=write, 
                                verbose=verbose, 
                                **kwargs)
            except:
                # Most of the time there is just an issue with the website
                # blocking the request, if still within the retries simply 
                # wait a few seconds and retry
                current_try+=1
                if current_try >= retries:
                    time.sleep(5)
                    self._process_page(url=pull_url, 
                                    write_status=write, 
                                    verbose=verbose, 
                                    **kwargs)
            self._pop_item(current_url)

    def update_data(self, 
                    knowledge_base):
        pass

    def _process_page(self, 
                      url, 
                      write_status, 
                      verbose, 
                      **kwargs):
        as_pickle = False
        # crawl page 
        crawl_object = requests.get(url)
        file_type, file_name = self._get_filenames(url)

        # if html parse and get new links
        if file_type in ['html']:
            as_pickle=True
            crawl_object, file_type, file_name, linked_docs = self._process_html(url=url, 
                                                                        crawl_object=crawl_object,
                                                                        file_name=file_name, 
                                                                        **kwargs)
        else:
            linked_docs = []

        hash_value = self._hash_file(crawl_object)
        # Store according to type
        self._store_object(url=url, 
                           object=crawl_object, 
                           file_name=file_name, 
                           file_type=file_type,
                           hex_hash=hash_value, 
                           neighbour_list=linked_docs, 
                           write=write_status, 
                           as_pickle=as_pickle,
                           )

        if verbose:
            print(f'processed: {url}')

        

    def _setup_crawling(self):
        self.link_dict = {}
        self.done_links = []
        self.internal_list = [] 
        self.error_list = []

        self._setup_write()

    def _setup_write(self):
        self.defined_filetypes = ['pdf', 'html', 
                                  'legal_xml', 'xml', 
                                  'zip', 
                                  'xlsx', 'xls', 'docx', 'doc', 'dotx', 'pptx', 'ppt', 
                                  'jpg', 'png',
                                  'dxf', 'dwg', 'mpg']
        self.write_split = {
            'pdf': 'pdf', 

            'html': 'html',

            'legal_xml': 'legal',

            'zip': 'zip',

            'xls': 'excel',
            'xlsx': 'excel', 

            'doc': 'word', 
            'docx': 'word', 
            'dotx': 'word', 

            'pptx': 'powerpoint',
            'ppt': 'powerpoint', 

            'jpg': 'images', 
            'png': 'images', 

            'dxf': 'cad', 
            'dwg': 'cad', 

            'xml': 'else',
            'mpg': 'else',
            'else': 'else'
        }

    
    def _gather_links(self,
                      soup_obj: BeautifulSoup,
                      filter_function: Optional[Callable] = None,
                      filter_string: Optional[str] = None):
        """
        Gather links from the soup object.

        Parameters:
        soup_obj (BeautifulSoup): The BeautifulSoup object.
        filter (Callable): A function to filter URLs (default is None).
        filter_string (str): A string to filter URLs (default is None).
        """

        new_list = isolate_simple(soup_obj,
                                  filter_function=filter_function,
                                  search_string=filter_string)

        if self.link_dict:
            set_new = set(new_list)
            set_existing = set(self.link_dict)

            crawl_new = list(set_new - set_existing)
            self.todo_links = crawl_new + self.todo_links
            self.todo_links = list(set(self.todo_links)  - set(self.done_links))

            self.link_dict = self.link_dict + crawl_new
        else:
            self.link_dict = new_list
            self.todo_links = new_list

        return new_list
    
    def _process_html(self, url, crawl_object, file_name, **kwargs):
        soup = BeautifulSoup(crawl_object.content, 'html.parser')
        is_javascript = detect_javascript(soup)

        # If javascript - then it is from fedlex
        if is_javascript:
            new_page, legal_status = isolate_legal_xml(url)
            # reperform crawling
            crawl_object = requests.get(new_page)
            soup = BeautifulSoup(crawl_object.content, 'xml')
            try:
                for name_item in soup.find_all('FRBRname'):
                    if name_item['xml:lang'] == 'de':
                        file_name = name_item['value']
                        file_name = re.sub(r'\\|\/','_' , file_name)
            except:
                print(f'name issue with link {new_page}')
                file_name = f'legal_text_{self.error_iterator}'
                self.error_iterator += 1

            linked_docs = []
            if legal_status == 'in_force':
                file_type = 'legal_xml'
            else:
                file_type = 'else'
            
        else:
            file_type = 'html'
            file_name = file_name
            # Gather new links
            linked_docs = self._gather_links(soup, **kwargs)
        
        parsed_data = self._parse_site(soup, file_type)
        
        return parsed_data, file_type, file_name, linked_docs


    def _parse_site(self, soup_obj, file_type):
        return soup_obj
    
    def _pop_item(self, 
                  url: str,
                  writing_steps: Optional[int] = 400):
        """
        Pop the current item from the todo links.

        Parameters:
        url (str): The URL to pop.
        verbose (bool): If True, print a message (default is True).
        """
        self.done_links.append(url)
        self.todo_links = list(set(self.todo_links)  - set(self.done_links))
        self.link_dict = list(set(self.link_dict))
        
        if len(self.link_dict) % writing_steps == 0:
            print(len(self.link_dict))
            with open(os.path.join(self.write_dir, '_overview', 'link_dict.pkl'), 'wb') as con:
                pickle.dump(self.link_dict, con)

    def _get_filenames(self, 
                       url,):
        extract_name = re.compile(r'([^\/]+$)')
        extract_type = re.compile(r'([^\.]+$)')

        string_main = re.search(extract_name, url)[0]
        file_name = unquote(string_main)

        file_type = re.search(extract_type, file_name.lower())[0]
        if not file_type in self.defined_filetypes:
            for file_t in self.defined_filetypes:
                if file_t in file_type:
                    file_type = file_t
                    return file_type, file_name
                
            file_type = 'else'
            return file_type, file_name
        else:
            return file_type, file_name

    def _hash_file(self, response_object):
        if type(response_object) == requests.models.Response:
            hash_object = hashlib.md5(response_object.content).hexdigest()
        elif type(response_object) == BeautifulSoup:
            hash_object = hashlib.md5(response_object.text.encode('utf-8')).hexdigest()
        else:
            print('issue found')
            hash_object = '__error__'
        return hash_object
    
    def _store_object(self,
                      url, 
                      object, 
                      file_name, 
                      file_type,
                      hex_hash,
                      neighbour_list,
                      write=False,
                      as_pickle=False):
        
        # prepare write path
        write_end_split = self.write_split[file_type]
        write_path = os.path.join(self.write_dir, write_end_split, file_name)

        # store relevant stuff to overview object
        self.knowledge_base[url] = {}
        self.knowledge_base[url]['storage_location'] = write_path
        self.knowledge_base[url]['file_hash'] = hex_hash
        self.knowledge_base[url]['neighbour_list'] = neighbour_list

        if write:
            # write object
            if not as_pickle:
                with open(write_path, 'wb') as con:
                    con.write(object.content)
            else:
                if '.html' in write_path:
                    comp_name = re.compile(r'(\.html)')
                    write_path = re.sub(comp_name, '.pkl', write_path)
                else:
                    write_path = write_path+'.pkl'
                with open(write_path, 'wb') as con:
                    pickle.dump(object, con)


class FedlexScraper:
    def __init__(self) -> None:
        # fet full set of uris
        self.full_set = fetch_full_fedlex()
        self.crawled_legal_knowledge = {}

    def _scrap_feldex(self, id_counter=0, reset_counter=0):
        for legal_entry in self.full_set:
            # Set up feature to restart crawling if there is an error
            # use the reset counter if necessary
            if id_counter <= reset_counter:
                id_counter += 1
                continue
            print(f"Crawling {legal_entry['titel']}")
            web_string = legal_entry['sr_uri']
            web_string = re.sub('fedlex.data.admin.ch', 'www.fedlex.admin.ch', web_string)
            web_string = web_string + '/de'

            xml_url, in_force_status = isolate_legal_xml(web_string)

            crawl_object = requests.get(xml_url)
            soup = BeautifulSoup(crawl_object.content, 'xml')

            # add some meta
            try:
                articles_citing_current = fetch_citing_art(legal_entry['sr_uri'])
            except:
                articles_citing_current = {}
            try:
                articles_cited_in_current = fetch_cited_by_art(legal_entry['sr_uri'])
            except:
                articles_cited_in_current = {}

            legal_entry['citing_article'] = articles_citing_current

            legal_entry['cited_in_article'] = articles_cited_in_current

            # save as pickle
            with open(f'data/01_raw/01_all/legal/legal_doc_{id_counter}.pkl', 'wb') as con:
                pickle.dump(soup, con)
            
            # add entry to knowledge base
            self.crawled_legal_knowledge[f'legal_doc_{id_counter}.pkl'] = legal_entry

            id_counter += 1
            