from tkinter import *
import read_write


class CredentialWindow:

    def __init__(self, credential_manager):

        self._credential_manager = credential_manager

        self._root = Tk()
        self._root.resizable(False, False)
        self._root.title('SLT Credentials')

        Label(self._root, text='Username :').grid(row=0, column=0)
        Label(self._root, text='Password :').grid(row=1, column=0)

        self._tf_username = Entry(self._root)
        self._tf_username.grid(row=0, column=1)
        self._tf_password = Entry(self._root, justify=LEFT)
        self._tf_password.grid(row=1, column=1)

        frame = Frame(self._root)
        frame.grid(row=2, columnspan=2)
        Button(frame, text='Save',
               command=self._function_save).grid(row=0, column=0,)
        Button(frame, text='Cancel',
               command=self._function_cancel).grid(row=0, column=1)

    def _function_save(self):
        self._credential_manager.write_credentials_to_file(
            self._tf_username.get(), self._tf_password.get())
        self._root.destroy()

    def _function_cancel(self):
        self._root.destroy()

    def start_window(self):
        self._root.mainloop()
