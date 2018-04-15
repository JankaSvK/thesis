import signal
import threading
import tkinter as tk
import threading, sys, os


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

from Arrow3D import Arrow3D
from Provider import Provider
from QueuesProvider import QueuesProvider
from Tracking import Tracking


class GUI(object):
    def __init__(self, tracked_points):
        self.colors = ['C0', 'C1', 'C2']
        self.tracked_points = tracked_points
        self.stop_event = False
        self.initialized = threading.Event()

    def do_nothing(self):
        pass

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

    def tracker_callback(self, id):
        print("tracker initialization")
        self.tracker_buttons[id].config(relief='sunken')
#        Tracking.tracking_object.reinitialize_tracker(index=id)
        QueuesProvider.MouseClicks[id] = []

        print("id", id)
        Queue
        self.trackers_initialization_events[id].set()


        pass

    def ask_quit(self):
        self.stop_event = True
        # self.stop_event.set()
        self.exit.set()

       # raise RuntimeError

        #from Main import check_stop
        #check_stop("GUI to vyplo")


    def start(self, image_streams, exiting_program, trackers_initialization_events, localization_data = []):
        self.root = tk.Tk()
        f = Figure(figsize=(5, 4), dpi=100)
        self.subplot = f.add_subplot(111, projection='3d')
        print("Tkinter")
        self.exit = exiting_program
        self.root.protocol("WM_DELETE_WINDOW", self.ask_quit)

        self.trackers_initialization_events = trackers_initialization_events

        self.streams = image_streams
        self.localization_data = localization_data

        count = len(self.streams)
        self.create_labels_for_streams(count)


        self.graph = FigureCanvasTkAgg(f, master=self.root)

        self.subplot.mouse_init()
        self.organize_labels()

        self.initialized.set()
        self.start_streaming()

    def start_streaming(self):
        minimal_distance = 20
        self.last_point_drawn = None
        self.last_scattered = None
        while self.stop_event == False:
            self.update_cameras_views()
            self.draw_located_points(minimal_distance)

            self.root.update_idletasks()
            self.root.update()

    def draw_located_points(self, minimal_distance):
        if 0 != len(QueuesProvider.LocalizatedPoints3D):
            point = QueuesProvider.LocalizatedPoints3D[-1].coords
            if self.last_point_drawn is None or np.linalg.norm(point - self.last_point_drawn) > minimal_distance:
                if self.last_point_drawn is not None:
                    zipped = list(zip(self.last_point_drawn, point))
                    self.subplot.plot(zipped[0], zipped[1], zipped[2], self.colors[0])

                self.last_point_drawn = point
                if self.last_scattered is not None:
                    self.last_scattered.set_visible(False)

                self.last_scattered = self.subplot.scatter(*point, c = self.colors[1])
                print(point)

                self.graph.show()

    def update_cameras_views(self):
        for i, stream in enumerate(self.streams):
            if len(stream) < 1:
                image = self.create_empty_image()
            else:
                img = stream[-1]
                self.add_tracker_information(i, img)
                image = self.process_image(img)

            self.video_labels[i].configure(image=image)
            self.video_labels[i].image = image

    def add_tracker_information(self, i, img):
        if len(self.tracked_points[i]) > 0:
            coords = self.tracked_points[i][-1]
            if coords[1] is None:
                cv2.putText(img[1], "Object was not found", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
            else:
                cv2.circle(img[1], coords[1], 5, (0, 0, 255), -1)
                #print(i, coords[1])

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

            bind_tracker = functools.partial(self.tracker_callback, id=i)
            button = tk.Button(self.root, text="Initialize tracker", command=bind_tracker)
            self.tracker_buttons.append(button)


    def organize_labels(self):
        if len(self.video_labels) <= 10:
            for i, label in enumerate(self.video_labels):
                label.grid(row = 0, column = i)
                self.tracker_buttons[i].grid(row = 1, column = i)
        self.graph.get_tk_widget().grid(row = 0, column = len(self.video_labels))


    def create_empty_image(self):# TODO fix resolution
        img  = Image.new("RGB", (640, 480), "white")
        return ImageTk.PhotoImage(image = img)



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
