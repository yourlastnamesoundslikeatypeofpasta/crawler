import tkinter
import tkinter.messagebox
import sys


class MyGUI:
    def __init__(self):
        # create the main window widget
        self.mainWindow = tkinter.Tk()

        self.nameValue = tkinter.StringVar()
        self.streetValue = tkinter.StringVar()
        self.cszValue = tkinter.StringVar()

        self.infoFrame = tkinter.Frame(self.mainWindow)
        self.buttonFrame = tkinter.Frame(self.mainWindow)

        self.nameLabel = tkinter.Label(self.infoFrame,
                                       textvariable=self.nameValue)
        self.streetLabel = tkinter.Label(self.infoFrame,
                                         textvariable=self.streetValue)
        self.cszLabel = tkinter.Label(self.infoFrame,
                                      textvariable=self.cszValue)
        self.nameLabel.pack()
        self.streetLabel.pack()
        self.cszLabel.pack()

        self.myButton = tkinter.Button(self.buttonFrame,
                                       text='Show Info',
                                       command=self.showAddress)

        self.quitButton = tkinter.Button(self.buttonFrame,
                                         text='Quit',
                                         command=self.mainWindow.destroy)

        self.myButton.pack(side='left')
        self.quitButton.pack(side='right')

        self.infoFrame.pack()
        self.buttonFrame.pack()

        tkinter.mainloop()

    def showAddress(self):
        self.nameValue.set('Christian Zagazeta')
        self.streetValue.set('42 Wallaby Way')
        self.cszValue.set('Sydney, Australia 30101')


mygui = MyGUI()
