from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pickle
import time
import os
from datetime import datetime, timedelta
import getpass
import msvcrt
from typing import List
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor
import winsound
import msvcrt
from gtts import gTTS
from playsound import playsound
import tempfile
import threading


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get(r"C:\Users\PGCB\Downloads\New folder\Dashboard.html")
name = driver.find_element(By.ID, 'navbarDropdown10')
print(name.get_attribute('outerHTML'))
print('name is: ', name.text)
time.sleep(3)
driver.quit()