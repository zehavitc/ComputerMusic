
import Tkinter as tk
from PIL import Image, ImageTk
root = tk.Tk()

img = Image.open(r'nysunset.jpg')
imgTk = ImageTk.PhotoImage(img)

def motion(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))
    print(img.getpixel((x,y)))

p = tk.Label(root, image = imgTk)
p.pack(side = "bottom", fill = "both", expand = "yes")
root.bind('<Motion>', motion)
root.mainloop()