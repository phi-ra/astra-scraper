import re
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

def isolate_css_selector(web_element, css_element='h4', logical=False):
    """
    Find elements by CSS selector and isolate their text content.

    Parameters:
    web_element (WebElement): The parent web element to search within.
    css_element (str): The CSS selector to match the child elements (default is 'h4').
    logical (bool): If True, returns True if at least one element is found, otherwise False (default is False).

    Returns:
    str or bool: Text content of the matched element if found and logical is False. 
    True if element(s) found and logical is True, otherwise False.
    """
    for element in web_element.find_elements(By.CSS_SELECTOR, css_element):
        try:
            key_title = element.text
            pass_part = True
        except:
            pass_part = False

    if pass_part and not logical:
        return key_title
    elif logical:
        return pass_part
    
def detect_inforce(driver):
    status_bar = driver.find_element(By.CSS_SELECTOR, "app-in-force-status")
    if 'Dieser Text ist nicht in Kraft' in status_bar.text:
        legal_status = 'not_in_force'
    elif 'Dieser Text ist in Kraft' in status_bar.text:
        legal_status = 'in_force'
    else:
        legal_status = 'unknown'
    return legal_status

def get_parent(element, level=1):
    """
    Get the parent element of a given element up to a specified level.

    Parameters:
    element (WebElement): The child element.
    level (int): The depth of parent elements to traverse up (default is 1).

    Returns:
    WebElement: The parent element at the specified level.
    """
    tmp = element
    for parent_level in range(level):
        parent = tmp.find_element(By.XPATH,'./..')
        tmp = parent

    return parent

def grab_xml_link(parent_element):
    """
    Grab XML link and publication date from a parent element.

    Parameters:
    parent_element (WebElement): The parent element containing XML link and publication date.

    Returns:a
    tuple: A tuple containing the XML link and publication date.
    """
    for data_element in parent_element.find_elements(By.CSS_SELECTOR, 'td'):
        if re.compile('\d{2}').search(data_element.accessible_name):
            publication_date = data_element.accessible_name
        if 'XML' in data_element.accessible_name:
            # get container
            # now loop through linebreaks
            for link_element in data_element.find_elements(By.CSS_SELECTOR, 'a[href]'):
                if link_element.accessible_name == 'XML':
                    link_xml = link_element.get_attribute('href')

    return link_xml, publication_date

def get_xml_link(driver, date=True):
    """
    Get XML link and publication date from a driver instance.

    Parameters:
    driver (WebDriver): The WebDriver instance.
    date (bool): If True, returns the publication date along with the XML link (default is True).

    Returns:
    tuple or str: A tuple containing the XML link and publication date if date is True,
    otherwise just the XML link.
    """
    sidebars = driver.find_elements(By.CSS_SELECTOR, "div[class*='well well-white'")

    for sidebar in sidebars:
        key_ = isolate_css_selector(sidebar)

        if key_ == 'Alle Fassungen':
            # get current version
            active_sub = sidebar.find_element(By.CSS_SELECTOR, 'span[class*="soft-green"]')
            
            # get parent
            active_parent = get_parent(active_sub, 2)

            # grab XML link and data
            xml_link, publi_date = grab_xml_link(active_parent)

    if date:
        return xml_link, publi_date
    else: 
        return xml_link

def isolate_legal_xml(url, date=False):
    """
    Isolate legal XML link and publication date from a given URL.

    Parameters:
    url (str): The URL to scrape for legal XML link and publication date.
    date (bool): If True, returns the publication date along with the XML link (default is False).

    Returns:
    tuple or str: A tuple containing the XML link and publication date if date is True,
    otherwise just the XML link.
    """
    options = webdriver.ChromeOptions() 
    options.add_argument("--headless") 
    options.page_load_strategy = "none"

    driver = Chrome(options=options) 
    driver.implicitly_wait(3)

    driver.get(url)
    
    legal_status = detect_inforce(driver=driver)
    if legal_status == 'in_force':
        if date:
            xml_link, publi_date = get_xml_link(driver=driver, date=date)
            driver.close()
            return xml_link, legal_status, publi_date
        else:
            xml_link = get_xml_link(driver=driver, date=date)
            driver.close()
            return xml_link, legal_status
    else: 
        return url, legal_status
