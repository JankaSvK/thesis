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
from Provider import Provider
from QueuesProvider import QueuesProvider
from TrackersProvider import get_tracker_uid
import tkinter.scrolledtext as tkst


class GUI(object):
    def __init__(self, tracked_points, console_output = []):
        self.outputted_messages = 0
        self.last_outputted_message = 0
        self.rgbcolors = [(1, 0, 0), (0, 0, 1), (0, 1, 0), (0.5, 0.5, 0.5), (0.1, 0.2, 0.5)]
        self.tracked_points = tracked_points
        self.stop_event = False
        self.initialized = threading.Event()
        self.objects_count = Config.objects_count
        self.last_drawn_points = [(None, None) for _ in range(self.objects_count)]
        self.tracker_buttons = []
        self.console_output = console_output

    def draw_cameras(self, cameras):
        for i, cam in enumerate(cameras):
            start, end = cam
            self.subplot.text(*start, i)
            self.subplot.scatter(*start, s=0.5) # Plot is not changing camera view to see arrows, so creating point to include
            a = Arrow3D([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], mutation_scale=20, lw=1, arrowstyle="-|>", color="k")
            self.subplot.add_artist(a)

    def click_callback(self, event, id):
        print ("clicked at", id,'-', event.x, event.y)
        QueuesProvider.add_mouse_click(window_index=id, x=event.x, y=event.y)

    def tracker_callback(self, cam_ind, obj_ind):
        uid = get_tracker_uid(cam_ind, obj_ind)
        self.tracker_buttons[uid].config(relief='sunken')
        QueuesProvider.MouseClicks[cam_ind] = []
        self.trackers_initialization_events[uid].set()

    def ask_quit(self):
        self.stop_event = True
        self.exit.set()


    def start(self, image_streams, exiting_program, trackers_initialization_events, localization_data = []):
        self.root = tk.Tk()
        f = Figure(figsize=(5, 4), dpi=100)
        self.subplot = f.add_subplot(111, projection='3d')
#        self.subplot.set_xlim([-500, 1000])
#        self.subplot.set_ylim([-500, 1000])
#        self.subplot.set_zlim([-500, 1000])

        self.exit = exiting_program
        self.root.protocol("WM_DELETE_WINDOW", self.ask_quit)

        self.trackers_initialization_events = trackers_initialization_events

        self.streams = image_streams
        self.localization_data = localization_data

        count = len(self.streams)
        self.create_labels_for_streams(count)
        self.console = tkst.ScrolledText(self.root, height=10)
        self.console.grid(column=0, row=2, columnspan=3, sticky="nsew")

        self.graph = FigureCanvasTkAgg(f, master=self.root)

        self.subplot.mouse_init()
        self.organize_labels()

        self.initialized.set()
        self.start_streaming()

    def start_streaming(self):
        minimal_distance = 20
        self.last_scattered = None
        while self.stop_event == False:
            self.update_cameras_views()

            for object_id in range(self.objects_count):
                self.draw_located_points(minimal_distance, object_id)

            for i, event in enumerate(self.trackers_initialization_events):
                if not event.is_set():
                    self.tracker_buttons[i].config(relief='raised')

            if self.console_output and len(self.console_output) > self.outputted_messages:
                self.console.insert(tk.END, self.console_output[self.outputted_messages] + '\n')
                self.outputted_messages += 1

            self.root.update_idletasks()
            self.root.update()

    def draw_located_points(self, minimal_distance, object_id):
        if 0 != len(QueuesProvider.LocalizatedPoints3D[object_id]):
            point = QueuesProvider.LocalizatedPoints3D[object_id][-1].coords

            last_drawn, last_scattered = self.last_drawn_points[object_id]
            if last_drawn is None or np.linalg.norm(point - last_drawn) > minimal_distance:
                if last_drawn is not None:
                    zipped = list(zip(last_drawn, point))
                    self.subplot.plot(zipped[0], zipped[1], zipped[2], color=self.rgbcolors[object_id])

                if last_scattered is not None:
                    last_scattered.set_visible(False)

                scattered = self.subplot.scatter(*point, c=self.rgbcolors[object_id])
                self.last_drawn_points[object_id] = (point, scattered)
                self.graph.show()

    def update_cameras_views(self):
        for i, stream in enumerate(self.streams):
            if len(stream) < 1:
                image = self.create_empty_image()
            else:
                img = stream[-1]
                img = (img[0], img[1])
                self.add_tracker_information(i, img)
                image = self.process_image(img)

            self.video_labels[i].configure(image=image)
            self.video_labels[i].image = image

    def add_tracker_information(self, i, img):
        for obj_id in range(self.objects_count):
            uid = get_tracker_uid(i, obj_id)
            tracked_points = self.tracked_points[uid]

            if len(tracked_points) == 0:
                continue
            color = self.process_rgb_color(self.rgbcolors[obj_id])
            coords = tracked_points[-1]
            if coords[1] is None:
                cv2.putText(img[1], "Object "+str(obj_id + 1)+" was not found", (10, (obj_id + 1) * 30), cv2.FONT_HERSHEY_COMPLEX, 1, color)
            else:
                cv2.circle(img[1], coords[1], 5, color, -1)

    def process_rgb_color(self, color):
        return [c * 255 for c in reversed(color)]

    def process_image(self, image):
        if isinstance(image, tuple):
            image = image[1]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        return ImageTk.PhotoImage(image)

    def create_labels_for_streams(self, count):
        self.video_labels = []
        self.tracker_buttons = []
        import functools
        for i in range(count):
            label = tk.Label(self.root)
            bind = functools.partial(self.click_callback, id=i)
            label.bind("<Button-1>", bind)
            self.video_labels.append(label)

    def organize_labels(self):
        if len(self.video_labels) <= 10:
            for i, label in enumerate(self.video_labels):
                label.grid(row = 0, column = i)
        self.create_buttons()
        self.graph.get_tk_widget().grid(row = 0, column = len(self.video_labels), stick="nsew")


    def create_empty_image(self):# TODO fix resolution
        img  = Image.new("RGB", (640, 480), "white")
        return ImageTk.PhotoImage(image = img)

    def create_buttons(self):
        for cam_ind in range(len(self.streams)):
            f = tk.Frame(self.root)
            for obj_ind in range(self.objects_count):
                bind_tracker = functools.partial(self.tracker_callback, cam_ind=cam_ind, obj_ind=obj_ind)
                b = tk.Button(f,
                              text = "Initialize object " + str(obj_ind + 1),
                              command = bind_tracker)
                b.grid(row = 0, column = obj_ind)
                self.tracker_buttons.append(b)
            f.grid(row = 1, column = cam_ind, stick="w")

if __name__ == '__main__':
    provider = Provider([0, 1])
    provider.initialize_cameras()
    provider.start_capturing()

    gui_actions_queue = Queue()
    gui = GUI(gui_actions_queue)

    queue = Queue()
    queue.put([1, 1, 1])
    queue.put([1, 1, 0])

    guiThread = threading.Thread(target=gui.start, args=(provider.images, queue), name="GUI")
    guiThread.start()
