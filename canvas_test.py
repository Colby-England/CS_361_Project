from tkinter import * 
from tkinter import messagebox
from tkinter.colorchooser import askcolor
from tkinter.filedialog import asksaveasfilename
import tkinter.tix as tix
from PIL import ImageTk, Image, ImageGrab
import requests
from urllib.request import urlopen
import uuid
from io import BytesIO
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)


# Define Contants for use on the microservice call
SERVICE_URL = "https://www.weshavens.info:443/uploadV2"
SERVICE_PATH = "/CanvasApp/"


# Define tooltip constants
URL_HELP = "Enter the URL\nfor the image\nyou wish to\nedit."

BEGIN_HELP = "Start your project\nwith the image and size\nspecified above."

IMAGE_SIZE_HELP = """Select the size you would like
                     your image to be. The first number is
                     the width and the the second number is
                     the height."""

BRUSH_HELP = """This button toggles the
brush tool on and off.
When toggled on it will
allow you to click and
hold to draw on the picture."""

LINE_HELP = """This button toggles the
line tool on and off.
When toggled on it will
allow you to draw a line
between two points by clicking
at the first point, dragging the 
mouse to the second point and
releasing the mouse button."""

COLOR_HELP = """This button opens a color
select window. The color will then
be used for the drawing tools.
"""

BRUSH_SIZE_HELP = """This slide changes the width
of the brush tool. The units
are in pixels and range from
1 to 100.
"""

UNDO_HELP = """This button will remove
edits from the canvas
in reverse order of when
they were made."""

SAVE_HELP = """This button will open
a dialog to save your image."""

