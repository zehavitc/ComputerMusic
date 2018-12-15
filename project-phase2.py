from Tkinter import *
from tkMessageBox import *
import tkFileDialog
from PIL import Image, ImageTk
import OSC

#FREQ_RANGE = (0, )
DEGREE_RANGE = (0, 7)
DURATION_RANGE = (0.2, 0.8)
AMP_RANGE = (0.4, 3)

class App(Tk):
	def __init__(self):
		Tk.__init__(self)
		self.title("RGB Music")

		w = 500
		h = 400
		ws = self.winfo_screenwidth()
		hs = self.winfo_screenheight()
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		self.geometry('%dx%d+%d+%d' % (w,h,x, y))
		
		#self.geometry("500x400")
		self.iconbitmap(default='icon.ico')
		self.resizable(width=False, height=False)
		self.img = None
		self.imgTk = None		
		
		menubar = Menu(self)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Load image", command=self.load_image)
		filemenu.add_command(label="Settings", command=self.settings)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.quit)
		menubar.add_cascade(label="File", menu=filemenu)
		helpmenu = Menu(menubar, tearoff=0)
		helpmenu.add_command(label="About", command=self.about)
		menubar.add_cascade(label="Help", menu=helpmenu)
		self.config(menu=menubar)
	
	def load_image(self):
		imagePath = tkFileDialog.askopenfilename(initialdir = ".",title = "Select image file",filetypes = (("jpeg files","*.jpg"),("png","*.png")))
		self.img = Image.open(imagePath)
		self.imgTk = ImageTk.PhotoImage(self.img)
		
		self.imageLabel = Label(self, image = self.imgTk)
		self.imageLabel .pack(side = "bottom", fill = "both", expand = "yes")
		self.bind('<Button-1>', self.click)
		
	def click(self, event):
		x, y = event.x, event.y
		print('{}, {}'.format(x, y))
		rgb = self.img.getpixel((x,y))
		print(rgb)
		self.makesound(*rgb)

	def get_value(self, range, num):
		return range[0] + ((num / 255.0) * (range[1]-range[0]))
		
	def settings(self):
		settingsWindow = Toplevel(self)
		settingsWindow.transient(self)
		settingsWindow.grab_set()
		
		w = 500
		h = 500
		ws = self.winfo_screenwidth()
		hs = self.winfo_screenheight()
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		
		settingsWindow.geometry('+%d+%d' % (x, y))
		
		Label(settingsWindow, text="Instruments:").grid(row=0, column=0,padx=20, pady=20)
		listbox = Listbox(settingsWindow, selectmode=MULTIPLE)
		listbox.pack()
		for instrument in ["piano", "violin", "guitar", "bass"]:
			listbox.insert(END, instrument)		
		listbox.grid(row=0,column=1,padx=20, pady=20)
		
		Label(settingsWindow, text="Amplitude range:").grid(row=1, column=0,padx=20, pady=20)
		Label(settingsWindow, text="Degree range:").grid(row=2, column=0,padx=20, pady=20)
		Label(settingsWindow, text="Duration range:").grid(row=2, column=0,padx=20, pady=20)
		Label(settingsWindow, text="Duration neighbours radius:").grid(row=3, column=0,padx=20, pady=20)
		Button(settingsWindow, text="Save").grid(row=4, columnspan=2,padx=20, pady=20)
		
		settingsWindow.title("Settings")
		settingsWindow.mainloop()
		
	def about(self): 
		aboutWindow = Toplevel(self)
		aboutWindow.transient(self)
		aboutWindow.grab_set()
		
		w = 600
		h = 200
		ws = self.winfo_screenwidth()
		hs = self.winfo_screenheight()
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		aboutWindow.geometry('%dx%d+%d+%d' % (w, h, x, y))
		aboutText = Label(aboutWindow, height=200, width=600, text="RGB Music is a software interface for creating music from an image through clicking on the image.\n\nInstructions: Load an image and start making sounds by clicking the image.\n\nCreators: Zehavit Leibovich & Oran Gilboa")
		aboutText.pack()
		aboutWindow.title("About RGB Music")
		aboutWindow.mainloop()

	def makesound(self, r, g, b):
		degree = int(self.get_value(DEGREE_RANGE, r))
		duration = self.get_value(DURATION_RANGE, g)
		amp = self.get_value(AMP_RANGE, b)

		client = OSC.OSCClient()
		client.connect(('127.0.0.1', 57120))
		msg = OSC.OSCMessage()
		msg.setAddress("/makesound")
		msg.append(degree)
		msg.append(duration)
		msg.append(amp)
		client.send(msg)

def main():
	app = App()
	app.mainloop()
	
if __name__ == "__main__":
	main()
