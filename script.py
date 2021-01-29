from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from dotenv import load_dotenv
import requests, os, codecs
load_dotenv()

#==========GLOBAL VARIABLES==========#
TXT_API_KEY = os.environ.get('TXTBELT_API_KEY')
PHONE_NUM = os.environ.get('CELL_NUM')
START_URL = "https://myturn.ca.gov/"
TEXTBELT_URL = "https://textbelt.com/text"
COUNTY = 'Los Angeles'
ZIPCODE = '90242'
AGE_RANGE = '65 - 74'
HIT_RESPONSE = "Found appointment(s) available. Text notification sent."
MISS_RESPONSE = "no appointments yet"
SHORT_PAUSE = 2
LONGER_PAUSE = 3

def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

def launch_page(chrome_driver):
    return chrome_driver.get(START_URL)

#==========MAIN FUNCTION==========#
def check_availability(CHECKSUM=0):
    chrome_driver = get_driver()
    CHECKSUM += 1
    sleep(SHORT_PAUSE)
    chrome_driver.maximize_window() # open new browser
    
    #...START PAGE
    launch_page(chrome_driver)
    browser_title_text = 'CDPH'
    assert browser_title_text in chrome_driver.title
    sleep(LONGER_PAUSE)
    
    elem_tag_name = 'button'
    title_btn = chrome_driver.find_element_by_tag_name(elem_tag_name)
    title_btn.click()
    CHECKSUM += 1
    sleep(SHORT_PAUSE)
    
    #...SCREENING PAGE
    browser_title_text = 'Screening'
    assert browser_title_text in chrome_driver.title
    sleep(LONGER_PAUSE)
    
    elem_name = "q-screening-18-yr-of-age"
    chrome_driver.find_element_by_name(elem_name).click()
    elem_name = "q-screening-health-data"
    chrome_driver.find_element_by_name(elem_name).click()
    
    elem_id = "q-screening-eligibility-county"
    county_opt = Select(chrome_driver.find_element_by_id(elem_id))
    county_opt.select_by_visible_text(COUNTY)
    
    xpath = "//input[@name='q-screening-healthworker'][@value='No']"
    chrome_driver.find_element_by_xpath(xpath).click()
    xpath = "//input[@name='q-screening-eligibility-age-range'][@value='{}']".format(AGE_RANGE)
    chrome_driver.find_element_by_xpath(xpath).click()
    
    xpath = "//button[@type='submit']"
    chrome_driver.find_element_by_xpath(xpath).click()
    CHECKSUM += 1
    sleep(LONGER_PAUSE)
    
    #...LOCATION SEARCH PAGE
    xpath = "//input[@id='location-search-input']"
    location_elem = chrome_driver.find_element_by_xpath(xpath)
    location_elem.send_keys(ZIPCODE)
    xpath = "//button[text()='Continue']"
    chrome_driver.find_element_by_xpath(xpath).click()
    CHECKSUM += 1
    sleep(LONGER_PAUSE)
    
    #...LOCATION SELECT PAGE
    elem_tag_name = "button"
    locations_btn_list = chrome_driver.find_elements_by_tag_name(elem_tag_name)
    print("location list contains {} locations".format(len(locations_btn_list)))
    locations_btn_list[len(locations_btn_list)-1].click()
    CHECKSUM += 1
    sleep(LONGER_PAUSE)
    
    #...APPOINTMENT SELECT PAGE
    elem_css_selector = 'h3'
    if chrome_driver.find_elements_by_css_selector(elem_css_selector):
        CHECKSUM += 1
        elem_property = "innerHTML"
        appts_avail_text = chrome_driver.find_element_by_tag_name(elem_css_selector).get_property(elem_property)
        num_appts = int(appts_avail_text[0]) # appointments number count
    
        curr_URL = chrome_driver.current_url # current window's URL
        print(curr_URL)
        
        # send text to notify appointments available to schedule
        if num_appts > 0:
            resp = requests.post(
                TEXTBELT_URL, {
                    'phone': PHONE_NUM,
                    'message': curr_URL,
                    'key': TXT_API_KEY,
                }
            )
            print(HIT_RESPONSE)
            CHECKSUM += 1
        else:
            print(MISS_RESPONSE)
            CHECKSUM += 1
        sleep(LONGER_PAUSE)
    
    print("CHECKSUM is {}".format(CHECKSUM))
    assert CHECKSUM >= 5
    
    chrome_driver.close()
    
if __name__ == "__main__":
    check_availability()