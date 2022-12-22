
# ======> PROJECT: AMAZON REVIEW CRAWLER FOR NLP MODEL
# ======> CREDIT: VI PHAM/anhvi02
# ======> GITHUB SOURCE: https://github.com/anhvi02/AmazonReview_Crawl_NLP.git

import pandas as pd
import numpy as np
import smtplib
import bs4
from tqdm import tqdm
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# ignore warning
import warnings
warnings.filterwarnings('ignore')

# # Setting browser
# Setting browser's options
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--start-maximized")
options.add_argument("--disable-popup-blocking")
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(0)
print("=== DRIVER SET UP AND BROWSER OPENED")

# INPUT
# list view link
while True:
    try:
        link = input('-- List view link? ')
        print('=== CHECKING LINK WITH 3 TRIES...')
        for i in range(3):
            try:
                driver.get(link)
                element = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="a-page"]')))
                html_of_interest = driver.execute_script('return arguments[0].innerHTML',element)
                soup = BeautifulSoup(html_of_interest, 'lxml')
                print('=== ACCESS LINK SUCCESSFULLY')
                break
            except:
                continue
        break
    except:
        print('=== ACCESS LINK FAILED, PLEASE TRY ANOTHER ONE')
        continue
# data file name
while True:
    filename = input('-- Data CSV file name? ')
    if filename.endswith('.csv') == True:
        break
    else:
        continue

# number of page of list views
while True:
    try:
        page_num = int(input('-- Number of products pages to extract? '))
        break
    except:
        continue

print('=== LOADING PAGES TO GET PRODUCTS CODE')
products = []
cnt = 1
try:
    while True:
        # GET PRODUCTS CODE AND SAVE AS A CSV FILE
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="a-page"]')))
        html_of_interest = driver.execute_script('return arguments[0].innerHTML',element)
        soup = BeautifulSoup(html_of_interest, 'lxml')

        # roll page to the end
        page_height = driver.execute_script("return document.body.scrollHeight")
        target_height = page_height - 1400
        driver.execute_script("window.scrollTo(0, %s);" %target_height )
        sleep(1)
        # get product code
        tag_a = soup.select('a[class="a-link-normal s-no-outline"]')
        for tag in tag_a:
            link = tag['href']
            if link.split('/')[3].endswith('.html') == False:
                url = link.split('/')[1], link.split('/')[3]
                products.append(url)
            else:
                continue
        # stop condition
        if page_num == cnt:
            break
        # click Next to go to the next list view page
        next_button = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Next')[0]
        next_button.click()
        # update count
        cnt += 1
        sleep(2.5)
except Exception as err:
    print(f'=== ERROR: {err.__class__}')
finally:
    df = pd.DataFrame(products)
    df = df.drop_duplicates(subset=1)
    df.to_csv('products_code.csv')
    print(f'-- EXTRACTION FINISHED - NUMBER OF PRODUCT URL EXTRACTED: {len(df)}')


# EXTRACT FUNCTION
def extract_function(i):
    item_dict = {}
    # Company Name
    try:
        item_dict['Name'] = soup.select('div[class="a-profile-content"]>span')[i].text 
        # TopFoldsc__JobOverviewHeader-sc-kklg8i-22 ihxBLZ
    except:
        item_dict['Name'] = None 
    # Star
    try:
        item_dict['Star'] = soup.select('span[class="a-icon-alt"]')[i].text.split(' ')[0]
        # TopFoldsc__JobOverviewHeader-sc-kklg8i-22 ihxBLZ
    except:
        item_dict['Star'] = None 
    # Location
    try:
        item_dict['Location'] = soup.select('span[data-hook="review-date"]')[i].text.split('in ')[-1].split('on ')[0]
        # TopFoldsc__JobOverviewHeader-sc-kklg8i-22 ihxBLZ
    except:
        item_dict['Location'] = None 
    # Date
    try:
        item_dict['Date'] = soup.select('span[data-hook="review-date"]')[i].text.split('in ')[-1].split('on ')[-1]
        # TopFoldsc__JobOverviewHeader-sc-kklg8i-22 ihxBLZ
    except:
        item_dict['Date'] = None    
    # Title
    try:
        item_dict['Title'] = soup.select('a[data-hook="review-title"]')[i].text.strip()
        # TopFoldsc__JobOverviewHeader-sc-kklg8i-22 ihxBLZ
    except:
        item_dict['Title'] = None 
    # Review
    try:
        item_dict['Review'] = soup.select('span[data-hook="review-body"]')[i].text.strip()
        # TopFoldsc__JobOverviewHeader-sc-kklg8i-22 ihxBLZ
    except:
        item_dict['Review'] = None 
    return item_dict

# BEGIN THE CRAWLER
# IMPORT PRODUCTS CODE

df = pd.read_csv('products_code.csv')
df.drop(columns='Unnamed: 0', inplace=True)
df = df.drop_duplicates()
print(f'-- BEGIN THE CRAWLER PROGRAMM - ESTIMATED TIME: {len(df)*5*5}s')

# ACCESS AND EXTRACT DATA
star = ['one_star','two_star','three_star','four_star','five_star']

try:
    # a list to store data
    list_df = []
    # a loop to access every product
    for i in tqdm(range(len(df))):
        try:
            # a loop to access reviews of product (based on number of star)
            for num_star in star:                     # access url
                url = f'https://www.amazon.com/{df.iloc[i,0]}/product-reviews/{df.iloc[i,1]}/ref=?ie=UTF8&reviewerType=all_reviews&pageNumber=1&filterByStar={num_star}'
                driver.get(url)
                try:
                    # extract html
                    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="a-section a-spacing-none review-views celwidget"]')))
                    html_of_interest = driver.execute_script('return arguments[0].innerHTML',element)
                    soup = BeautifulSoup(html_of_interest, 'lxml')

                    # get number of review
                    review_count = len(soup.select('div[class="a-profile-content"]>span'))
                    # loop through number of review and extract each of them
                    for rev in range(review_count):
                        data_dict = extract_function(rev)
                        list_df.append(data_dict)
                    sleep(5)
                except:
                    continue
            sleep(5)
        except Exception as e:
            print(f'-- Error raised: {e.__class__} at url number {i}. Passed to the next url')
            continue

except Exception as err:
    print(f'=== PROGRAMM SHUT DOWN AT URL NUMBER{i}. Error: {err.__class__}')
finally:
    df_extracted = pd.DataFrame(list_df)
    df_extracted.to_csv(f'{filename}')
    driver.close()
    print(f'=== DATA EXTRACTED TO {filename}')
