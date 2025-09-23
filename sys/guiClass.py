from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import Tk
from tkinter import ttk
from tkinter import messagebox
from typing import List, Dict, Tuple, Callable, Optional, Union
from database import *
import time


# GUI main class
class entryField:
    """
    Creates entry field having label, entry field and stringVar togather
    """

    def __init__(self, master:Tk):
        self._fieldsFrame = ttk.Frame(master,borderwidth=5, relief="solid")
        '''all fields will be residing inside this frame'''
        self._fields : Dict[str, Tuple[ttk.Label, ttk.Entry, tk.StringVar]] = {}
        ''' ditionary accessing hint:
            fields[field id][0 for label,1 for entryField,2 for strVar].
            This dictionary is used for collection of ttk.Entry in a window for letter use.
        '''

    def addField(self, id:str, label:str, passField: bool = False):
        '''adds a field to self.fields dictionary.'''
        __var = tk.StringVar()
        if passField:
            self._fields[id] = (ttk.Label(self._fieldsFrame, text=label),ttk.Entry(self._fieldsFrame, textvariable=__var, show='*'), __var)
        else:
            self._fields[id] = (ttk.Label(self._fieldsFrame, text=label),ttk.Entry(self._fieldsFrame, textvariable=__var), __var)

    def getEntryField(self, id:str) -> Optional[ttk.Entry]:
        try:
            return self._fields[id][1]
        except:
            return None
        
    def getLabel(self, id:str) -> Optional[ttk.Entry]:
        try:
            return self._fields[id][0]
        except:
            return None
        
    def getFieldVal(self, id:str):
        '''return a specific entry field widget by it's id.'''
        return self._fields[id][1].get()
    
    def setFieldVal(self,id,value:str):
        self._fields[id][2].set(value=value)


    def getEmptyField(self) -> ttk.Entry|None:
        '''return first ttk.Entry widget that is empty.'''
        for field in self._fields:
            __inputStr = self._fields[field][1].get()
            if __inputStr == "":
                return self._fields[field][1]
        return None
            
    def clearInputFeilds(self):
        '''clear all ttk.Entry widget.'''
        for field in self._fields:
            self._fields[field][2].set("")
        for field in self._fields:
            self._fields[field][1].focus_set()
            break
    
    @property
    def getFrame(self) -> ttk.Frame:
        return self._fieldsFrame
    
    @property
    def haveField(self) -> bool:
        if self._fields:
            return True
        else:
            return False
        
    def view(self):
        self.getFrame.pack(fill='both', padx=1, pady=1)
        self.getFrame.columnconfigure(0, weight=1)
        self.getFrame.columnconfigure(1,weight=2)
        for r, id in enumerate(self._fields):
            self.getLabel(id).grid(row=r, column=0, sticky='e', padx=5, pady=3)
            self.getEntryField(id).grid(row=r, column=1, sticky='ew', padx=5,pady=3)
        


class button:
    def __init__(self, master:Tk):
        self._frame = ttk.Frame(master,borderwidth=5, relief="solid")
        self._buttons:dict[str, tuple[ttk.Button, Callable]] = {}
        '''button dictionary of class button. _buttons[button id:str][0 for ttk.Button widget, 1 for callable]'''
    
    def addButton(self, id:str, label:str, callable: Callable):
        self._buttons[id] = (ttk.Button(self._frame, text=label, command=callable))

    def getButton(self,id:str) -> Optional[ttk.Button]:
        try:
            return self._buttons[id][0]
        except:
            return self._buttons[id]
        
    @property
    def getFrame(self) -> ttk.Frame:
        return self._frame
    
    def view(self):
        self.getFrame.pack(side='top', fill='both')
        for id in self._buttons:
            self.getButton(id).pack(side='right', anchor='e', expand=True, fill='x')

class menu:
    '''
    create and manages menubar.
    '''
    def __init__(self, root:Tk):
        self.menubar = tk.Menu(root) #creating menu bar
        root.config(menu=self.menubar) #configuring menubar of root window
        self.menuTree:dict[str, list[str]] = {}           #[parentLabel][childLabels]
        self.commands:dict[str, dict[str, function]]={} #command=commands[parentLabel][label]
    

    def view(self):
        '''build and place menubar with it's items on root window'''
        self.buildMenu(self.menubar, 'root')
        pass

    def buildMenu(self,_parentMenu:tk.Menu, _parentLabel:str):
        '''build menu from menuTree and commands dictionary.
        menu is tree like data structure, here we are creating menu tree by DFS traversing.
        this is a recursive function and it takes a parent menu and it's label,
        explores, creats, and cascades it's child menu.'''
        try:
            '''this try block tries _parentLabel's child menu.
            if child exists, it explores child's children recursively.'''
            for childLabel in self.menuTree[_parentLabel]:
                # creaitng child menu and cascade under parent menu
                childMenu = tk.Menu(_parentMenu, tearoff=0)
                _parentMenu.add_cascade(menu=childMenu, label=childLabel)
                # recursion call
                self.buildMenu(childMenu, childLabel)
        except KeyError:
            '''if try block is failed, that indicates that the parent menu has no child menu
            so we are adding command labels/menu uder the parent menu
            '''
            commands = self.commands[_parentLabel]
            for commandLabel in commands:
                _parentMenu.add_command(label=commandLabel, command=commands[commandLabel])    
        

