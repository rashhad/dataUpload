from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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




SYS_URL = "https://pdbsystemcontrol.com/"
INCOMER_URL = "https://pdbsystemcontrol.com/grid-load/create"
FEEDER_URL = "https://pdbsystemcontrol.com/sub-station-load/create"
OIS_URL = "https://ois.powergrid.gov.bd"
OIS_EDIT_URL = "https://ois.powergrid.gov.bd/logsheet_current/edit/"
PASS_FIELD_NAME = "password" 
OIS_ID_FIELD_NAME =  "username"
SYS_ID_FIELD_NAME = "email"
EMAIL = "shahmirpur@gmail.com"
PASSWORD = "123456789"
OIS_COOKIE_FILE = "oisCookies.pkl"
SYS_COOKIE_FILE = "sysCookies.pkl"
DELAY = 0.25

times = [
    "00:00",
    "01:00",
    "02:00",
    "03:00",
    "04:00",
    "05:00",
    "06:00",
    "07:00",
    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "18:30",
    "19:00",
    "19:30",
    "20:00",
    "21:00",
    "22:00",
    "23:00",
]

war:bool = False

class data:
    def __init__(self, val1:str = '0', val2:str = '0'):
        self.val1 = val1
        self.val2 = val2

class feeder:
    def __init__(self, name:str):
        self.name = name
        self.data = {}  #"hrs":data(load,shed)
    
    def showData(self):
        print("----------------------\nYour given " + self.name + " data:\n----------------------")
        print('Time\tMW\tL/S')
        for hrs in self.data:
            print(hrs+"\t"+ self.getLoad(hrs) + "\t" + self.getShed(hrs))
    
    def takingLoadInput(self, hrs:str, load:str):
        self.data[hrs] = data()
        self.data[hrs].val1 = load

    def takingShedInput(self, hrs:str, shed:str):
        self.data[hrs].val2 = shed

    def getLoad(self, hrs) -> str :
        return self.data[hrs].val1
    
    def getShed(self, hrs) -> str:
        return self.data[hrs].val2
    
    def dataUpload(self, driver: webdriver.Chrome, idx: int, date=""):
        pvDate = False
        done = True
        if date != "":
            pvDate = True
            driver.get(FEEDER_URL+"?date="+date)
        for hrs in self.data:
            if pvDate and hrs == "00:00":
                pvDate = False
                driver.get(FEEDER_URL)
            try:
                form = driver.find_element(By.XPATH, "//div[@class='sub_station_load_form_" + str(idx) +"']/form//input[@value='" + hrs + "']/ancestor::form")
            except Exception as e:
                print(f"{e}: {self.name}")
                driver.save_screenshot("error_page.png")
                driver.quit()

            load_input= form.find_element(By.NAME, "load")
            shed_input= form.find_element(By.NAME, "shed")
            if self.getShed(hrs) != "0":
                if load_input.get_attribute('value') in [None, ""] or shed_input.get_attribute('value') in [None, '']:
                    done = False
                if load_input.get_attribute('value') == '':
                    load_input.send_keys(self.getLoad(hrs)+Keys.TAB)
                    time.sleep(DELAY)
                if shed_input.get_attribute('value') == '':
                    shed_input.send_keys(self.getShed(hrs) + Keys.TAB)
                    time.sleep(DELAY)
            else:
                if load_input.get_attribute('value') in [None, ""]:
                    done = False
                if load_input.get_attribute('value') == '':
                    load_input.send_keys(self.getLoad(hrs)+Keys.TAB)
                    time.sleep(DELAY)

        return done
    

class busKV:
    def __init__(self):
        self.data = {} # "hrs" : data(kv1, kv2)
    
    def takingKv(self, hrs, kv1, kv2):
        self.data[hrs]=data(kv1, kv2)

    def getBus1Kv(self, hrs):
        return self.data[hrs].val1
    
    def getBus2Kv(self, hrs):
        return self.data[hrs].val2

    def upload(self, hrs, driver:webdriver.Chrome):
        war:bool = False
        bus1Field=driver.find_element(By.NAME, "Bus-1 ")
        bus2Field=driver.find_element(By.NAME, "Bus-2")
        if bus1Field.get_attribute('value') == '':
            bus1Field.send_keys(self.getBus1Kv(hrs))
        else:
            print(colored(f"OIS WARNING: {hrs} Update failed due to previous data exists."+"\nIt could be the server time isn't update yet. Please, Inspect manually.", "yellow"))
            war = True
            return war
        if bus2Field.get_attribute('value') =='':
            bus2Field.send_keys(self.getBus2Kv(hrs))
        else:
            print(colored(f"OIS WARNING: {hrs} Update failed due to previous data exists."+"\nIt could be the server time isn't update yet. Please, Inspect manually.", "yellow"))
            war = True
        return war

