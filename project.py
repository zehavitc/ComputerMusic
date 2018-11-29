
# Requirements:
# 0. python 2.7 installed
# 1. install dependencies: "pip install image"

import Tkinter as tk
from PIL import Image, ImageTk
root = tk.Tk()

def motion(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))
img = ImageTk.PhotoImage(Image.open(r'nysunset.jpg'))
panel = tk.Label(root, image = img)
panel.pack(side = "bottom", fill = "both", expand = "yes")
root.bind('<Motion>', motion)
root.mainloop()