class baseWindow(ABC):
    '''abstract class for creating a window class.'''
    def __init__(self, title, size, parent=True, parentBaseWindow:Optional[Tk]=None, resizable=True):
        super().__init__()
        if parent:
            self.root = Tk()
        else:
            self.root = tk.Toplevel(parentBaseWindow[0].root)
            self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.title(title)
        self.root.geometry(size)
        if not resizable:
            self.root.resizable(False, False)
        self.tryStyle('clam')

    @staticmethod
    def tryStyle(theme:str):
        style=ttk.Style()
        style.theme_use('clam')

    @abstractmethod
    def view(self):
        '''abstract class method for show up window class.'''
        self.root.mainloop()

class mainAppWindow(baseWindow):
    def __init__(self, title, size, parent=True, parentBaseWindow = None, resizable=True):
        super().__init__(title, size, parent, parentBaseWindow, resizable)
        self.menu:menu=menu(self.root)
        self.statusFrame = ttk.Frame(self.root, border=2, relief='sunken')
        self.statusLabel = ttk.Label(self.statusFrame, text='Status bar...')

    def addMenuTree(self, menuTree:dict[str, list[str]]):
        self.menu.menuTree=menuTree

    def addCommandTree(self, menuCommandTree):
        self.menu.commands = menuCommandTree
    
    def view(self):
        self.statusFrame.pack(fill='x', anchor='s',expand=True)
        self.statusLabel.pack(anchor='w', expand=True)
        self.menu.view()
        return super().view()



class formWindow(baseWindow):
    def __init__(self, title, size, parent=True, parentBaseWindow = None, resizable=True):
        super().__init__(title, size, parent, parentBaseWindow, resizable)
        self.entries = entryField(self.root)
        self.buttons = button(self.root)


    def view(self):
        self.entries.view()
        self.buttons.view()
        return super().view()

class loginWindoww(formWindow):
    def __init__(self, title, size, parent=True, parentBaseWindow = None, resizable=True):
        super().__init__(title, size, parent, parentBaseWindow, resizable=True)
        self.root.bind('<Return>',lambda e:self.submit())
        self.root.bind('<Escape>',lambda e:self.root.destroy())
        self.entries.addField('id','OIS ID')
        self.entries.addField('passw', 'Password', True)
        self.buttons.addButton('cancel', 'Cancel', lambda: self.root.destroy())
        self.buttons.addButton('submit', 'Login', lambda:self.submit())
        self.buttons.addButton('create', 'New User', lambda:self.switchToAddUser())
        self.view()

    def submit(self):
        id = self.entries.getFieldVal('id')
        passw=self.entries.getFieldVal('passw')
        if id == '' or passw == '':
            messagebox.showerror('Login Error','ID or Password cannot be empty!')
        elif sysLogin(id,passw):
            messagebox.showinfo('Login Success', 'Login success!')
        else:
            messagebox.showwarning('Credential Mismatch', 'ID and Password mismatch!')

    @staticmethod
    def switchToAddUser():
        addNewUser('Add a User', '560x320')

