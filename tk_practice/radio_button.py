from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

root = Tk()

root.title('Select a character...')

# create size of window to a fixed size that doesn't allow resizing
# root.geometry("300x200")
# root.resizable(0, 0)

mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

mode = StringVar()
characters = ['eric', 'kenny', 'kyle', 'mrhankey', 'mrslave', 'randy', 'satan', 'token']

# create image references for each character
image_list = [ImageTk.PhotoImage(Image.open(f'./resources/{character}.png'))
              for character in characters]

# create radio button list for each image
radio_button_list = [ttk.Radiobutton(mainframe, image=image,
                                     variable=mode, value=character.title())  # todo: create a function that gets the correct character name
                     for image, character in zip(image_list, characters)]

# grid the characters
for character in enumerate(radio_button_list):
    column = character[0]+1
    row = 0
    character[1].grid(column=column, row=row)
    if column >= 5:
        column = character[0] - 3
        row = 1
        character[1].grid(column=column, row=row)

# create labels that show which character is currently selected
ttk.Label(mainframe, text='Character Selected:').grid(column=1, row=2, sticky=W)
ttk.Label(mainframe, textvariable=mode).grid(column=1, row=2, sticky=E)
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# todo: create a button that allows the user to

root.mainloop()

