from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pickle
import time
import os
import getpass
import msvcrt
# constants definition

SYS_URL = "https://pdbsystemcontrol.com/"
INCOMER_URL = "https://pdbsystemcontrol.com/grid-load/create"
APBS_URL = "https://pdbsystemcontrol.com/sub-station-load/create?sub_station=1"
HM_URL = "https://pdbsystemcontrol.com/sub-station-load/create?sub_station=2"
BPBS_URL = "https://pdbsystemcontrol.com/sub-station-load/create?sub_station=3"
OIS_URL = "https://ois.pgcb.gov.bd"
OIS_EDIT_URL = "https://ois.pgcb.gov.bd/logsheet_current/edit/"
FEEDER_URLs = [APBS_URL, HM_URL, BPBS_URL]
PASSWORD = "123456789"
EMAIL = "shahmirpur@gmail.com"
KV = 0
TOTAL_MW = 1
FEEDER_MW = 0
LS = 1
WAIT = 10

# lookup dictionary for time 24 to 12 hrs conversion:
timeLookUp = {
    "00:00" : "12:00 AM",
    "01:00" : "01:00 AM",
    "02:00" : "02:00 AM",
    "03:00" : "03:00 AM",
    "04:00" : "04:00 AM",
    "05:00" : "05:00 AM",
    "06:00" : "06:00 AM",
    "07:00" : "07:00 AM",
    "08:00" : "08:00 AM",
    "09:00" : "09:00 AM",
    "10:00" : "10:00 AM",
    "11:00" : "11:00 AM",
    "12:00" : "12:00 PM",
    "13:00" : "01:00 PM",
    "14:00" : "02:00 PM",
    "15:00" : "03:00 PM",
    "16:00" : "04:00 PM",
    "17:00" : "05:00 PM",
    "18:00" : "06:00 PM",
    "18:30" : "06:30 PM",
    "19:00" : "07:00 PM",
    "19:30" : "07:30 PM",
    "20:00" : "08:00 PM",
    "21:00" : "09:00 PM",
    "22:00" : "10:00 PM",
    "23:00" : "11:00 PM",
    "24:00" : "12:00 AM"
}

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

# user defined class definition
# -----------------------------
class data:
    def __init__(self, data: dict, name: str):
        self.data = {} # time : [data1, data2, data3]
        self.name = name

    def load(self, key, val):
        if key in self.data:
            self.data[key].append(val)
        else:
            self.data[key]=[val]

    def loadEditingURLs(self, driver: webdriver):
        for hrs in self.data:
            try:
                WebDriverWait(driver, WAIT).until(
                    EC.visibility_of_element_located((By.XPATH, "//tr[td/strong[contains(@title, " + "'" + timeLookUp[hrs] + "'" ")]]/td/a"))
                        )
            except Exception as e:
                print(f'Particular: {self.name}, time: {hrs} - Pursing link loading timed out: {e}')
                continue
            self.data[hrs].append(driver.find_element(By.XPATH, "//tr[td/strong[contains(@title, " + "'" + timeLookUp[hrs] + "'" ")]]/td/a").get_attribute('href'))

    def showData(self):
        pass

class feeder33kV(data):
    def showData(self):
        print("----------------------\nYour given " + self.name + " data:\n----------------------")
        print('Time\tMW\tL/S')
        for key in self.data:
            print(key+"\t"+ self.data[key][0] + "\t" + self.data[key][1])

    def uploadData(self, driver: webdriver.Chrome):
        for hrs in self.data:
            driver.get(self.data[hrs][2])
            try:
                WebDriverWait(driver, WAIT).until(
                    EC.visibility_of_element_located((By.NAME, "load"))
                        )
                WebDriverWait(driver, WAIT).until(
                    EC.visibility_of_element_located((By.NAME, "shed"))
                        )
                WebDriverWait(driver, WAIT).until(
                    EC.visibility_of_element_located((By.TAG_NAME, "button"))
                        )
            except Exception as e:
                print(f"Particular: {self.name}, Time: {hrs} - Uploading page timed out: {e}")
                continue
            
            loadInput = driver.find_element(By.NAME, "load")
            loadInput.clear()
            loadInput.send_keys(self.data[hrs][KV])
            shedInput = driver.find_element(By.NAME, "shed")
            shedInput.clear()
            shedInput.send_keys(self.data[hrs][TOTAL_MW])
            driver.find_element(By.TAG_NAME, "button").click()

