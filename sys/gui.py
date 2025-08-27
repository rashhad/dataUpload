from guiClass import *

try:
    name, id = findActiveUser()
    startAppWindow(name=name, id=id)
except TypeError:
    loginWindow()