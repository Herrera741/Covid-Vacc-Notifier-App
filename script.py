from selenium import webdriver
from selenium.webdriver.support.ui import Select
from datetime import datetime
from time import sleep
import requests, os, itertools


#==========GLOBAL VARIABLES==========#
TXT_API_KEY = os.environ.get('TXTBELT_API_KEY')
PHONE_NUM = os.environ.get('CELL_NUM')
DRIVER_PATH = "D:/Selenium-Drivers/Chrome-Driver/chromedriver_win32/chromedriver.exe"
START_URL = "https://myturn.ca.gov/"
TEXTBELT_URL = "https://textbelt.com/text"
COUNTY = 'Los Angeles'
ZIPCODE = '90242'
AGE_RANGE = '65 - 74'
HIT_RESPONSE = "Found appointment(s) available. Text notification sent."
MISS_RESPONSE = "no appointments yet"
SHORT_PAUSE = 2
LONG_PAUSE = 3
LONGER_PAUSE = 7

def get_driver():
    return webdriver.Chrome(DRIVER_PATH)

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
    sleep(LONG_PAUSE)
    
    elem_tag_name = 'button'
    title_btn = chrome_driver.find_element_by_tag_name(elem_tag_name)
    title_btn.click()
    CHECKSUM += 1
    sleep(SHORT_PAUSE)
    
    #...SCREENING PAGE
    browser_title_text = 'Screening'
    assert browser_title_text in chrome_driver.title
    sleep(LONG_PAUSE)
    
    elem_name = "q-screening-18-yr-of-age"
    chrome_driver.find_element_by_name(elem_name).click()
    elem_name = "q-screening-health-data"
    chrome_driver.find_element_by_name(elem_name).click()
    
    elem_id = "q-screening-eligibility-county"
    county_opt = Select(chrome_driver.find_element_by_id(elem_id))
    county_opt.select_by_visible_text(COUNTY)
    
    xpath = "//input[@name='q-screening-eligibility-age-range'][@value='{}']".format(AGE_RANGE)
    chrome_driver.find_element_by_xpath(xpath).click()
    elem_id = "q-screening-eligibility-industry"
    work_industry_opt = Select(chrome_driver.find_element_by_id(elem_id))
    work_industry_opt.select_by_visible_text("Other")
    
    
    xpath = "//button[@type='submit']"
    chrome_driver.find_element_by_xpath(xpath).click()
    CHECKSUM += 1
    sleep(LONG_PAUSE)
    
    #...LOCATION SEARCH PAGE
    xpath = "//input[@id='location-search-input']"
    location_elem = chrome_driver.find_element_by_xpath(xpath)
    location_elem.send_keys(ZIPCODE)
    xpath = "//button[text()='Continue']"
    chrome_driver.find_element_by_xpath(xpath).click()
    CHECKSUM += 1
    sleep(LONG_PAUSE)
    
    #...LOCATION SELECT PAGE
    elem_css_selector = "h2.tw-text-n800.tw-text-xl"
    dose_num_list = None
    if "No appointments" in chrome_driver.find_elements_by_css_selector(elem_css_selector)[0].text:
        curr_datetime = datetime.now()
        print("\nStill no appointments.\nCurrently: {}\n".format(curr_datetime.strftime("%Y-%m-%d %H:%M:%S")))
    else:
        message = "Appointments opened up." + chrome_driver.current_url
        resp = requests.post(
            TEXTBELT_URL, {
                'phone': PHONE_NUM,
                'message': message,
                'key': TXT_API_KEY,
            }
        )
        sleep(LONGER_PAUSE)
        
        dose_num_list = chrome_driver.find_elements_by_css_selector(elem_css_selector)
        print("vacc list contains {} vaccs".format(len(dose_num_list)))
    elem_css_selector = "div.tw-text-n700"
    address_list = None
    if chrome_driver.find_elements_by_css_selector(elem_css_selector)[1::3]:
        address_list = chrome_driver.find_elements_by_css_selector(elem_css_selector)[1::3]
        print("address list contains {} addresses".format(len(address_list)))
        print("inner HTML for second address is {}".format(address_list[2].get_property("innerHTML")))
    elem_css_selector = "div.tw-p-5.tw-pt-3.tw-border-t.tw-border-n200 button"
    button_list = None
    if chrome_driver.find_elements_by_css_selector(elem_css_selector):
        button_list = chrome_driver.find_elements_by_css_selector(elem_css_selector)
        print("button list contains {} buttons".format(len(button_list)))
    
    if dose_num_list and address_list and button_list:
        for (title_elem, address_elem, button_elem) in zip(dose_num_list, address_list, button_list):
            if "1st" in title_elem.text and "Downey" in address_elem.text:
                print("1st and Downey found in title and address")
            else:
                print("doesnt contain match. iteration has {} and {}".format(title_elem.text, address_elem.text))
            if re.search("1st", title_elem.text) and re.search("Downey", address_elem.text):
                button_elem.click()
                print("1st dose in downey was found")
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
    else:
        print("pre appts page had issue")
    
    print("CHECKSUM is {}".format(CHECKSUM))
    assert CHECKSUM >= 5
    chrome_driver.quit()
    
if __name__ == "__main__":
    check_availability()