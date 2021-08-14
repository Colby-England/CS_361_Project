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

import webbrowser


# Define Contants for use on the microservice call
SERVICE_URL = "https://www.weshavens.info:443/uploadV2"
SERVICE_PATH = "/CanvasApp/"


# Define tooltip constants
URL_HELP = "Enter the URL\nfor the image\nyou wish to\nedit."

BEGIN_HELP = "Start your project\nwith the image and size\nspecified above."

IMAGE_WIDTH_HELP = """Select the width of your
modified image. Valid 
ranges are from 100 pixels
to 720 pixels."""

IMAGE_HEIGHT_HELP = """Select the height of your
modified image. Valid 
ranges are from 100 pixels
to 576 pixels."""

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

        # initialize variables for tracking edits and undoing
        self.edit_num = 0
        self.undo_stack = []

        # create frame to hold canvas    
        self.canvas_frame = Frame(master)
        self.canvas_frame.grid(row=0, column=0)

        # create frame to hold buttons
        self.button_frame = Frame(master)
        self.button_frame.grid(row=1, column=0, sticky='nsew')

        # populate canvas and button frames
        self.config_button_frame(master)
        self.setup_drawing_area()

        # open the start menu ontop of the root menu
        self.open_start_menu()

    def setup_buttons(self, master):

        self.line_scale = Scale(self.button_frame, from_=1, to=100, orient=HORIZONTAL)
        self.line_scale.grid(row=0, column=4)

        self.color_btn = Button(self.button_frame, text='Select a Color', command=self.choose_color, fg=self.selected_color[1])
        self.color_btn.grid(row=1, column=4)

        self.copy_image = Button(self.button_frame, text='Save Image', command= lambda: self.save_image(master, self.drawing_area))
        self.copy_image.grid(row=1, column=7)

        self.undo_btn = Button(self.button_frame, text='Undo', command=self.confrim_undo)
        self.undo_btn.grid(row=0, column=7)

        self.help_btn = Button(self.button_frame, text="Help", command=self.open_help_menu)
        self.help_btn.grid(row=0, column=9)
    
    def setup_tooltips(self):

        help_text = [BRUSH_HELP, BRUSH_SIZE_HELP, UNDO_HELP, LINE_HELP, COLOR_HELP, SAVE_HELP]


        help_counter = 0
        for row_num in range(0, 2):
            for col_num in range(2, 11, 3):
                label = Label(self.button_frame, text="?")
                tooltip = tix.Balloon(self.button_frame)
                tooltip.bind_widget(label, balloonmsg=help_text[help_counter])
                label.grid(row=row_num, column=col_num)

                help_counter += 1

    def setup_tool_radio(self):

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
                        value=tool).grid(row=row_count, column=1)
            row_count += 1

    def config_button_frame(self, master):

        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(3, weight=1)
        self.button_frame.columnconfigure(6, weight=1)
        self.button_frame.columnconfigure(9, weight=1)

        self.setup_tooltips()
        self.setup_tool_radio()
        self.setup_buttons(master)
    
    def setup_drawing_area(self):
        # create default canvas
        self.drawing_area = Canvas(self.canvas_frame, width=600, height=600, bg='white')
        self.drawing_area.pack()

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
        self.splash_screen.grid_rowconfigure(5, weight=1)

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
        self.image_width_label = Label(self.splash_screen, text="Image Width")
        self.image_height_label = Label(self.splash_screen, text="Image Height")
        self.image_width_help_icon = Label(self.splash_screen, text="?")
        self.image_height_help_icon = Label(self.splash_screen, text="?")

        # create tooltip for image sizes
        self.image_width_help = tix.Balloon(self.splash_screen)
        self.image_width_help.bind_widget(self.image_width_help_icon, balloonmsg=IMAGE_WIDTH_HELP)

        self.image_height_help = tix.Balloon(self.splash_screen)
        self.image_height_help.bind_widget(self.image_height_help_icon, balloonmsg=IMAGE_HEIGHT_HELP)

        # create options for image size
        # self.image_sizes = ['320x240', '1024x768', '1280x1024', '720x576', '1280x720', '1920x1080']
        # self.image_size_string = StringVar(self.splash_screen)
        # self.image_size_string.set("Select Image Size")
        # self.image_size_option = OptionMenu(self.splash_screen, self.image_size_string, *self.image_sizes)
        # self.image_size_option.grid(row=2, column=2, pady=10)

        # create options for image width and height
        self.width_spin_val = StringVar()
        self.width_spin = Spinbox(self.splash_screen, from_=100, to=720, textvariable=self.width_spin_val)

        self.height_spin_val = StringVar()
        self.height_spin = Spinbox(self.splash_screen, from_=100, to=576, textvariable=self.height_spin_val)
        
        # place image sizes row in grid
        self.width_spin.grid(row=2, column=2, pady=10)
        self.height_spin.grid(row=3, column=2, pady=10)

        self.image_width_help_icon.grid(row=2, column=3, pady=10)
        self.image_height_help_icon.grid(row=3, column=3, pady=10)


        self.image_width_label.grid(row=2, column=1, pady=10)
        self.image_height_label.grid(row=3, column=1, pady=10)

        # create button to open canvas page
        self.begin_help_icon = Label(self.splash_screen, text="?")

        # create begin tooltip
        self.begin_help = tix.Balloon(self.splash_screen)
        self.begin_help.bind_widget(self.begin_help_icon, balloonmsg=BEGIN_HELP)

        # create begin project button
        self.begin_btn = Button(self.splash_screen, text='Open Canvas Page', command=self.start_project)
        
        # place begin project row in grid
        self.begin_btn.grid(row=4, column=2, pady=10)
        self.begin_help_icon.grid(row=4, column=3, pady=10)

    def open_help_menu(self):

        webbrowser.open("file://C:/Users/engla/Desktop/OSU_Online_Comp_Sci/2021_Summer/CS_361/Project/canvas_help.html")

    def start_project(self):

        if self.url.get() == "Enter the image url:":
            messagebox.showerror("URL Error", "Please enter an image url!")
            return
        
        try:
            int(self.width_spin_val.get())
        except:
            messagebox.showerror("Width Error", "Please enter a number between 100 & 720 for width!")
            return

        try:
            int(self.height_spin_val.get())
        except:
            messagebox.showerror("Height Error", "Please enter a number between 100 & 576 for height!")
            return

        if int(self.width_spin_val.get()) > 720 or int(self.width_spin_val.get()) < 100:
            messagebox.showerror("Width Error", "Please enter a number between 100 & 720 for width!")
            return

        if int(self.height_spin_val.get()) > 576 or int(self.height_spin_val.get()) < 100:
            messagebox.showerror("Height Error", "Please enter a number between 100 & 576 for height!")
            return

        self.resize_canvas()

    def resize_canvas(self):

        self.drawing_area.config(width=int(self.width_spin_val.get()), height=int(self.height_spin_val.get()))
        self.canvas_frame.config(width=int(self.width_spin_val.get()), height=int(self.height_spin_val.get()))

        self.image_width = self.width_spin_val.get()
        self.image_height = self.height_spin_val.get()

        self.open_image(self.width_spin_val.get(), self.height_spin_val.get())

    def open_image(self, width, height):

        self.image_type = self.url.get()[self.url.get().rfind("."):]

        self.remote_url = self.request_image(self.url.get())["url"]

        # self.img_url = 'https://pernetyp.sirv.com/CanvasApp/3fcd2d4c-7fb4-4919-851b-2426605178b3'

        self.modified_url = self.remote_url + "?scale.width=" + width + "&scale.height=" + height + "&scale.option=ignore"

        self.raw_image = urlopen(self.modified_url).read()

        self.img = ImageTk.PhotoImage(Image.open(BytesIO(self.raw_image)))  # PIL solution
        self.drawing_area.create_image(0, 0, anchor=NW, image=self.img)
        self.splash_screen.destroy()
    
    def request_image(self, image_url):
        self.request_params = {"url": image_url,
                  "path": SERVICE_PATH,
                  "file": str(uuid.uuid4()) + self.image_type
        }
        
        request = requests.post(SERVICE_URL, data=self.request_params)

        return request.json()

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

        if self.selected_tool.get() == "brush":
            self.brush_draw(event)

    def line_draw(self, event=None):

        if None not in (self.x1, self.y1, self.x2, self.y2):
            event.widget.create_line(self.x1,
                                     self.y1,
                                     self.x2,
                                     self.y2,
                                     smooth=True,
                                     fill=self.selected_color[1],
                                     tags=("edit#" + str(self.edit_num)))

    def brush_draw(self, event=None):

        if self.left_mouse_position == "down":

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

        self.canvas_geometry = widget.winfo_geometry().split(sep="+")

        self.widget_x1 = int(self.canvas_geometry[1])
        self.widget_y1 = int(self.canvas_geometry[2])
        self.widget_x2 = self.widget_x1 + int(self.image_width)
        self.widget_y2 = self.widget_y1 + int(self.image_height)

        file_name = asksaveasfilename(initialdir="/", title="Save as...", filetypes=(("png files", ".png"), ("all files", "*.*")))

        ImageGrab.grab().crop((self.x, self.y, self.x + self.widget_x2, self.y + self.widget_y2)).save(file_name)

    def undo(self):

        if len(self.undo_stack) > 0:
            self.drawing_area.delete(self.undo_stack.pop())

    def confrim_undo(self):

        answer = messagebox.askyesno(title='Confirm Undo', message="Are you sure that you want to undo?")
        
        if answer:
            self.undo()
            
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

if __name__ == "__main__":
    # Create main window and set to full-screen
    root = tix.Tk()
    root.state('zoomed')
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # configure grid rows & columns to center the frames within the main window
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # create a new Canvas page object 
    canvas = CanvasPage(root)


    root.mainloop()