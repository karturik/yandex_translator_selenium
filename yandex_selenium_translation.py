import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from tqdm import tqdm
from fake_useragent import UserAgent
import random
import pandas as pd
from openpyxl import Workbook
import pyperclip
import csv

useragent = UserAgent()

src_language = ''
dst_language = ''

# TO AVOID BOT DETECTION
def block_avoid(driver):
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    time.sleep(random.randint(1, 10))
    driver.find_element(By.ID, 'fakeArea').click()

options = Options()
options.add_argument("--window-size=1920,1080")
options.add_argument(f"user-agent={useragent.random}")
driver = webdriver.Chrome(options=options)

# GET TO TRANSLATOR PAGE
driver.get(f'https://translate.yandex.by/?ui=ru&lang={src_language}-{dst_language}')
WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.ID, "fakeArea")))
work_list = []

# OPEN FILES WITH DATA AND PAST IT TO TRANSLATOR
for file in os.listdir('docs_to_tansl'):
    dst_df = pd.DataFrame(None, columns=['INPUT:translatedText'])
    open(f'transl_docs/{file}', 'w', encoding='utf-8').write('INPUT:translatedText'+'\n')
    work_list = []
    src = pd.read_csv(f'docs_to_tansl/{file}', sep='\t')
    src = src.rename(columns={'INPUT:text': 'INPUT:originalText'})
    for i in range(1, len(src)+1):
        work_list.append(src['INPUT:originalText'][i-1])
        if len(work_list) < 150 and i < len(src):
            pass
        else:
            print("Let's go")
            text = ' ###\n'.join(map(str, work_list))
            field = driver.find_element(By.ID, 'fakeArea')
            pyperclip.copy(text)
            field.send_keys(Keys.CONTROL, 'v')
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.CLASS_NAME, "translation-word")))
            time.sleep(4)
            block_avoid(driver)
            trans_text = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[1]/div[1]/div[3]/div[2]/div/div[1]/div[1]/pre/span').text
            if len(trans_text.split(' ###\n')) != 0:
                for i in trans_text.split(' ###\n'):
                    dst_df = dst_df.append({'INPUT:translatedText': i}, ignore_index = True)
            else:
                print('Empty translated text')
            clear_button = driver.find_element(By.ID, 'clearButton')
            clear_button.click()
            time.sleep(2)
            work_list = []
    dst_df.to_csv(f'transl_docs/{file}', index=False, sep='\t')

    df = pd.read_csv(f'docs_to_tansl/{file}', sep='\t')
    tf = pd.read_csv(f'transl_docs/{file}', sep='\t')
    df['INPUT:translatedText'] = tf['INPUT:translatedText']
    df.to_excel(f'excel/{file.replace(".tsv", ".xlsx")}', index=False)
driver.close()

for file in os.listdir('docs_to_tansl'):
    try:
        excel = pd.read_excel(f'excel/{file.replace(".tsv", ".xlsx")}', sheet_name='Sheet1')
        excel_col = excel['INPUT:originalText']
        src_df = pd.read_csv(f'docs_to_tansl/{file}', sep='\t')
        src_df_col = src_df['INPUT:text']
        for i in range(1, len(excel_col) + 1):
            if excel_col[i - 1] != src_df_col[i - 1]:
                print(file, ': ', excel_col[i - 1], ', ', src_df_col[i - 1])
    except Exception as e:
        print(e)