class transformer:
    def __init__(self, name):
        self.data = {} # "hrs" : data(mw, mvar)
        self.name = name
    
    def taikingData(self, hrs, mw, mvar):
        self.data[hrs]=data(mw, mvar)

    def getMW(self, hrs):
        return self.data[hrs].val1
    
    def getMVAR(self, hrs):
        return self.data[hrs].val2
    
    def getFloatMW(self, hrs):
        return float(self.getMW(hrs))
    
    def upload(self, hrs, driver:webdriver.Chrome):
        war:bool = False
        mwField = driver.find_element(By.NAME, self.name+"-MW")
        mvarField = driver.find_element(By.NAME, self.name+"-MVAR")
        if mwField.get_attribute('value') =='':
            mwField.send_keys(self.getMW(hrs))
        else:
            print(colored(f"OIS WARNING: {hrs} Update failed due to previous data exists."+"\nIt could be the server time isn't update yet. Please, Inspect manually.", "yellow"))
            war = True
            return war
        if mvarField.get_attribute('value') == '':
            mvarField.send_keys(self.getMVAR(hrs))
        else:
            print(colored(f"OIS WARNING: {hrs} Update failed due to previous data exists."+"\nIt could be the server time isn't update yet. Please, Inspect manually.", "yellow"))
            war = True
        return war

class incomer:
    def __init__(self, name:str):
        self.name = name
        self.data = {}  #"hrs":data(mw,kv)
    
    def showData(self):
        print("----------------------\nYour given " + self.name + " data:\n----------------------")
        print('Time\tMW\tL/S')
        for hrs in self.data:
            print(hrs+"\t"+ self.getMW(hrs) + "\t" + self.getKV(hrs))

    def loadOIS(self, bus:busKV, tr1:transformer, tr2:transformer):
        for hrs in bus.data:
            kv = bus.getBus1Kv(hrs)
            totalMW = tr1.getFloatMW(hrs)+tr2.getFloatMW(hrs)
            if totalMW.is_integer():
                totalMW=int(totalMW)
            totalMW = str(totalMW)
            self.data[hrs]=data(totalMW, kv)

    def getMW(self, hrs) ->str:
        return self.data[hrs].val1
    
    def getKV(self, hrs) -> str:
        return self.data[hrs].val2
    
    def dataUpload(self, driver: webdriver.Chrome, date = ""):
        pvDate = False
        done = True
        if date != "":
            driver.get(INCOMER_URL+"?date="+date)
            pvDate = True
        for hrs in self.data:
            if pvDate and hrs == "00:00":
                pvDate = False
                driver.get(INCOMER_URL)
            try:
                time_div = driver.find_element(By.XPATH, "//div[@class='grid_load_form_16']//input[@value='" + hrs + "']")
            except Exception as e:
                print(f'error: {e}')
                exit(-1)

            # Find the parent form for the time input (the div where the MW input is located)
            form = time_div.find_element(By.XPATH, "./ancestor::form")

            # Locate the input field for MW inside the form
            mw_input = form.find_element(By.NAME, "mw")
            kv_input = form.find_element(By.NAME, "kv")

            if mw_input.get_attribute('value') in [None, ""] or kv_input.get_attribute('value') in [None, ""]:
                done = False

            if mw_input.get_attribute('value') == '':
                mw_input.send_keys(self.getMW(hrs)+Keys.TAB)
                time.sleep(DELAY)
            if kv_input.get_attribute('value') == '':
                kv_input.send_keys(self.getKV(hrs)+Keys.TAB)
                time.sleep(DELAY)
        return done

# user defined function definition --------------

