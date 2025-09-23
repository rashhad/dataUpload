from guiClass import mainAppWindow
from tkinter import ttk


# ('clam', 'alt', 'default', 'classic')

menuTree ={
    'root':['user','help'],
    'user':['add user','remove user'],
    'help':['about','contact']
}
commandTree={
    'add user':{'new user':lambda:print('new user'), 'existing user':lambda:print('existing user')},
    'remove user':{'remove last user':lambda:print('removing last user'), 'remove a user':lambda:print('enter id to remove')}
    , 'about':{'about Me':lambda:print('about')}
    , 'contact':{'email':lambda:print('email'), 'phone':lambda:print('phone')}
}

app = mainAppWindow('Main', '1000x1000')
app.addMenuTree(menuTree)
app.addCommandTree(commandTree)
app.view()