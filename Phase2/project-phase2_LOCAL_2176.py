
# TODO: load multiple images
# TODO: let the user choose the role for every coordinate in (r,g,b)
# TODO: status bar?

from Tkinter import *
from tkMessageBox import *
import tkFileDialog
from PIL import Image, ImageTk
import OSC
import pickle
import os
from collections import namedtuple
import time

INSTRUMENTS = ["piano", "violin", "bass"]
SETTINGS_FILENAME = 'settings.pkl'
SERVER_IP='127.0.0.1'
SERVER_PORT=57120
SERVER_MSG_ADDRESS="/makesound"
SERVER_MSG_START_RECORDING="/startRecording"
SERVER_MSG_STOP_RECORDING="/stopRecording"


# helper func
def entry_set_text(entry, text):
    entry.delete(0,END)
    entry.insert(0,text)

SongItem = namedtuple('SongItem', ['instrument', 'deg', 'amp', 'dur'])

class ConfigFile():
	def __init__(self):
		# default values
		self.instruments = INSTRUMENTS
		self.amp_range = (0.4, 3)
		self.amp_avg = False
		self.dur_range = (0.2, 0.8)
		self.dur_avg = False
		self.deg_range = (0, 7)
		self.deg_avg = False
		self.neigh_scale = 5

	def save(self):
		print "saving configuration:"
		print self
		with open(SETTINGS_FILENAME,'wb') as outfile:
			pickle.dump(self, outfile)

	def set_values(self, instruments, amp_min,amp_max,amp_avg,deg_min,deg_max,deg_avg,dur_min,dur_max,dur_avg,neigh_scale):
		self.instruments = instruments
		self.amp_range = (amp_min, amp_max)
		self.dur_range = (dur_min, dur_max)
		self.deg_range = (deg_min, deg_max)
		self.amp_avg = amp_avg
		self.dur_avg = dur_avg
		self.deg_avg = deg_avg
		self.neigh_scale = neigh_scale

	def __repr__(self):
		return "instruments="+str(self.instruments)+"\namp_range="+str(self.amp_range)+"\ndur_range="+str(self.dur_range)+"\ndeg_range="+str(self.deg_range)+"\nneigh_scale="+str(self.neigh_scale)+"\namp_avg="+str(self.amp_avg)+"\ndur_avg="+str(self.dur_avg)+"\ndeg_avg="+str(self.deg_avg)

	@classmethod
	def load(cls):
		if os.path.exists(SETTINGS_FILENAME):
			with open(SETTINGS_FILENAME,'rb') as infile:
				return pickle.load(infile)
		
		return ConfigFile()

class StatusBar(Frame):   
    def __init__(self, master):
        Frame.__init__(self, master)
        self.variable=StringVar()        
        self.label=Label(self, bd=1, relief=SUNKEN, anchor=W,
                           textvariable=self.variable,
                           font=('arial',10,'normal'))
        self.variable.set('Status Bar')
        self.label.pack(fill=X)        
        self.pack()