def lastEntryTime() -> str:
    currentTime = time.strftime("%H:%M", time.localtime())
    if(currentTime[0:2] == "18" or currentTime[0:2] == "19"):
        temp = currentTime[0:2]
        if(currentTime[3:] >= "30"):
            temp += ":30"
        else:
            temp += ":00"
        return temp
    else:
        temp = currentTime[0:2]
        temp += ":00"
        return temp
    
def takingOISdata(startIndex, endTime, bus:busKV, tr1:transformer, tr2:transformer):
    dataList = ("Bus-1 kV","Bus-2 kV", "Tr-02 MW", "Tr-02 MVAR", "Tr-01 MW", "Tr-01 MVAR")
    itr=0
    while(times[startIndex+itr]<=endTime):
        print(f"------ {times[startIndex+itr]} -------")
        ls=[]
        for i in range(6):
            temp = input(f"Enter {dataList[i]}:")
            if(temp==""):
                temp = "0"
            ls.append(temp)
        bus.takingKv(times[startIndex+itr], ls[0], ls[1])
        tr1.taikingData(times[startIndex+itr],ls[4], ls[5])
        tr2.taikingData(times[startIndex+itr], ls[2], ls[3])
        itr+=1
        if(startIndex+itr >= len(times)):
            break

def takingInput(feeder:feeder, timeIndex :int, lastTime: str, loadData:bool = True) -> None:
    if loadData:
        print("----------------------\nEnter " + feeder.name + " MW data:\n----------------------")
    else:
        print("----------------------\nEnter " + feeder.name + " L/S data:\n----------------------")
        
    currentIndex = timeIndex
    while(times[currentIndex]<=lastTime):
        userInput = input(times[currentIndex] + ': ')
        if not userInput:
            if loadData:
                feeder.takingLoadInput(times[currentIndex], '0')
            else:
                feeder.takingShedInput(times[currentIndex], '0')
        else:
            if loadData:
                feeder.takingLoadInput(times[currentIndex], userInput)
            else:
                feeder.takingShedInput(times[currentIndex], userInput)
        currentIndex+=1
        if(currentIndex >= len(times)):
            return


def showOISdata():
    print("Time\tBus-1 kV\tBus-2 kV\tMW1\tMVAR1\tMW2\tMVAR2\tTotal")
    for hrs in bus.data:
        print(hrs + "\t" + bus.getBus1Kv(hrs) + "\t\t" + bus.getBus2Kv(hrs) + "\t\t" + tr1.getMW(hrs) + "\t" + tr1.getMVAR(hrs), end='\t')
        print(tr2.getMW(hrs) + "\t" + tr2.getMVAR(hrs) + "\t", (tr1.getFloatMW(hrs) + tr2.getFloatMW(hrs)))


def hide_input_with_symbol(prompt="Enter input: ", symbol="*"):
    print(prompt, end="", flush=True)
    input_value = []
    while True:
        char = msvcrt.getch()
        if char == b'\r':  # Enter key pressed
            break
        elif char == b'\x08':  # Backspace key pressed
            if input_value:
                input_value.pop()
                print("\b \b", end="", flush=True)  # Remove last symbol
        else:
            input_value.append(char.decode())
            print(symbol, end="", flush=True)
    print()  # To move to the next line
    return ''.join(input_value)

def initDriver(msg:str):
    print(msg)
    chrome_options = Options()
    # chrome_options.add_argument('--allow-insecure-localhost') # differ on driver version. can ignore. 

    # chrome_options.add_argument('--ignore-ssl-errors=yes')
    # chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')  # Useful for headless mode on some systems
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    # service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #     "source": """
    #         Object.defineProperty(navigator, 'webdriver', {
    #             get: () => undefined
    #         });
    #     """
    # })
    return driver

