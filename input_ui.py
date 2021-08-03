from tkinter import *
import read_write

root = None
TFUsername = None
TFPassword = None


def getUsername():
    global root, TFUsername
    userInput = TFUsername.get()
    return userInput


def getPassword():
    global root, TFPassword
    userInput = TFPassword.get()
    return userInput


def functionSave():
    global root
    read_write.writeCredentialsToFile(getUsername(), getPassword())
    root.destroy()


def functionCancel():
    global root
    root.destroy()


def change_account(icon):
    global root, TFUsername, TFPassword
    root = Tk()
    root.resizable(False, False)
    # root.overrideredirect(1)
    root.title('SLT Credentials')

    Label(root, text='Username :').grid(row=0, column=0)
    Label(root, text='Password :').grid(row=1, column=0)

    TFUsername = Entry(root)
    TFUsername.grid(row=0, column=1)
    TFPassword = Entry(root, justify=LEFT)
    TFPassword.grid(row=1, column=1)

    frame = Frame(root)
    frame.grid(row=2, columnspan=2)
    Button(frame, text='Save', command=functionSave).grid(row=0, column=0,)
    Button(frame, text='Cancel', command=functionCancel).grid(row=0, column=1)

    root.mainloop()