class App(Tk):
	def __init__(self):
		Tk.__init__(self)
		self.title("RGB Music")
		self.song = []
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
		songmenu = Menu(menubar, tearoff=0)
		songmenu.add_command(label="Reset", command=self.reset)
		songmenu.add_command(label="Play", command=self.play)
		songmenu.add_command(label="Export to file", command=self.export)
		menubar.add_cascade(label="Song", menu=songmenu)
		helpmenu = Menu(menubar, tearoff=0)
		helpmenu.add_command(label="About", command=self.about)
		menubar.add_cascade(label="Help", menu=helpmenu)
		self.config(menu=menubar)
		
		#d=StatusBar(self)

		self.config_file = ConfigFile.load()
		print "config file was loaded:"
		print self.config_file

	def reset(self):
		self.song = []
		showinfo("Success", "Song was reset successfuly")

	def play(self):
		if not self.song:
			showerror("Error", "Song is empty")
			return

		self.send_make_sound_to_server(self.song)

	def export(self):
		if not self.song:
			showerror("Error", "Song is empty")
			return
		
		path_to_save = tkFileDialog.asksaveasfilename(initialdir = ".",title = "Export to file",filetypes = [("aiff files","*.aiff")])
		if path_to_save:
			self.send_make_sound_to_server(self.song, path_to_save + ".aiff")

	def load_image(self):
		ftypes = [('Image files', '*.png;*.jpg;*.jpeg')]
		imagePath = tkFileDialog.askopenfilename(initialdir = ".",title = "Select image file",filetypes = ftypes)
		if imagePath:
			self.img = Image.open(imagePath)
			self.imgTk = ImageTk.PhotoImage(self.img)

			# TODO: show border for image
			self.imageLabel = Label(self, image = self.imgTk)
			self.imageLabel.pack(side = "bottom", fill = "both", expand = "yes")
			self.bind('<Button-1>', self.click)
			
	def createSongItemFromRGB(self, instrument, degree, duration, amplitude):
		return SongItem(instrument = instrument, deg = degree, dur = duration, amp = amplitude)

	def calculate_params(self, rgb, point):
		def get_value(range, num):
			return float(range[0]) + ((num / 255.0) * (float(range[1])-float(range[0])))

		def calc_avg_rgb(img, point, radius):
			(x,y) = point
			sum = [0.0,0.0,0.0]
			count = 0
			for i in xrange(x-radius, x+radius+1):
				for j in xrange(y-radius, y+radius+1):
					if i >= 0 and j >=0 and i < img.width and j < img.height:
						(r,g,b) = img.getpixel((i,j))[:3]
						sum[0] = sum[0] + r
						sum[1] = sum[1] + g
						sum[2] = sum[2] + b
						count += 1

			sum[0] = sum[0] / count
			sum[1] = sum[1] / count
			sum[2] = sum[2] / count
			return sum

		(r,g,b) = rgb
		(ar,ag,ab) = calc_avg_rgb(self.img, point, self.config_file.neigh_scale)

		if self.config_file.deg_avg:
			r = ar
		if self.config_file.dur_avg:
			g = ag
		if self.config_file.amp_avg:
			b = ab

		degree = int(get_value(self.config_file.deg_range, r))
		duration = get_value(self.config_file.dur_range, g)
		amplitude = get_value(self.config_file.amp_range, b)
		instrument = self.config_file.instruments[int(get_value(range(len(self.config_file.instruments)), r+g+b))]
		return instrument, degree, duration, amplitude

	def click(self, event):
		x, y = event.x, event.y
		print('The user clicked on {}, {}'.format(x, y))
		rgb = self.img.getpixel((x,y))[:3]
		print("rgb="+str(rgb))
		params = self.calculate_params(rgb, (x,y))
		item = self.createSongItemFromRGB(*params)
		self.makesound(item)
		self.song.append(item) 
		print str(item)+" was appended to song"
		
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
		
		Label(settingsWindow, text="Instruments:").grid(row=0, column=0,padx=10, pady=10)
		listbox = Listbox(settingsWindow, selectmode=MULTIPLE)
		listbox.configure(exportselection=False)
		listbox.grid(row=0,column=1,padx=10, pady=10)
		for instrument in INSTRUMENTS:
			listbox.insert(END, instrument)	

		idx = 0
		for instrument in INSTRUMENTS:
			if instrument in self.config_file.instruments:
				listbox.select_set(idx)
			idx += 1	
		
		Label(settingsWindow, text="Amplitude range:").grid(row=1, column=0,padx=10, pady=10)
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

		Label(settingsWindow, text="Degree range:").grid(row=2, column=0,padx=10, pady=10)
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

		Label(settingsWindow, text="Duration range:").grid(row=3, column=0,padx=10, pady=10)		
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

		Label(settingsWindow, text="Neighbours avg radius:").grid(row=4, column=0, padx=10, pady=10)
		neigh_scale = Scale(settingsWindow, from_=1, to=50, orient=HORIZONTAL)
		neigh_scale.set(self.config_file.neigh_scale)
		neigh_scale.grid(row=4,column=1, padx=10, pady=10)
		
		Label(settingsWindow, text="Amplitude average?").grid(row=5, column=0, padx=10, pady=10)
		amp_avg = IntVar()
		amp_avg_checkbutton = Checkbutton(settingsWindow, text="", variable=amp_avg)
		if self.config_file.amp_avg:
			amp_avg_checkbutton.select()
		amp_avg_checkbutton.grid(row=5,column=1, padx=10, pady=10)

		Label(settingsWindow, text="Degree average?").grid(row=6, column=0, padx=10, pady=10)
		deg_avg = IntVar()
		deg_avg_checkbutton = Checkbutton(settingsWindow, text="", variable=deg_avg)
		if self.config_file.deg_avg:
			deg_avg_checkbutton.select()
		deg_avg_checkbutton.grid(row=6,column=1, padx=10, pady=10)

		Label(settingsWindow, text="Duration average?").grid(row=7, column=0, padx=10, pady=10)
		dur_avg = IntVar()
		dur_avg_checkbutton = Checkbutton(settingsWindow, text="", variable=dur_avg)
		if self.config_file.dur_avg:
			dur_avg_checkbutton.select()
		dur_avg_checkbutton.grid(row=7,column=1, padx=10, pady=10)

		def validate(instruments, amp_min,amp_max,deg_min,deg_max,dur_min,dur_max):
			try:
				if not instruments:
					return "Pick at least one instrument"
				if not amp_min or not amp_max or float(amp_min) > float(amp_max):
					return "Invalid amplitude range"
				if not dur_min or not dur_max or float(dur_min) > float(dur_max):
					return "Invalid duration range"
				if not deg_min or not deg_max or int(deg_min) > int(deg_max):
					return "Invalid degree range"
			except:
				return "Please insert only numbers"

		def save_btn(conf_file, window, instruments, amp_min,amp_max,amp_avg, deg_min,deg_max,deg_avg, dur_min,dur_max,dur_avg,neigh_scale):
			validation = validate(instruments, amp_min,amp_max,deg_min,deg_max,dur_min,dur_max)
			if validation:
				showerror("Error", validation)
			else:
				window.destroy()	
				conf_file.set_values(instruments, amp_min,amp_max,amp_avg,deg_min,deg_max,deg_avg,dur_min,dur_max,dur_avg,neigh_scale)
				conf_file.save()

		Button(settingsWindow, text="Save", command=lambda: save_btn(self.config_file, settingsWindow,[listbox.get(idx) for idx in listbox.curselection()], amp_min.get(),amp_max.get(),bool(amp_avg.get()),deg_min.get(),deg_max.get(),bool(deg_avg.get()),dur_min.get(),dur_max.get(),bool(dur_avg.get()),neigh_scale.get())).grid(row=8, columnspan=2,padx=10, pady=10)
		
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

	def send_start_recording_command_to_server(self, path_to_save):
		client = OSC.OSCClient()
		client.connect((SERVER_IP, SERVER_PORT))
		msg = OSC.OSCMessage()
		msg.setAddress(SERVER_MSG_START_RECORDING)
		msg.append(path_to_save)
		client.send(msg)


	def send_stop_recording_command_to_server(self, path_to_save):
		client = OSC.OSCClient()
		client.connect((SERVER_IP, SERVER_PORT))
		msg = OSC.OSCMessage()
		msg.setAddress(SERVER_MSG_STOP_RECORDING)
		msg.append(path_to_save)
		client.send(msg)

	def send_make_sound_to_server(self, songItems, path_to_save =""):
		path_to_save = '/'.join(path_to_save.split('\\'))
		self.send_start_recording_command_to_server(path_to_save)
		client = OSC.OSCClient()
		client.connect((SERVER_IP, SERVER_PORT))
		msg = OSC.OSCMessage()
		msg.setAddress(SERVER_MSG_ADDRESS)
		#itemsToSend = [list(item) for item in items]
		msg.append(len(songItems))
		msg.append(path_to_save)
		totalDuration = 0;
		for songItem in songItems:
			msg.append(songItem.instrument)
			msg.append(songItem.deg)
			totalDuration+=songItem.dur
			msg.append(songItem.dur)
			msg.append(songItem.amp)

		client.send(msg)
		time.sleep(totalDuration)
		self.send_stop_recording_command_to_server(path_to_save)

	def makesound(self, songItem):
		self.send_make_sound_to_server([songItem])

def main():
	app = App()
	app.mainloop()
	
if __name__ == "__main__":
	main()