def loadCookies(driver:webdriver.Chrome, url:str, cookieFileName:str):
    # -- loading cookies --
    try:
        driver.get(url)
        with open(cookieFileName, 'rb') as cookie_file:
            cookies = pickle.load(cookie_file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        print("cookies loaded!")
        return True
    except FileNotFoundError:
        print("No cookies file found")
        return False

def savingCookies(driver:webdriver.Chrome, cookieName):
    cookies = driver.get_cookies()
    with open(cookieName, 'wb') as cookie_file:
        pickle.dump(cookies, cookie_file)

def clearCookies(driver:webdriver.Chrome):
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")

def logingIn(driver:webdriver.Chrome, id:str, passw:str, url:str, idField:str, passwField:str, cookieFile:str) -> bool:
    driver.get(url)
# -- login to system website --
    if "login" in driver.current_url:
        clearCookies(driver)
        driver.get(url)
        try:
            emailField = driver.find_element(By.NAME, idField)
            passField = driver.find_element(By.NAME, passwField)
        except Exception as e:
            print("problem finding id/pass field.")
            print(f'error: {e}')
            driver.save_screenshot("error_page.png")
            return False
        emailField.send_keys(id)
        passField.send_keys(passw+Keys.ENTER)
        driver.get(url)
        if "login" in driver.current_url:
            return False
        else:
            savingCookies(driver, cookieFile)
            return True
    else:
        print("Already loged In: " + driver.current_url)
        return True

def saveLastState(_time, id, name):
    ti = times.index(_time)
    ti+=1
    if ti>=len(times):
        ti=0
    l = [times[ti], id, name]
    with open("lastStates.pkl","wb") as savedState:
        pickle.dump(l, savedState)
    return

def loadLastState() -> list:
    with open("lastStates.pkl","rb") as savedState:
        return pickle.load(savedState)

def clearLogInState():
    try:
        with open("lastStates.pkl","rb") as savedSate:
            l = pickle.load(savedSate)
        l[1]=""
        with open("lastStates.pkl","wb") as savedSate:
            pickle.dump(l,savedSate)
    except FileNotFoundError:
        print("no state file")

def updateLoginState(id:str, name:str):
    with open("lastStates.pkl","rb") as savedSate:
        l = pickle.load(savedSate)
    l[1]=id
    l[2]=name
    with open("lastStates.pkl","wb") as savedSate:
        pickle.dump(l,savedSate)

def flush_input_windows():
    """Flushes the stdin buffer on Windows."""
    while msvcrt.kbhit():
        msvcrt.getch()

def speak(text, speed_factor=1, db=5):
    pass
    # tts = gTTS(text=text, lang='en')
    
    # # Create a temporary file manually
    # fd, path = tempfile.mkstemp(suffix='.mp3')
    # os.close(fd)  # Close the file descriptor so gTTS can write
    
    # tts.save(path)
    # playsound(path)
    
    # os.remove(path)  # Clean up

# -- main program starting from here --

try:
    savedState = loadLastState()
    if savedState[1]=="":
        print("No user is logged in to OIS. Please, login -")
        # threading.Thread(target=speak, args=(f"Welcome! Please, login to OIS.",)).start()

        while True:
            userID = input("OIS ID: ")
            passw = hide_input_with_symbol("OIS Pass: ")
            driver = initDriver("Initializing...")
            if loadCookies(driver, OIS_URL, OIS_COOKIE_FILE):
                driver.get(OIS_URL+"/logout")
            if logingIn(driver, userID, passw, OIS_URL, OIS_ID_FIELD_NAME, PASS_FIELD_NAME, OIS_COOKIE_FILE):
                # userName = driver.find_element(By.ID, "navbarDropdown10").text
                userName = driver.execute_script("return document.getElementById('navbarDropdown10').innerText").strip()

                updateLoginState(userID, userName)
                savedState = loadLastState()
                os.system('cls')
                print(f"Wellcome {savedState[2]} ({savedState[1]})")
                break
            else:
                try:
                    message=driver.find_element(By.ID, "messages").text
                except:
                    print("login failed!")
                finally:
                    driver.quit()
                    os.system('cls')
                    print("No user is logged in to OIS. Please, login -")
                    if message:
                        print(message)
        driver.quit()
    else:
        print(f"Wellcome {savedState[2]} ({savedState[1]})")
    print(f"Next uploading time: {savedState[0]}")
    # threading.Thread(target=speak, args=(f"Welcome {savedState[2].split()[1]}. Choose an option.",)).start()

except FileNotFoundError:
    print("No saved state.")
    savedState = ['','','']
print("\nChoose an option - enter 0, 1 or leave empty [enter]")
print("[enter]: Next upload time\t[0]: Manual time input\t\t[1]: logout OIS")
opt = input()

match opt:
    case "":
        startTime= savedState[0]
        # threading.Thread(target=speak, args=(f"Current uploading time {savedState[0]}",)).start()
    case '0':
        startTime = ""
    case '1':
        threading.Thread(target=speak, args=(f"Logging out.",)).start()
        driver = initDriver("")
        if loadCookies(driver,OIS_URL,OIS_COOKIE_FILE):
            driver.get(OIS_URL+"/logout")
            os.remove(OIS_COOKIE_FILE)
        time.sleep(0.1)
        try:
            threading.Thread(target=speak, args=(f"Logging out successful! See you again, {savedState[2].split()[1]}.",)).start()
        except Exception as e:
            print(f'{e}')
            driver.save_screenshot("error_page.png")
        clearLogInState()
        driver.quit()
        print("logged out successful!")
        exit(0)
    



feeders: List[feeder] = []

feeders.append(feeder("Anowara"))
feeders.append(feeder("HM Steel"))
feeders.append(feeder("Baskhali-2"))

gridLoad= incomer("Grid Load")

bus = busKV()
tr1 = transformer("406T")
tr2 = transformer("416T")



# taking starting time
if startTime == "":
    startTime = input(("Enter starting time (HH.MM): "))
    ls=startTime.split(".")
    startTime = ":".join(ls)
    while(not (startTime in times)):
        print("Invalid input! ")
        startTime = input("Enter starting time (HH:MM): ")
        ls=startTime.split(".")
        startTime = ":".join(ls)
startIndex = times.index(startTime)

# calculating last entry time
endTime=lastEntryTime()


previousDate = ""
if(startTime>endTime):
    print(colored("Warning! The starting time is greater than the end time.\nBE SURE THAT THE TIME SLOT IS CORRECT.", 'red'))
    winsound.PlaySound('warning.wav',winsound.SND_FILENAME)
    # threading.Thread(target=speak, args=(f"Watchout!",)).start()

    previousDate = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

print(("\nTime slot: " + startTime + "-->" + endTime + "\n"))


if previousDate:
    takingOISdata(startIndex, "23:00", bus, tr1, tr2)
    takingOISdata(0, endTime, bus, tr1, tr2)
    for feeder in feeders:
        takingInput(feeder, startIndex, "23:00")
        takingInput(feeder, 0, endTime)
else:
    takingOISdata(startIndex, endTime, bus, tr1, tr2)
    for feeder in feeders:
        takingInput(feeder, startIndex, endTime)

gridLoad.loadOIS(bus, tr1, tr2)

while(1):
    confirmation = input(("Do you want to upload feeder load shed data? (y/enter): "))
    if(confirmation.isalpha()):
        confirmation.lower()
        if(confirmation == 'y' or confirmation == 'n'):
            break
        else:
            print("Invalid input")
    elif confirmation=="":
        break
    else:
        print("Invalid input")

if(confirmation=='y'):
    for feeder in feeders:
        if(previousDate !=""):
            takingInput(feeder, startIndex, "23:00", False)
            takingInput(feeder, 0, endTime, False)
        else:
            takingInput(feeder, startIndex, endTime, False)

showOISdata()
gridLoad.showData()
for feeder in feeders:
    feeder.showData()


# --- OIS log in credentials ---
if savedState[1]=="":
    print("----------------------------------------------")
    print("Give Employee ID and Password to get access to OIS\n-- LEAVE BLANK IF YOU'RE ALREADY LOGGED IN --")
    print("----------------------------------------------")
    userID = input(("ID: "))
    if userID == "":
        passw=""
    else:
        passw = hide_input_with_symbol(("Pass: "))
msg=""

try:
    # threading.Thread(target=speak, args=(f"Working on data uploading.",)).start()
    pbsSystemDriver = initDriver(("Initializing PBS system driver..."))
    loadCookies(pbsSystemDriver, SYS_URL, SYS_COOKIE_FILE)
    success=logingIn(pbsSystemDriver, EMAIL, PASSWORD, SYS_URL, SYS_ID_FIELD_NAME, PASS_FIELD_NAME, SYS_COOKIE_FILE)
    if success:
        print(("pbs system: login success!!! :) :" + pbsSystemDriver.current_url))
        done = False
        while(not done):
            pbsSystemDriver.get(INCOMER_URL)
            done = gridLoad.dataUpload(pbsSystemDriver, previousDate)
        done = False
        while(not done):
            pbsSystemDriver.get(FEEDER_URL)
            for f in feeders:
                done = f.dataUpload(pbsSystemDriver, feeders.index(f)+1, previousDate)
        # speak("PBS data uploading is done.")
        threading.Thread(target=speak, args=(f"Finished PBS data uploading.",)).start()
    else:
        print(("pbs system: login not success :("))
        msg = "system data upload failed: loging in not success." + '\n'
except Exception as e:
    print((f"error uploading system data: {e}"))
    msg = "system data upload failed! +'\n"
    driver.save_screenshot("error_page.png")

finally:
    pbsSystemDriver.quit()

try:
    oisDriver = initDriver("Initializing OIS Driver...")
    oisDriver.delete_all_cookies()
    # threading.Thread(target=speak, args=(f"Working on OIS data uploading.",)).start()
    loadCookies(oisDriver, OIS_URL, OIS_COOKIE_FILE)
    if savedState[1]=="":
        if userID and passw:
            oisDriver.get(OIS_URL+"/logout")
            if logingIn(oisDriver, userID, passw, OIS_URL, OIS_ID_FIELD_NAME, PASS_FIELD_NAME, OIS_COOKIE_FILE):
                print(("OIS system: login success: " + oisDriver.current_url))
            else:
                print(("OIS system: login failed - "), end=' ')
                try:
                    print((oisDriver.find_element(By.ID, "messages").text))
                except:
                    pass
                while not logingIn(oisDriver, userID, passw, OIS_URL, OIS_ID_FIELD_NAME, PASS_FIELD_NAME, OIS_COOKIE_FILE):
                    try:
                        print((oisDriver.find_element(By.ID, "messages").text))
                    except:
                        pass
                    userID = input(("ID: "))
                    passw = hide_input_with_symbol(("Pass: "))
        else:
            while not logingIn(oisDriver, userID, passw, OIS_URL, OIS_ID_FIELD_NAME, PASS_FIELD_NAME, OIS_COOKIE_FILE):
                print(("OIS system: login failed - "), end=' ')
                try:
                    print((oisDriver.find_element(By.ID, "messages").text))
                except:
                    pass
                userID = input(("ID: "))
                passw = hide_input_with_symbol(("Pass: "))
    oisDriver.get(OIS_URL)
    if 'login' in oisDriver.current_url:
        print(("login failed somehow!"))
        msg+="login to ois failed somehow!"
    else:
        try:
            # userName = oisDriver.find_element(By.ID, "navbarDropdown10").text
            # userNameElement = oisDriver.find_element(By.ID, "navbarDropdown10").get_attribute('outerHTML')
            userName = oisDriver.execute_script("return document.getElementById('navbarDropdown10').innerText").strip()
            print("OIS system: logged in as - " + userName)

            # print(userNameElement)

            # print("OIS system: logged in as - " + userName)
        except Exception as e:
            print('error while fetching user name')
            print(f"{e}")
            driver.save_screenshot("error_page.png")

        for t in bus.data:
            oisDriver.get(OIS_EDIT_URL+t)
            if bus.upload(t, oisDriver) or tr1.upload(t, oisDriver) or tr2.upload(t, oisDriver):
                war = True
            else:
                oisDriver.find_element(By.NAME, "SubmitBtn").click()
                time.sleep(DELAY)
        if not war:
            threading.Thread(target=speak, args=(f"Finished OIS data uploading.",)).start()
    try:
        if userID == "":
            userID = savedState[1]
    except:
        userID = savedState[1]
    saveLastState(endTime, userID, userName)
except Exception as e:
    print(f"Error in uploading ois data: {e}")
    msg+="error uploading ois data"
    driver.save_screenshot("error_page.png")

finally:
    oisDriver.quit()
if war:
    # winsound.PlaySound("warning.wav",winsound.SND_FILENAME)
    playsound('warning.wav')
    print(colored(f"Press enter to dismiss...", "yellow"))
    speak('Warning! Some OIS data could not be uploaded due to older data will get overwritten. Press enter to dismiss.')
    flush_input_windows()
    input()
else:
    winsound.PlaySound('success.wav', winsound.SND_FILENAME)
    speak("We're done! Closing the program now.")