class incomerData(data):
    def showData(self):
        print("----------------------\nYour given " + self.name + " data:\n----------------------")
        print('Time\tkV\tMW')
        for key in self.data:
            print(key+"\t"+ self.data[key][0] + "\t" + self.data[key][1])

    def uploadData(self, driver: webdriver.Chrome):
        for hrs in self.data:
            driver.get(self.data[hrs][2])
            try:
                WebDriverWait(driver, WAIT).until(
                    EC.visibility_of_element_located((By.NAME, "kv"))
                        )
                WebDriverWait(driver, WAIT).until(
                    EC.visibility_of_element_located((By.NAME, "mw"))
                        )
                WebDriverWait(driver, WAIT).until(
                    EC.visibility_of_element_located((By.TAG_NAME, "button"))
                        )
            except Exception as e:
                print(f"Particular: {self.name}, Time: {hrs} - Uploading page timed out: {e}")
                continue
            
            kvInput = driver.find_element(By.NAME, "kv")
            kvInput.clear()
            kvInput.send_keys(self.data[hrs][KV])
            
            mwInput = driver.find_element(By.NAME, "mw")
            mwInput.clear()
            mwInput.send_keys(self.data[hrs][TOTAL_MW])
            driver.find_element(By.TAG_NAME, "button").click()

class oisLoad():
    def __init__(self, mw, mvar):
        self.mw = mw
        self.mvar = mvar



class oisKV():
    def __init__(self, kv1, kv2):
        self.bus1 = kv1
        self.bus2 = kv2

class oisBusData():
    def __init__(self):
        self.data = {} # time:oisKV()

    def load(self, time, kv1, kv2):
        self.data[time] = oisKV(kv1, kv2)
        
    def getVol1(self, time):
        return self.data[time].bus1

    def getVol2(self, time):
        return self.data[time].bus2
    

class oisTrafo():
    def __init__(self, name:str):
        self.name = name
        self.data = {} # time: oisLoad

    def load(self, time, mw, mvar):
        self.data[time] = oisLoad(mw,mvar)

    def mwValu(self, time):
        return float(self.data[time].mw)

    def getValMW(self, time):
        return self.data[time].mw

    def getValMVAR(self, time):
        return self.data[time].mvar



# user defined function definition --------------

def takingOISdata(startIndex, endTime):
    dataList = ("Bus-A kV","Bus-B kV", "Tr-02 MW", "Tr-02 MVAR", "Tr-01 MW", "Tr-01 MVAR")
    itr=0
    while(times[startIndex+itr]<=endTime):
        print(f"------ {times[startIndex+itr]} -------")
        ls=[]
        for i in range(6):
            temp = input(f"Enter {dataList[i]}:")
            if(temp==""):
                temp = "0"
            ls.append(temp)
            
        busKV.load(times[startIndex+itr], ls[0], ls[1])
        tr2.load(times[startIndex+itr],ls[2], ls[3])
        tr1.load(times[startIndex+itr],ls[4], ls[5])
        itr+=1
        if(startIndex+itr >= len(times)):
            break

def showOISdata():
    print("Time\tBus-1 kV\tBus-2 kV\tMW1\tMVAR1\tMW2\tMVAR2\tTotal")
    for time in busKV.data:
        print(time + "\t" + busKV.getVol1(time) + "\t\t" + busKV.getVol2(time) + "\t\t" + tr1.getValMW(time) + "\t" + tr1.getValMVAR(time), end='\t')
        print(tr2.getValMW(time) + "\t" + tr2.getValMVAR(time) + "\t", (tr1.mwValu(time) + tr2.mwValu(time)))

def loadOIStoIncomer(src1: oisBusData, src2: oisTrafo, src3: oisTrafo, dst: incomerData):
    for time in src1.data:
        totalMW = src2.mwValu(time) + src3.mwValu(time)
        if(totalMW.is_integer()):
            totalMW = int(totalMW)
        dst.load(time, src1.getVol1(time))
        dst.load(time, str(totalMW))

def takingInput(data, timeIndex :int, lastTime: str) -> None:
    currentIndex = timeIndex
    while(times[currentIndex]<=lastTime):
        userInput = input(times[currentIndex] + ': ')
        if not userInput:
            data.load(times[currentIndex], "0")
        else:
            data.load(times[currentIndex], userInput)
        currentIndex+=1
        if(currentIndex >= len(times)):
            return

def noLS(data, timeIndex: int, lastTime: str):
    currentIndex = timeIndex
    while(times[currentIndex]<=lastTime):
        data.load(times[currentIndex], "0")
        currentIndex+=1
        if(currentIndex >= len(times)):
            return

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

def initChromDriver():
    print("Initializing...")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Optional: if you want to run without opening a window
    # chrome_options.add_argument("--disable-gpu")  # Optional: useful in headless mode

    service = Service(executable_path="chromedriver.exe")
    browsingDriver=webdriver.Chrome(service=service, options=chrome_options)

    # -- loading cookies --
    try:
        with open('cookies.pkl', 'rb') as cookie_file:
            cookies = pickle.load(cookie_file)
        browsingDriver.get(SYS_URL)
        for cookie in cookies:
            browsingDriver.add_cookie(cookie)
        browsingDriver.refresh()
    except FileNotFoundError:
        print("No cookies file found")

    print("Initialization completed.")
    return browsingDriver