class CanvasPage():

    def __init__(self, master) -> None:

        # initialize variables for drawing tools
        self.left_mouse_position = "up"
        self.x_pos, self.y_pos = None, None
        self.x1, self.y1, self.x2, self.y2 = None, None, None, None
        self.selected_color = [None, "Black"]

        self.edit_num = 0
        

        self.undo_stack = []

        # create frame to hold canvas    
        self.canvas_frame = Frame(master)
        self.canvas_frame.grid(row=0, column=0)

        # create default canvas
        self.drawing_area = Canvas(self.canvas_frame, width=600, height=600, bg='white')
        self.drawing_area.pack()

        # create a frame to hold the drawing tool buttons
        self.button_frame = Frame(master)
        self.button_frame.grid(row=1, column=0, sticky='nsew')

        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(3, weight=1)
        self.button_frame.columnconfigure(6, weight=1)
        self.button_frame.columnconfigure(9, weight=1)

        # intialize list of tool types
        self.tools = ["brush", "line"]

        # create radio buttons of tool types
        self.selected_tool = StringVar(self.button_frame)
        self.selected_tool.set("brush")

        row_count = 0
        for tool in self.tools:
            Radiobutton(self.button_frame,
                        text=tool,
                        variable=self.selected_tool,
                        value=tool,
                        command=self.show_choice
            ).grid(row=row_count, column=1)
            row_count += 1
        
        # create tooltip for brush toggle
        self.brush_help_icon = Label(self.button_frame, text="?")
        self.brush_help = tix.Balloon(self.button_frame)
        self.brush_help.bind_widget(self.brush_help_icon, balloonmsg=BRUSH_HELP)
        self.brush_help_icon.grid(row=0, column=2)

        # line tooltip
        self.line_help_icon = Label(self.button_frame, text="?")
        self.line_help = tix.Balloon(self.button_frame)
        self.line_help.bind_widget(self.line_help_icon, balloonmsg=LINE_HELP)
        self.line_help_icon.grid(row=1, column=2)
        
        # slider tooltip
        self.brush_size_icon = Label(self.button_frame, text="?")
        self.brush_size_help = tix.Balloon(self.button_frame)
        self.brush_size_help.bind_widget(self.brush_size_icon, balloonmsg=BRUSH_SIZE_HELP)
        self.brush_size_icon.grid(row=0, column=5)

        # color chooser tooltip
        self.color_icon = Label(self.button_frame, text="?")
        self.color_help = tix.Balloon(self.button_frame)
        self.color_help.bind_widget(self.color_icon, balloonmsg=COLOR_HELP)
        self.color_icon.grid(row=1, column=5)

        # undo tooltip
        self.undo_help_icon = Label(self.button_frame, text="?")
        self.undo_help = tix.Balloon(self.button_frame)
        self.undo_help.bind_widget(self.undo_help_icon, balloonmsg=UNDO_HELP)
        self.undo_help_icon.grid(row=0, column=8)

        # save image tooltip
        self.save_help_icon = Label(self.button_frame, text="?")
        self.save_help = tix.Balloon(self.button_frame)
        self.save_help.bind_widget(self.save_help_icon, balloonmsg=SAVE_HELP)
        self.save_help_icon.grid(row=1, column=8)

        # create slider for line width
        self.line_scale = Scale(self.button_frame, from_=1, to=100, orient=HORIZONTAL)
        self.line_scale.grid(row=0, column=4)

        self.color_btn = Button(self.button_frame, text='Select a Color', command=self.choose_color, fg=self.selected_color[1])
        self.color_btn.grid(row=1, column=4)

        self.copy_image = Button(self.button_frame, text='Save Image', command= lambda: self.save_image(master, self.drawing_area))
        self.copy_image.grid(row=1, column=7)

        self.undo_btn = Button(self.button_frame, text='Undo', command=self.undo)
        self.undo_btn.grid(row=0, column=7)
        # open the start menu ontop of the root menu
        self.open_start_menu()

        self.help_btn = Button(self.button_frame, text="Help", command=self.open_help_menu)
        self.help_btn.grid(row=0, column=9)

        # bind events to the canvas
        self.drawing_area.bind("<Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.left_mouse_down)
        # master.bind("<ButtonPress-1>", self.left_mouse_down)
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

    def open_help_menu(self):

        self.help_menu = Toplevel(root)
        self.help_menu.state("zoomed")

        self.text = f'URL:\n{URL_HELP}\n\nBegin:\n{BEGIN_HELP}\n\nImage Size:\n{IMAGE_SIZE_HELP}\n\nBrush:\n{BRUSH_HELP}\n\nLine:\n{LINE_HELP}\n\nColor:\n{COLOR_HELP}\n\nBrush Size:\n{BRUSH_SIZE_HELP}\n\nUndo:\n{UNDO_HELP}\n\nSave:\n{SAVE_HELP}'
        self.help_text = Label(self.help_menu, text=self.text, font=("Arial", 8))

        self.help_text.pack()

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
        self.canvas_frame.config(width=int(self.dimensions[0]), height=int(self.dimensions[1]))
        # self.remote_image_url = self.request_image(self.url.get())['url']
        self.remote_image_url = 'https://pernetyp.sirv.com/CanvasApp/3fcd2d4c-7fb4-4919-851b-2426605178b3'
        self.open_image(self.remote_image_url, self.dimensions[0], self.dimensions[1])

    def request_image(self, image_url):
        self.request_params = {"url": image_url,
                  "path": SERVICE_PATH,
                  "file": str(uuid.uuid4())
        }
        
        request = requests.post(SERVICE_URL, data=self.request_params)

        return request.json()

    def open_image(self, img_url, width, height):

        self.modified_url = img_url + "?scale.width=" + width + "&scale.height=" + height + "&scale.option=ignore"

        self.raw_image = urlopen(self.modified_url).read()

        self.img = ImageTk.PhotoImage(Image.open(BytesIO(self.raw_image)))  # PIL solution
        self.drawing_area.create_image(0, 0, anchor=NW, image=self.img)
        self.splash_screen.destroy()

    def left_mouse_down(self, event=None):

        self.left_mouse_position = "down"

        self.x1 = event.x
        self.y1 = event.y

        # print(f'x: {self.x1}, y: {self.y1}')

    def left_mouse_up(self, event=None):

        self.left_mouse_position = "up"

        self.x_pos = None
        self.y_pos = None

        self.x2 = event.x
        self.y2 = event.y

        current_tool = self.selected_tool.get()

        if current_tool == "line":
            self.line_draw(event)
        
        self.undo_stack.append("edit#" + str(self.edit_num))
        print(self.undo_stack)
        self.edit_num += 1

    def motion(self, event=None):
        # print("motion detected")
        if self.selected_tool.get() == "brush":
            self.brush_draw(event)

    def line_draw(self, event=None):

        if None not in (self.x1, self.y1, self.x2, self.y2):
            event.widget.create_line(self.x1, self.y1, self.x2, self.y2, smooth=True, fill=self.selected_color[1], tags=("edit#" + str(self.edit_num)))

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
                                        joinstyle=ROUND,
                                        fill=self.selected_color[1],
                                        tags=("edit#" + str(self.edit_num)))
                
            self.x_pos = event.x
            self.y_pos = event.y

    def show_choice(self):
        print(self.selected_tool.get())

    def handle_focus_in(self, event=None):
        if self.url.get() == "Enter the image url:":
            event.widget.delete(0, END)
            event.widget.config(fg="black")
    
    def choose_color(self):
        self.selected_color = askcolor(title='Choose a color')
        self.color_btn.config(fg=self.selected_color[1])
        # print(self.selected_color)

    def save_image(self, master, widget):
        self.x = master.winfo_rootx() + widget.winfo_rootx()
        self.y = widget.winfo_rooty()

        # print(widget.winfo_geometry())
        # print(widget.winfo_rootx())
        # print(widget.winfo_rooty())
        # print(master.winfo_rootx())
        # print(master.winfo_rooty())

        self.canvas_geometry = widget.winfo_geometry().split(sep="+")
        # print(self.canvas_geometry)

        self.widget_x1 = int(self.canvas_geometry[1])
        self.widget_y1 = int(self.canvas_geometry[2])
        self.widget_x2 = self.widget_x1 + int(self.dimensions[0])
        self.widget_y2 = self.widget_y1 + int(self.dimensions[1])

        # print(f'{self.x}, {self.y}')
        # print(f"{self.x}, {self.y}, {self.x + self.widget_x2}, {self.y + self.widget_y2}")

        file_name = asksaveasfilename(initialdir="/", title="Save as...", filetypes=(("png files", ".png"), ("all files", "*.*")))
        # print(file_name)

        ImageGrab.grab().crop((self.x, self.y, self.x + self.widget_x2, self.y + self.widget_y2)).save(file_name)
        # .crop((self.x, self.y, self.x + self.widget_x2, self.y + self.widget_y2))

    def undo(self):

        if len(self.undo_stack) > 0:
            self.drawing_area.delete(self.undo_stack.pop())

# Create main window and set to full-screen
root = tix.Tk()
root.state('zoomed')

# configure grid rows & columns to center the frames within the main window
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# create a new Canvas page object 
canvas = CanvasPage(root)


root.mainloop()