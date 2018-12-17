
import Tkinter as tk
from PIL import Image, ImageTk
import OSC

root = tk.Tk()

#FREQ_RANGE = (0, )
DEGREE_RANGE = (0, 7)
DURATION_RANGE = (0.2, 0.8)
AMP_RANGE = (0.4, 3)

img = Image.open(r'pics/nysunset.jpg')
imgTk = ImageTk.PhotoImage(img)

def click(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))
    rgb = img.getpixel((x,y))
    print(rgb)
    makesound(*rgb)

def get_value(range, num):
	return range[0] + ((num / 255.0) * (range[1]-range[0]))

def makesound(r, g, b):
	degree = int(get_value(DEGREE_RANGE, r))
	duration = get_value(DURATION_RANGE, g)
	amp = get_value(AMP_RANGE, b)

	client = OSC.OSCClient()
	client.connect(('127.0.0.1', 57120))
	msg = OSC.OSCMessage()
	msg.setAddress("/makesound")
	msg.append(degree)
	msg.append(duration)
	msg.append(amp)
	client.send(msg)

p = tk.Label(root, image = imgTk)
p.pack(side = "bottom", fill = "both", expand = "yes")
root.bind('<Button-1>', click)

root.mainloop()