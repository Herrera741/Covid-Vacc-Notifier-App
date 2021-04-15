from selenium import webdriver
from selenium.webdriver.support.ui import Select
from datetime import datetime
from time import sleep
import requests, os, itertools

#==========ENV VARIABLES==========#
op = webdriver.ChromeOptions()
op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
op.add_argument("--headless")
op.add_argument("--no-sandbox")
op.add_argument("--disable-dev-sh-usage")
TXT_API_KEY = os.environ.get('TXTBELT_API_KEY')
PHONE_NUM = os.environ.get('CELL_NUM')

START_URL = "https://myturn.ca.gov/"
TEXTBELT_URL = "https://textbelt.com/text"

HIT_RESPONSE = "Found appointment(s) available."
MISS_RESPONSE = "Sorry, no appointments yet."

SHORT_PAUSE = 2
LONG_PAUSE = 3
LONGER_PAUSE = 7

answerNO = "No"
answerYES = "Yes"

def get_driver():
    return webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=op)

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
    sleep(LONG_PAUSE)
    
    btnTag = 'button'
    checkEligibilityBtn = chrome_driver.find_element_by_tag_name(btnTag)
    checkEligibilityBtn.click()
    flagChecker += 1
    sleep(SHORT_PAUSE)
    
    #...SCREENING PAGE
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
    
    underlyingHealthSelect = "//input[@name='q-screening-underlying-health-condition'][@value='{}']".format(answerNO)
    chrome_driver.find_element_by_xpath(underlyingHealthSelect).click()
    
    disabilitySelect = "//input[@name='q-screening-disability'][@value='{}']".format(answerNO)
    chrome_driver.find_element_by_xpath(disabilitySelect).click()
    
    industrySelect = "q-screening-eligibility-industry"
    optionOther = "Other"
    selectIndustryOption = Select(chrome_driver.find_element_by_id(industrySelect))
    selectIndustryOption.select_by_visible_text(optionOther)
    
    homelessSelect = "//input[@name='q-screening-homeless'][@value='{}']".format(answerNO)
    chrome_driver.find_element_by_xpath(homelessSelect).click()
    
    countySelect = "q-screening-eligibility-county"
    countyOption = "Los Angeles"
    selectCountyOption = Select(chrome_driver.find_element_by_id(countySelect))
    selectCountyOption.select_by_visible_text(countyOption)
    
    diffCountySelect = "//input[@name='q-screening-different-county'][@value='{}']".format(answerNO)
    chrome_driver.find_element_by_xpath(diffCountySelect).click()
    
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
        
        preferredCity = "mega pod lacoe/downey"
        # nonPrefVONS = "vons"
        # nonPrefSAVON = "sav-on"
        # nonPrefMEDICAL = "medical"
        preferredVacc = "pfizer"
        preferredGroup = "all eligible groups"
        resultsSelector = "h2.tw-text-n800"
        locationSelector = "div.tw-text-n700"
        resultsBatch = chrome_driver.find_elements_by_css_selector(resultsSelector)
        
        apptBtns = chrome_driver.find_elements_by_css_selector("button.tw-w-full")
        apptsBackBtn = chrome_driver.find_element_by_css_selector("button.tw-py-4")
        
        preferredList = []
        locationList = []
        
        results = []
        for result in resultsBatch:
            results.append(result.text)
        
        print('='*5, "results before filtering: ", len(results), '='*5)
        
        for index, result in enumerate(results):
            titleText = result.lower()
            if (preferredGroup in titleText and preferredVacc in titleText):
                preferredList.append(result)
               
               
        # print("results after filtering: ", len(results))
        # print(results)                
        print('='*5, "preferred list after filtering: ", len(preferredList), '='*5)
        print(preferredList)
                
        # apptBtns[0].click()
        # sleep(LONGER_PAUSE)
        # apptsBackBtn.click()
        # sleep(SHORT_PAUSE)        
               
        if len(preferredList) > 0:
                
            message = HIT_RESPONSE + chrome_driver.current_url
            resp = requests.post(
                TEXTBELT_URL, {
                    'phone': PHONE_NUM,
                    'message': message,
                    'key': TXT_API_KEY+'_test',
                }
            )
            print("Message sent at {}. \nMessage response: {}".format(datetime.now(), resp.json()))
    else:
        print(MISS_RESPONSE)
                  
    flagChecker += 1
    
    print("flagChecker count is {}".format(flagChecker))
    sleep(LONG_PAUSE)
    chrome_driver.quit()
    
if __name__ == "__main__":
    check_availability()