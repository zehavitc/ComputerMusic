from Tkinter import *
from tkMessageBox import *
import tkFileDialog
from PIL import Image, ImageTk
import OSC
import pickle
import os

INSTRUMENTS = ["piano", "violin", "guitar", "bass"]
SETTINGS_FILENAME = 'settings.pkl'

# helper func
def entry_set_text(entry, text):
    entry.delete(0,END)
    entry.insert(0,text)

class ConfigFile():
	def __init__(self):
		# defaults
		self.instruments = ["piano"]
		self.amp_range = (0.4, 3)
		self.dur_range = (0.2, 0.8)
		self.deg_range = (0, 7)
		self.dur_neigh_scale = 5

	def save(self):
		print "saving configuration:"
		print self
		with open(SETTINGS_FILENAME,'wb') as outfile:
			pickle.dump(self, outfile)

	def set_values(self, instruments, amp_min,amp_max,deg_min,deg_max,dur_min,dur_max,dur_neigh_scale):
		self.instruments = instruments
		self.amp_range = (amp_min, amp_max)
		self.dur_range = (dur_min, dur_max)
		self.deg_range = (deg_min, deg_max)
		self.dur_neigh_scale = dur_neigh_scale

	def __repr__(self):
		return "instruments="+str(self.instruments)+"\namp_range="+str(self.amp_range)+"\ndur_range="+str(self.dur_range)+"\ndeg_range="+str(self.deg_range)+"\ndur_neigh_scale="+str(self.dur_neigh_scale)

	@classmethod
	def load(cls):
		if os.path.exists(SETTINGS_FILENAME):
			with open(SETTINGS_FILENAME,'rb') as infile:
				return pickle.load(infile)
		
		return ConfigFile()

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

		self.config_file = ConfigFile.load()
		print "config file was loaded:"
		print self.config_file
	
	def load_image(self):
		# TODO: load multiple images
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
		return float(range[0]) + ((num / 255.0) * (float(range[1])-float(range[0])))
		
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
		listbox.grid(row=0,column=1,padx=20, pady=20)
		for instrument in INSTRUMENTS:
			listbox.insert(END, instrument)	

		idx = 0
		for instrument in INSTRUMENTS:
			if instrument in self.config_file.instruments:
				listbox.select_set(idx)

			idx += 1	
		
		Label(settingsWindow, text="Amplitude range:").grid(row=1, column=0,padx=20, pady=20)
		f1 = Frame(settingsWindow)
		Label(f1, text="Min=").grid(row=0, column=0,padx=5, pady=5)
		amp_min = Entry(f1, width=5)
		entry_set_text(amp_min, self.config_file.amp_range[0])
		amp_min.grid(row=0, column=1,padx=5, pady=5)
		Label(f1, text="Max=").grid(row=0, column=2,padx=5, pady=5)
		amp_max=Entry(f1, width=5)
		entry_set_text(amp_max, self.config_file.amp_range[1])
		amp_max.grid(row=0, column=3,padx=5, pady=5)
		f1.grid(row=1,column=1)

		Label(settingsWindow, text="Degree range:").grid(row=2, column=0,padx=20, pady=20)
		f2 = Frame(settingsWindow)
		Label(f2, text="Min=").grid(row=0, column=0,padx=5, pady=5)
		deg_min = Entry(f2, width=5)
		entry_set_text(deg_min, self.config_file.deg_range[0])
		deg_min.grid(row=0, column=1,padx=5, pady=5)
		Label(f2, text="Max=").grid(row=0, column=2,padx=5, pady=5)
		deg_max=Entry(f2, width=5)
		entry_set_text(deg_max, self.config_file.deg_range[1])
		deg_max.grid(row=0, column=3,padx=5, pady=5)
		f2.grid(row=2,column=1)

		Label(settingsWindow, text="Duration range:").grid(row=3, column=0,padx=20, pady=20)		
		f3 = Frame(settingsWindow)
		Label(f3, text="Min=").grid(row=0, column=0,padx=5, pady=5)
		dur_min = Entry(f3, width=5)
		entry_set_text(dur_min, self.config_file.dur_range[0])
		dur_min.grid(row=0, column=1,padx=5, pady=5)
		Label(f3, text="Max=").grid(row=0, column=2,padx=5, pady=5)
		dur_max=Entry(f3, width=5)
		entry_set_text(dur_max, self.config_file.dur_range[1])
		dur_max.grid(row=0, column=3,padx=5, pady=5)
		f3.grid(row=3,column=1)

		Label(settingsWindow, text="Duration neighbours radius:").grid(row=4, column=0, padx=20, pady=20)
		dur_neigh_scale = Scale(settingsWindow, from_=1, to=50, orient=HORIZONTAL)
		dur_neigh_scale.set(self.config_file.dur_neigh_scale)
		dur_neigh_scale.grid(row=4,column=1, padx=20, pady=20)

		def validate(instruments, amp_min,amp_max,deg_min,deg_max,dur_min,dur_max,dur_neigh_scale):
			return "not impl."

		def save_btn(conf_file, window, instruments, amp_min,amp_max,deg_min,deg_max,dur_min,dur_max,dur_neigh_scale):
			validation = validate(instruments, amp_min,amp_max,deg_min,deg_max,dur_min,dur_max,dur_neigh_scale)
			if validation:
				showerror("Error", validation)
			else:
				window.destroy()	
				conf_file.set_values(instruments, amp_min,amp_max,deg_min,deg_max,dur_min,dur_max,dur_neigh_scale)
				conf_file.save()

		Button(settingsWindow, text="Save", command=lambda: save_btn(self.config_file, settingsWindow,[listbox.get(idx) for idx in listbox.curselection()], amp_min.get(),amp_max.get(),deg_min.get(),deg_max.get(),dur_min.get(),dur_max.get(),dur_neigh_scale.get())).grid(row=5, columnspan=2,padx=20, pady=20)
		
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
		# TODO: implement duration neighbours and different instruments
		degree = int(self.get_value(self.config_file.deg_range, r))
		duration = self.get_value(self.config_file.dur_range, g)
		amp = self.get_value(self.config_file.amp_range, b)

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