class addNewUser(formWindow):
    def __init__(self, title, size, parent=True, parentBaseWindow=None, resizable=True):
        super().__init__(title, size, parent, parentBaseWindow, resizable)
        self.entries.addField('id','OIS ID')
        self.entries.addField('name', 'Name')
        self.entries.addField('passw', 'Password', True)
        self.entries.addField('cPassw', 'Confirm Password', True)
        self.buttons.addButton('cancel', 'Cancel', lambda:self.root.destroy())
        self.buttons.addButton('create', 'Create', lambda: self.create())
        self.root.bind('<Escape>',lambda e:self.escape())
        self.view()

    def create(self):
        id=self.entries.getFieldVal('id')
        passw=self.entries.getFieldVal('passw')
        cPass=self.entries.getFieldVal('cPassw')
        name = self.entries.getFieldVal('name')
        if id =='' or name == '' or passw =='' or cPass == '':
            messagebox.showerror('Failed', message='Fill all the required fields.')
        elif passw==cPass:
            try:
                creatingUser(id, name, passw)
                messagebox.showinfo('Success', message=f'OIS id: {id} added successfully')
                self.root.destroy()
            except sqlite3.IntegrityError:
                self.entries.clearInputFeilds()
                print(messagebox.showerror('Failed!', message=f'OIS id: {id} already exists.', parent=self.root))
                self.entries.clearInputFeilds()
        else:
            self.entries.clearInputFeilds()
            print(messagebox.showerror('Failed',message='Password mismatched! Try again.'))

    def escape(self):
        self.root.destroy()
        loginWindoww('Login', '560x160')






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
        self.labelFrame = ttk.Frame(self.root,borderwidth=5, relief="solid")
        self.fieldsFrame = ttk.Frame(self.root,borderwidth=5, relief="solid")
        self.buttonsFrame = ttk.Frame(self.root,borderwidth=5, relief="solid")
        self.tableFrame = ttk.Frame(self.root)
        self.tableFrame132 = ttk.Frame(self.tableFrame, borderwidth=5, relief="solid")
        self.tableFrame33 = ttk.Frame(self.tableFrame, borderwidth=5, relief="solid")
        self.tableFrame33ls = ttk.Frame(self.tableFrame, borderwidth=5, relief="solid")
        # widgets collection
        self.fields : Dict[str, Tuple[ttk.Label, ttk.Entry, tk.StringVar]] = {}
        self.buttons:dict[str, tuple[ttk.Button, Callable]] = {}
        self.table:dict[int,dict[str,dict[str,ttk.Entry]]] = {}
        self.label = ttk.Label(self.labelFrame, text=heading, justify='right', anchor='e', font=('Arial', 14, 'bold'))

    @staticmethod
    def tillTime() -> str:
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

    def createTable(self):
        headings132 = ['Bus 1', 'Bus 2', 'T2 MW', 'T2 MVAR', 'T1 MW', 'T1 MVAR']
        headings33 = ['Anowara', 'HM', 'Banskhali2']
        headings33ls = ['Anowara', 'HM', 'Banskhali2']
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
            "23:00"
        ]
        startTimeIdx = times.index(findLastEntryTime())
        if startTimeIdx>=23:
            startTimeIdx=0
        else:
            startTimeIdx+=1
        # print(startTimeIdx)
        endTimeIdx = times.index(self.tillTime())
        if startTimeIdx<=endTimeIdx:
            workingTime =times[startTimeIdx:endTimeIdx+1]
        else:
            workingTime = times[startTimeIdx:] + times[:endTimeIdx+1]

        self.table[132] = {}
        for t in workingTime:
            self.table[132][t]={}
            for i,h in enumerate(headings132):
                self.table[132][t][h] = ttk.Entry(self.tableFrame132, width=8)
        self.table[33] = {}
        for t in workingTime:
            self.table[33][t]={}
            for i,h in enumerate(headings33):
                self.table[33][t][h] = ttk.Entry(self.tableFrame33,width=8)
        self.table[3315]={}
        for t in workingTime:
            self.table[3315][t]={}
            for i,h in enumerate(headings33ls):
                self.table[3315][t][h] = ttk.Entry(self.tableFrame33ls,width=8)




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

    def __findEmptyTable(self):
        pass

    def clearInputFeilds(self):
        for field in self.fields:
            self.fields[field][2].set("")
        for field in self.fields:
            self.fields[field][1].focus_set()
            break


    def view(self):
        self.labelFrame.pack(fill='both')
        self.label.grid(sticky='ns')
        # viewing fields
        if self.fields:
            self.fieldsFrame.columnconfigure(0, weight=2)
            self.fieldsFrame.rowconfigure(0, weight=2)
            self.fieldsFrame.pack(fill='both', padx=1, pady=1)
            for i, field in enumerate(self.fields):
                # label and fields
                self.fields[field][0].grid(row = i, column= 0, padx=5, pady=5, sticky='nsew')
                self.fields[field][1].grid(row = i, column = 1, padx=5, pady=5, sticky='nsew')
                if i ==0:
                    self.fields[field][1].focus_set()
        # viewing table
        if self.table:
            self.tableFrame.pack(fill='both')
            self.tableFrame132.pack(fill='both')
            # viewing heading row
            ttk.Label(self.tableFrame132, text='Time',font=('Arial', 9, 'bold'), justify='center').grid(row=0, column=0, padx=5,pady=5,sticky='nsew')
            for i, h in enumerate(self.table[132][next(iter(self.table[132]))],start=1):
                ttk.Label(self.tableFrame132, text=h,font=('Arial', 9, 'bold'), justify='center').grid(row=0, column=i, padx=5,pady=5,sticky='nsew')
            # viewing entry rows
            for r, t in enumerate(self.table[132]):
                ttk.Label(self.tableFrame132, text=t).grid(row=r+1, column=0,padx=5,pady=5, sticky='nsew')
                for c, heading in enumerate(self.table[132][t]):
                    self.table[132][t][heading].grid(row=r+1, column=c+1, padx=5, pady=5, sticky='nsew')
                    if r==0 and c == 0:
                        self.table[132][t][heading].focus_set()
                        

        # viewing buttons
        if self.buttons:
            self.buttonsFrame.pack(fill='both',padx=1, pady=1)
            for btn in self.buttons:
                self.buttons[btn].pack(side='right', padx=5, pady=2)
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
        # messagebox.showinfo('Success!', 'Successfully loged in.')
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
    appWindow.createTable()
    # appWindow.addButton('ok', 'ok', lambda: appWindow.tableFrame.pack_forget())
    appWindow.view()

    
def addMeWindow(parentWindow:Tk):
    addUserWindow = window('New User','Adding New User', size='250x220', resizable=False, parent=False, parWindow=parentWindow)
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
    loginWindow = window("Login", 'Login Please:', size='250x150', resizable=False)
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