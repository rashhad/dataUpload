import tkinter as tk
from tkinter import ttk

def update_label_text():
    my_label.config(text="New Label Text!")

root = tk.Tk()
root.title("Label Update Example")

my_label = ttk.Label(root, text="Initial Label Text")
my_label.pack(pady=20)

update_button = ttk.Button(root, text="Update Label", command=update_label_text)
update_button.pack()

root.mainloop()