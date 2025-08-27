import sqlite3
import os
import msvcrt
from database import *
from typing import List
import ctypes
from ctypes import wintypes

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

def flush_input_buffer_windows():
    STD_INPUT_HANDLE = -10
    kernel32 = ctypes.windll.kernel32
    hConsoleInput = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    kernel32.FlushConsoleInputBuffer(hConsoleInput)


def startReadingInput(t:str):
    pass


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


        
while(1):
    try:
        name, id = findActiveUser()
        print(f'Active user: {name} ({id})')
        print('Choose an option:')
        print('[enter] enter reading\t[1] logout\t[2] update password\t[3] update name\t [4] delete this user\n')
        opt = input()
        os.system('cls')
        match opt:
            case '1':
                sysLogOut(id)
                # break
            case '2':
                print('updating password.')
                oldPass = hide_input_with_symbol("Old password: ")
                newPass = hide_input_with_symbol("New password: ")
                os.system('cls')
                if updatePass(id, oldPass, newPass):
                    print('Password update successfull!')
                else:
                    print("Password update failed due to old password mismatched!")
            case '3':
                print('UPDATING NAME')
                print(f'Current name: {name}')
                updateName(id, input('New name: '))
                os.system('cls')
            case '4':
                print('DELETING THIS USER.')
                passw = hide_input_with_symbol('Password: ')
                print('ARE YOU DOUBLE SURE? (Y/N)')
                try:
                    sure = input().lower()
                    os.system('cls')
                    if sure == 'y':
                        if deleteUser(id, passw):
                            print('User has been deleted!'.upper())
                        else:
                            print('failed deleting user. password mismatched!'.upper())
                    else:
                        print('request canceled!'.upper())
                except:
                        print('request canceled!'.upper())
            case "":
                print('ENTER READING')
                while(True):
                    print(f'Choose an option:\n[enter]\tLast time [{findLastEntryTime()}]\t[0]\tManual time')
                    choice = input()
                    if(choice=='0'):
                        startReadingInput(findLastEntryTime())
                        break
                    elif(choice==''):
                        break
                    os.system('cls')
                    print('OPTION CHOSEN IS INVALID!')


    except TypeError:
        print('No active user')
        while(1):
            choice = input('[1] login\t[2] new user\n')
            os.system('cls')
            match choice:
                case '1':
                    # login user
                    print('Login to an user account')
                    id = input("OIS id: ")
                    pin = hide_input_with_symbol("OIS password: ")
                    os.system('cls')
                    try:
                        if sysLogin(id, pin):
                            print('login success!')
                            break
                        else:
                            print('password mismatched!')
                    except TypeError:
                        print(f'user id {id} not found!')
                    pass
                case '2':
                    # creating user
                    print('Creating new user.')
                    name = input('Your name: ')
                    id = input('OIS id: ')
                    passw = hide_input_with_symbol('OIS password: ')
                    try:
                        creatingUser(id,name,passw)
                        os.system('cls')
                        print(f'user id: {id} created successfullly!')
                    except sqlite3.IntegrityError:
                        os.system('cls')
                        print(f'user {id} already exist!')
                    pass