def loggingIn(driver) -> bool:
    driver.get(SYS_URL)
# -- login to system website --
    if "login" in driver.current_url:
        print("Previous session is out.")
        emailField = driver.find_element(By.NAME, "email")
        passField = driver.find_element(By.NAME, "password")

        emailField.send_keys(EMAIL)
        passField.send_keys(PASSWORD+Keys.ENTER)
        # -- saving cookies --
        cookies = driver.get_cookies()
        with open('cookies.pkl', 'wb') as cookie_file:
            pickle.dump(cookies, cookie_file)

    if "dashboard" in driver.current_url:
        print("Logged in successfully!!")
        return True
    elif "login" in driver.current_url:
        print("Not logged in, try resetting cookies file.")
        try:
            os.remove("cookies.pkl")
            return False
        except Exception as e:
            print("Error! {e}")
            exit(-1)


def logInOIS(browsingDriver:webdriver.Chrome, id:str, passw:str):
    try:
        with open('OIScookies.pkl', 'rb') as cookie_file:
            cookies = pickle.load(cookie_file)
        browsingDriver.get(OIS_URL)
        for cookie in cookies:
            browsingDriver.add_cookie(cookie)
        browsingDriver.refresh()
    except FileNotFoundError:
        print("No cookies file found")
    
    if(id and passw):
        print("logging in by id and pass")
        browsingDriver.get(OIS_URL)
        if("login" not in browsingDriver.current_url):
            # logout
            print("Logged in already. Logging out...")
            browsingDriver.get(OIS_URL+"/logout")
        browsingDriver.get(OIS_URL)
        try:
            idField = browsingDriver.find_element(By.NAME, "username")
            passField = browsingDriver.find_element(By.NAME, "password")

            idField.send_keys(id)
            passField.send_keys(passw + Keys.ENTER)
            cookies = driver.get_cookies()
            with open('OIScookies.pkl', 'wb') as cookie_file:
                pickle.dump(cookies, cookie_file)
        except Exception as e:
            print(f"{e}")
    return "dashboard" in browsingDriver.current_url


# def submitOIS(tr1: oisTrafo, tr2: oisTrafo, bur: oisBusData):
#     for hrs in 


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

# -- main program starting from here --


feeders = []

apbs = feeder33kV(data, "APBS")
hm = feeder33kV(data,"HM")
bpbs = feeder33kV(data, "BPBS")

feeders.append(apbs)
feeders.append(hm)
feeders.append(bpbs)


tr1=oisTrafo("Tr-01")
tr2=oisTrafo("Tr-02")
busKV=oisBusData()

incomer = incomerData(data, "Grid Load")

# taking starting time
startTime = input("Enter starting time (HH.MM): ")
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


if(startTime>endTime):
    print("Time is not yet. Try again later.")
    exit(-1)
print("\nTime slot: " + startTime + "-->" + endTime + "\n")

# ----- taking OIS data ------

userID = input("Enter ID: ")
passw = hide_input_with_symbol("Enter your password: ", "*")

takingOISdata(startIndex, endTime)
showOISdata()

# ----- copy ois dato to system data
loadOIStoIncomer(busKV,tr1, tr2, incomer)
incomer.showData()


# ----- taking feeder data ----
for feeder in feeders:
    print("----------------------\nEnter " + feeder.name + " MW data:\n----------------------")
    takingInput(feeder, startIndex, endTime)
while(1):
    confirmation = input("Do you want to upload feeder load shed data? (y/n): ")
    if(confirmation.isalpha):
        confirmation.lower()
        if(confirmation == 'y' or confirmation == 'n'):
            break
        else:
            print("Invalid input")
    else:
        print("Invalid input")

if(confirmation=='y'):
    for feeder in feeders:
        print("----------------------\nEnter " + feeder.name + " L/S data:\n----------------------")
        takingInput(feeder, startIndex, endTime)
else:
    for feeder in feeders:
        noLS(feeder, startIndex, endTime)

# --------------- Input data preview ---------------
incomer.showData()
for feeder in feeders:
    feeder.showData()


# -- initializing driver
driver = initChromDriver()
if(logInOIS(driver, userID, passw)):
    print("logged in successfully!")
else:
    print("logging in failed.")

# -- logging In --
if not loggingIn(driver):
    driver=initChromDriver()

print("Working on incomer data...")
# pursing incomer editing URLs and upload data
driver.get(INCOMER_URL)
incomer.loadEditingURLs(driver)
incomer.uploadData(driver)

print("Working on feeder data...")
# pursing feeder editing URLs and upload data
for feeder in feeders:
    driver.get(FEEDER_URLs[feeders.index(feeder)])
    feeder.loadEditingURLs(driver)
    feeder.uploadData(driver)
print("We're done! Closing soon...")
driver.quit()