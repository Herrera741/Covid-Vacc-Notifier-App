from selenium import webdriver
from selenium.webdriver.support.ui import Select
from datetime import datetime
from time import sleep
import requests, os, itertools
from dotenv import load_dotenv
load_dotenv()

#==========GLOBAL VARIABLES==========#
TXT_API_KEY = os.getenv('TXTBELT_API_KEY')
PHONE_NUM = os.getenv('CELL_NUM')
DRIVER_PATH = "D:/Selenium-Drivers/Chrome-Driver/chromedriver_win32/chromedriver.exe"
START_URL = "https://myturn.ca.gov/"
TEXTBELT_URL = "https://textbelt.com/text"

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
def check_availability(flagChecker=0):
    chrome_driver = get_driver()
    flagChecker += 1
    sleep(SHORT_PAUSE)
    chrome_driver.maximize_window() # open new browser
    
    #...START PAGE
    launch_page(chrome_driver)
    browser_title_text = 'My Turn'
    assert browser_title_text in chrome_driver.title
    sleep(LONG_PAUSE)
    
    btnTag = 'button'
    checkEligibilityBtn = chrome_driver.find_element_by_tag_name(btnTag)
    checkEligibilityBtn.click()
    flagChecker += 1
    sleep(SHORT_PAUSE)
    
    #...SCREENING PAGE
    browser_title_text = 'Screening'
    assert browser_title_text in chrome_driver.title
    sleep(LONG_PAUSE)
    
    checkBoxAge = "q-screening-18-yr-of-age"
    chrome_driver.find_element_by_name(checkBoxAge).click()
    checkBoxData = "q-screening-health-data"
    chrome_driver.find_element_by_name(checkBoxData).click()
    checkBoxAccuracy = "q-screening-accuracy-attestation"
    chrome_driver.find_element_by_name(checkBoxAccuracy).click()
    checkBoxPrivacy = "q-screening-privacy-statement"
    chrome_driver.find_element_by_name(checkBoxPrivacy).click()
    
    ageRange = '16 - 49'
    ageSelect = "//input[@name='q-screening-eligibility-age-range'][@value='{}']".format(ageRange)
    chrome_driver.find_element_by_xpath(ageSelect).click()
    
    answerNo = "No"
    underlyingHealthSelect = "//input[@name='q-screening-underlying-health-condition'][@value='{}']".format(answerNo)
    chrome_driver.find_element_by_xpath(underlyingHealthSelect).click()
    
    answerYes = "Yes"
    disabilitySelect = "//input[@name='q-screening-disability'][@value='{}']".format(answerYes)
    chrome_driver.find_element_by_xpath(disabilitySelect).click()
    
    industrySelect = "q-screening-eligibility-industry"
    optionOther = "Other"
    selectIndustryOption = Select(chrome_driver.find_element_by_id(industrySelect))
    selectIndustryOption.select_by_visible_text(optionOther)
    
    countySelect = "q-screening-eligibility-county"
    countyOption = "Los Angeles"
    selectCountyOption = Select(chrome_driver.find_element_by_id(countySelect))
    selectCountyOption.select_by_visible_text(countyOption)
    
    submitBtn = "//button[@type='submit']"
    chrome_driver.find_element_by_xpath(submitBtn).click()
    flagChecker += 1
    sleep(LONG_PAUSE)
    
    #...LOCATION SEARCH PAGE
    locationSearchElement = "//input[@id='location-search-input']"
    zipcode = "90242"
    locationInput = chrome_driver.find_element_by_xpath(locationSearchElement)
    locationInput.send_keys(zipcode)
    
    continueBtn = "//button[text()='Continue']"
    chrome_driver.find_element_by_xpath(continueBtn).click()
    flagChecker += 1
    sleep(LONG_PAUSE)
    
    #...LOCATION SELECT PAGE
    sleep(SHORT_PAUSE)
    resultSelector = "div.tw-border-n200"
    if chrome_driver.find_elements_by_css_selector(resultSelector):
        
        preferredCity = "downey"
        preferredVacc = "pfizer"
        titleSelector = "h2.tw-text-n800"
        preferredLocations = {}
        locationSelector = "div.tw-text-n700"
        locationList = []
        titles = chrome_driver.find_elements_by_css_selector(titleSelector)
        buttons = chrome_driver.find_elements_by_css_selector("button.tw-w-full")
        
        sleep(SHORT_PAUSE)
        nonPreferredLocationFound = False
        for index, title in enumerate(titles):
            titleText = title.text.lower()
            if (preferredVacc in titleText) and (preferredCity in titleText):
                preferredLocations[index] = titleText
                
        
                
                
        # if len(titleList) > 0:
        #     for index, location in preferredLocations.items():
                
             
             
             
            # message = "Appointments in Downey found. " + chrome_driver.current_url
            # resp = requests.post(
            #     TEXTBELT_URL, {
            #         'phone': PHONE_NUM,
            #         'message': message,
            #         'key': TXT_API_KEY,
            #     }
            # )
            # print(resp.json())
            
            
    flagChecker += 1

    # else:
    #     curr_datetime = datetime.now()
    #     print("\nNo appointments available.\nTimestamp is {}\n".format(curr_datetime.strftime("%Y-%m-%d %H:%M:%S")))
    
    print("flagChecker count is {}".format(flagChecker))
    sleep(LONG_PAUSE)
    chrome_driver.quit()
    
if __name__ == "__main__":
    check_availability()
