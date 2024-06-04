import re
from SPARQLWrapper import SPARQLWrapper2

def extract_entries(sparql_query):
    parsed_queryset = []
    full_set = sparql_query[sparql_query.variables]
    for entry in full_set:
        sub_set = {}
        for key_, val_ in entry.items():
            val_raw = val_.value
            val_raw = re.sub('\xa0', '', val_raw)
            sub_set[key_] = val_raw

        parsed_queryset.append(sub_set)

    return parsed_queryset

def fetch_full_fedlex(sparql_ep='https://fedlex.data.admin.ch/sparqlendpoint'):
    fetcher = SPARQLWrapper2(sparql_ep)
    fetch_string = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT DISTINCT ?sr_number ?titel ?abbreviation ?sr_uri WHERE {
        ?sr_uri rdf:type jolux:ConsolidationAbstract .
        ?sr_uri jolux:classifiedByTaxonomyEntry ?TaxonomyEntry ;
                jolux:isRealizedBy ?Expression .
        
        ?TaxonomyEntry skos:notation ?sr_number .
        
        ?Expression jolux:language <http://publications.europa.eu/resource/authority/language/DEU> .
        
        ?Expression jolux:title ?titel ;
                    jolux:titleShort ?abbreviation .

        ?sr_uri jolux:dateEntryInForce ?datumInKraft .
        FILTER( ( xsd:date(?datumInKraft) <= xsd:date(now()) ) )
        OPTIONAL { ?sr_uri jolux:dateNoLongerInForce ?datumAufhebung . }
        FILTER( !bound(?datumAufhebung) || xsd:date(?datumAufhebung) >= xsd:date(now()) )
    }
    """
    fetcher.setQuery(fetch_string)
    returner = fetcher.query()
    extracted = extract_entries(returner)

    return extracted

def fetch_cited_by_art(article_uri, 
                       sparql_ep='https://fedlex.data.admin.ch/sparqlendpoint'):
    fetcher = SPARQLWrapper2(sparql_ep)
    raw_string = """
    PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
 
    SELECT DISTINCT ?abbreviation ?id_cited ?title_cited ?article_cited ?uri_citation_loc WHERE {
    
        ?Consolidation jolux:isMemberOf <__REPLACER__> . 
        ?Subdivision jolux:legalResourceSubdivisionIsPartOf ?Consolidation .
        
        ?uri_citation_loc jolux:citationFromLegalResource ?Subdivision . 
        ?uri_citation_loc jolux:language <http://publications.europa.eu/resource/authority/language/DEU> .
        
        ?uri_citation_loc jolux:citationToLegalResource/jolux:legalResourceSubdivisionIsPartOf ?Zitiertes_Gesetz .
        ?Zitiertes_Gesetz rdf:type jolux:ConsolidationAbstract .
        
        ?Zitiertes_Gesetz jolux:isRealizedBy ?Expression . # Wähle alle Expressions (Sprachausgaben)
        ?Expression jolux:language <http://publications.europa.eu/resource/authority/language/DEU> .
        ?Expression jolux:title ?title_cited ;
                    jolux:titleShort ?abbreviation ;
                    jolux:historicalLegalId ?id_cited .
                    
        OPTIONAL { ?uri_citation_loc jolux:descriptionFrom ?article_cited . }
        
        ?Zitiertes_Gesetz jolux:dateEntryInForce ?datumInKraft .
        FILTER( ( xsd:date(?datumInKraft) <= xsd:date(now()) ) )
        OPTIONAL { ?Zitiertes_Gesetz jolux:dateNoLongerInForce ?datumAufhebung . }
        FILTER( !bound(?datumAufhebung) || xsd:date(?datumAufhebung) >= xsd:date(now()) )
        } 
    """
    fetch_string = re.sub('__REPLACER__', article_uri, raw_string)

    fetcher.setQuery(fetch_string)
    returner = fetcher.query()
    extracted = extract_entries(returner)

    return extracted

def fetch_citing_art(article_uri, 
                     sparql_ep='https://fedlex.data.admin.ch/sparqlendpoint'):
    fetcher = SPARQLWrapper2(sparql_ep)
    raw_string = """
    PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
 
    SELECT DISTINCT ?abbreviation ?citing_id ?citing_title ?citing_article ?citing_uri WHERE {
        ?Subdivision jolux:legalResourceSubdivisionIsPartOf <__REPLACER__> . 
        
        ?citing_uri jolux:citationToLegalResource ?Subdivision . 
        ?citing_uri jolux:language <http://publications.europa.eu/resource/authority/language/DEU> .
        
        ?citing_uri jolux:citationFromLegalResource/jolux:legalResourceSubdivisionIsPartOf/jolux:isMemberOf ?Zitierendes_Gesetz .
        
        ?Zitierendes_Gesetz jolux:classifiedByTaxonomyEntry ?TaxonomyEntry ; # Wähle alle TaxonomyEntries
                            jolux:isRealizedBy ?Expression . # Wähle alle Expressions (Sprachausgaben)
        ?TaxonomyEntry skos:notation ?citing_id .
        ?Expression jolux:language <http://publications.europa.eu/resource/authority/language/DEU> ;
                    jolux:titleShort ?abbreviation ;
                    jolux:title ?citing_title .
                    
        OPTIONAL { ?citing_uri jolux:descriptionFrom ?citing_article . }
        
        ?Zitierendes_Gesetz jolux:dateEntryInForce ?datumInKraft .
        FILTER( ( xsd:date(?datumInKraft) <= xsd:date(now()) ) )
        OPTIONAL { ?Zitierendes_Gesetz jolux:dateNoLongerInForce ?datumAufhebung . }
        FILTER( !bound(?datumAufhebung) || xsd:date(?datumAufhebung) >= xsd:date(now()) )
    }
    """
    fetch_string = re.sub('__REPLACER__', article_uri, raw_string)
    
    fetcher.setQuery(fetch_string)
    returner = fetcher.query()
    extracted = extract_entries(returner)

    return extracted

