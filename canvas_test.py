from tkinter import *
from tkinter import messagebox
import tkinter.tix as tix
from PIL import ImageTk, Image
import tkinter.colorchooser

URL_HELP = "Enter the URL\nfor the image\nyou wish to\nedit."
IMAGE_SIZE_HELP = "Select the size you would like\nyour image to be. 1st number is\nthe width and then 2nd number is\nthe height."
BEGIN_HELP = "Start your project\nwith the image and size\nspecified above."

class CanvasPage():

    def __init__(self, master) -> None:

        # initialize variables for drawing tools
        self.left_mouse_position = "up"
        self.x_pos, self.y_pos = None, None
        self.x1, self.y1, self.x2, self.y2 = None, None, None, None

        self.undo_stack = []

        # create frame to hold canvas    
        self.canvas_frame = Frame(master)
        self.canvas_frame.grid(row=0, column=0)

        # create default canvas
        self.drawing_area = Canvas(self.canvas_frame, width=600, height=600, bg='white')
        self.drawing_area.pack()

        # create a frame to hold the drawing tool buttons
        self.button_frame = Frame(master)
        self.button_frame.grid(row=1, column=0)

        # intialize list of tool types
        self.tools = ["brush", "line", "text"]

        # create radio buttons of tool types
        self.selected_tool = StringVar(self.button_frame)
        self.selected_tool.set("brush")

        for tool in self.tools:
            Radiobutton(self.button_frame,
                        text=tool,
                        variable=self.selected_tool,
                        value=tool,
                        command=self.show_choice
            ).pack()
        
        # create slider for line width
        self.line_scale = Scale(self.button_frame, from_=1, to=100, orient=HORIZONTAL)
        self.line_scale.pack()

        # open the start menu ontop of the root menu
        self.open_start_menu()

        # bind events to the canvas
        self.drawing_area.bind("<Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.left_mouse_down)
        self.drawing_area.bind("<ButtonRelease-1>", self.left_mouse_up)

    def open_start_menu(self):
        
        # create toplevel menu on top of root menu
        self.splash_screen = Toplevel(root)
        self.splash_screen.attributes('-topmost', 'true')
        self.splash_screen.grab_set()

        # place top level in middle of root window
        self.splash_screen.geometry("300x300")

        # configure column and row weights to center the widgets
        self.splash_screen.grid_columnconfigure(0, weight=1)
        self.splash_screen.grid_columnconfigure(4, weight=1)
        self.splash_screen.grid_rowconfigure(0, weight=1)
        self.splash_screen.grid_rowconfigure(4, weight=1)

        # create url labels
        self.url_label = Label(self.splash_screen, text="Image URL")
        self.url_help_icon = Label(self.splash_screen, text="?")
        
        # create tooltip for url 
        self.url_help = tix.Balloon(self.splash_screen)
        self.url_help.bind_widget(self.url_help_icon, balloonmsg=URL_HELP)

        # create entry for URL
        self.url = StringVar(self.splash_screen)
        self.url.set("Enter the image url:")
        self.url_entry = Entry(self.splash_screen, textvariable=self.url, fg="grey")
        self.url_entry.bind("<FocusIn>", self.handle_focus_in)
       
        # place the url row in the grid
        self.url_entry.grid(row=1, column=2, pady=10)
        self.url_label.grid(row=1, column=1, pady=10)
        self.url_help_icon.grid(row=1, column=3, pady=10)

        # create image_sizes labels
        self.image_sizes_label = Label(self.splash_screen, text="Image Size")
        self.image_sizes_help_icon = Label(self.splash_screen, text="?")

        # create tooltip for image sizes
        self.image_sizes_help = tix.Balloon(self.splash_screen)
        self.image_sizes_help.bind_widget(self.image_sizes_help_icon, balloonmsg=IMAGE_SIZE_HELP)

        # create options for image size
        self.image_sizes = ['320x240', '1024x768', '1280x1024', '720x576', '1280x720', '1920x1080']
        self.image_size_string = StringVar(self.splash_screen)
        self.image_size_string.set("Select Image Size")
        self.image_size_option = OptionMenu(self.splash_screen, self.image_size_string, *self.image_sizes)
        
        # place image sizes row in grid
        self.image_size_option.grid(row=2, column=2, pady=10)
        self.image_sizes_help_icon.grid(row=2, column=3, pady=10)
        self.image_sizes_label.grid(row=2, column=1, pady=10)

        # create button to open canvas page
        self.begin_help_icon = Label(self.splash_screen, text="?")

        # create begin tooltip
        self.begin_help = tix.Balloon(self.splash_screen)
        self.begin_help.bind_widget(self.begin_help_icon, balloonmsg=BEGIN_HELP)

        # create begin project button
        self.begin_btn = Button(self.splash_screen, text='Open Canvas Page', command=self.start_project)
        
        # place begin project row in grid
        self.begin_btn.grid(row=3, column=2, pady=10)
        self.begin_help_icon.grid(row=3, column=3, pady=10)

    def start_project(self):

        if self.url.get() == "Enter the image url:":
            messagebox.showerror("showerror", "Please enter an image url")
            return
        
        if self.image_size_string.get() == "Select Image Size":
            messagebox.showerror("showerror", "Please select an image size")
            return

        self.resize_canvas()

    def resize_canvas(self):

        self.dimensions = self.image_size_string.get().split(sep='x')
        self.drawing_area.config(width=int(self.dimensions[0]), height=int(self.dimensions[1]))
        self.open_image(self.url.get())

    def open_image(self, img_url):

        self.img = ImageTk.PhotoImage(Image.open(img_url))  # PIL solution
        self.drawing_area.create_image(0, 0, anchor=NW, image=self.img)
        self.splash_screen.destroy()

    def left_mouse_down(self, event=None):

        self.left_mouse_position = "down"

        self.x1 = event.x
        self.y1 = event.y

        print(f'x: {self.x1}, y: {self.y1}')

    def left_mouse_up(self, event=None):

        self.left_mouse_position = "up"

        self.x_pos = None
        self.y_pos = None

        self.x2 = event.x
        self.y2 = event.y

        current_tool = self.selected_tool.get()

        if current_tool == "line":
            self.line_draw(event)

    def motion(self, event=None):
        # print("motion detected")
        if self.selected_tool.get() == "brush":
            self.brush_draw(event)

    def line_draw(self, event=None):

        if None not in (self.x1, self.y1, self.x2, self.y2):
            event.widget.create_line(self.x1, self.y1, self.x2, self.y2, smooth=True, fill="green")

    def brush_draw(self, event=None):

        if self.left_mouse_position == "down":
            # print("made it here")

            if self.x_pos is not None and self.y_pos is not None:
                event.widget.create_line(self.x_pos, 
                                        self.y_pos, 
                                        event.x, 
                                        event.y, 
                                        smooth=True, 
                                        width=self.line_scale.get(), 
                                        capstyle=ROUND, 
                                        joinstyle=ROUND)
                
            self.x_pos = event.x
            self.y_pos = event.y

    def show_choice(self):
        print(self.selected_tool.get())

    def handle_focus_in(self, event=None):
        if self.url.get() == "Enter the image url:":
            event.widget.delete(0, END)
            event.widget.config(fg="black")
        
# initialize root window and setup grid to center horizontally.
root = tix.Tk()
root.state('zoomed')

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
canvas = CanvasPage(root)
root.mainloop()