import tkinter as tk
from tkinter import Tk
from tkinter import ttk
from tkinter import messagebox
from typing import List, Dict, Tuple, Callable
from database import *

# GUI main class

class window:
    def __init__(self, title, heading:str, size:str, resizable:bool=True, parent:bool = True, **kwargs):
        if parent:
            self.root = Tk()
        else:
            self.root = tk.Toplevel(kwargs['parWindow'])
        self.root.title(title)
        self.root.geometry(size)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        if not resizable:
            self.root.resizable(False, False)
        # frames
        self.labelFrame = ttk.Frame(self.root)
        self.fieldsFrame = ttk.Frame(self.root)
        self.buttonsFrame = ttk.Frame(self.root)
        # widgets collection
        self.fields : Dict[str, Tuple[ttk.Label, ttk.Entry, tk.StringVar]] = {}
        self.buttons:dict[str, tuple[ttk.Button, Callable]] = {}
        self.label = ttk.Label(self.labelFrame, text=heading, font=('Arial', 14, 'bold'))



    def addField(self, id:str, label:str, passField: bool = False):
        __var = tk.StringVar()
        if passField:
            self.fields[id] = (ttk.Label(self.fieldsFrame, text=label),ttk.Entry(self.fieldsFrame, textvariable=__var, show='*'), __var)
        else:
            self.fields[id] = (ttk.Label(self.fieldsFrame, text=label),ttk.Entry(self.fieldsFrame, textvariable=__var), __var)

    def getFieldVal(self, id:str):
        return self.fields[id][1].get()

    def addButton(self, id:str, label:str, callable: Callable):
        self.buttons[id] = (ttk.Button(self.buttonsFrame, text=label, command=callable))


    def __findEmptyField(self):
        for field in self.fields:
            __inputStr = self.fields[field][1].get()
            if __inputStr == "":
                self.fields[field][1].focus_set()
                return
        messagebox.showinfo("Success!!", message="All fields are completed!")
        self.clearInputFeilds()

    def clearInputFeilds(self):
        for field in self.fields:
            self.fields[field][2].set("")
        for field in self.fields:
            self.fields[field][1].focus_set()
            break


    def view(self):
        self.label.grid(sticky='ns')
        self.labelFrame.pack(fill='both', padx=1, pady=1)
        for i, field in enumerate(self.fields):
            # label and fields
            self.fields[field][0].grid(row = i, column= 0, padx=5, pady=5, sticky='nsew')
            self.fields[field][1].grid(row = i, column = 1, padx=5, pady=5, sticky='nsew')
            if i ==0:
                self.fields[field][1].focus_set()
        for btn in self.buttons:
            self.buttons[btn].pack(side='right', padx=5, pady=2)
        self.fieldsFrame.pack(fill='both', padx=1, pady=1)
        self.fieldsFrame.columnconfigure(0, weight=2)
        self.fieldsFrame.rowconfigure(0, weight=2)
        self.buttonsFrame.pack(fill='both',padx=1, pady=1)
        # self.root.bind('<Return>', lambda e: self.__findEmptyField())
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.mainloop()

# GUI commands here

def submit(newUserWindow: window):
    id = newUserWindow.getFieldVal('id')
    name = newUserWindow.getFieldVal('name')
    passw = newUserWindow.getFieldVal('pass')
    cPass = newUserWindow.getFieldVal('confPass')
    if id =='' or name == '' or passw =='' or cPass == '':
        messagebox.showerror('Failed', message='Fill all the required fields.')
    elif passw==cPass:
        try:
            creatingUser(id, name, passw)
            messagebox.showinfo('Success', message=f'OIS id: {id} added successfully')
            newUserWindow.root.destroy()
        except sqlite3.IntegrityError:
            newUserWindow.clearInputFeilds()
            print(messagebox.showerror('Failed!', message=f'OIS id: {id} already exists.', parent=newUserWindow.root))
            newUserWindow.clearInputFeilds()
    else:
        newUserWindow.clearInputFeilds()
        print(messagebox.showerror('Failed',message='Password mismatched! Try again.'))

def login(loginWindow:window):
    id = loginWindow.getFieldVal('id')
    passw = loginWindow.getFieldVal('pass')
    if id=='' or passw =='':
        messagebox.showerror('Error!', 'ID or Password cannot be empty.')
    elif sysLogin(id=id, pin=passw):
        messagebox.showinfo('Success!', 'Successfully loged in.')
        loginWindow.root.destroy()
        name, id = findActiveUser()
        startAppWindow(name=name, id=id)
    else:
        messagebox.showerror('Failed', 'Incorrect ID or Password.')

def logOut(id, appWindow:window):
    sysLogOut(id)
    appWindow.root.destroy()
    loginWindow()

def submitUpdateName(id:str, gui:window, parWindow:window):
    print(parWindow.label)
    name=gui.getFieldVal('newName')
    gui.root.grab_set()
    messagebox.showinfo('Success', 'Name updated successfull', parent=gui.root) if updateName(id=id, name=name) else messagebox.showerror('Failed', 'Failed update name', parent=gui.root)
    parWindow.label.config(text=f"Welcome {name} ({id})")
    gui.root.destroy()


# GUI windows

def startAppWindow(name, id):
    # creating the windows
    appWindow = window('Shift Assistant Software', f'Welcome {name} ({id})','600x600')
    menubar = tk.Menu(appWindow.root)
    appWindow.root.config(menu=menubar)
    userMenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='User', menu=userMenu)
    userMenu.add_command(label='Update Name', command=lambda:updateNameWindow(name=name, id=id, parentWindow=appWindow))
    userMenu.add_command(label='Update Password', command=lambda:print('update password'))
    userMenu.add_command(label='Delete Me', command=lambda:print('Are you sure?'))
    userMenu.add_command(label='Logout', command=lambda:logOut(id=id,appWindow=appWindow))
    appWindow.view()

    
def addMeWindow(parentWindow:Tk):
    addUserWindow = window('New User','Adding New User', size='250x200', resizable=False, parent=False, parWindow=parentWindow)
    # parentWindow.withdraw()
    addUserWindow.root.grab_set()
    addUserWindow.addField('id', 'OIS ID')
    addUserWindow.addField('name', 'Name')
    addUserWindow.addField('pass', 'Password', passField=True)
    addUserWindow.addField('confPass', 'Confirm Password', passField=True)
    addUserWindow.addButton('submit', 'Submit', lambda:submit(addUserWindow))
    addUserWindow.root.bind('<Return>', lambda e:submit(addUserWindow))
    addUserWindow.view()

def loginWindow():
    loginWindow = window("Login", 'Login Please:', size='250x130', resizable=False)
    loginWindow.addField('id', 'OIS ID')
    loginWindow.addField('pass', 'Password', passField=True)
    loginWindow.addButton('login', 'Login', lambda:login(loginWindow=loginWindow))
    loginWindow.addButton('cancel', 'Cancel', lambda:loginWindow.root.destroy())
    loginWindow.addButton('creatAccount', 'Add Me', lambda:addMeWindow(loginWindow.root))
    loginWindow.root.bind('<Return>', lambda e: login(loginWindow=loginWindow))
    loginWindow.view()

def updateNameWindow(name, id, parentWindow):
    gui = window('Update Name', f'Current Name: {name}', '250x150', resizable=False, parent=False, parWindow=parentWindow.root)
    gui.addField('newName', 'New Name')
    gui.addButton('updateName', 'Update', lambda:submitUpdateName(id, gui,parentWindow))
    gui.view()