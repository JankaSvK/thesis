import random
import threading
import tkinter as tk
import threading, sys, os
import functools
import matplotlib
import numpy as np
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import logging
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from queue import Queue
import cv2
from PIL import Image, ImageTk
import Config
from Arrow3D import Arrow3D
from QueuesProvider import QueuesProvider
from TrackersProvider import get_tracker_uid, get_tracker_by_uid
import tkinter.scrolledtext as tkst
import functools

class GUI(object):
    def __init__(self, stop_event, objects_count, tracked_points, trackers_initialization_events, image_streams, localization_data, console_output = None):
        self.camera_count = Config.camera_count()

        self.initialized = threading.Event()
        self.stop_event = stop_event
        self.trackers_initialization_events = trackers_initialization_events

        self.streams = image_streams
        self.video_views = []

        self.objects_count = objects_count
        self.tracked_points = tracked_points
        self.initialization_buttons = []

        self.localization_data = localization_data
        self.last_drawn_points = [(None, None) for _ in range(self.objects_count)]
        self.minimal_distance = 20 # between points to be scattered, in millimeters

        if console_output is None:
            console_output = []
        self.console_output = console_output
        self.outputted_messages = 0

        self.rgb_colors_for_objects = [(1, 0, 0), (0, 0, 1), (0, 1, 0), (0.5, 0.5, 0.5), (0.1, 0.2, 0.5)]
        if len(self.rgb_colors_for_objects) < self.objects_count:
            for _ in range(self.objects_count - len(self.rgb_colors_for_objects)):
                self.rgb_colors_for_objects.append([random.random() for _ in range(3)])

    def create_gui_objects(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.ask_quit)
        self.root.title("Thesis")

        for cam_ind in range(self.camera_count):

            # Create camera view windows
            video_view = tk.Label(self.root)
            click_bind = functools.partial(self.click_callback, id = cam_ind)
            video_view.bind("<Button-1>", click_bind)
            self.video_views.append(video_view)

            # Create buttons for tracker initialization
            buttons_frame = tk.Frame(self.root)
            buttons = []
            for obj_ind in range(self.objects_count):
                tracker_bind = functools.partial(self.tracker_callback, cam_ind=cam_ind, obj_ind=obj_ind)
                button = tk.Button(buttons_frame, text = "Initialize object " + str(obj_ind + 1), command=tracker_bind)
                buttons.append(button)
            self.initialization_buttons.append({'frame':buttons_frame, 'buttons':buttons})

        # Create graph
        self.graph_figure = Figure(figsize=(5, 4), dpi=100)
        self.graph = FigureCanvasTkAgg(self.graph_figure, master=self.root)

        self.subplot = self.graph_figure.add_subplot(111, projection='3d')
        self.subplot.mouse_init()

        # Create logging windows
        self.console = tkst.ScrolledText(self.root, height = 10)

    def set_gui_layout(self):
        # Place the camera vies
        for i in range(self.camera_count):
            self.video_views[i].grid(row = 0, column = i)

        # Place graph
        self.graph.get_tk_widget().grid(row = 0, column = self.camera_count, stick = "nsew")

        # Place the buttons
        for cam_ind, buttons_pack in enumerate(self.initialization_buttons):
            frame = buttons_pack['frame']
            buttons = buttons_pack['buttons']
            frame.grid(row=1, column = cam_ind, stick="w")
            for obj_ind, button in enumerate(buttons):
                button.grid(row = 0, column = obj_ind)

        # Place Console output
        self.console.grid(column=0, row = 2, columnspan=3, sticky="nsew")

    def draw_cameras(self, cameras):
        for i, cam in enumerate(cameras):
            start, end = cam
            self.subplot.text(*start, i)
            self.subplot.scatter(*start, s=0.5) # Plot is not changing camera view to see arrows, so creating point to include
            a = Arrow3D([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], mutation_scale=20, lw=1, arrowstyle="-|>", color="k")
            self.subplot.add_artist(a)

    def click_callback(self, event, id):
        QueuesProvider.add_mouse_click(window_index=id, x=event.x, y=event.y)

    def tracker_callback(self, cam_ind, obj_ind):
        uid = get_tracker_uid(cam_ind, obj_ind)
        self.initialization_buttons[cam_ind]['buttons'][obj_ind].config(relief='sunken')
        QueuesProvider.MouseClicks[cam_ind] = []
        self.trackers_initialization_events[uid].set()
        self.console_output.append("To select an object, draw a rectangle by clicking on its top left and bottom right corner.")

    def ask_quit(self):
        self.stop_event.set()

    def start(self):
        self.create_gui_objects()
        self.initialized.set() #initialization is finished, so the program may correctly start
        self.set_gui_layout()
        self.start_streaming()

    def start_streaming(self):
        self.last_scattered = None
        while not self.stop_event.is_set():
            self.update_cameras_views()

            for object_id in range(self.objects_count):
                self.draw_located_point(object_id)

            # Raise buttons
            for tracker_id, initialize_tracker in enumerate(self.trackers_initialization_events):
                if not initialize_tracker.is_set():
                    cam_ind, obj_id = get_tracker_by_uid(tracker_id)
                    self.initialization_buttons[cam_ind]['buttons'][obj_id].config(relief='raised')

            # Add messages to output
            if self.console_output and len(self.console_output) > self.outputted_messages:
                self.console.insert(tk.END, self.console_output[self.outputted_messages] + '\n')
                self.console.see(tk.END)
                self.outputted_messages += 1

            self.root.update_idletasks()
            self.root.update()

    def draw_located_point(self, object_id):
        if 0 != len(QueuesProvider.LocalizatedPoints3D[object_id]):
            point = QueuesProvider.LocalizatedPoints3D[object_id][-1].coords

            last_drawn, last_scattered = self.last_drawn_points[object_id]
            if last_drawn is None or np.linalg.norm(point - last_drawn) > self.minimal_distance:
                if last_drawn is not None:
                    zipped = list(zip(last_drawn, point))
                    self.subplot.plot(zipped[0], zipped[1], zipped[2], color=self.rgb_colors_for_objects[object_id])

                if last_scattered is not None:
                    last_scattered.set_visible(False)

                scattered = self.subplot.scatter(*point, c=self.rgb_colors_for_objects[object_id])
                self.last_drawn_points[object_id] = (point, scattered)
                self.graph.show()

    def update_cameras_views(self):
        for i, stream in enumerate(self.streams):
            if len(stream) == 0:
                image = self.create_empty_image()
            else:
                time, image = stream[-1].time, stream[-1].image
                self.add_tracker_information(i, image)
                image = self.process_image_for_displaying(image)

            self.video_views[i].configure(image=image)
            self.video_views[i].image = image

    def add_tracker_information(self, cam_ind, image):
        for obj_id in range(self.objects_count):
            uid = get_tracker_uid(cam_ind, obj_id)
            tracked_points = self.tracked_points[uid]

            if len(tracked_points) == 0:
                continue

            color = self.bgr_to_rgb_color_and_scale(self.rgb_colors_for_objects[obj_id])

            time, coords = tracked_points[-1]
            if coords is None:
                cv2.putText(image,
                            "Object " + str(obj_id + 1) + " was not found",
                            (10, (obj_id + 1) * 30), cv2.FONT_HERSHEY_COMPLEX, 1, color)
            else:
                cv2.circle(image, coords, 5, color, -1)

    def bgr_to_rgb_color_and_scale(self, color):
        return [c * 255 for c in reversed(color)]

    def process_image_for_displaying(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        return ImageTk.PhotoImage(image)

    def create_empty_image(self):# TODO fix resolution
        img  = Image.new("RGB", (640, 480), "white")
        return ImageTk.PhotoImage(image = img)

